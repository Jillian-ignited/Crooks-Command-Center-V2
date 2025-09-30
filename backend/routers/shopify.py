# backend/routers/shopify.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def shopify_root():
    return {"integration": "shopify", "status": "connected"}

@router.get("/analytics")
async def get_shopify_analytics():
    return {
        "revenue": 125000,
        "orders": 450,
        "avg_order_value": 277.78,
        "top_products": []
    }

@router.get("/products")
async def get_shopify_products():
    return {"products": [], "total": 0}

@router.get("/orders")
async def get_shopify_orders():
    return {"orders": [], "total": 0}

@router.get("/customers")
async def get_shopify_customers():
    return {"customers": [], "total": 0}
