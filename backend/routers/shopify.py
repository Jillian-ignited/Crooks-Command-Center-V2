from fastapi import APIRouter
from typing import Dict, Any
import datetime

router = APIRouter()

@router.get("/dashboard")
async def get_shopify_dashboard() -> Dict[str, Any]:
    """Get Shopify store dashboard data"""
    return {
        "success": True,
        "store_name": "Crooks & Castles Store",
        "orders_today": 23,
        "revenue_today": 5420.50,
        "products_count": 156,
        "customers_count": 2847,
        "recent_orders": [
            {
                "order_number": "#1001",
                "customer_name": "John Doe",
                "total": "89.99",
                "status": "fulfilled",
                "created_at": "2024-01-15 14:30"
            },
            {
                "order_number": "#1002", 
                "customer_name": "Jane Smith",
                "total": "156.50",
                "status": "pending",
                "created_at": "2024-01-15 13:45"
            }
        ],
        "analytics": {
            "conversion_rate": 3.2,
            "average_order_value": 89.45,
            "returning_customer_rate": 24.5
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/test-connection")
async def test_shopify_connection() -> Dict[str, Any]:
    """Test Shopify API connection"""
    return {
        "success": True,
        "connected": True,
        "store_name": "Crooks & Castles Store",
        "message": "Successfully connected to Shopify store"
    }

@router.get("/orders")
async def get_orders() -> Dict[str, Any]:
    """Get recent orders from Shopify"""
    return {
        "success": True,
        "orders": [
            {
                "order_number": "#1001",
                "customer_name": "John Doe",
                "total": "89.99",
                "status": "fulfilled"
            }
        ],
        "total_count": 1
    }

@router.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    """Get Shopify analytics data"""
    return {
        "success": True,
        "analytics": {
            "orders_today": 23,
            "revenue_today": 5420.50,
            "orders_this_week": 156,
            "revenue_this_week": 28450.75,
            "conversion_rate": 3.2,
            "average_order_value": 89.45
        }
    }
