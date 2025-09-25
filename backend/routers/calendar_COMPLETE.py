from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import calendar

router = APIRouter()

class CalendarRequest(BaseModel):
    timeframe: str = "30_days"  # 7_days, 30_days, 60_days, 90_days, quarterly
    include_cultural_moments: bool = True
    include_campaigns: bool = True

def get_cultural_moments() -> List[Dict[str, Any]]:
    """Get cultural moments and heritage celebrations"""
    cultural_moments = [
        {
            "date": "2025-09-15",
            "title": "Hispanic Heritage Month Begins",
            "description": "Celebrate Latino culture and contributions",
            "category": "heritage",
            "priority": "high",
            "content_themes": ["community", "culture", "heritage", "celebration"],
            "hashtags": ["#HispanicHeritageMonth", "#LatinoHeritage", "#CommunityPride"],
            "duration_days": 31
        },
        {
            "date": "2025-09-21",
            "title": "International Day of Peace",
            "description": "Global unity and peace celebration",
            "category": "global",
            "priority": "medium",
            "content_themes": ["unity", "peace", "community", "global"],
            "hashtags": ["#PeaceDay", "#Unity", "#GlobalCommunity"],
            "duration_days": 1
        },
        {
            "date": "2025-10-01",
            "title": "Black History Month (UK)",
            "description": "Celebrate Black history and achievements",
            "category": "heritage",
            "priority": "high",
            "content_themes": ["history", "achievement", "culture", "community"],
            "hashtags": ["#BlackHistoryMonth", "#BlackExcellence", "#Heritage"],
            "duration_days": 31
        },
        {
            "date": "2025-10-11",
            "title": "Hip-Hop History Month",
            "description": "Celebrate hip-hop culture and its impact",
            "category": "culture",
            "priority": "high",
            "content_themes": ["hip-hop", "music", "culture", "street", "authenticity"],
            "hashtags": ["#HipHopHistory", "#HipHopCulture", "#StreetCulture"],
            "duration_days": 31
        },
        {
            "date": "2025-11-01",
            "title": "BFCM Prep Season",
            "description": "Black Friday Cyber Monday preparation",
            "category": "commercial",
            "priority": "high",
            "content_themes": ["deals", "exclusive", "limited", "streetwear"],
            "hashtags": ["#BFCM", "#BlackFriday", "#ExclusiveDeals"],
            "duration_days": 30
        },
        {
            "date": "2025-11-29",
            "title": "Black Friday",
            "description": "Major shopping event",
            "category": "commercial",
            "priority": "high",
            "content_themes": ["deals", "limited", "exclusive", "drop"],
            "hashtags": ["#BlackFriday", "#LimitedDrop", "#ExclusiveDeal"],
            "duration_days": 4
        },
        {
            "date": "2025-12-01",
            "title": "Holiday Season Launch",
            "description": "Holiday shopping and gift season",
            "category": "seasonal",
            "priority": "high",
            "content_themes": ["gifts", "holiday", "family", "celebration"],
            "hashtags": ["#HolidayGifts", "#HolidayStyle", "#GiftGuide"],
            "duration_days": 31
        }
    ]
    
    return cultural_moments

def get_strategic_campaigns() -> List[Dict[str, Any]]:
    """Get strategic campaign recommendations"""
    campaigns = [
        {
            "title": "Street Heritage Fusion",
            "start_date": "2025-09-15",
            "end_date": "2025-10-15",
            "description": "Blend street culture with heritage celebration",
            "category": "cultural_strategy",
            "priority": "high",
            "content_pillars": [
                "Street culture meets heritage",
                "Community storytelling",
                "Authentic representation",
                "Cultural pride"
            ],
            "posting_schedule": {
                "frequency": "daily",
                "optimal_times": ["12:00", "18:00", "21:00"],
                "platforms": ["Instagram", "TikTok", "Twitter"]
            },
            "kpis": ["engagement_rate", "brand_mentions", "cultural_sentiment"],
            "budget_allocation": {
                "content_creation": 40,
                "paid_promotion": 35,
                "influencer_partnerships": 25
            }
        },
        {
            "title": "Hip-Hop Authenticity Series",
            "start_date": "2025-10-11",
            "end_date": "2025-11-11",
            "description": "Celebrate hip-hop culture with authentic storytelling",
            "category": "culture_celebration",
            "priority": "high",
            "content_pillars": [
                "Hip-hop history",
                "Street credibility",
                "Music culture",
                "Community voices"
            ],
            "posting_schedule": {
                "frequency": "3x_weekly",
                "optimal_times": ["15:00", "19:00", "22:00"],
                "platforms": ["TikTok", "Instagram", "YouTube"]
            },
            "kpis": ["video_completion_rate", "shares", "cultural_authenticity_score"],
            "budget_allocation": {
                "video_production": 50,
                "music_licensing": 20,
                "community_partnerships": 30
            }
        },
        {
            "title": "BFCM Exclusive Drops",
            "start_date": "2025-11-01",
            "end_date": "2025-12-02",
            "description": "Limited edition releases for Black Friday Cyber Monday",
            "category": "commercial_campaign",
            "priority": "high",
            "content_pillars": [
                "Exclusive access",
                "Limited availability",
                "Premium quality",
                "Street credibility"
            ],
            "posting_schedule": {
                "frequency": "2x_daily",
                "optimal_times": ["10:00", "16:00", "20:00"],
                "platforms": ["Instagram", "TikTok", "Email", "SMS"]
            },
            "kpis": ["conversion_rate", "revenue", "email_open_rate", "cart_abandonment"],
            "budget_allocation": {
                "paid_ads": 60,
                "content_creation": 25,
                "email_marketing": 15
            }
        }
    ]
    
    return campaigns

def get_optimal_posting_times() -> Dict[str, List[str]]:
    """Get optimal posting times by platform"""
    return {
        "Instagram": {
            "weekdays": ["12:00", "17:00", "21:00"],
            "weekends": ["11:00", "14:00", "19:00"],
            "best_days": ["Tuesday", "Wednesday", "Friday"]
        },
        "TikTok": {
            "weekdays": ["15:00", "18:00", "21:00"],
            "weekends": ["12:00", "16:00", "20:00"],
            "best_days": ["Tuesday", "Thursday", "Sunday"]
        },
        "Twitter": {
            "weekdays": ["09:00", "12:00", "15:00"],
            "weekends": ["10:00", "13:00", "16:00"],
            "best_days": ["Wednesday", "Thursday", "Friday"]
        },
        "YouTube": {
            "weekdays": ["14:00", "20:00"],
            "weekends": ["12:00", "18:00"],
            "best_days": ["Thursday", "Friday", "Saturday"]
        }
    }

def generate_content_calendar(timeframe: str, include_cultural: bool, include_campaigns: bool) -> List[Dict[str, Any]]:
    """Generate comprehensive content calendar"""
    calendar_items = []
    
    # Calculate date range
    start_date = datetime(2025, 9, 15)  # Start from September 15, 2025
    
    if timeframe == "7_days":
        end_date = start_date + timedelta(days=7)
    elif timeframe == "30_days":
        end_date = start_date + timedelta(days=30)
    elif timeframe == "60_days":
        end_date = start_date + timedelta(days=60)
    elif timeframe == "90_days":
        end_date = start_date + timedelta(days=90)
    elif timeframe == "quarterly":
        end_date = start_date + timedelta(days=90)
    else:
        end_date = start_date + timedelta(days=30)
    
    # Add cultural moments
    if include_cultural:
        cultural_moments = get_cultural_moments()
        for moment in cultural_moments:
            moment_date = datetime.strptime(moment["date"], "%Y-%m-%d")
            if start_date <= moment_date <= end_date:
                calendar_items.append({
                    "date": moment["date"],
                    "type": "cultural_moment",
                    "title": moment["title"],
                    "description": moment["description"],
                    "category": moment["category"],
                    "priority": moment["priority"],
                    "content_suggestions": [
                        f"Create {theme} focused content" for theme in moment["content_themes"]
                    ],
                    "hashtags": moment["hashtags"],
                    "duration": moment["duration_days"]
                })
    
    # Add strategic campaigns
    if include_campaigns:
        campaigns = get_strategic_campaigns()
        for campaign in campaigns:
            campaign_start = datetime.strptime(campaign["start_date"], "%Y-%m-%d")
            campaign_end = datetime.strptime(campaign["end_date"], "%Y-%m-%d")
            
            if (start_date <= campaign_start <= end_date) or (start_date <= campaign_end <= end_date):
                calendar_items.append({
                    "date": campaign["start_date"],
                    "type": "campaign_launch",
                    "title": campaign["title"],
                    "description": campaign["description"],
                    "category": campaign["category"],
                    "priority": campaign["priority"],
                    "content_pillars": campaign["content_pillars"],
                    "posting_schedule": campaign["posting_schedule"],
                    "kpis": campaign["kpis"],
                    "budget_allocation": campaign["budget_allocation"],
                    "duration": (campaign_end - campaign_start).days
                })
    
    # Add regular content recommendations
    current_date = start_date
    while current_date <= end_date:
        day_name = current_date.strftime("%A")
        
        # Daily content themes
        daily_themes = {
            "Monday": "Motivation Monday - Inspirational street culture content",
            "Tuesday": "Trend Tuesday - Latest streetwear trends and styles",
            "Wednesday": "Wisdom Wednesday - Brand heritage and history",
            "Thursday": "Throwback Thursday - Classic pieces and vintage vibes",
            "Friday": "Fresh Friday - New drops and exclusive previews",
            "Saturday": "Style Saturday - Outfit inspiration and styling tips",
            "Sunday": "Sunday Stories - Community features and user content"
        }
        
        # Skip if there's already a major event on this day
        existing_events = [item for item in calendar_items if item["date"] == current_date.strftime("%Y-%m-%d")]
        if not any(event["priority"] == "high" for event in existing_events):
            calendar_items.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "type": "daily_content",
                "title": f"{day_name} Content Theme",
                "description": daily_themes[day_name],
                "category": "regular_content",
                "priority": "medium",
                "content_suggestions": [
                    "Instagram post with high-quality imagery",
                    "TikTok video showcasing style/culture",
                    "Twitter engagement with community"
                ],
                "optimal_times": get_optimal_posting_times()["Instagram"]["weekdays" if day_name not in ["Saturday", "Sunday"] else "weekends"]
            })
        
        current_date += timedelta(days=1)
    
    # Sort by date and priority
    calendar_items.sort(key=lambda x: (x["date"], {"high": 0, "medium": 1, "low": 2}[x["priority"]]))
    
    return calendar_items

def get_content_planning_tools() -> Dict[str, Any]:
    """Get content planning and creation tools"""
    return {
        "content_generators": {
            "campaign_generator": {
                "name": "Strategic Campaign Generator",
                "description": "Generate culturally authentic campaigns",
                "features": ["Cultural sensitivity check", "Hashtag optimization", "Timeline planning"],
                "status": "available"
            },
            "trend_analyzer": {
                "name": "Trend Analysis Tool",
                "description": "Analyze current streetwear and culture trends",
                "features": ["Hashtag trending", "Competitor analysis", "Cultural moment detection"],
                "status": "available"
            },
            "content_calendar_creator": {
                "name": "Content Calendar Creator",
                "description": "Create comprehensive content calendars",
                "features": ["Cultural integration", "Optimal timing", "Multi-platform planning"],
                "status": "available"
            }
        },
        "optimization_tools": {
            "posting_optimizer": {
                "name": "Posting Time Optimizer",
                "description": "Find optimal posting times for maximum engagement",
                "platforms": ["Instagram", "TikTok", "Twitter", "YouTube"],
                "status": "available"
            },
            "hashtag_optimizer": {
                "name": "Hashtag Strategy Optimizer",
                "description": "Optimize hashtag strategy for reach and authenticity",
                "features": ["Trending analysis", "Cultural relevance", "Competition analysis"],
                "status": "available"
            }
        },
        "cultural_tools": {
            "cultural_calendar": {
                "name": "Cultural Moment Calendar",
                "description": "Track important cultural and heritage moments",
                "coverage": ["Hispanic Heritage", "Black History", "Hip-Hop Culture", "Global Events"],
                "status": "available"
            },
            "authenticity_checker": {
                "name": "Cultural Authenticity Checker",
                "description": "Ensure content respects cultural authenticity",
                "features": ["Sensitivity analysis", "Cultural context", "Community feedback"],
                "status": "available"
            }
        }
    }

@router.get("/planning")
async def get_content_planning(
    timeframe: str = "30_days",
    include_cultural_moments: bool = True,
    include_campaigns: bool = True
):
    """Get comprehensive content planning calendar"""
    try:
        # Generate content calendar
        calendar_items = generate_content_calendar(timeframe, include_cultural_moments, include_campaigns)
        
        # Get planning tools
        planning_tools = get_content_planning_tools()
        
        # Get optimal posting times
        optimal_times = get_optimal_posting_times()
        
        # Calculate calendar statistics
        total_items = len(calendar_items)
        cultural_moments = len([item for item in calendar_items if item["type"] == "cultural_moment"])
        campaigns = len([item for item in calendar_items if item["type"] == "campaign_launch"])
        daily_content = len([item for item in calendar_items if item["type"] == "daily_content"])
        
        # Priority breakdown
        high_priority = len([item for item in calendar_items if item["priority"] == "high"])
        medium_priority = len([item for item in calendar_items if item["priority"] == "medium"])
        low_priority = len([item for item in calendar_items if item["priority"] == "low"])
        
        return JSONResponse({
            "success": True,
            "timeframe": timeframe,
            "calendar": calendar_items,
            "statistics": {
                "total_items": total_items,
                "cultural_moments": cultural_moments,
                "strategic_campaigns": campaigns,
                "daily_content": daily_content,
                "priority_breakdown": {
                    "high": high_priority,
                    "medium": medium_priority,
                    "low": low_priority
                }
            },
            "planning_tools": planning_tools,
            "optimal_posting_times": optimal_times,
            "recommendations": [
                "Focus on high-priority cultural moments for maximum impact",
                "Maintain consistent daily content themes for brand recognition",
                "Align campaign launches with cultural celebrations",
                "Use optimal posting times for each platform"
            ],
            "next_major_events": [
                item for item in calendar_items 
                if item["priority"] == "high" and item["type"] in ["cultural_moment", "campaign_launch"]
            ][:5],
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Content planning generation failed: {str(e)}",
            "calendar": [],
            "statistics": {},
            "planning_tools": {},
            "recommendations": ["Unable to generate content calendar - check system configuration"]
        })

@router.get("/cultural-moments")
async def get_cultural_moments_calendar():
    """Get cultural moments and heritage celebrations"""
    try:
        cultural_moments = get_cultural_moments()
        
        # Categorize by type
        heritage_moments = [m for m in cultural_moments if m["category"] == "heritage"]
        cultural_events = [m for m in cultural_moments if m["category"] == "culture"]
        commercial_events = [m for m in cultural_moments if m["category"] == "commercial"]
        global_events = [m for m in cultural_moments if m["category"] == "global"]
        
        return JSONResponse({
            "success": True,
            "cultural_moments": cultural_moments,
            "categories": {
                "heritage": heritage_moments,
                "culture": cultural_events,
                "commercial": commercial_events,
                "global": global_events
            },
            "upcoming": [
                moment for moment in cultural_moments
                if datetime.strptime(moment["date"], "%Y-%m-%d") >= datetime.now()
            ][:5],
            "total_moments": len(cultural_moments)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Cultural moments retrieval failed: {str(e)}",
            "cultural_moments": []
        })

@router.get("/campaigns")
async def get_strategic_campaigns_list():
    """Get strategic campaign recommendations"""
    try:
        campaigns = get_strategic_campaigns()
        
        return JSONResponse({
            "success": True,
            "campaigns": campaigns,
            "active_campaigns": [
                campaign for campaign in campaigns
                if datetime.strptime(campaign["start_date"], "%Y-%m-%d") <= datetime.now() <= datetime.strptime(campaign["end_date"], "%Y-%m-%d")
            ],
            "upcoming_campaigns": [
                campaign for campaign in campaigns
                if datetime.strptime(campaign["start_date"], "%Y-%m-%d") > datetime.now()
            ],
            "total_campaigns": len(campaigns)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Campaign retrieval failed: {str(e)}",
            "campaigns": []
        })

@router.get("/tools")
async def get_planning_tools():
    """Get content planning and creation tools"""
    try:
        tools = get_content_planning_tools()
        
        return JSONResponse({
            "success": True,
            "tools": tools,
            "available_tools": sum(
                len(category) for category in tools.values()
            ),
            "tool_categories": list(tools.keys())
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Tools retrieval failed: {str(e)}",
            "tools": {}
        })

@router.get("/health")
async def calendar_health_check():
    """Health check for calendar module"""
    try:
        cultural_moments = get_cultural_moments()
        campaigns = get_strategic_campaigns()
        
        return JSONResponse({
            "status": "healthy",
            "cultural_moments_loaded": len(cultural_moments),
            "campaigns_available": len(campaigns),
            "planning_tools_active": True,
            "last_check": datetime.now().isoformat(),
            "message": "Calendar module operational with strategic planning capabilities"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "message": "Calendar module health check failed"
        })
