from fastapi import APIRouter, Query
from typing import Dict, Any
from datetime import datetime

router = APIRouter(tags=["summary"])

def _summary(days: int) -> Dict[str, Any]:
    return {
        "ok": True,
        "window_days": days,
        "executive": {"overview": {"success": True, "notes": "stub exec summary"}, "recommendations": []},
        "intelligence": {"brands": 11, "notes": "stub competitive intelligence summary"},
        "agency": {"active_projects": 0, "completion_rate": 0},
        "media": {"assets": 0},
        "content": {"briefs": 0, "ideas": 0},
        "shopify": {"total_sales": 0, "orders": 0, "aov": 0},
        "last_updated": datetime.utcnow().isoformat(),
    }

@router.get("")
@router.get("/")
def root(days: int = Query(30, ge=1, le=365)):
    return _summary(days)

@router.get("/overview")
@router.get("/summary")
def overview(days: int = Query(30, ge=1, le=365)):
    return _summary(days)
