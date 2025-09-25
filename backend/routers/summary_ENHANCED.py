from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.analyzer import weekly_summary, brand_intelligence, enhanced_sentiment_analysis, detect_content_gaps
from services.scraper import load_all_uploaded_frames
from typing import Dict, Any, List
import pandas as pd
from collections import Counter
import re
from datetime import datetime, timedelta

router = APIRouter()

def generate_prioritized_actions(df: pd.DataFrame, intelligence_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate top 3 prioritized actions based on competitive intelligence"""
    
    actions = []
    
    if df.empty:
        return [
            {
                "priority": 1,
                "action": "Upload Competitive Data",
                "description": "Import social media scraper data to begin competitive analysis",
                "impact": "High",
                "effort": "Low",
                "timeline": "Immediate",
                "category": "Data Collection"
            },
            {
                "priority": 2,
                "action": "Set Up Data Sources",
                "description": "Configure regular data collection from key competitors",
                "impact": "High", 
                "effort": "Medium",
                "timeline": "This Week",
                "category": "Infrastructure"
            },
            {
                "priority": 3,
                "action": "Define Success Metrics",
                "description": "Establish KPIs for competitive positioning and content performance",
                "impact": "Medium",
                "effort": "Low", 
                "timeline": "This Week",
                "category": "Strategy"
            }
        ]
    
    # Analyze real data for actionable insights
    
    # Action 1: Content Gap Opportunities
    content_gaps = intelligence_data.get('content_gaps', [])
    if content_gaps and content_gaps[0] != "No data available for gap analysis":
        top_gap = content_gaps[0]
        actions.append({
            "priority": 1,
            "action": "Address Content Gap",
            "description": f"Capitalize on identified opportunity: {top_gap}",
            "impact": "High",
            "effort": "Medium",
            "timeline": "Next 7 Days",
            "category": "Content Strategy"
        })
    
    # Action 2: Trending Hashtag Leverage
    trending_hashtags = intelligence_data.get('trending_hashtags', [])
    if trending_hashtags:
        top_hashtag = trending_hashtags[0]
        actions.append({
            "priority": 2,
            "action": "Leverage Trending Hashtag",
            "description": f"Create content around high-performing hashtag: {top_hashtag}",
            "impact": "Medium",
            "effort": "Low",
            "timeline": "Next 3 Days",
            "category": "Content Creation"
        })
    
    # Action 3: Competitor Analysis
    competitor_analysis = intelligence_data.get('competitor_analysis', [])
    if competitor_analysis:
        # Find rising competitors
        rising_competitors = [c for c in competitor_analysis if c.get('momentum') == '↗']
        if rising_competitors:
            top_rising = rising_competitors[0]
            actions.append({
                "priority": 3,
                "action": "Monitor Rising Competitor",
                "description": f"Analyze {top_rising['brand']}'s strategy - they're gaining momentum",
                "impact": "Medium",
                "effort": "Low",
                "timeline": "Ongoing",
                "category": "Competitive Intelligence"
            })
    
    # Action 4: Sentiment Improvement (if needed)
    sentiment_breakdown = intelligence_data.get('sentiment_breakdown', {})
    positive_sentiment = sentiment_breakdown.get('positive', 0)
    if positive_sentiment < 70:  # If sentiment is below 70%
        actions.append({
            "priority": 2,
            "action": "Improve Content Sentiment",
            "description": f"Current positive sentiment at {positive_sentiment}% - focus on more engaging content",
            "impact": "High",
            "effort": "Medium",
            "timeline": "Next 14 Days",
            "category": "Content Quality"
        })
    
    # Action 5: Cultural Moment Timing
    current_month = datetime.now().strftime("%B")
    cultural_actions = {
        "September": "Leverage Hispanic Heritage Month (Sep 15 - Oct 15) for authentic cultural content",
        "October": "Prepare Black Friday/Cyber Monday campaigns with street culture angle",
        "November": "Create holiday season content that maintains street authenticity",
        "December": "Develop New Year content focusing on community and culture",
        "January": "Capitalize on New Year motivation with lifestyle content",
        "February": "Honor Black History Month with meaningful cultural collaborations"
    }
    
    if current_month in cultural_actions:
        actions.append({
            "priority": 1,
            "action": "Cultural Moment Activation",
            "description": cultural_actions[current_month],
            "impact": "High",
            "effort": "Medium",
            "timeline": "This Month",
            "category": "Cultural Strategy"
        })
    
    # Sort by priority and return top 3
    actions.sort(key=lambda x: x['priority'])
    return actions[:3]

def generate_enhanced_analysis(df: pd.DataFrame, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate enhanced analysis with strategic insights"""
    
    if df.empty:
        return {
            "market_position": "Awaiting Data",
            "competitive_landscape": "No competitive data available",
            "content_performance": "Upload data to analyze content performance",
            "strategic_opportunities": ["Set up competitive intelligence data collection"],
            "risk_factors": ["Limited visibility into competitor activities"],
            "trend_analysis": "Insufficient data for trend analysis",
            "cultural_insights": "Upload social media data to identify cultural trends"
        }
    
    # Analyze market position
    competitor_analysis = intelligence_data.get('competitor_analysis', [])
    cc_position = "Not ranked"
    total_competitors = len(competitor_analysis)
    
    for comp in competitor_analysis:
        if 'crooks' in comp.get('brand', '').lower() or 'castles' in comp.get('brand', '').lower():
            cc_position = f"#{comp.get('rank', 'N/A')} of {total_competitors}"
            break
    
    # Analyze competitive landscape
    rising_competitors = [c['brand'] for c in competitor_analysis if c.get('momentum') == '↗']
    declining_competitors = [c['brand'] for c in competitor_analysis if c.get('momentum') == '↘']
    
    landscape_summary = f"Tracking {total_competitors} competitors. "
    if rising_competitors:
        landscape_summary += f"{len(rising_competitors)} brands gaining momentum: {', '.join(rising_competitors[:3])}. "
    if declining_competitors:
        landscape_summary += f"{len(declining_competitors)} brands declining."
    
    # Content performance analysis
    sentiment_breakdown = intelligence_data.get('sentiment_breakdown', {})
    positive_pct = sentiment_breakdown.get('positive', 0)
    
    if positive_pct >= 80:
        content_performance = f"Strong content performance with {positive_pct}% positive sentiment"
    elif positive_pct >= 60:
        content_performance = f"Moderate content performance at {positive_pct}% positive sentiment"
    else:
        content_performance = f"Content needs improvement - only {positive_pct}% positive sentiment"
    
    # Strategic opportunities
    opportunities = []
    content_gaps = intelligence_data.get('content_gaps', [])
    if content_gaps and content_gaps[0] != "No data available for gap analysis":
        opportunities.extend(content_gaps[:2])
    
    trending_hashtags = intelligence_data.get('trending_hashtags', [])
    if trending_hashtags:
        opportunities.append(f"Leverage trending hashtag: {trending_hashtags[0]}")
    
    # Risk factors
    risks = []
    if rising_competitors:
        risks.append(f"Rising competition from {rising_competitors[0]}")
    
    if positive_pct < 60:
        risks.append("Below-average content sentiment")
    
    if not trending_hashtags:
        risks.append("Limited hashtag trend visibility")
    
    # Trend analysis
    total_posts = len(df)
    brands_tracked = df['brand'].nunique() if 'brand' in df.columns else 0
    
    trend_summary = f"Analyzed {total_posts} posts across {brands_tracked} brands. "
    if trending_hashtags:
        trend_summary += f"Top trend: {trending_hashtags[0]}. "
    
    # Cultural insights
    hashtags_text = ' '.join(trending_hashtags) if trending_hashtags else ""
    cultural_keywords = ['heritage', 'culture', 'community', 'street', 'hip-hop', 'urban', 'authentic']
    cultural_mentions = sum(1 for keyword in cultural_keywords if keyword in hashtags_text.lower())
    
    if cultural_mentions > 0:
        cultural_insights = f"Strong cultural relevance detected with {cultural_mentions} cultural themes in trending content"
    else:
        cultural_insights = "Opportunity to increase cultural authenticity in content strategy"
    
    return {
        "market_position": cc_position,
        "competitive_landscape": landscape_summary,
        "content_performance": content_performance,
        "strategic_opportunities": opportunities[:3],
        "risk_factors": risks[:3] if risks else ["No significant risks identified"],
        "trend_analysis": trend_summary,
        "cultural_insights": cultural_insights
    }

@router.get("/overview")
async def get_summary_overview():
    """Get comprehensive summary overview with enhanced analysis and prioritized actions"""
    
    try:
        # Load real data
        df = load_all_uploaded_frames()
        
        # Get weekly summary
        weekly_data = weekly_summary()
        
        # Get detailed intelligence
        intelligence_data = brand_intelligence([], lookback_days=7)
        
        # Generate enhanced analysis
        enhanced_analysis = generate_enhanced_analysis(df, intelligence_data)
        
        # Generate prioritized actions
        prioritized_actions = generate_prioritized_actions(df, intelligence_data)
        
        # Calculate key performance indicators
        total_posts = weekly_data.get('total_posts', 0)
        total_brands = weekly_data.get('total_brands', 0)
        positive_sentiment = weekly_data.get('positive_sentiment', 0)
        cc_rank = weekly_data.get('cc_rank', 'N/A')
        
        # Determine overall health score
        health_factors = []
        if total_posts > 0:
            health_factors.append(25)  # Data availability
        if positive_sentiment > 70:
            health_factors.append(25)  # Good sentiment
        elif positive_sentiment > 50:
            health_factors.append(15)  # Moderate sentiment
        if isinstance(cc_rank, int) and cc_rank <= 10:
            health_factors.append(25)  # Good ranking
        elif isinstance(cc_rank, int) and cc_rank <= 20:
            health_factors.append(15)  # Moderate ranking
        if intelligence_data.get('trending_hashtags'):
            health_factors.append(25)  # Trend awareness
        
        overall_health = sum(health_factors)
        
        # Determine health status
        if overall_health >= 80:
            health_status = "Excellent"
            health_color = "green"
        elif overall_health >= 60:
            health_status = "Good"
            health_color = "blue"
        elif overall_health >= 40:
            health_status = "Fair"
            health_color = "yellow"
        else:
            health_status = "Needs Attention"
            health_color = "red"
        
        return JSONResponse({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "key_metrics": {
                    "total_posts": total_posts,
                    "total_brands": total_brands,
                    "positive_sentiment": positive_sentiment,
                    "cc_rank": cc_rank,
                    "overall_health": overall_health,
                    "health_status": health_status,
                    "health_color": health_color
                },
                "enhanced_analysis": enhanced_analysis,
                "prioritized_actions": prioritized_actions,
                "weekly_highlights": weekly_data.get('weekly_highlights', []),
                "trending_hashtags": intelligence_data.get('trending_hashtags', [])[:5],
                "competitor_summary": {
                    "total_tracked": len(intelligence_data.get('competitor_analysis', [])),
                    "rising_count": len([c for c in intelligence_data.get('competitor_analysis', []) if c.get('momentum') == '↗']),
                    "declining_count": len([c for c in intelligence_data.get('competitor_analysis', []) if c.get('momentum') == '↘'])
                }
            },
            "data_status": "real_data" if not df.empty else "no_data"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary overview: {str(e)}")

@router.get("/")
async def get_weekly_summary():
    """Get basic weekly summary (existing endpoint)"""
    try:
        summary_data = weekly_summary()
        return JSONResponse(summary_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weekly summary: {str(e)}")

@router.get("/health")
async def summary_health_check():
    """Health check for summary service"""
    return JSONResponse({
        "status": "healthy",
        "service": "summary",
        "timestamp": datetime.now().isoformat()
    })
