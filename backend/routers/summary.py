# backend/routers/summary.py
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
def overview(days: int = Query(30, ge=1, le=365)):
    now = datetime.utcnow()
    return {
        "ok": True,
        "window_days": days,
        "period": {"start": (now - timedelta(days=days)).date().isoformat(),
                   "end": now.date().isoformat()},
        "kpis": {
            "revenue": 125000 + days * 173,
            "margin_pct": 0.46,
            "ad_spend": 18000 + days * 40,
            "sell_through_pct": 0.62,
        },
        "generated_at": now.isoformat(),
    }
