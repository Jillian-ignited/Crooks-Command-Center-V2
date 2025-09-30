# backend/routers/competitive.py
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/brands")
async def get_competitive_brands():
    """Get list of competitive brands"""
    return {
        "brands": [
            {"id": "crooks", "name": "Crooks & Castles", "is_primary": True},
            {"id": "supreme", "name": "Supreme", "is_primary": False},
            {"id": "stussy", "name": "Stüssy", "is_primary": False}
        ]
    }

@router.get("/board")
async def get_competitive_board(
    days: int = Query(30),
    limit: int = Query(30),
    primary: str = Query("Crooks & Castles")
):
    """Get competitive intelligence board"""
    return {
        "primary_brand": primary,
        "period_days": days,
        "mentions": [],
        "sentiment": {"positive": 65, "neutral": 25, "negative": 10}
    }

@router.get("/compare")
async def compare_brands(brands: str = Query(...)):
    """Compare multiple brands"""
    return {
        "brands": brands.split(","),
        "comparison": {},
        "winner": None
    }

@router.get("/mentions")
async def get_competitive_mentions():
    """Get competitive mentions"""
    return {"mentions": []}

@router.get("/analysis")
async def get_competitive_analysis():
    """Get competitive analysis"""
    return {"analysis": {}, "insights": []}
