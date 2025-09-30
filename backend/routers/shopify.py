# backend/routers/shopify.py
from fastapi import APIRouter
from typing import Dict, Any
import datetime

router = APIRouter()

# Mock Shopify data for development
MOCK_SHOPIFY_DATA = {
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
        },
    ],
    "top_products": [
        {
            "title": "Crooks Logo Hoodie",
            "sales_count": 45,
            "revenue": "2,250.00",
            "price": "89.99"
        },
    ]
}

@router.get("/dashboard")
def get_shopify_dashboard() -> Dict[str, Any]:
    """Get Shopify store dashboard data"""
    return {
        "success": True,
        **MOCK_SHOPIFY_DATA,
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/test-connection")
def test_shopify_connection() -> Dict[str, Any]:
    """Test Shopify API connection"""
    return {
        "success": True,
        "connected": True,
        "store_name": MOCK_SHOPIFY_DATA["store_name"],
        "message": "Successfully connected to Shopify store"
    }

@router.get("/orders")
def get_orders(limit: int = 50) -> Dict[str, Any]:
    """Get recent orders from Shopify"""
    return {
        "success": True,
        "orders": MOCK_SHOPIFY_DATA["recent_orders"],
        "total_count": len(MOCK_SHOPIFY_DATA["recent_orders"])
    }

@router.get("/products")
def get_products(limit: int = 50) -> Dict[str, Any]:
    """Get products from Shopify"""
    return {
        "success": True,
        "products": MOCK_SHOPIFY_DATA["top_products"],
        "total_count": len(MOCK_SHOPIFY_DATA["top_products"])
    }

@router.get("/analytics")
def get_analytics() -> Dict[str, Any]:
    """Get Shopify analytics data"""
    return {
        "success": True,
        "orders_today": MOCK_SHOPIFY_DATA["orders_today"],
        "revenue_today": MOCK_SHOPIFY_DATA["revenue_today"],
        "conversion_rate": 3.2,
        "average_order_value": 89.45
    }

@router.get("/customers")
def get_customers(limit: int = 50) -> Dict[str, Any]:
    """Get customer data from Shopify"""
    return {
        "success": True,
        "customers": [],
        "total_count": MOCK_SHOPIFY_DATA["customers_count"]
    }
