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
    print(f"[Shopify] Database setup error: {e}")
    DB_AVAILABLE = False

@router.get("/dashboard")
async def get_shopify_dashboard():
    """Get comprehensive Shopify dashboard data from the database"""
    
    try:
        print("[Shopify] Generating dashboard from real data")
        
        if not DB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")

        with SessionLocal() as session:
            # Query aggregated data from the database
            query = text("SELECT * FROM shopify_metrics ORDER BY date DESC")
            result = session.execute(query).fetchall()
            
            # Convert to list of dicts
            dashboard_data = [dict(row) for row in result]

        return {
            "success": True,
            "dashboard": dashboard_data,
            "data_sources": len(dashboard_data),
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"[Shopify] Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

@router.post("/upload")
async def upload_shopify_data(
    file: UploadFile = File(...),
    data_type: str = Form("orders"),  # orders, products, customers, analytics
    description: Optional[str] = Form(None)
):
    """Upload and process Shopify data files"""
    
    try:
        print(f"[Shopify] Starting upload: {file.filename} ({data_type})")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(SHOPIFY_UPLOAD_DIR, safe_filename)

        # Read and save file
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        print(f"[Shopify] File saved: {file_path} ({len(content)} bytes)")

        # Process file content for insights
        processing_result = await process_shopify_data(content, file_extension)

        # Save aggregated metrics to the database
        save_shopify_metrics(processing_result)

        return {
            "success": True,
            "message": f"Shopify data ‘{file.filename}’ uploaded and processed successfully",
            "file_id": file_id,
            "processing_result": processing_result
        }

    except Exception as e:
        print(f"[Shopify] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

async def process_shopify_data(content: bytes, file_extension: str) -> Dict[str, Any]:
    """Process a single Shopify data file and return aggregated metrics"""
    
    try:
        if file_extension == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        elif file_extension in [".xls", ".xlsx"]:
            df = pd.read_excel(io.BytesIO(content))
        else:
            return {"error": "Unsupported file type"}

        # Basic data processing and aggregation
        total_sales = df["total_sales"].sum() if "total_sales" in df else 0
        total_orders = df["orders"].sum() if "orders" in df else len(df)
        
        # More complex analysis can be added here

        return {
            "date": datetime.now().date(),
            "total_sales": total_sales,
            "total_orders": total_orders,
            "total_records": len(df),
            "columns": list(df.columns)
        }

    except Exception as e:
        print(f"[Shopify] Error processing file: {e}")
        return {"error": f"Failed to process file: {e}"}

def save_shopify_metrics(metrics: Dict[str, Any]):
    """Save aggregated Shopify metrics to the database"""
    
    if not DB_AVAILABLE:
        return

    try:
        with SessionLocal() as session:
            # Create table if it doesn't exist
            create_table_sql = text("""
            CREATE TABLE IF NOT EXISTS shopify_metrics (
                id SERIAL PRIMARY KEY,
                date DATE,
                total_sales FLOAT,
                total_orders INTEGER,
                total_records INTEGER,
                columns JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            session.execute(create_table_sql)
            session.commit()

            # Insert new metrics
            query = text("""
                INSERT INTO shopify_metrics (date, total_sales, total_orders, total_records, columns)
                VALUES (:date, :total_sales, :total_orders, :total_records, :columns)
            """)
            
            session.execute(query, {
                "date": metrics["date"],
                "total_sales": metrics["total_sales"],
                "total_orders": metrics["total_orders"],
                "total_records": metrics["total_records"],
                "columns": json.dumps(metrics["columns"])
            })
            session.commit()
            
    except Exception as e:
        print(f"[Shopify] Database save error: {e}")

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

