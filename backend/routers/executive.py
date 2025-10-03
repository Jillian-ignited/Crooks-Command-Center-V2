from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()

@router.get("/overview")
def get_executive_overview():
    return {
        "total_sales": 0,
        "total_orders": 0,
        "conversion_rate": 0.0,
        "engagement_rate": 0.0,
        "sales_trend": "flat",
        "orders_trend": "flat",
        "conversion_trend": "flat",
        "engagement_trend": "flat",
        "data_source": "no_uploads",
        "last_updated": datetime.now().isoformat(),
        "status": "awaiting_data",
        "recommendations": [
            "Upload Shopify sales data to see real performance metrics",
            "Connect social media data for engagement analytics",
            "Add content performance data for comprehensive insights"
        ]
    }

@router.get("/summary")
def get_executive_summary():
    return {
        "period": "Current Period",
        "highlights": [
            {
                "title": "Sales Performance",
                "value": "$0",
                "change": "0%",
                "status": "awaiting_data"
            },
            {
                "title": "Order Volume", 
                "value": "0",
                "change": "0%",
                "status": "awaiting_data"
            },
            {
                "title": "Engagement Rate",
                "value": "0%", 
                "change": "0%",
                "status": "awaiting_data"
            }
        ],
        "key_metrics": {
            "revenue": 0,
            "orders": 0,
            "customers": 0,
            "engagement": 0
        },
        "insights": [
            "No data uploaded yet - upload Shopify reports to see real insights",
            "Connect social media data for engagement analysis",
            "Add competitive intelligence for market positioning"
        ],
        "status": "ready_for_data"
    }

@router.get("/metrics")
def get_executive_metrics():
    return {
        "status": "connected",
        "data_sources": 0,
        "last_updated": datetime.now().isoformat(),
        "metrics": {
            "sales": 0,
            "orders": 0,
            "engagement": 0,
            "conversion": 0
        }
    }

@router.post("/refresh")
def refresh_executive_data():
    return {
        "status": "refreshed",
        "timestamp": datetime.now().isoformat(),
        "message": "Executive data refreshed successfully"
    }

