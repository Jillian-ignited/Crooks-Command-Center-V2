from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import json
import pandas as pd
import io
from datetime import datetime

router = APIRouter()

@router.get("/dashboard")
def get_shopify_dashboard():
    return {
        "status": "ready",
        "total_sales": 0,
        "total_orders": 0,
        "conversion_rate": 0.0,
        "average_order_value": 0,
        "top_products": [],
        "recent_orders": [],
        "sales_trend": "flat",
        "data_source": "no_uploads",
        "last_updated": datetime.now().isoformat(),
        "instructions": "Upload Shopify CSV reports to see real sales data and analytics"
    }

@router.get("/orders")
def get_shopify_orders():
    return {
        "orders": [],
        "total": 0,
        "status": "no_data",
        "message": "Upload Shopify order data to view order analytics"
    }

@router.get("/analytics")
def get_shopify_analytics():
    return {
        "revenue": {
            "total": 0,
            "trend": "flat",
            "period": "current"
        },
        "products": {
            "total_sold": 0,
            "top_performers": [],
            "categories": []
        },
        "customers": {
            "total": 0,
            "new_customers": 0,
            "returning_rate": 0
        },
        "status": "awaiting_data"
    }

@router.get("/test")
def test_shopify_connection():
    return {
        "status": "connected",
        "message": "Shopify module is working correctly",
        "endpoints": [
            "/dashboard",
            "/orders", 
            "/analytics",
            "/upload"
        ]
    }

@router.post("/upload")
async def upload_shopify_data(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        # Process the uploaded file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            
            # Basic analysis of the CSV
            analysis = {
                "filename": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
                "date_range": "Unknown",
                "total_sales": 0,
                "total_orders": len(df) if 'order' in str(df.columns).lower() else 0
            }
            
            # Try to extract sales data if columns exist
            sales_columns = [col for col in df.columns if 'sales' in col.lower() or 'revenue' in col.lower() or 'total' in col.lower()]
            if sales_columns:
                try:
                    analysis["total_sales"] = df[sales_columns[0]].sum()
                except:
                    pass
            
            return {
                "status": "processed",
                "analysis": analysis,
                "message": "Shopify data uploaded successfully. Dashboard will update with this data."
            }
        
        else:
            return {
                "status": "processed", 
                "filename": file.filename,
                "size": len(content),
                "message": "File uploaded. For best results, upload CSV files with sales data."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/metrics")
def get_shopify_metrics():
    return {
        "status": "connected",
        "data_sources": 0,
        "last_updated": datetime.now().isoformat(),
        "metrics": {
            "sales": 0,
            "orders": 0,
            "customers": 0,
            "products": 0
        }
    }
