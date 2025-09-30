# backend/routers/executive.py
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

@router.get("/")
async def executive_root():
    return {"module": "executive", "status": "active"}

@router.get("/overview")
async def get_executive_overview(brand: Optional[str] = Query(None)):
    """Get executive overview metrics"""
    return {
        "brand": brand or "Crooks & Castles",
        "metrics": {
            "engagement_rate": 4.8,
            "follower_growth": 12.3,
            "content_performance": 87.5,
            "sentiment_score": 0.72
        },
        "top_posts": [],
        "trending_topics": ["streetwear", "urban fashion", "lifestyle"],
        "competitor_insights": []
    }

@router.get("/metrics")
async def get_executive_metrics(brand: Optional[str] = Query(None)):
    """Get detailed executive metrics"""
    return {
        "brand": brand or "Crooks & Castles",
        "period": "30d",
        "kpis": {
            "reach": 245000,
            "impressions": 890000,
            "engagement": 42500,
            "conversions": 1250
        },
        "trends": {
            "reach": 15.2,
            "engagement": 8.7,
            "sentiment": 3.4
        }
    }

@router.get("/kpis")
async def get_kpis():
    """Get key performance indicators"""
    return {
        "social": {"followers": 125000, "engagement_rate": 4.8},
        "content": {"posts": 45, "avg_engagement": 2500},
        "sales": {"revenue": 125000, "conversion_rate": 3.2}
    }

@router.post("/refresh")
async def refresh_metrics():
    """Refresh executive metrics"""
    return {"status": "refreshed", "timestamp": "2025-09-30T17:00:00Z"}
