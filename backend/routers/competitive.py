# backend/routers/competitive.py
""" Enhanced Competitive Analysis Router - Preserves brand intelligence + adds real data

Combines existing brand positioning with real intelligence uploads for comprehensive analysis
"""

from fastapi import APIRouter
from typing import Dict, Any, List, Optional
import datetime
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from data_service import DataService
except ImportError:
    # Fallback if data_service isn't available
    class DataService:
        @staticmethod
        def get_competitive_insights():
            return {"brands_analyzed": 0, "insights": [], "analysis": {"market_position": "no_data", "differentiation": [], "opportunities": []}}

router = APIRouter()

# PRESERVED BRAND INTELLIGENCE - Core competitive positioning for Crooks & Castles
CORE_BRAND_INTELLIGENCE = {
    "brand_identity": {
        "name": "Crooks & Castles",
        "positioning_statement": "Authentic streetwear pioneer rooted in the hustle of street culture, empowering the new generation of creators and entrepreneurs.",
        "market_position": "strong",
        "heritage_positioning": "authentic streetwear pioneer"
    },
    "brand_pillars": {
        "differentiation": [
            "heritage",
            "streetwear authenticity",
            "urban culture",
            "hip-hop legacy",
            "premium positioning"
        ],
        "strategic_opportunities": [
            "digital engagement",
            "collaborations",
            "international expansion",
            "gen-z market penetration",
            "sustainable streetwear"
        ]
    },
    "competitive_advantages": [
        {
            "advantage": "20+ year heritage",
            "description": "Established brand with a long history of authenticity and credibility in the streetwear space.",
            "strength": "high"
        },
        {
            "advantage": "Authentic hip-hop culture connection",
            "description": "Deep roots in hip-hop culture, with a history of organic celebrity endorsements and cultural relevance.",
            "strength": "high"
        },
        {
            "advantage": "Premium quality positioning",
            "description": "Reputation for high-quality materials and construction, justifying a premium price point.",
            "strength": "medium"
        },
        {
            "advantage": "Celebrity endorsements history",
            "description": "Long history of being worn by major celebrities, creating aspirational value.",
            "strength": "medium"
        },
        {
            "advantage": "Distinctive design aesthetic",
            "description": "Recognizable branding and design language that stands out in a crowded market.",
            "strength": "high"
        }
    ]
}

COMPETITOR_BRANDS = {
    "high_threat": [
        {"name": "Hellstar", "notes": "Competes for youth/Gen Z hype, heavy rap co-signs, viral graphics. Threat in digital + influencer space."},
        {"name": "Memory Lane", "notes": "Pulls Gen Z into Y2K nostalgia with graphic-heavy tees/hoodies. Threat in DTC + mall retail."},
        {"name": "Smoke Rise", "notes": "Mass mall/streetwear at price-driven level. Threat in urban mall doors + off-price crossover."},
        {"name": "Reason Clothing", "notes": "Graphic-led, online + mall presence. Threat in same consumer tier (accessible streetwear)."},
        {"name": "Purple Brand", "notes": "Denim + streetwear hybrid, strong in department stores/luxury malls. Threat in premium denim + wholesale channels."},
        {"name": "Amiri", "notes": "Luxury LA streetwear with celebrity influence. Threat aspirationally (Crooks customers “trade up” to Amiri)."}
    ],
    "medium_threat": [
        {"name": "Aimé Leon Dore (ALD)", "notes": "Competes in credibility and boutique culture storytelling, but aesthetic is more retro-luxe than Crooks’ grit. Threat in cultural positioning."},
        {"name": "Kith", "notes": "Collab-driven and aspirational, but less “armor.” Threat in premium lifestyle collabs + global visibility."},
        {"name": "Supreme", "notes": "Still iconic, but corporate era erodes authenticity. Threat in global brand recognition and resale hype."},
        {"name": "Fear of God (Essentials)", "notes": "Minimalist luxe basics. Threat in comfort/lifestyle category, not codes."},
        {"name": "Off-White", "notes": "High-fashion crossover, but fading without Virgil. Threat in luxury status appeal."},
        {"name": "BAPE", "notes": "Commercialized, but still has global name. Threat in international markets and legacy positioning."},
        {"name": "Palace", "notes": "UK skate/street credibility. Threat in European streetwear."},
        {"name": "Godspeed", "notes": "Newer, niche but rising. Threat in youth discovery channels (TikTok, IG, resale)."}
    ],
    "low_threat": [
        {"name": "LRG", "notes": "Heritage, but nostalgia-only."},
        {"name": "Ecko Unlimited", "notes": "Off-price, no cultural pull left."},
        {"name": "Sean John / Rocawear", "notes": "Dormant, minimal activity."},
        {"name": "Von Dutch", "notes": "Trend revival, narrow niche."},
        {"name": "Ed Hardy", "notes": "Tattoo-driven Y2K revival, but not a fortress brand."},
        {"name": "Affliction", "notes": "Rock/club niche, irrelevant for Crooks customer."},
        {"name": "Nike Sportswear / Jordan / Adidas Originals", "notes": "Borrow street cred via collabs; not true competitor in codes."},
        {"name": "Puma / New Balance Lifestyle", "notes": "Sneaker-first, minor overlap."},
        {"name": "H&M / Zara / BoohooMAN / Shein", "notes": "Compete on price, not brand."},
        {"name": "PacSun / Zumiez Private Label", "notes": "Trend-only, low cultural threat."}
    ]
}

@router.get("/analysis")
async def get_competitive_analysis() -> Dict[str, Any]:
    """Get competitive analysis, combining preserved brand intelligence with real data"""
    
    # Get real data from intelligence uploads
    competitive_data = DataService.get_competitive_insights()
    
    # Combine preserved intelligence with real data
    combined_analysis = {
        "brand_positioning": CORE_BRAND_INTELLIGENCE,
        "competitor_landscape": COMPETITOR_BRANDS,
        "data_from_uploads": competitive_data,
        "intelligence_score": _calculate_intelligence_score(competitive_data),
        "strategic_recommendations": _generate_strategic_recommendations(competitive_data),
        "brand_comparisons": _generate_brand_comparisons(competitive_data) # New
    }
    
    return combined_analysis

@router.get("/positioning")
async def get_brand_positioning() -> Dict[str, Any]:
    """Get the core brand positioning and competitive advantages"""
    return CORE_BRAND_INTELLIGENCE

def _calculate_intelligence_score(competitive_data: Dict) -> Dict[str, Any]:
    """Calculate an intelligence score based on the amount of data available"""
    
    base_score = 75  # From preserved brand intelligence
    upload_bonus = min(25, competitive_data["brands_analyzed"] * 5) # 5 points per brand analyzed
    total_score = base_score + upload_bonus
    
    if total_score >= 90:
        coverage = "excellent"
    elif total_score >= 80:
        coverage = "good"
    else:
        coverage = "basic"
        
    return {
        "total_score": total_score,
        "base_from_brand_intel": base_score,
        "bonus_from_uploads": upload_bonus,
        "coverage_level": coverage
    }

def _generate_strategic_recommendations(competitive_data: Dict) -> list:
    """Generate strategic recommendations based on competitive data"""
    
    recommendations = []
    
    # If no competitive data, recommend uploading some
    if competitive_data["brands_analyzed"] == 0:
        recommendations.append({
            "area": "Competitive Intelligence",
            "recommendation": "No competitor data found. Upload competitive intelligence to identify market opportunities and threats.",
            "priority": "High"
        })
    
    # If there are insights, recommend actions
    if competitive_data["insights"]:
        recommendations.append({
            "area": "Market Opportunities",
            "recommendation": "Analyze competitive insights to identify market gaps and opportunities for growth.",
            "priority": "Medium"
        })
        
    return recommendations

def _generate_brand_comparisons(competitive_data: Dict) -> Dict[str, Any]:
    """Generate brand comparisons based on competitive data"""
    
    # Get a list of competitor brands from the uploaded data
    competitor_brands = [insight["brand"] for insight in competitive_data["insights"] if "brand" in insight]
    
    # For now, we'll create a placeholder comparison. 
    # In a real scenario, you'd pull metrics for each competitor.
    comparisons = {}
    for brand in competitor_brands:
        comparisons[brand] = {
            "market_position": "strong" if "supreme" in brand.lower() else "medium",
            "differentiation": ["hype", "scarcity"] if "supreme" in brand.lower() else ["mainstream", "accessible"],
            "estimated_revenue": 1000000 if "supreme" in brand.lower() else 500000
        }
        
    return {
        "crooks_and_castles": {
            "market_position": CORE_BRAND_INTELLIGENCE["brand_identity"]["market_position"],
            "differentiation": CORE_BRAND_INTELLIGENCE["brand_pillars"]["differentiation"],
            "estimated_revenue": DataService.get_shopify_metrics()["total_sales"]
        },
        "competitors": comparisons
    }

# --- Helper functions to extract insights from text (can be expanded) ---

def _extract_trending_topics(mentions: List[Dict]) -> List[str]:
    """Extract trending topics from mentions"""
    
    # Get top trending words
    word_counts = {}
    for mention in mentions:
        text = str(mention.get("text", "")).lower()
        for word in text.split():
            word_counts[word] = word_counts.get(word, 0) + 1
            
    trending = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in trending[:10] if count > 1]

def _extract_growth_trends(insights: List[Dict]) -> List[str]:
    """Extract growth trends from insights"""
    
    trends = []
    growth_keywords = ["growth", "growing", "increase", "rising", "expanding", "boom"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in growth_keywords:
                if keyword in text:
                    trends.append(insight.get("description", f"Growth {keyword} identified"))
                    break
    
    return trends[:5]

def _identify_competitive_gaps(insights: List[Dict]) -> List[str]:
    """Identify competitive gaps from insights"""
    
    gaps = []
    gap_keywords = ["gap", "missing", "lacking", "opportunity", "unmet", "underserved"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in gap_keywords:
                if keyword in text:
                    gap_desc = insight.get("description", f"Market {keyword} identified")
                    if gap_desc not in gaps:
                        gaps.append(gap_desc)
                        break
                        
    return gaps[:5] # Return top 5 gaps

