# backend/routers/shopify.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

router = APIRouter()

# ---- Config / feature flag ----
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "").strip()          # e.g. "mystore"
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "").strip()  # Admin API token

def _ready() -> bool:
    return bool(SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN)

# ---- Models (shape what the FE expects) ----
class ShopifyMetric(BaseModel):
    name: str
    value: float
    delta: float

class Product(BaseModel):
    id: str
    title: str
    price: float
    status: str

class Order(BaseModel):
    id: str
    total: float
    currency: str
    financial_status: str

class Customer(BaseModel):
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    orders_count: int = 0


# ---- Root (status / capabilities) ----
@router.get("/", summary="Shopify root status")
def root():
    return {
        "ok": True,
        "configured": _ready(),
        "store": SHOPIFY_STORE or None,
        "endpoints": [
            "/api/shopify/analytics",
            "/api/shopify/products",
            "/api/shopify/orders",
            "/api/shopify/customers",
        ],
    }


# ---- Analytics (stubbed if not configured) ----
@router.get("/analytics", response_model=List[ShopifyMetric], summary="Basic Shopify analytics")
def analytics(days: int = Query(30, ge=1, le=365)):
    if not _ready():
        # Return 501 so you know creds are missing (not a 404)
        raise HTTPException(status_code=501, detail="Shopify not configured: set SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN")

    # TODO: replace with real Admin API calls (orders, revenue, etc.)
    # Stubbed numbers so FE renders:
    return [
        ShopifyMetric(name="Revenue", value=125000.0, delta=+12.3),
        ShopifyMetric(name="Orders", value=1830, delta=+5.6),
        ShopifyMetric(name="AOV", value=68.31, delta=-1.2),
        ShopifyMetric(name="Customers", value=1420, delta=+3.4),
    ]


# ---- Products ----
@router.get("/products", response_model=List[Product], summary="List products (stub)")
def products(limit: int = Query(20, ge=1, le=250), status: str = Query("active")):
    if not _ready():
        raise HTTPException(status_code=501, detail="Shopify not configured")
    # TODO: call /admin/api/2024-07/products.json with params
    return [
        Product(id="p_1001", title="Core Tee", price=38.0, status=status),
        Product(id="p_1002", title="Logo Hoodie", price=89.0, status=status),
        Product(id="p_1003", title="Denim Jacket", price=129.0, status=status),
    ][:limit]


# ---- Orders ----
@router.get("/orders", response_model=List[Order], summary="List orders (stub)")
def orders(limit: int = Query(20, ge=1, le=250), financial_status: str = Query("paid")):
    if not _ready():
        raise HTTPException(status_code=501, detail="Shopify not configured")
    # TODO: call /admin/api/2024-07/orders.json with params
    return [
        Order(id="o_5001", total=189.0, currency="USD", financial_status=financial_status),
        Order(id="o_5002", total=58.0,  currency="USD", financial_status=financial_status),
        Order(id="o_5003", total=420.0, currency="USD", financial_status=financial_status),
    ][:limit]


# ---- Customers ----
@router.get("/customers", response_model=List[Customer], summary="List customers (stub)")
def customers(limit: int = Query(20, ge=1, le=250)):
    if not _ready():
        raise HTTPException(status_code=501, detail="Shopify not configured")
    # TODO: call /admin/api/2024-07/customers.json
    return [
        Customer(id="c_9001", email="gee@example.com", first_name="Gee", last_name="R.", orders_count=3),
        Customer(id="c_9002", email="alice@example.com", first_name="Alice", last_name="M.", orders_count=1),
        Customer(id="c_9003", email="bob@example.com", first_name="Bob", last_name="K.", orders_count=6),
    ][:limit]
