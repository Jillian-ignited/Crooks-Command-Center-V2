# backend/routers/competitive.py
""" Complete Competitive Analysis Router - Full frontend compatibility

Preserves brand intelligence + adds real data + all frontend endpoints
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
        {"name": "Hellstar", "notes": "Competes for youth/Gen Z hype, heavy rap co-signs, viral graphics. Threat in digital + influencer space.", "threat_level": "high"},
        {"name": "Memory Lane", "notes": "Pulls Gen Z into Y2K nostalgia with graphic-heavy tees/hoodies. Threat in DTC + mall retail.", "threat_level": "high"},
        {"name": "Smoke Rise", "notes": "Mass mall/streetwear at price-driven level. Threat in urban mall doors + off-price crossover.", "threat_level": "high"},
        {"name": "Reason Clothing", "notes": "Graphic-led, online + mall presence. Threat in same consumer tier (accessible streetwear).", "threat_level": "high"},
        {"name": "Purple Brand", "notes": "Denim + streetwear hybrid, strong in department stores/luxury malls. Threat in premium denim + wholesale channels.", "threat_level": "high"},
        {"name": "Amiri", "notes": "Luxury LA streetwear with celebrity influence. Threat aspirationally (Crooks customers trade up to Amiri).", "threat_level": "high"}
    ],
    "medium_threat": [
        {"name": "Aimé Leon Dore (ALD)", "notes": "Competes in credibility and boutique culture storytelling, but aesthetic is more retro-luxe than Crooks' grit. Threat in cultural positioning.", "threat_level": "medium"},
        {"name": "Kith", "notes": "Collab-driven and aspirational, but less armor. Threat in premium lifestyle collabs + global visibility.", "threat_level": "medium"},
        {"name": "Supreme", "notes": "Still iconic, but corporate era erodes authenticity. Threat in global brand recognition and resale hype.", "threat_level": "medium"},
        {"name": "Fear of God (Essentials)", "notes": "Minimalist luxe basics. Threat in comfort/lifestyle category, not codes.", "threat_level": "medium"},
        {"name": "Off-White", "notes": "High-fashion crossover, but fading without Virgil. Threat in luxury status appeal.", "threat_level": "medium"},
        {"name": "BAPE", "notes": "Commercialized, but still has global name. Threat in international markets and legacy positioning.", "threat_level": "medium"},
        {"name": "Palace", "notes": "UK skate/street credibility. Threat in European streetwear.", "threat_level": "medium"},
        {"name": "Godspeed", "notes": "Newer, niche but rising. Threat in youth discovery channels (TikTok, IG, resale).", "threat_level": "medium"}
    ],
    "low_threat": [
        {"name": "LRG", "notes": "Heritage, but nostalgia-only.", "threat_level": "low"},
        {"name": "Ecko Unlimited", "notes": "Off-price, no cultural pull left.", "threat_level": "low"},
        {"name": "Sean John / Rocawear", "notes": "Dormant, minimal activity.", "threat_level": "low"},
        {"name": "Von Dutch", "notes": "Trend revival, narrow niche.", "threat_level": "low"},
        {"name": "Ed Hardy", "notes": "Tattoo-driven Y2K revival, but not a fortress brand.", "threat_level": "low"},
        {"name": "Affliction", "notes": "Rock/club niche, irrelevant for Crooks customer.", "threat_level": "low"},
        {"name": "Nike Sportswear / Jordan / Adidas Originals", "notes": "Borrow street cred via collabs; not true competitor in codes.", "threat_level": "low"},
        {"name": "Puma / New Balance Lifestyle", "notes": "Sneaker-first, minor overlap.", "threat_level": "low"},
        {"name": "H&M / Zara / BoohooMAN / Shein", "notes": "Compete on price, not brand.", "threat_level": "low"},
        {"name": "PacSun / Zumiez Private Label", "notes": "Trend-only, low cultural threat.", "threat_level": "low"}
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
        "brand_comparisons": _generate_brand_comparisons(competitive_data),
        "total_brands_analyzed": 24  # 6 high + 8 medium + 10 low threat brands
    }
    
    return combined_analysis

@router.get("/positioning")
async def get_brand_positioning() -> Dict[str, Any]:
    """Get the core brand positioning and competitive advantages"""
    return CORE_BRAND_INTELLIGENCE

@router.get("/compare")
async def compare_brands(brand1: Optional[str] = None, brand2: Optional[str] = None) -> Dict[str, Any]:
    """Compare specific brands from the competitive landscape"""
    
    # Get all brands from our competitive landscape
    all_brands = []
    for threat_level, brands in COMPETITOR_BRANDS.items():
        all_brands.extend([brand["name"] for brand in brands])
    
    if not brand1 or not brand2:
        return {
            "available_brands": ["Crooks & Castles"] + all_brands,
            "message": "Specify brand1 and brand2 parameters to compare",
            "example": f"/compare?brand1=Crooks & Castles&brand2={all_brands[0] if all_brands else 'Supreme'}"
        }
    
    # Find brand data
    brand1_data = _get_brand_data(brand1)
    brand2_data = _get_brand_data(brand2)
    
    comparison = {
        "brand_1": brand1_data,
        "brand_2": brand2_data,
        "comparison_summary": _generate_comparison_summary(brand1_data, brand2_data),
        "competitive_advantages": _identify_competitive_advantages(brand1_data, brand2_data),
        "generated_at": datetime.datetime.now().isoformat()
    }
    
    return comparison

@router.get("/mentions")
async def get_competitive_mentions() -> Dict[str, Any]:
    """Get competitive brand mentions and analysis"""
    
    # Get real data from intelligence uploads
    competitive_data = DataService.get_competitive_insights()
    insights = competitive_data.get("insights", [])
    
    # Generate mentions from our competitive landscape
    mentions = []
    for threat_level, brands in COMPETITOR_BRANDS.items():
        for brand in brands:
            mentions.append({
                "brand": brand["name"],
                "threat_level": threat_level,
                "notes": brand["notes"],
                "mention_type": "competitive_analysis",
                "timestamp": datetime.datetime.now().isoformat()
            })
    
    # Add any mentions from uploaded intelligence
    for insight in insights:
        if isinstance(insight, dict) and insight.get("brand"):
            mentions.append({
                "brand": insight["brand"],
                "threat_level": "unknown",
                "notes": insight.get("description", ""),
                "mention_type": "intelligence_upload",
                "timestamp": insight.get("timestamp", datetime.datetime.now().isoformat())
            })
    
    return {
        "total_mentions": len(mentions),
        "mentions": mentions,
        "mention_analysis": {
            "by_threat_level": _group_mentions_by_threat(mentions),
            "by_brand": _group_mentions_by_brand(mentions),
            "trending_topics": _extract_trending_topics(mentions)
        },
        "last_updated": datetime.datetime.now().isoformat(),
        "data_source": "competitive_intelligence"
    }

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
    
    # High threat brand recommendations
    recommendations.append({
        "area": "High Threat Competitors",
        "recommendation": "Monitor and differentiate against 6 high-threat brands including Hellstar, Memory Lane, and Amiri.",
        "priority": "High",
        "action": "Develop counter-strategies for each high-threat competitor"
    })
    
    # Medium threat brand recommendations
    recommendations.append({
        "area": "Medium Threat Competitors", 
        "recommendation": "Track 8 medium-threat brands for market positioning opportunities.",
        "priority": "Medium",
        "action": "Identify gaps in medium-threat competitor offerings"
    })
    
    # If no competitive data, recommend uploading some
    if competitive_data["brands_analyzed"] == 0:
        recommendations.append({
            "area": "Competitive Intelligence",
            "recommendation": "Upload competitive intelligence to enhance the 24-brand analysis framework.",
            "priority": "Medium",
            "action": "Gather and upload competitor research data"
        })
        
    return recommendations

def _generate_brand_comparisons(competitive_data: Dict) -> Dict[str, Any]:
    """Generate brand comparisons based on competitive data"""
    
    comparisons = {
        "crooks_and_castles": {
            "market_position": CORE_BRAND_INTELLIGENCE["brand_identity"]["market_position"],
            "differentiation": CORE_BRAND_INTELLIGENCE["brand_pillars"]["differentiation"],
            "threat_level": "baseline",
            "competitive_advantages": len(CORE_BRAND_INTELLIGENCE["competitive_advantages"])
        }
    }
    
    # Add comparisons for each threat level
    for threat_level, brands in COMPETITOR_BRANDS.items():
        for brand in brands:
            comparisons[brand["name"].lower().replace(" ", "_")] = {
                "market_position": "strong" if threat_level == "high_threat" else "medium" if threat_level == "medium_threat" else "weak",
                "threat_level": threat_level,
                "notes": brand["notes"]
            }
        
    return comparisons

def _get_brand_data(brand_name: str) -> Dict[str, Any]:
    """Get data for a specific brand"""
    
    if brand_name.lower() == "crooks & castles":
        return {
            "name": "Crooks & Castles",
            "market_position": CORE_BRAND_INTELLIGENCE["brand_identity"]["market_position"],
            "differentiation": CORE_BRAND_INTELLIGENCE["brand_pillars"]["differentiation"],
            "competitive_advantages": CORE_BRAND_INTELLIGENCE["competitive_advantages"],
            "threat_level": "baseline",
            "heritage": "20+ years",
            "strengths": ["Heritage", "Hip-hop culture", "Premium quality", "Celebrity endorsements", "Distinctive design"]
        }
    
    # Find brand in competitive landscape
    for threat_level, brands in COMPETITOR_BRANDS.items():
        for brand in brands:
            if brand["name"].lower() == brand_name.lower():
                return {
                    "name": brand["name"],
                    "threat_level": threat_level,
                    "notes": brand["notes"],
                    "market_position": "strong" if threat_level == "high_threat" else "medium" if threat_level == "medium_threat" else "weak",
                    "strengths": _extract_strengths_from_notes(brand["notes"]),
                    "weaknesses": _extract_weaknesses_from_notes(brand["notes"])
                }
    
    return {"name": brand_name, "data": "not_found"}

def _generate_comparison_summary(brand1_data: Dict, brand2_data: Dict) -> str:
    """Generate a comparison summary between two brands"""
    
    if brand1_data.get("name") == "Crooks & Castles":
        return f"Crooks & Castles (heritage streetwear pioneer) vs {brand2_data.get('name')} ({brand2_data.get('threat_level', 'unknown')} threat level)"
    elif brand2_data.get("name") == "Crooks & Castles":
        return f"{brand1_data.get('name')} ({brand1_data.get('threat_level', 'unknown')} threat level) vs Crooks & Castles (heritage streetwear pioneer)"
    else:
        return f"{brand1_data.get('name')} vs {brand2_data.get('name')} competitive comparison"

def _identify_competitive_advantages(brand1_data: Dict, brand2_data: Dict) -> List[str]:
    """Identify competitive advantages between brands"""
    
    advantages = []
    
    if brand1_data.get("name") == "Crooks & Castles":
        advantages.extend([
            "20+ year heritage advantage",
            "Authentic hip-hop culture connection",
            "Premium quality positioning",
            "Celebrity endorsement history"
        ])
    
    if brand2_data.get("name") == "Crooks & Castles":
        advantages.extend([
            "20+ year heritage advantage",
            "Authentic hip-hop culture connection", 
            "Premium quality positioning",
            "Celebrity endorsement history"
        ])
    
    return advantages

def _group_mentions_by_threat(mentions: List[Dict]) -> Dict[str, int]:
    """Group mentions by threat level"""
    
    threat_counts = {"high_threat": 0, "medium_threat": 0, "low_threat": 0, "unknown": 0}
    
    for mention in mentions:
        threat_level = mention.get("threat_level", "unknown")
        threat_counts[threat_level] = threat_counts.get(threat_level, 0) + 1
    
    return threat_counts

def _group_mentions_by_brand(mentions: List[Dict]) -> Dict[str, int]:
    """Group mentions by brand"""
    
    brand_counts = {}
    
    for mention in mentions:
        brand = mention.get("brand", "Unknown")
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    return brand_counts

def _extract_trending_topics(mentions: List[Dict]) -> List[str]:
    """Extract trending topics from mentions"""
    
    topics = []
    for mention in mentions:
        notes = mention.get("notes", "")
        if "Gen Z" in notes:
            topics.append("Gen Z targeting")
        if "digital" in notes.lower():
            topics.append("Digital marketing")
        if "collaboration" in notes.lower() or "collab" in notes.lower():
            topics.append("Brand collaborations")
        if "luxury" in notes.lower():
            topics.append("Luxury positioning")
        if "nostalgia" in notes.lower():
            topics.append("Nostalgia marketing")
    
    # Return unique topics
    return list(set(topics))

def _extract_strengths_from_notes(notes: str) -> List[str]:
    """Extract strengths from brand notes"""
    
    strengths = []
    if "hype" in notes.lower():
        strengths.append("Hype generation")
    if "viral" in notes.lower():
        strengths.append("Viral marketing")
    if "luxury" in notes.lower():
        strengths.append("Luxury positioning")
    if "celebrity" in notes.lower():
        strengths.append("Celebrity influence")
    if "global" in notes.lower():
        strengths.append("Global reach")
    
    return strengths

def _extract_weaknesses_from_notes(notes: str) -> List[str]:
    """Extract weaknesses from brand notes"""
    
    weaknesses = []
    if "fading" in notes.lower():
        weaknesses.append("Declining relevance")
    if "corporate" in notes.lower():
        weaknesses.append("Corporate image")
    if "dormant" in notes.lower():
        weaknesses.append("Inactive brand")
    if "nostalgia-only" in notes.lower():
        weaknesses.append("Limited to nostalgia")
    if "off-price" in notes.lower():
        weaknesses.append("Low price positioning")
    
    return weaknesses
