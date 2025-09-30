# backend/routers/competitive.py
from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter()

# Comprehensive streetwear brand list
STREETWEAR_BRANDS = [
    {"id": "crooks", "name": "Crooks & Castles", "is_primary": True, "category": "streetwear"},
    {"id": "supreme", "name": "Supreme", "is_primary": False, "category": "streetwear"},
    {"id": "stussy", "name": "Stüssy", "is_primary": False, "category": "streetwear"},
    {"id": "edhardy", "name": "Ed Hardy", "is_primary": False, "category": "streetwear"},
    {"id": "vondutch", "name": "Von Dutch", "is_primary": False, "category": "streetwear"},
    {"id": "godspeed", "name": "Godspeed", "is_primary": False, "category": "streetwear"},
    {"id": "smokerise", "name": "Smoke Rise", "is_primary": False, "category": "streetwear"},
    {"id": "reason", "name": "Reason Clothing", "is_primary": False, "category": "streetwear"},
    {"id": "bape", "name": "A Bathing Ape (BAPE)", "is_primary": False, "category": "streetwear"},
    {"id": "offwhite", "name": "Off-White", "is_primary": False, "category": "luxury-streetwear"},
    {"id": "palace", "name": "Palace", "is_primary": False, "category": "streetwear"},
    {"id": "kith", "name": "Kith", "is_primary": False, "category": "streetwear"},
    {"id": "fog", "name": "Fear of God", "is_primary": False, "category": "luxury-streetwear"},
    {"id": "huf", "name": "HUF", "is_primary": False, "category": "skate-streetwear"},
    {"id": "diamond", "name": "Diamond Supply Co.", "is_primary": False, "category": "skate-streetwear"},
    {"id": "10deep", "name": "10.Deep", "is_primary": False, "category": "streetwear"},
    {"id": "hundreds", "name": "The Hundreds", "is_primary": False, "category": "streetwear"},
    {"id": "undefeated", "name": "Undefeated", "is_primary": False, "category": "streetwear"},
    {"id": "carrots", "name": "Carrots", "is_primary": False, "category": "streetwear"},
    {"id": "pleasures", "name": "Pleasures", "is_primary": False, "category": "streetwear"},
    {"id": "braindead", "name": "Brain Dead", "is_primary": False, "category": "streetwear"},
    {"id": "noah", "name": "Noah", "is_primary": False, "category": "streetwear"},
    {"id": "aime", "name": "Aimé Leon Dore", "is_primary": False, "category": "streetwear"},
    {"id": "awge", "name": "AWGE", "is_primary": False, "category": "streetwear"},
    {"id": "anti", "name": "Antisocial Social Club", "is_primary": False, "category": "streetwear"},
    {"id": "billionaire", "name": "Billionaire Boys Club", "is_primary": False, "category": "streetwear"},
    {"id": "icecream", "name": "Ice Cream", "is_primary": False, "category": "streetwear"},
    {"id": "golf", "name": "Golf Wang", "is_primary": False, "category": "streetwear"},
    {"id": "babylon", "name": "Babylon LA", "is_primary": False, "category": "streetwear"},
    {"id": "ripndip", "name": "RIPNDIP", "is_primary": False, "category": "streetwear"},
    {"id": "ftp", "name": "FTP (FuckThePopulation)", "is_primary": False, "category": "streetwear"},
    {"id": "midnight", "name": "Midnight Studios", "is_primary": False, "category": "streetwear"},
    {"id": "rhude", "name": "Rhude", "is_primary": False, "category": "luxury-streetwear"},
    {"id": "amiri", "name": "Amiri", "is_primary": False, "category": "luxury-streetwear"},
    {"id": "essentials", "name": "Essentials (Fear of God)", "is_primary": False, "category": "streetwear"},
    {"id": "represent", "name": "Represent", "is_primary": False, "category": "streetwear"},
    {"id": "trapstar", "name": "Trapstar", "is_primary": False, "category": "streetwear"},
    {"id": "corteiz", "name": "Corteiz", "is_primary": False, "category": "streetwear"},
    {"id": "hellstar", "name": "Hellstar", "is_primary": False, "category": "streetwear"},
    {"id": "misbhv", "name": "MISBHV", "is_primary": False, "category": "streetwear"},
]

@router.get("/brands")
async def get_competitive_brands(category: Optional[str] = None):
    """Get list of competitive brands"""
    brands = STREETWEAR_BRANDS
    
    if category:
        brands = [b for b in brands if b.get("category") == category]
    
    return {
        "brands": brands,
        "total": len(brands),
        "categories": ["streetwear", "luxury-streetwear", "skate-streetwear"]
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
        "competitors": [b["name"] for b in STREETWEAR_BRANDS if not b["is_primary"]][:10],
        "mentions": [],
        "sentiment": {"positive": 65, "neutral": 25, "negative": 10},
        "total_brands": len(STREETWEAR_BRANDS)
    }

@router.get("/compare")
async def compare_brands(brands: str = Query(...)):
    """Compare multiple brands"""
    brand_list = brands.split(",")
    return {
        "brands": brand_list,
        "comparison": {
            brand: {
                "engagement_rate": 4.2,
                "follower_count": 150000,
                "post_frequency": 3.5
            } for brand in brand_list
        },
        "leader": brand_list[0] if brand_list else None
    }

@router.get("/mentions")
async def get_competitive_mentions(brand: Optional[str] = None):
    """Get competitive mentions"""
    return {
        "mentions": [],
        "brand": brand,
        "total": 0
    }

@router.get("/analysis")
async def get_competitive_analysis(brands: Optional[str] = None):
    """Get competitive analysis"""
    return {
        "analysis": {
            "market_position": "strong",
            "differentiation": ["heritage", "streetwear authenticity", "urban culture"],
            "opportunities": ["digital engagement", "collaborations", "international expansion"]
        },
        "insights": [],
        "brands_analyzed": len(STREETWEAR_BRANDS)
    }
