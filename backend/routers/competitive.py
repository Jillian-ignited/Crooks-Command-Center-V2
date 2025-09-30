# backend/routers/competitive.py
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.services import intelligence_store as store

DEFAULT_BRAND = os.getenv("DEFAULT_BRAND", "Crooks & Castles")

router = APIRouter()


def _row_for_brand(name: str, days: int) -> Dict[str, Any]:
    # Use the same aggregator the executive view uses, per brand
    data = store.executive_overview(brand=name)
    r = data["recaps"][f"{days}d"]
    s = data["recaps"]["social"][f"{days}d"]

    return {
        "brand": name,
        "days": days,
        "orders": float(r.get("orders", 0.0)),
        "net_sales": float(r.get("net_sales", 0.0)),
        "aov": float(r.get("aov", 0.0)),
        "conversion_pct": float(r.get("conversion_pct", 0.0)),
        "sessions": float(r.get("sessions", 0.0)),
        "plays": float(s.get("plays", 0.0)),
        "likes": float(s.get("likes", 0.0)),
        "comments": float(s.get("comments", 0.0)),
        "refreshed_at": r.get("refreshed_at"),
        "wow": {
            "orders": r["wow"]["orders"],
            "net_sales": r["wow"]["net_sales"],
            "aov": r["wow"]["aov"],
            "conversion_pct": r["wow"]["conversion_pct"],
            "sessions": r["wow"]["sessions"],
            "plays": s["wow"]["plays"],
            "likes": s["wow"]["likes"],
            "comments": s["wow"]["comments"],
        },
    }


@router.get("/brands", summary="List tracked brands for competitive view")
def list_brands():
    store.init()
    brands = store.list_brands()
    return JSONResponse({"ok": True, "brands": brands})


@router.get("/board", summary="Competitive board (rows per brand for given window)")
def board(
    days: int = Query(30, ge=7, le=90, description="Window size in days (7 or 30 recommended)"),
    limit: int = Query(30, ge=1, le=100),
    primary: str = Query(DEFAULT_BRAND, description="Primary brand to prioritize first"),
):
    store.init()
    # Build the brand list, prioritizing primary first
    brands = [b["name"] for b in store.list_brands()]
    if not brands:
        # Ensure at least DEFAULT_BRAND exists
        store.ensure_brand(DEFAULT_BRAND)
        brands = [DEFAULT_BRAND]

    # put primary first, then others
    uniq: List[str] = []
    if primary in brands:
        uniq.append(primary)
    uniq.extend([b for b in brands if b != primary])

    # cap list
    uniq = uniq[:limit]

    rows = [_row_for_brand(b, days) for b in uniq]
    return JSONResponse({"ok": True, "days": days, "rows": rows, "count": len(rows), "primary": primary})


@router.get("/compare", summary="Direct A vs B comparison")
def compare(
    a: str = Query(DEFAULT_BRAND),
    b: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=90),
):
    store.init()
    brands = [x["name"] for x in store.list_brands()]
    if b is None:
        # pick first non-a brand if possible
        b = next((x for x in brands if x != a), a)

    return JSONResponse({
        "ok": True,
        "days": days,
        "a": _row_for_brand(a, days),
        "b": _row_for_brand(b, days),
    })
