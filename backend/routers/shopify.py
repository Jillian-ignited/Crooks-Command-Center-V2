# backend/routers/shopify.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import csv
import io
import uuid

router = APIRouter()

# Mock Shopify data for realistic responses
SHOPIFY_MOCK_DATA = {
    "store_info": {
        "name": "Crooks & Castles",
        "domain": "crooksandcastles.com",
        "currency": "USD",
        "timezone": "America/Los_Angeles",
        "plan": "Shopify Plus",
        "created_at": "2020-03-15T10:00:00Z"
    },
    "recent_orders": [
        {
            "id": "5001",
            "order_number": "#CC-5001",
            "customer": "Marcus Johnson",
            "email": "marcus.j@email.com",
            "total": 189.99,
            "status": "fulfilled",
            "created_at": "2025-09-30T14:30:00Z",
            "items": [
                {"name": "Medusa Chain Hoodie", "quantity": 1, "price": 149.99},
                {"name": "Crown Logo Beanie", "quantity": 1, "price": 39.99}
            ]
        },
        {
            "id": "5002", 
            "order_number": "#CC-5002",
            "customer": "Sarah Chen",
            "email": "sarah.chen@email.com",
            "total": 299.97,
            "status": "processing",
            "created_at": "2025-09-30T12:15:00Z",
            "items": [
                {"name": "Bandana Print Joggers", "quantity": 2, "price": 89.99},
                {"name": "Castle Logo Tee", "quantity": 1, "price": 59.99}
            ]
        },
        {
            "id": "5003",
            "order_number": "#CC-5003", 
            "customer": "David Rodriguez",
            "email": "d.rodriguez@email.com",
            "total": 449.95,
            "status": "fulfilled",
            "created_at": "2025-09-30T09:45:00Z",
            "items": [
                {"name": "Premium Leather Jacket", "quantity": 1, "price": 399.99},
                {"name": "Skull Chain Necklace", "quantity": 1, "price": 49.96}
            ]
        }
    ],
    "top_products": [
        {
            "id": "prod_001",
            "title": "Medusa Chain Hoodie",
            "handle": "medusa-chain-hoodie",
            "price": 149.99,
            "inventory": 45,
            "sales_30d": 127,
            "revenue_30d": 19048.73,
            "image": "https://cdn.shopify.com/medusa-hoodie.jpg"
        },
        {
            "id": "prod_002",
            "title": "Bandana Print Joggers", 
            "handle": "bandana-print-joggers",
            "price": 89.99,
            "inventory": 78,
            "sales_30d": 89,
            "revenue_30d": 8009.11,
            "image": "https://cdn.shopify.com/bandana-joggers.jpg"
        },
        {
            "id": "prod_003",
            "title": "Castle Logo Tee",
            "handle": "castle-logo-tee", 
            "price": 59.99,
            "inventory": 156,
            "sales_30d": 203,
            "revenue_30d": 12177.97,
            "image": "https://cdn.shopify.com/castle-tee.jpg"
        }
    ]
}

@router.get("/dashboard")
async def get_shopify_dashboard():
    """Get comprehensive Shopify dashboard data"""
    
    try:
        # Calculate metrics from mock data
        total_orders = len(SHOPIFY_MOCK_DATA["recent_orders"])
        total_revenue = sum(order["total"] for order in SHOPIFY_MOCK_DATA["recent_orders"])
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Calculate 30-day metrics from top products
        total_sales_30d = sum(product["sales_30d"] for product in SHOPIFY_MOCK_DATA["top_products"])
        total_revenue_30d = sum(product["revenue_30d"] for product in SHOPIFY_MOCK_DATA["top_products"])
        
        dashboard_data = {
            "store_info": SHOPIFY_MOCK_DATA["store_info"],
            "metrics": {
                "total_orders_today": total_orders,
                "revenue_today": round(total_revenue, 2),
                "avg_order_value": round(avg_order_value, 2),
                "conversion_rate": 3.2,
                "total_customers": 1247,
                "total_products": 89,
                "inventory_value": 156789.45,
                "sales_30d": total_sales_30d,
                "revenue_30d": round(total_revenue_30d, 2),
                "growth_rate": 12.5
            },
            "recent_orders": SHOPIFY_MOCK_DATA["recent_orders"][:5],
            "top_products": SHOPIFY_MOCK_DATA["top_products"],
            "traffic": {
                "sessions_today": 1456,
                "page_views": 4321,
                "bounce_rate": 45.2,
                "avg_session_duration": "2:34"
            },
            "alerts": [
                {
                    "type": "inventory",
                    "message": "Low stock alert: Medusa Chain Hoodie (45 units remaining)",
                    "severity": "warning"
                },
                {
                    "type": "performance", 
                    "message": "Sales up 12.5% compared to last month",
                    "severity": "success"
                }
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load Shopify dashboard: {str(e)}")

@router.get("/test-connection")
async def test_shopify_connection():
    """Test connection to Shopify store"""
    
    try:
        # Simulate connection test
        connection_status = {
            "connected": True,
            "store_name": SHOPIFY_MOCK_DATA["store_info"]["name"],
            "domain": SHOPIFY_MOCK_DATA["store_info"]["domain"],
            "plan": SHOPIFY_MOCK_DATA["store_info"]["plan"],
            "api_version": "2024-01",
            "permissions": [
                "read_orders",
                "read_products", 
                "read_customers",
                "read_analytics",
                "write_products"
            ],
            "last_sync": datetime.now().isoformat(),
            "status": "healthy"
        }
        
        return {
            "success": True,
            "connection": connection_status,
            "message": "Successfully connected to Shopify store"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Shopify connection: {str(e)}")

@router.get("/orders")
async def get_shopify_orders(
    limit: int = 50,
    status: Optional[str] = None,
    since: Optional[str] = None
):
    """Get Shopify orders with filtering"""
    
    try:
        orders = SHOPIFY_MOCK_DATA["recent_orders"].copy()
        
        # Apply status filter
        if status:
            orders = [order for order in orders if order["status"] == status]
        
        # Apply date filter
        if since:
            since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
            orders = [
                order for order in orders 
                if datetime.fromisoformat(order["created_at"].replace('Z', '+00:00')) >= since_date
            ]
        
        # Apply limit
        orders = orders[:limit]
        
        # Add summary statistics
        total_value = sum(order["total"] for order in orders)
        avg_value = total_value / len(orders) if orders else 0
        
        return {
            "orders": orders,
            "summary": {
                "total_orders": len(orders),
                "total_value": round(total_value, 2),
                "average_value": round(avg_value, 2),
                "status_breakdown": {
                    "fulfilled": len([o for o in orders if o["status"] == "fulfilled"]),
                    "processing": len([o for o in orders if o["status"] == "processing"]),
                    "pending": len([o for o in orders if o["status"] == "pending"])
                }
            },
            "filters_applied": {
                "status": status,
                "since": since,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Shopify orders: {str(e)}")

@router.get("/analytics")
async def get_shopify_analytics(
    period: str = "30d",
    metrics: Optional[str] = None
):
    """Get Shopify analytics and performance metrics"""
    
    try:
        # Generate analytics based on period
        if period == "7d":
            days = 7
            multiplier = 0.2
        elif period == "30d":
            days = 30
            multiplier = 1.0
        elif period == "90d":
            days = 90
            multiplier = 3.2
        else:
            days = 30
            multiplier = 1.0
        
        base_revenue = 39235.67 * multiplier
        base_orders = 419 * multiplier
        base_sessions = 12456 * multiplier
        
        analytics_data = {
            "period": period,
            "date_range": {
                "start": (datetime.now() - timedelta(days=days)).isoformat(),
                "end": datetime.now().isoformat()
            },
            "revenue": {
                "total": round(base_revenue, 2),
                "growth": 12.5 if period == "30d" else 8.3,
                "daily_average": round(base_revenue / days, 2),
                "trend": "increasing"
            },
            "orders": {
                "total": int(base_orders),
                "growth": 15.2 if period == "30d" else 11.1,
                "daily_average": round(base_orders / days, 1),
                "avg_order_value": round(base_revenue / base_orders, 2)
            },
            "traffic": {
                "sessions": int(base_sessions),
                "page_views": int(base_sessions * 2.8),
                "conversion_rate": 3.36,
                "bounce_rate": 42.1,
                "avg_session_duration": "2:47"
            },
            "top_channels": [
                {"channel": "Direct", "sessions": int(base_sessions * 0.35), "revenue": round(base_revenue * 0.42, 2)},
                {"channel": "Instagram", "sessions": int(base_sessions * 0.28), "revenue": round(base_revenue * 0.31, 2)},
                {"channel": "Google Ads", "sessions": int(base_sessions * 0.22), "revenue": round(base_revenue * 0.18, 2)},
                {"channel": "TikTok", "sessions": int(base_sessions * 0.15), "revenue": round(base_revenue * 0.09, 2)}
            ],
            "product_performance": SHOPIFY_MOCK_DATA["top_products"],
            "customer_insights": {
                "new_customers": int(base_orders * 0.34),
                "returning_customers": int(base_orders * 0.66),
                "customer_lifetime_value": 287.45,
                "repeat_purchase_rate": 28.3
            }
        }
        
        return analytics_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Shopify analytics: {str(e)}")

@router.post("/upload")
async def upload_shopify_data(
    file: UploadFile = File(...),
    data_type: str = Form("orders"),
    brand: str = Form("Crooks & Castles")
):
    """Upload and process Shopify data files (CSV/JSON)"""
    
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process based on file type
        if file.filename.endswith('.csv'):
            processed_data = await process_csv_upload(content, data_type, brand)
        else:
            processed_data = await process_json_upload(content, data_type, brand)
        
        # Generate upload ID for tracking
        upload_id = f"upload_{uuid.uuid4().hex[:8]}"
        
        return {
            "success": True,
            "upload_id": upload_id,
            "filename": file.filename,
            "data_type": data_type,
            "brand": brand,
            "processed_data": processed_data,
            "upload_time": datetime.now().isoformat(),
            "message": f"Successfully processed {file.filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload Shopify data: {str(e)}")

@router.get("/upload/history")
async def get_upload_history(limit: int = 20):
    """Get history of Shopify data uploads"""
    
    try:
        # Mock upload history
        upload_history = [
            {
                "upload_id": "upload_a1b2c3d4",
                "filename": "shopify_orders_september.csv",
                "data_type": "orders",
                "brand": "Crooks & Castles",
                "status": "completed",
                "records_processed": 1247,
                "upload_time": "2025-09-30T10:15:00Z",
                "file_size": "2.3 MB"
            },
            {
                "upload_id": "upload_e5f6g7h8", 
                "filename": "product_catalog_update.json",
                "data_type": "products",
                "brand": "Crooks & Castles",
                "status": "completed",
                "records_processed": 89,
                "upload_time": "2025-09-29T14:30:00Z",
                "file_size": "1.8 MB"
            },
            {
                "upload_id": "upload_i9j0k1l2",
                "filename": "customer_data_export.csv", 
                "data_type": "customers",
                "brand": "Crooks & Castles",
                "status": "processing",
                "records_processed": 0,
                "upload_time": "2025-09-30T16:45:00Z",
                "file_size": "5.1 MB"
            }
        ]
        
        return {
            "uploads": upload_history[:limit],
            "total_uploads": len(upload_history),
            "summary": {
                "completed": len([u for u in upload_history if u["status"] == "completed"]),
                "processing": len([u for u in upload_history if u["status"] == "processing"]),
                "failed": len([u for u in upload_history if u["status"] == "failed"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch upload history: {str(e)}")

async def process_csv_upload(content: bytes, data_type: str, brand: str) -> Dict[str, Any]:
    """Process uploaded CSV file"""
    
    try:
        # Parse CSV content
        csv_text = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(csv_reader)
        
        if not rows:
            raise ValueError("CSV file is empty or invalid")
        
        # Process based on data type
        if data_type == "orders":
            processed = process_orders_csv(rows, brand)
        elif data_type == "products":
            processed = process_products_csv(rows, brand)
        elif data_type == "customers":
            processed = process_customers_csv(rows, brand)
        else:
            processed = {
                "records": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "sample_data": rows[:3]
            }
        
        return processed
        
    except Exception as e:
        raise ValueError(f"Failed to process CSV: {str(e)}")

async def process_json_upload(content: bytes, data_type: str, brand: str) -> Dict[str, Any]:
    """Process uploaded JSON file"""
    
    try:
        # Parse JSON content
        json_text = content.decode('utf-8')
        data = json.loads(json_text)
        
        if isinstance(data, list):
            records = len(data)
            sample = data[:3] if data else []
        elif isinstance(data, dict):
            records = 1
            sample = [data]
        else:
            raise ValueError("Invalid JSON structure")
        
        return {
            "records": records,
            "data_type": data_type,
            "brand": brand,
            "sample_data": sample,
            "structure": "array" if isinstance(data, list) else "object"
        }
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to process JSON: {str(e)}")

def process_orders_csv(rows: List[Dict], brand: str) -> Dict[str, Any]:
    """Process orders CSV data"""
    
    total_revenue = 0
    order_count = len(rows)
    
    for row in rows:
        # Try to extract revenue from common column names
        revenue = 0
        for col in ['total', 'amount', 'revenue', 'Total', 'Amount', 'Revenue']:
            if col in row and row[col]:
                try:
                    revenue = float(row[col].replace('$', '').replace(',', ''))
                    break
                except:
                    continue
        total_revenue += revenue
    
    return {
        "data_type": "orders",
        "records": order_count,
        "total_revenue": round(total_revenue, 2),
        "avg_order_value": round(total_revenue / order_count, 2) if order_count > 0 else 0,
        "columns": list(rows[0].keys()) if rows else [],
        "sample_orders": rows[:3]
    }

def process_products_csv(rows: List[Dict], brand: str) -> Dict[str, Any]:
    """Process products CSV data"""
    
    product_count = len(rows)
    categories = set()
    
    for row in rows:
        # Extract categories from common column names
        for col in ['category', 'type', 'product_type', 'Category', 'Type']:
            if col in row and row[col]:
                categories.add(row[col])
    
    return {
        "data_type": "products",
        "records": product_count,
        "categories": list(categories),
        "columns": list(rows[0].keys()) if rows else [],
        "sample_products": rows[:3]
    }

def process_customers_csv(rows: List[Dict], brand: str) -> Dict[str, Any]:
    """Process customers CSV data"""
    
    customer_count = len(rows)
    locations = set()
    
    for row in rows:
        # Extract locations from common column names
        for col in ['country', 'state', 'city', 'location', 'Country', 'State']:
            if col in row and row[col]:
                locations.add(row[col])
    
    return {
        "data_type": "customers", 
        "records": customer_count,
        "locations": list(locations)[:10],  # Top 10 locations
        "columns": list(rows[0].keys()) if rows else [],
        "sample_customers": rows[:3]
    }
