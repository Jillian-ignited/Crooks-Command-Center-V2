from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

router = APIRouter(tags=["shopify"])

# Stubs — replace with real data source when ready
_FAKE_ORDERS = [
    {"id": 1, "created_at": (datetime.now() - timedelta(days=1)).isoformat(), "total_price": 120.50},
    {"id": 2, "created_at": (datetime.now() - timedelta(days=2)).isoformat(), "total_price": 75.00},
    {"id": 3, "created_at": (datetime.now() - timedelta(days=6)).isoformat(), "total_price": 42.00},
]

@router.get("/status")
def status() -> Dict[str, Any]:
    return {"connected": False, "note": "Wire credentials/env to enable live data", "checked_at": datetime.now().isoformat()}

@router.get("/orders")
def orders(days: int = Query(7, ge=1, le=90)) -> Dict[str, Any]:
    cutoff = datetime.now() - timedelta(days=days)
    items = [o for o in _FAKE_ORDERS if datetime.fromisoformat(o["created_at"]) >= cutoff]
    return {"count": len(items), "orders": items, "window_days": days}

@router.get("/summary")
def summary(days: int = Query(30, ge=1, le=365)) -> Dict[str, Any]:
    cutoff = datetime.now() - timedelta(days=days)
    window = [o for o in _FAKE_ORDERS if datetime.fromisoformat(o["created_at"]) >= cutoff]
    total_sales = sum(float(o["total_price"]) for o in window)
    total_orders = len(window)
    aov = total_sales / max(total_orders, 1)
    return {
        "window_days": days,
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "aov": round(aov, 2),
        "currency": "USD",
        "last_updated": datetime.now().isoformat()
    }
