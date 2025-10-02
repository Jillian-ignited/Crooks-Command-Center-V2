# backend/routers/competitive.py
"""
Competitive Analysis Router - Now using REAL data from intelligence uploads
Replaces all mock data with actual uploaded competitive intelligence
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

@router.get("/analysis")
async def get_competitive_analysis() -> Dict[str, Any]:
    """Get competitive analysis from real intelligence uploads"""
    
    # Get real competitive data from intelligence uploads
    competitive_data = DataService.get_competitive_insights()
    
    # Build analysis from real data
    analysis = competitive_data.get("analysis", {})
    insights = competitive_data.get("insights", [])
    brands_analyzed = competitive_data.get("brands_analyzed", 0)
    
    # Process insights to extract actionable intelligence
    processed_insights = _process_competitive_insights(insights)
    
    return {
        "analysis": {
            "market_position": analysis.get("market_position", "no_data"),
            "differentiation": analysis.get("differentiation", []),
            "opportunities": analysis.get("opportunities", []),
            "threats": _extract_threats(insights),
            "competitive_advantages": _extract_advantages(insights)
        },
        "insights": processed_insights,
        "brands_analyzed": brands_analyzed,
        "market_intelligence": _build_market_intelligence(insights),
        "recommendations": _generate_competitive_recommendations(insights, brands_analyzed),
        "data_freshness": {
            "last_updated": competitive_data.get("last_updated"),
            "intelligence_sources": brands_analyzed
        },
        "generated_at": datetime.datetime.now().isoformat(),
        "data_source": "real_intelligence_uploads"
    }

@router.get("/brands")
async def get_competitive_brands() -> Dict[str, Any]:
    """Get list of analyzed competitive brands from uploads"""
    
    competitive_data = DataService.get_competitive_insights()
    insights = competitive_data.get("insights", [])
    
    # Extract brand information from insights
    brands = _extract_brand_data(insights)
    
    return {
        "total_brands": len(brands),
        "brands": brands,
        "analysis_coverage": {
            "with_insights": len([b for b in brands if b.get("insights_count", 0) > 0]),
            "with_metrics": len([b for b in brands if b.get("has_metrics", False)]),
            "recently_updated": len([b for b in brands if b.get("recently_updated", False)])
        },
        "last_updated": competitive_data.get("last_updated"),
        "data_source": "intelligence_uploads"
    }

@router.get("/board")
async def get_competitive_board() -> Dict[str, Any]:
    """Get competitive intelligence board/dashboard"""
    
    competitive_data = DataService.get_competitive_insights()
    insights = competitive_data.get("insights", [])
    brands_analyzed = competitive_data.get("brands_analyzed", 0)
    
    # Create competitive board with key metrics
    board_data = {
        "overview": {
            "total_competitors": brands_analyzed,
            "active_monitoring": brands_analyzed,  # Assuming all analyzed brands are monitored
            "intelligence_points": len(insights),
            "last_analysis": competitive_data.get("last_updated")
        },
        "key_competitors": _get_key_competitors(insights),
        "market_trends": _extract_market_trends(insights),
        "competitive_gaps": _identify_competitive_gaps(insights),
        "opportunity_matrix": _build_opportunity_matrix(insights),
        "threat_assessment": _assess_threats(insights)
    }
    
    return board_data

@router.get("/compare")
async def compare_brands(brand1: Optional[str] = None, brand2: Optional[str] = None) -> Dict[str, Any]:
    """Compare specific brands from intelligence data"""
    
    competitive_data = DataService.get_competitive_insights()
    insights = competitive_data.get("insights", [])
    
    if not brand1 or not brand2:
        # Return available brands for comparison
        brands = _extract_brand_names(insights)
        return {
            "available_brands": brands,
            "message": "Specify brand1 and brand2 parameters to compare",
            "example": f"/compare?brand1={brands[0] if brands else 'BrandA'}&brand2={brands[1] if len(brands) > 1 else 'BrandB'}"
        }
    
    # Get insights for each brand
    brand1_insights = [insight for insight in insights if _matches_brand(insight, brand1)]
    brand2_insights = [insight for insight in insights if _matches_brand(insight, brand2)]
    
    comparison = {
        "brand_1": {
            "name": brand1,
            "insights_count": len(brand1_insights),
            "key_insights": brand1_insights[:5],  # Top 5 insights
            "strengths": _extract_brand_strengths(brand1_insights),
            "weaknesses": _extract_brand_weaknesses(brand1_insights)
        },
        "brand_2": {
            "name": brand2,
            "insights_count": len(brand2_insights),
            "key_insights": brand2_insights[:5],  # Top 5 insights
            "strengths": _extract_brand_strengths(brand2_insights),
            "weaknesses": _extract_brand_weaknesses(brand2_insights)
        },
        "comparison_summary": _generate_comparison_summary(brand1_insights, brand2_insights),
        "competitive_advantages": _identify_competitive_advantages(brand1_insights, brand2_insights),
        "generated_at": datetime.datetime.now().isoformat()
    }
    
    return comparison

@router.get("/mentions")
async def get_competitive_mentions() -> Dict[str, Any]:
    """Get competitive brand mentions from intelligence data"""
    
    competitive_data = DataService.get_competitive_insights()
    insights = competitive_data.get("insights", [])
    
    # Extract mentions and references
    mentions = _extract_mentions(insights)
    
    return {
        "total_mentions": len(mentions),
        "mentions": mentions,
        "mention_analysis": {
            "by_brand": _group_mentions_by_brand(mentions),
            "by_sentiment": _analyze_mention_sentiment(mentions),
            "trending_topics": _extract_trending_topics(mentions)
        },
        "last_updated": competitive_data.get("last_updated"),
        "data_source": "intelligence_uploads"
    }

# Helper functions for processing competitive intelligence

def _process_competitive_insights(insights: List[Dict]) -> List[Dict[str, Any]]:
    """Process raw insights into structured competitive intelligence"""
    
    processed = []
    for insight in insights[:20]:  # Limit to top 20 insights
        if isinstance(insight, dict):
            processed_insight = {
                "id": insight.get("id", f"insight_{len(processed)}"),
                "title": insight.get("title", "Competitive Insight"),
                "description": insight.get("description", str(insight)),
                "brand": insight.get("brand", "Unknown"),
                "category": insight.get("category", "general"),
                "impact": insight.get("impact", "medium"),
                "confidence": insight.get("confidence", 0.7),
                "source": insight.get("source", "intelligence_upload"),
                "timestamp": insight.get("timestamp", datetime.datetime.now().isoformat())
            }
            processed.append(processed_insight)
    
    return processed

def _extract_threats(insights: List[Dict]) -> List[str]:
    """Extract competitive threats from insights"""
    
    threats = []
    threat_keywords = ["threat", "risk", "challenge", "competition", "aggressive", "undercut"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in threat_keywords:
                if keyword in text:
                    threat_desc = insight.get("description", f"Competitive {keyword} identified")
                    if threat_desc not in threats:
                        threats.append(threat_desc)
                    break
    
    return threats[:5]  # Return top 5 threats

def _extract_advantages(insights: List[Dict]) -> List[str]:
    """Extract competitive advantages from insights"""
    
    advantages = []
    advantage_keywords = ["advantage", "strength", "unique", "superior", "leader", "innovative"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in advantage_keywords:
                if keyword in text:
                    advantage_desc = insight.get("description", f"Competitive {keyword} identified")
                    if advantage_desc not in advantages:
                        advantages.append(advantage_desc)
                    break
    
    return advantages[:5]  # Return top 5 advantages

def _build_market_intelligence(insights: List[Dict]) -> Dict[str, Any]:
    """Build market intelligence summary"""
    
    if not insights:
        return {
            "market_size": "No data available",
            "growth_trends": [],
            "key_players": [],
            "market_dynamics": "Upload competitive intelligence to see market analysis"
        }
    
    # Extract market information from insights
    key_players = list(set([
        insight.get("brand", "Unknown") 
        for insight in insights 
        if isinstance(insight, dict) and insight.get("brand")
    ]))
    
    growth_trends = _extract_growth_trends(insights)
    market_dynamics = _extract_market_dynamics(insights)
    
    return {
        "market_size": f"{len(insights)} intelligence points analyzed",
        "growth_trends": growth_trends,
        "key_players": key_players[:10],  # Top 10 players
        "market_dynamics": market_dynamics
    }

def _generate_competitive_recommendations(insights: List[Dict], brands_analyzed: int) -> List[Dict[str, Any]]:
    """Generate competitive recommendations based on intelligence"""
    
    recommendations = []
    
    if brands_analyzed == 0:
        recommendations.append({
            "priority": "high",
            "title": "Start Competitive Intelligence Gathering",
            "description": "No competitive data found. Begin uploading competitor research and market intelligence.",
            "action": "Upload competitive analysis files through the Intelligence module",
            "impact": "strategic_positioning"
        })
        return recommendations
    
    if brands_analyzed < 5:
        recommendations.append({
            "priority": "medium",
            "title": "Expand Competitive Analysis",
            "description": f"Only {brands_analyzed} competitors analyzed. Expand to include more market players.",
            "action": "Research and upload data on additional 5-10 key competitors",
            "impact": "market_coverage"
        })
    
    # Analyze insights for specific recommendations
    if insights:
        # Look for opportunity patterns
        opportunity_insights = [
            insight for insight in insights 
            if isinstance(insight, dict) and "opportunity" in str(insight.get("description", "")).lower()
        ]
        
        if opportunity_insights:
            recommendations.append({
                "priority": "high",
                "title": "Capitalize on Market Opportunities",
                "description": f"Found {len(opportunity_insights)} market opportunities in competitive analysis.",
                "action": "Review opportunity insights and develop action plans",
                "impact": "growth"
            })
    
    return recommendations

def _extract_brand_data(insights: List[Dict]) -> List[Dict[str, Any]]:
    """Extract brand data from insights"""
    
    brands = {}
    
    for insight in insights:
        if isinstance(insight, dict):
            brand_name = insight.get("brand", "Unknown")
            if brand_name not in brands:
                brands[brand_name] = {
                    "name": brand_name,
                    "insights_count": 0,
                    "has_metrics": False,
                    "recently_updated": False,
                    "categories": set()
                }
            
            brands[brand_name]["insights_count"] += 1
            
            if insight.get("metrics"):
                brands[brand_name]["has_metrics"] = True
            
            if insight.get("category"):
                brands[brand_name]["categories"].add(insight["category"])
    
    # Convert to list and clean up
    brand_list = []
    for brand_data in brands.values():
        brand_data["categories"] = list(brand_data["categories"])
        brand_list.append(brand_data)
    
    return sorted(brand_list, key=lambda x: x["insights_count"], reverse=True)

def _get_key_competitors(insights: List[Dict]) -> List[Dict[str, Any]]:
    """Get key competitors from insights"""
    
    brand_data = _extract_brand_data(insights)
    return brand_data[:5]  # Top 5 competitors by insight count

def _extract_market_trends(insights: List[Dict]) -> List[str]:
    """Extract market trends from insights"""
    
    trends = []
    trend_keywords = ["trend", "growing", "increasing", "emerging", "popular", "rising"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in trend_keywords:
                if keyword in text:
                    trend_desc = insight.get("description", f"Market {keyword} identified")
                    if trend_desc not in trends:
                        trends.append(trend_desc)
                    break
    
    return trends[:5]  # Return top 5 trends

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
    
    return gaps[:5]  # Return top 5 gaps

def _build_opportunity_matrix(insights: List[Dict]) -> Dict[str, Any]:
    """Build opportunity matrix from insights"""
    
    opportunities = []
    for insight in insights:
        if isinstance(insight, dict) and "opportunity" in str(insight.get("description", "")).lower():
            opportunities.append({
                "description": insight.get("description", ""),
                "impact": insight.get("impact", "medium"),
                "effort": insight.get("effort", "medium"),
                "brand": insight.get("brand", "Market")
            })
    
    return {
        "high_impact_low_effort": [op for op in opportunities if op["impact"] == "high" and op["effort"] == "low"],
        "high_impact_high_effort": [op for op in opportunities if op["impact"] == "high" and op["effort"] == "high"],
        "total_opportunities": len(opportunities)
    }

def _assess_threats(insights: List[Dict]) -> Dict[str, Any]:
    """Assess competitive threats"""
    
    threats = _extract_threats(insights)
    
    return {
        "immediate_threats": [t for t in threats if "immediate" in t.lower() or "urgent" in t.lower()],
        "long_term_threats": [t for t in threats if "long" in t.lower() or "future" in t.lower()],
        "total_threats": len(threats),
        "threat_level": "high" if len(threats) > 3 else "medium" if len(threats) > 1 else "low"
    }

# Additional helper functions for brand comparison and mentions

def _extract_brand_names(insights: List[Dict]) -> List[str]:
    """Extract unique brand names from insights"""
    brands = set()
    for insight in insights:
        if isinstance(insight, dict) and insight.get("brand"):
            brands.add(insight["brand"])
    return list(brands)

def _matches_brand(insight: Dict, brand_name: str) -> bool:
    """Check if insight matches a specific brand"""
    if not isinstance(insight, dict):
        return False
    
    insight_brand = insight.get("brand", "").lower()
    return brand_name.lower() in insight_brand or insight_brand in brand_name.lower()

def _extract_brand_strengths(insights: List[Dict]) -> List[str]:
    """Extract brand strengths from insights"""
    strengths = []
    strength_keywords = ["strength", "advantage", "strong", "leader", "best", "superior"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in strength_keywords:
                if keyword in text:
                    strengths.append(insight.get("description", f"Brand {keyword}"))
                    break
    
    return strengths[:3]  # Top 3 strengths

def _extract_brand_weaknesses(insights: List[Dict]) -> List[str]:
    """Extract brand weaknesses from insights"""
    weaknesses = []
    weakness_keywords = ["weakness", "weak", "lacking", "poor", "behind", "struggling"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in weakness_keywords:
                if keyword in text:
                    weaknesses.append(insight.get("description", f"Brand {keyword}"))
                    break
    
    return weaknesses[:3]  # Top 3 weaknesses

def _generate_comparison_summary(brand1_insights: List[Dict], brand2_insights: List[Dict]) -> str:
    """Generate comparison summary between two brands"""
    
    if not brand1_insights and not brand2_insights:
        return "No competitive intelligence available for comparison"
    
    brand1_count = len(brand1_insights)
    brand2_count = len(brand2_insights)
    
    if brand1_count > brand2_count:
        return f"Brand 1 has more intelligence coverage ({brand1_count} vs {brand2_count} insights)"
    elif brand2_count > brand1_count:
        return f"Brand 2 has more intelligence coverage ({brand2_count} vs {brand1_count} insights)"
    else:
        return f"Both brands have equal intelligence coverage ({brand1_count} insights each)"

def _identify_competitive_advantages(brand1_insights: List[Dict], brand2_insights: List[Dict]) -> List[str]:
    """Identify competitive advantages between brands"""
    
    advantages = []
    
    # Compare insight quality and coverage
    if len(brand1_insights) > len(brand2_insights):
        advantages.append("Brand 1 has more comprehensive market intelligence")
    elif len(brand2_insights) > len(brand1_insights):
        advantages.append("Brand 2 has more comprehensive market intelligence")
    
    # This could be enhanced with more sophisticated analysis
    return advantages

def _extract_mentions(insights: List[Dict]) -> List[Dict[str, Any]]:
    """Extract brand mentions from insights"""
    
    mentions = []
    for insight in insights:
        if isinstance(insight, dict):
            mentions.append({
                "brand": insight.get("brand", "Unknown"),
                "mention": insight.get("description", ""),
                "source": insight.get("source", "intelligence_upload"),
                "timestamp": insight.get("timestamp", datetime.datetime.now().isoformat()),
                "category": insight.get("category", "general")
            })
    
    return mentions

def _group_mentions_by_brand(mentions: List[Dict]) -> Dict[str, int]:
    """Group mentions by brand"""
    
    brand_counts = {}
    for mention in mentions:
        brand = mention.get("brand", "Unknown")
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    return brand_counts

def _analyze_mention_sentiment(mentions: List[Dict]) -> Dict[str, int]:
    """Analyze sentiment of mentions (basic keyword analysis)"""
    
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    
    positive_keywords = ["good", "great", "excellent", "strong", "leader", "best"]
    negative_keywords = ["bad", "poor", "weak", "struggling", "behind", "worst"]
    
    for mention in mentions:
        text = str(mention.get("mention", "")).lower()
        
        has_positive = any(keyword in text for keyword in positive_keywords)
        has_negative = any(keyword in text for keyword in negative_keywords)
        
        if has_positive and not has_negative:
            sentiment_counts["positive"] += 1
        elif has_negative and not has_positive:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1
    
    return sentiment_counts

def _extract_trending_topics(mentions: List[Dict]) -> List[str]:
    """Extract trending topics from mentions"""
    
    # This is a simplified version - could be enhanced with NLP
    topics = []
    common_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
    
    word_counts = {}
    for mention in mentions:
        text = str(mention.get("mention", "")).lower()
        words = text.split()
        
        for word in words:
            word = word.strip(".,!?;:")
            if len(word) > 3 and word not in common_words:
                word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top trending words
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

def _extract_market_dynamics(insights: List[Dict]) -> str:
    """Extract market dynamics summary"""
    
    if not insights:
        return "No market dynamics data available"
    
    dynamics_keywords = ["dynamic", "changing", "shift", "evolution", "transformation"]
    
    for insight in insights:
        if isinstance(insight, dict):
            text = str(insight.get("description", "")).lower()
            for keyword in dynamics_keywords:
                if keyword in text:
                    return insight.get("description", "Market dynamics identified")
    
    return f"Market analysis based on {len(insights)} intelligence points"
