# backend/routers/summary.py
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

router = APIRouter()

def _coerce_days(val) -> int:
    s = str(val).strip().strip('"').strip("'")
    try: n = int(s)
    except: n = 30
    return max(1, min(365, n))

@router.get("/overview")
def overview(days: str | int = Query(30)):
    d = _coerce_days(days)
    now = datetime.utcnow()
    return {
        "ok": True,
        "window_days": d,
        "period": {"start": (now - timedelta(days=d)).date().isoformat(),
                   "end": now.date().isoformat()},
        "kpis": {
            "revenue": 125000 + d * 173,
            "margin_pct": 0.46,
            "ad_spend": 18000 + d * 40,
            "sell_through_pct": 0.62,
        },
        "generated_at": now.isoformat(),
    }
