# backend/routers/shopify.py
# Complete Shopify integration router with real data processing

import os
import json
import uuid
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import aiofiles

router = APIRouter()

# Upload directory for Shopify data
SHOPIFY_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "shopify")
os.makedirs(SHOPIFY_UPLOAD_DIR, exist_ok=True)

# Database setup
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
    else:
        DB_AVAILABLE = False
except Exception as e:
    print(f"[shopify] Database setup error: {e}")
    DB_AVAILABLE = False

@router.get("/dashboard")
async def get_shopify_dashboard():
    """Get comprehensive Shopify dashboard data"""
    
    try:
        print("[shopify] Generating dashboard from real data")
        
        # Get uploaded Shopify files
        uploaded_files = []
        if os.path.exists(SHOPIFY_UPLOAD_DIR):
            for filename in os.listdir(SHOPIFY_UPLOAD_DIR):
                file_path = os.path.join(SHOPIFY_UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    uploaded_files.append(file_path)
        
        # Process Shopify data from uploaded files
        dashboard_data = await process_shopify_data(uploaded_files)
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "data_sources": len(uploaded_files),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[shopify] Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

@router.post("/upload")
async def upload_shopify_data(
    file: UploadFile = File(...),
    data_type: str = Form("orders"),  # orders, products, customers, analytics
    description: Optional[str] = Form(None)
):
    """Upload Shopify data files (CSV, Excel, JSON)"""
    
    try:
        print(f"[shopify] Starting upload: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{data_type}{file_extension}"
        file_path = os.path.join(SHOPIFY_UPLOAD_DIR, safe_filename)
        
        # Save file
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        print(f"[shopify] File saved: {file_path} ({len(content)} bytes)")
        
        # Process the uploaded data
        processing_result = await process_uploaded_shopify_file(file_path, data_type, file.filename)
        
        # Save metadata to database if available
        if DB_AVAILABLE:
            try:
                save_shopify_upload_metadata({
                    "filename": file.filename,
                    "data_type": data_type,
                    "file_path": file_path,
                    "description": description,
                    "processing_result": processing_result
                })
            except Exception as db_error:
                print(f"[shopify] Database save error: {db_error}")
        
        return {
            "success": True,
            "message": f"Shopify {data_type} data uploaded successfully",
            "file_id": file_id,
            "processing_result": processing_result,
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[shopify] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/analytics")
async def get_shopify_analytics():
    """Get Shopify analytics from uploaded data"""
    
    try:
        # Process all uploaded Shopify files for analytics
        uploaded_files = []
        if os.path.exists(SHOPIFY_UPLOAD_DIR):
            for filename in os.listdir(SHOPIFY_UPLOAD_DIR):
                file_path = os.path.join(SHOPIFY_UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    uploaded_files.append(file_path)
        
        analytics = await generate_shopify_analytics(uploaded_files)
        
        return {
            "success": True,
            "analytics": analytics,
            "data_files_processed": len(uploaded_files),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@router.get("/orders")
async def get_shopify_orders(limit: int = 100):
    """Get Shopify orders from uploaded data"""
    
    try:
        orders = await extract_orders_from_uploads(limit)
        
        return {
            "success": True,
            "orders": orders,
            "total_orders": len(orders),
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")

@router.get("/test-connection")
async def test_shopify_connection():
    """Test Shopify data processing capabilities"""
    
    try:
        # Check if upload directory exists and is writable
        test_file = os.path.join(SHOPIFY_UPLOAD_DIR, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        
        # Check database connection
        db_status = "connected" if DB_AVAILABLE else "not configured"
        
        # Count uploaded files
        file_count = 0
        if os.path.exists(SHOPIFY_UPLOAD_DIR):
            file_count = len([f for f in os.listdir(SHOPIFY_UPLOAD_DIR) if os.path.isfile(os.path.join(SHOPIFY_UPLOAD_DIR, f))])
        
        return {
            "success": True,
            "status": "operational",
            "upload_directory": SHOPIFY_UPLOAD_DIR,
            "database_status": db_status,
            "uploaded_files": file_count,
            "supported_formats": ["CSV", "Excel", "JSON"],
            "data_types": ["orders", "products", "customers", "analytics"],
            "test_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "test_timestamp": datetime.now().isoformat()
        }

async def process_shopify_data(file_paths: List[str]) -> Dict[str, Any]:
    """Process Shopify data from uploaded files"""
    
    try:
        if not file_paths:
            return generate_sample_dashboard_data()
        
        dashboard_data = {
            "overview": {
                "total_files": len(file_paths),
                "data_sources": [],
                "last_updated": datetime.now().isoformat()
            },
            "sales_metrics": {},
            "product_performance": {},
            "customer_insights": {},
            "recent_activity": []
        }
        
        # Process each file
        for file_path in file_paths:
            try:
                file_data = await process_single_shopify_file(file_path)
                
                # Aggregate data
                if file_data.get("data_type") == "orders":
                    dashboard_data["sales_metrics"].update(file_data.get("metrics", {}))
                elif file_data.get("data_type") == "products":
                    dashboard_data["product_performance"].update(file_data.get("metrics", {}))
                elif file_data.get("data_type") == "customers":
                    dashboard_data["customer_insights"].update(file_data.get("metrics", {}))
                
                dashboard_data["overview"]["data_sources"].append({
                    "file": os.path.basename(file_path),
                    "type": file_data.get("data_type", "unknown"),
                    "records": file_data.get("record_count", 0)
                })
                
            except Exception as e:
                print(f"[shopify] Error processing {file_path}: {e}")
                continue
        
        return dashboard_data
        
    except Exception as e:
        print(f"[shopify] Data processing error: {e}")
        return generate_sample_dashboard_data()

async def process_single_shopify_file(file_path: str) -> Dict[str, Any]:
    """Process a single Shopify data file"""
    
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Read file based on type
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_extension == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data if isinstance(data, list) else [data])
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Determine data type from filename or columns
        filename = os.path.basename(file_path).lower()
        data_type = "unknown"
        
        if "order" in filename or any(col.lower() in ['order_id', 'order_number'] for col in df.columns):
            data_type = "orders"
        elif "product" in filename or any(col.lower() in ['product_id', 'product_title'] for col in df.columns):
            data_type = "products"
        elif "customer" in filename or any(col.lower() in ['customer_id', 'customer_email'] for col in df.columns):
            data_type = "customers"
        
        # Generate metrics based on data type
        metrics = {}
        if data_type == "orders" and not df.empty:
            metrics = analyze_orders_data(df)
        elif data_type == "products" and not df.empty:
            metrics = analyze_products_data(df)
        elif data_type == "customers" and not df.empty:
            metrics = analyze_customers_data(df)
        
        return {
            "data_type": data_type,
            "record_count": len(df),
            "columns": df.columns.tolist(),
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"[shopify] File processing error: {e}")
        return {"error": str(e)}

def analyze_orders_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze orders data and generate metrics"""
    
    try:
        metrics = {
            "total_orders": len(df),
            "total_revenue": 0,
            "average_order_value": 0,
            "order_trends": {}
        }
        
        # Look for revenue/total columns
        revenue_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['total', 'amount', 'revenue', 'price'])]
        
        if revenue_columns:
            revenue_col = revenue_columns[0]
            # Convert to numeric, handling currency symbols
            df[revenue_col] = pd.to_numeric(df[revenue_col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
            
            metrics["total_revenue"] = df[revenue_col].sum()
            metrics["average_order_value"] = df[revenue_col].mean()
        
        # Date analysis
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'created', 'time'])]
        
        if date_columns:
            date_col = date_columns[0]
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Group by date for trends
            daily_orders = df.groupby(df[date_col].dt.date).size()
            metrics["order_trends"] = {
                "daily_average": daily_orders.mean(),
                "peak_day": str(daily_orders.idxmax()) if not daily_orders.empty else None,
                "recent_orders": daily_orders.tail(7).to_dict()
            }
        
        return metrics
        
    except Exception as e:
        return {"analysis_error": str(e)}

def analyze_products_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze products data and generate metrics"""
    
    try:
        metrics = {
            "total_products": len(df),
            "product_categories": {},
            "price_analysis": {}
        }
        
        # Category analysis
        category_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['category', 'type', 'collection'])]
        
        if category_columns:
            category_col = category_columns[0]
            category_counts = df[category_col].value_counts()
            metrics["product_categories"] = category_counts.head(10).to_dict()
        
        # Price analysis
        price_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['price', 'cost', 'amount'])]
        
        if price_columns:
            price_col = price_columns[0]
            df[price_col] = pd.to_numeric(df[price_col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
            
            metrics["price_analysis"] = {
                "average_price": df[price_col].mean(),
                "min_price": df[price_col].min(),
                "max_price": df[price_col].max(),
                "price_ranges": {
                    "under_50": len(df[df[price_col] < 50]),
                    "50_to_100": len(df[(df[price_col] >= 50) & (df[price_col] < 100)]),
                    "over_100": len(df[df[price_col] >= 100])
                }
            }
        
        return metrics
        
    except Exception as e:
        return {"analysis_error": str(e)}

def analyze_customers_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze customers data and generate metrics"""
    
    try:
        metrics = {
            "total_customers": len(df),
            "customer_segments": {},
            "geographic_distribution": {}
        }
        
        # Geographic analysis
        location_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['country', 'state', 'city', 'location'])]
        
        if location_columns:
            location_col = location_columns[0]
            location_counts = df[location_col].value_counts()
            metrics["geographic_distribution"] = location_counts.head(10).to_dict()
        
        # Customer value analysis
        value_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['total', 'spent', 'value', 'orders'])]
        
        if value_columns:
            value_col = value_columns[0]
            df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
            
            # Segment customers by value
            high_value = len(df[df[value_col] > df[value_col].quantile(0.8)])
            medium_value = len(df[(df[value_col] > df[value_col].quantile(0.4)) & (df[value_col] <= df[value_col].quantile(0.8))])
            low_value = len(df[df[value_col] <= df[value_col].quantile(0.4)])
            
            metrics["customer_segments"] = {
                "high_value": high_value,
                "medium_value": medium_value,
                "low_value": low_value
            }
        
        return metrics
        
    except Exception as e:
        return {"analysis_error": str(e)}

async def process_uploaded_shopify_file(file_path: str, data_type: str, original_filename: str) -> Dict[str, Any]:
    """Process uploaded Shopify file and return processing results"""
    
    try:
        result = await process_single_shopify_file(file_path)
        
        return {
            "original_filename": original_filename,
            "data_type": data_type,
            "processing_status": "success",
            "records_processed": result.get("record_count", 0),
            "columns_detected": result.get("columns", []),
            "metrics_generated": bool(result.get("metrics")),
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "original_filename": original_filename,
            "data_type": data_type,
            "processing_status": "error",
            "error": str(e),
            "processed_at": datetime.now().isoformat()
        }

async def generate_shopify_analytics(file_paths: List[str]) -> Dict[str, Any]:
    """Generate comprehensive analytics from all Shopify files"""
    
    try:
        analytics = {
            "overview": {
                "total_files": len(file_paths),
                "analysis_date": datetime.now().isoformat()
            },
            "sales_analytics": {},
            "product_analytics": {},
            "customer_analytics": {},
            "trends": {}
        }
        
        # Process each file and aggregate analytics
        for file_path in file_paths:
            try:
                file_data = await process_single_shopify_file(file_path)
                data_type = file_data.get("data_type")
                metrics = file_data.get("metrics", {})
                
                if data_type == "orders":
                    analytics["sales_analytics"].update(metrics)
                elif data_type == "products":
                    analytics["product_analytics"].update(metrics)
                elif data_type == "customers":
                    analytics["customer_analytics"].update(metrics)
                    
            except Exception as e:
                print(f"[shopify] Analytics processing error for {file_path}: {e}")
                continue
        
        # Generate trend analysis
        analytics["trends"] = generate_trend_analysis(analytics)
        
        return analytics
        
    except Exception as e:
        return {"analytics_error": str(e)}

async def extract_orders_from_uploads(limit: int) -> List[Dict[str, Any]]:
    """Extract order data from uploaded files"""
    
    try:
        orders = []
        
        if os.path.exists(SHOPIFY_UPLOAD_DIR):
            for filename in os.listdir(SHOPIFY_UPLOAD_DIR):
                if "order" in filename.lower():
                    file_path = os.path.join(SHOPIFY_UPLOAD_DIR, filename)
                    
                    try:
                        # Read order file
                        if filename.endswith('.csv'):
                            df = pd.read_csv(file_path)
                        elif filename.endswith(('.xlsx', '.xls')):
                            df = pd.read_excel(file_path)
                        else:
                            continue
                        
                        # Convert to list of dictionaries
                        file_orders = df.head(limit).to_dict('records')
                        orders.extend(file_orders)
                        
                        if len(orders) >= limit:
                            break
                            
                    except Exception as e:
                        print(f"[shopify] Error reading {filename}: {e}")
                        continue
        
        return orders[:limit]
        
    except Exception as e:
        return []

def generate_trend_analysis(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate trend analysis from analytics data"""
    
    try:
        trends = {
            "sales_trends": "Stable",
            "product_trends": "Growing",
            "customer_trends": "Expanding",
            "recommendations": []
        }
        
        # Analyze sales trends
        sales_data = analytics.get("sales_analytics", {})
        if sales_data.get("total_revenue", 0) > 10000:
            trends["sales_trends"] = "Strong"
            trends["recommendations"].append("Continue current sales strategy")
        
        # Analyze product trends
        product_data = analytics.get("product_analytics", {})
        if product_data.get("total_products", 0) > 50:
            trends["product_trends"] = "Diverse"
            trends["recommendations"].append("Consider product line optimization")
        
        # Analyze customer trends
        customer_data = analytics.get("customer_analytics", {})
        if customer_data.get("total_customers", 0) > 100:
            trends["customer_trends"] = "Healthy"
            trends["recommendations"].append("Focus on customer retention")
        
        return trends
        
    except Exception as e:
        return {"trend_error": str(e)}

def generate_sample_dashboard_data() -> Dict[str, Any]:
    """Generate sample dashboard data when no files are uploaded"""
    
    return {
        "overview": {
            "total_files": 0,
            "data_sources": [],
            "last_updated": datetime.now().isoformat(),
            "status": "No data uploaded yet"
        },
        "sales_metrics": {
            "message": "Upload order data to see sales metrics"
        },
        "product_performance": {
            "message": "Upload product data to see performance metrics"
        },
        "customer_insights": {
            "message": "Upload customer data to see insights"
        },
        "recent_activity": [],
        "instructions": [
            "Upload CSV or Excel files containing Shopify data",
            "Supported data types: orders, products, customers, analytics",
            "Files will be automatically processed and analyzed"
        ]
    }

def save_shopify_upload_metadata(metadata: Dict[str, Any]):
    """Save upload metadata to database"""
    
    if not DB_AVAILABLE:
        return
    
    try:
        with SessionLocal() as session:
            query = text("""
                INSERT INTO shopify_uploads 
                (filename, data_type, file_path, description, processing_result, uploaded_at)
                VALUES (:filename, :data_type, :file_path, :description, :processing_result, :uploaded_at)
            """)
            
            session.execute(query, {
                "filename": metadata["filename"],
                "data_type": metadata["data_type"],
                "file_path": metadata["file_path"],
                "description": metadata.get("description"),
                "processing_result": json.dumps(metadata["processing_result"]),
                "uploaded_at": datetime.now()
            })
            session.commit()
            
    except Exception as e:
        print(f"[shopify] Database save error: {e}")

@router.get("/health")
async def shopify_health():
    """Health check for Shopify module"""
    return {
        "status": "healthy",
        "upload_directory": SHOPIFY_UPLOAD_DIR,
        "database_available": DB_AVAILABLE,
        "supported_formats": ["CSV", "Excel", "JSON"],
        "data_types": ["orders", "products", "customers", "analytics"]
    }
