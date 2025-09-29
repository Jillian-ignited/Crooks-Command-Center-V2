# backend/routers/shopify.py
from fastapi import APIRouter

router = APIRouter()

# Overview (with trailing slash)
@router.get("/")
async def get_shopify_overview():
    return {"ok": True, "message": "Shopify overview is live"}

# Alias so /api/shopify (no slash) also works
@router.get("")
async def get_shopify_overview_alias():
    return await get_shopify_overview()

@router.get("/analytics")
async def get_analytics():
    return {"ok": True, "analytics": "Shopify analytics placeholder"}

@router.get("/products")
async def get_products():
    return {"ok": True, "products": []}

@router.get("/orders")
async def get_orders():
    return {"ok": True, "orders": []}

@router.get("/customers")
async def get_customers():
    return {"ok": True, "customers": []}

@router.get("/products/{product_id}")
async def get_product(product_id: str):
    return {"ok": True, "product_id": product_id}

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    return {"ok": True, "order_id": order_id}

@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    return {"ok": True, "customer_id": customer_id}
