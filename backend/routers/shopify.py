# backend/routers/shopify.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import pandas as pd
import shutil
import uuid
from datetime import datetime
from typing import Optional

from backend.database import get_db

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads/shopify")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Store latest parsed data (could move to database model later)
_shopify_data = {
    "orders": None,
    "conversion": None,
    "products": None,
    "sales": None,
    "uploaded_at": None
}

def parse_shopify_csv(file_path: str, report_type: str) -> pd.DataFrame:
    """Parse Shopify CSV with proper handling"""
    try:
        df = pd.read_csv(file_path)
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error parsing {report_type}: {e}")
        return None

@router.post("/upload")
async def upload_shopify_report(
    file: UploadFile = File(...),
    report_type: Optional[str] = "auto",
    db: Session = Depends(get_db)
):
    """Upload and parse Shopify export files"""
    file_ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_name
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Detect report type from filename if auto
    filename_lower = file.filename.lower()
    if "orders over time" in filename_lower:
        report_type = "orders"
    elif "conversion" in filename_lower:
        report_type = "conversion"
    elif "sales by product" in filename_lower:
        report_type = "products"
    elif "sales over time" in filename_lower:
        report_type = "sales"
    
    # Parse the CSV
    df = parse_shopify_csv(str(file_path), report_type)
    
    if df is None:
        return {"error": "Failed to parse CSV", "filename": file.filename}
    
    # Store parsed data
    global _shopify_data
    _shopify_data[report_type] = df.to_dict('records')
    _shopify_data["uploaded_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "filename": file.filename,
        "report_type": report_type,
        "records": len(df),
        "columns": list(df.columns)
    }

@router.get("/dashboard")
def get_shopify_dashboard():
    """Get Shopify dashboard metrics from uploaded data"""
    
    if not any([_shopify_data.get("orders"), _shopify_data.get("sales")]):
        return {
            "store_name": "Crooks & Castles",
            "message": "Upload Shopify reports to see data",
            "orders_today": 0,
            "revenue_today": 0,
            "products_count": 0,
            "recent_orders": []
        }
    
    # Calculate metrics from uploaded data
    orders_data = _shopify_data.get("orders", [])
    sales_data = _shopify_data.get("sales", [])
    products_data = _shopify_data.get("products", [])
    conversion_data = _shopify_data.get("conversion", [])
    
    # Aggregate totals
    total_orders = sum([row.get("Orders", 0) for row in orders_data if row.get("Orders")])
    total_revenue = sum([row.get("Net sales", 0) for row in sales_data if row.get("Net sales")])
    avg_order_value = sum([row.get("Average order value", 0) for row in orders_data if row.get("Average order value")]) / len(orders_data) if orders_data else 0
    
    # Latest day metrics (most recent date)
    latest_orders = orders_data[-1] if orders_data else {}
    latest_sales = sales_data[-1] if sales_data else {}
    latest_conversion = conversion_data[-1] if conversion_data else {}
    
    # Top products
    top_products = []
    if products_data:
        sorted_products = sorted(products_data, key=lambda x: x.get("Net sales", 0), reverse=True)[:5]
        top_products = [
            {
                "title": p.get("Product title"),
                "sales_count": p.get("Net items sold", 0),
                "revenue": f"{p.get('Net sales', 0):,.2f}",
                "price": f"{p.get('Net sales', 0) / p.get('Net items sold', 1) if p.get('Net items sold') else 0:.2f}"
            }
            for p in sorted_products
        ]
    
    return {
        "store_name": "Crooks & Castles",
        "orders_today": latest_orders.get("Orders", 0),
        "revenue_today": latest_sales.get("Net sales", 0),
        "products_count": len(products_data) if products_data else 0,
        "customers_count": 0,  # Not in these reports
        "recent_orders": [],  # Not in these reports
        "top_products": top_products,
        "period_metrics": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "conversion_rate": latest_conversion.get("Conversion rate", 0) if latest_conversion else 0
        },
        "last_updated": _shopify_data.get("uploaded_at")
    }

@router.get("/test-connection")
def test_shopify_connection():
    """Check if data is uploaded"""
    has_data = any([_shopify_data.get(k) for k in ["orders", "sales", "products", "conversion"]])
    return {
        "connected": has_data,
        "last_upload": _shopify_data.get("uploaded_at"),
        "reports_uploaded": [k for k in ["orders", "sales", "products", "conversion"] if _shopify_data.get(k)]
    }

@router.get("/analytics")
def get_analytics():
    """Get detailed analytics from uploaded data"""
    
    orders_data = _shopify_data.get("orders", [])
    sales_data = _shopify_data.get("sales", [])
    conversion_data = _shopify_data.get("conversion", [])
    
    if not any([orders_data, sales_data]):
        return {"message": "No data available"}
    
    # Calculate trends
    total_orders = sum([row.get("Orders", 0) for row in orders_data if row.get("Orders")])
    total_revenue = sum([row.get("Net sales", 0) for row in sales_data if row.get("Net sales")])
    avg_conversion = sum([row.get("Conversion rate", 0) for row in conversion_data if row.get("Conversion rate")]) / len(conversion_data) if conversion_data else 0
    
    # Daily breakdown for charts
    daily_data = []
    for row in sales_data:
        if row.get("Day"):
            daily_data.append({
                "date": row.get("Day"),
                "orders": row.get("Orders", 0),
                "revenue": row.get("Net sales", 0),
                "gross_sales": row.get("Gross sales", 0),
                "discounts": row.get("Discounts", 0)
            })
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_conversion_rate": avg_conversion,
        "daily_breakdown": daily_data,
        "period": f"{sales_data[0].get('Day')} to {sales_data[-1].get('Day')}" if sales_data else "Unknown"
    }

@router.get("/products")
def get_products():
    """Get product performance data"""
    products_data = _shopify_data.get("products", [])
    
    if not products_data:
        return {"message": "Upload 'Total sales by product' report"}
    
    return {
        "products": products_data,
        "total_products": len(products_data),
        "top_performers": sorted(products_data, key=lambda x: x.get("Net sales", 0), reverse=True)[:10]
    }
