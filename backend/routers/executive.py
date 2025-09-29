from fastapi import APIRouter, Query
from datetime import datetime
from typing import Dict, Any

router = APIRouter(tags=["executive"])

def _payload(days: int) -> Dict[str, Any]:
    return {
        "success": True,
        "timeframe_days": days,
        "shopify_metrics": {"total_sales": 0, "total_orders": 0, "aov": 0, "status": "no_data"},
        "competitive_analysis": {"brands_analyzed": 0, "status": "no_data"},
        "recommendations": [],
        "alerts": [],
        "last_updated": datetime.utcnow().isoformat(),
    }

@router.api_route("", methods=["GET","POST"])
@router.api_route("/", methods=["GET","POST"])
def root(days: int = Query(30, ge=1, le=365)):
    return _payload(days)

@router.api_route("/overview", methods=["GET","POST"])
@router.api_route("/overview/", methods=["GET","POST"])
def overview(days: int = Query(30, ge=1, le=365)):
    return _payload(days)
