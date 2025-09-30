# backend/routers/competitive.py
from fastapi import APIRouter, Query
from typing import List, Optional
import random

router = APIRouter()

# Your 40 streetwear brands
STREETWEAR_BRANDS = [
    {"id": "crooks", "name": "Crooks & Castles", "is_primary": True, "category": "streetwear"},
    {"id": "supreme", "name": "Supreme", "is_primary": False, "category": "streetwear"},
    {"id": "stussy", "name": "Stüssy", "is_primary": False, "category": "streetwear"},
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
    {"id": "edhardy", "name": "Ed Hardy", "is_primary": False, "category": "streetwear"},
    {"id": "vondutch", "name": "Von Dutch", "is_primary": False, "category": "streetwear"},
    {"id": "godspeed", "name": "Godspeed", "is_primary": False, "category": "streetwear"},
    {"id": "smokerise", "name": "Smoke Rise", "is_primary": False, "category": "streetwear"},
    {"id": "reason", "name": "Reason Clothing", "is_primary": False, "category": "streetwear"},
]

def generate_mock_metrics(brand_name: str, is_primary: bool = False):
    """Generate realistic mock metrics for a brand"""
    # Primary brand gets better metrics
    multiplier = 1.0 if is_primary else random.uniform(0.5, 1.2)
    
    base_orders = int(450 * multiplier)
    base_sales = base_orders * random.uniform(180, 320)
    
    return {
        "brand": brand_name,
        "orders": base_orders,
        "net_sales": round(base_sales, 2),
        "aov": round(base_sales / base_orders if base_orders > 0 else 0, 2),
        "conversion_pct": round(random.uniform(2.1, 4.8), 2),
        "sessions": int(base_orders * random.uniform(45, 85)),
        "plays": int(random.uniform(15000, 85000) * multiplier),
        "likes": int(random.uniform(2500, 12000) * multiplier),
        "comments": int(random.uniform(180, 950) * multiplier),
        "wow": {
            "orders": {"pct": round(random.uniform(-15, 25), 1)},
            "net_sales": {"pct": round(random.uniform(-12, 28), 1)},
            "aov": {"pct": round(random.uniform(-8, 15), 1)},
            "conversion_pct": {"pct": round(random.uniform(-5, 12), 1)},
            "sessions": {"pct": round(random.uniform(-10, 20), 1)},
            "plays": {"pct": round(random.uniform(-18, 35), 1)},
            "likes": {"pct": round(random.uniform(-15, 30), 1)},
            "comments": {"pct": round(random.uniform(-20, 40), 1)},
        }
    }

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
    """Get competitive intelligence board with metrics for all brands"""
    
    # Generate metrics for top brands
    rows = []
    for brand in STREETWEAR_BRANDS[:limit]:
        is_primary = brand["name"] == primary
        metrics = generate_mock_metrics(brand["name"], is_primary)
        rows.append(metrics)
    
    return {
        "primary": primary,
        "period_days": days,
        "rows": rows,
        "total_brands": len(STREETWEAR_BRANDS)
    }

@router.get("/compare")
async def compare_brands(brands: str = Query(...)):
    """Compare multiple brands"""
    brand_list = brands.split(",")
    comparison = {}
    
    for brand_name in brand_list:
        comparison[brand_name] = generate_mock_metrics(brand_name)
    
    # Determine leader by net_sales
    leader = max(comparison.items(), key=lambda x: x[1]["net_sales"])[0] if comparison else None
    
    return {
        "brands": brand_list,
        "comparison": comparison,
        "leader": leader
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
