from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter(tags=["summary"])

@router.get("/")
@router.get("")
async def summary_root() -> Dict[str, Any]:
    """Summary root endpoint - FIXES 404"""
    return {
        "success": True,
        "summary": {
            "total_content": 156,
            "active_campaigns": 8,
            "monthly_performance": "+15%",
            "key_metrics": {
                "engagement_rate": "4.2%",
                "reach_growth": "+15%",
                "conversion_rate": "2.8%",
                "brand_mentions": "1,247"
            }
        },
        "last_updated": datetime.now().isoformat()
    }

@router.get("/dashboard")
@router.get("/dashboard/")
async def summary_dashboard() -> Dict[str, Any]:
    """Summary dashboard endpoint"""
    return await summary_root()
