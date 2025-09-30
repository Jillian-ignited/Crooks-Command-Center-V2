from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
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
        {
            "order_number": "#1003",
            "customer_name": "Mike Johnson", 
            "total": "234.00",
            "status": "fulfilled",
            "created_at": "2024-01-15 12:20"
        },
        {
            "order_number": "#1004",
            "customer_name": "Sarah Wilson",
            "total": "67.25",
            "status": "processing",
            "created_at": "2024-01-15 11:15"
        },
        {
            "order_number": "#1005",
            "customer_name": "David Brown",
            "total": "445.75",
            "status": "fulfilled", 
            "created_at": "2024-01-15 10:30"
        }
    ],
    "top_products": [
        {
            "title": "Crooks Logo Hoodie",
            "sales_count": 45,
            "revenue": "2,250.00",
            "price": "89.99"
        },
        {
            "title": "Castles Graphic Tee",
            "sales_count": 67,
            "revenue": "1,675.00", 
            "price": "39.99"
        },
        {
            "title": "Premium Joggers",
            "sales_count": 32,
            "revenue": "1,920.00",
            "price": "79.99"
        },
        {
            "title": "Snapback Cap",
            "sales_count": 28,
            "revenue": "840.00",
            "price": "34.99"
        }
    ]
}

@router.get("/dashboard")
def get_shopify_dashboard() -> Dict[str, Any]:
    """Get Shopify store dashboard data"""
    return {
        "success": True,
        "data": MOCK_SHOPIFY_DATA,
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/test-connection")
def test_shopify_connection() -> Dict[str, Any]:
    """Test Shopify API connection"""
    # In a real implementation, this would test the actual Shopify API
    return {
        "success": True,
        "connected": True,
        "store_name": MOCK_SHOPIFY_DATA["store_name"],
        "message": "Successfully connected to Shopify store"
    }

@router.get("/orders")
def get_orders(limit: int = 50) -> Dict[str, Any]:
    """Get recent orders from Shopify"""
    orders = MOCK_SHOPIFY_DATA["recent_orders"][:limit]
    return {
        "success": True,
        "orders": orders,
        "total_count": len(orders)
    }

@router.get("/products")
def get_products(limit: int = 50) -> Dict[str, Any]:
    """Get products from Shopify"""
    products = MOCK_SHOPIFY_DATA["top_products"][:limit]
    return {
        "success": True,
        "products": products,
        "total_count": len(products)
    }

@router.get("/analytics")
def get_analytics() -> Dict[str, Any]:
    """Get Shopify analytics data"""
    return {
        "success": True,
        "analytics": {
            "orders_today": MOCK_SHOPIFY_DATA["orders_today"],
            "revenue_today": MOCK_SHOPIFY_DATA["revenue_today"],
            "orders_this_week": 156,
            "revenue_this_week": 28450.75,
            "orders_this_month": 678,
            "revenue_this_month": 125680.25,
            "conversion_rate": 3.2,
            "average_order_value": 89.45,
            "returning_customer_rate": 24.5
        }
    }

@router.post("/sync")
def sync_shopify_data() -> Dict[str, Any]:
    """Trigger a sync of Shopify data"""
    # In a real implementation, this would trigger a background sync job
    return {
        "success": True,
        "message": "Shopify data sync initiated",
        "sync_id": "sync_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    }

@router.get("/customers")
def get_customers(limit: int = 50) -> Dict[str, Any]:
    """Get customer data from Shopify"""
    customers = [
        {
            "id": "cust_001",
            "name": "John Doe",
            "email": "john@example.com",
            "orders_count": 5,
            "total_spent": "445.95",
            "created_at": "2023-06-15"
        },
        {
            "id": "cust_002", 
            "name": "Jane Smith",
            "email": "jane@example.com",
            "orders_count": 3,
            "total_spent": "267.50",
            "created_at": "2023-08-22"
        },
        {
            "id": "cust_003",
            "name": "Mike Johnson",
            "email": "mike@example.com", 
            "orders_count": 8,
            "total_spent": "892.25",
            "created_at": "2023-04-10"
        }
    ]
    
    return {
        "success": True,
        "customers": customers[:limit],
        "total_count": MOCK_SHOPIFY_DATA["customers_count"]
    }

@router.get("/inventory")
def get_inventory() -> Dict[str, Any]:
    """Get inventory levels from Shopify"""
    inventory = [
        {
            "product_id": "prod_001",
            "title": "Crooks Logo Hoodie",
            "sku": "CRK-HOOD-001",
            "quantity": 45,
            "reserved": 3,
            "available": 42,
            "status": "in_stock"
        },
        {
            "product_id": "prod_002",
            "title": "Castles Graphic Tee", 
            "sku": "CAS-TEE-002",
            "quantity": 23,
            "reserved": 1,
            "available": 22,
            "status": "low_stock"
        },
        {
            "product_id": "prod_003",
            "title": "Premium Joggers",
            "sku": "PRM-JOG-003", 
            "quantity": 0,
            "reserved": 0,
            "available": 0,
            "status": "out_of_stock"
        }
    ]
    
    return {
        "success": True,
        "inventory": inventory,
        "low_stock_count": 1,
        "out_of_stock_count": 1
    }
