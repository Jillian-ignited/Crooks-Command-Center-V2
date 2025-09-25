from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import json
import os

router = APIRouter(tags=["calendar"])

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")

@router.get("/tactical7")
async def get_tactical_7day():
    """Get 7-day tactical content pipeline"""
    try:
        today = datetime.now()
        tactical_data = {
            "success": True,
            "view_type": "7-day tactical",
            "date_range": {
                "start": today.strftime("%Y-%m-%d"),
                "end": (today + timedelta(days=7)).strftime("%Y-%m-%d")
            },
            "weekly_pipeline": [
                {
                    "date": today.strftime("%Y-%m-%d"),
                    "day": "Today",
                    "content": [
                        {
                            "platform": "Instagram",
                            "type": "Story",
                            "title": "Behind the Scenes - New Collection",
                            "status": "scheduled",
                            "time": "10:00 AM"
                        },
                        {
                            "platform": "TikTok",
                            "type": "Video",
                            "title": "Street Style Challenge",
                            "status": "in_review",
                            "time": "3:00 PM"
                        }
                    ]
                },
                {
                    "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "day": "Tomorrow",
                    "content": [
                        {
                            "platform": "Instagram",
                            "type": "Feed Post",
                            "title": "New Drop Announcement",
                            "status": "draft",
                            "time": "12:00 PM"
                        },
                        {
                            "platform": "Twitter",
                            "type": "Thread",
                            "title": "Brand History Series",
                            "status": "planned",
                            "time": "2:00 PM"
                        }
                    ]
                }
            ],
            "asset_mapping": [
                {
                    "asset_type": "Photography",
                    "assigned_to": "High Voltage Digital",
                    "due_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "status": "in_progress",
                    "description": "Product shots for new collection"
                },
                {
                    "asset_type": "Video Content",
                    "assigned_to": "Internal Team",
                    "due_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "status": "planned",
                    "description": "Brand story video for website"
                }
            ]
        }
        
        return tactical_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load tactical data: {str(e)}"
        }

@router.get("/strategic30")
async def get_strategic_30day():
    """Get 30-day strategic content view"""
    try:
        today = datetime.now()
        strategic_data = {
            "success": True,
            "view_type": "30-day strategic",
            "date_range": {
                "start": today.strftime("%Y-%m-%d"),
                "end": (today + timedelta(days=30)).strftime("%Y-%m-%d")
            },
            "approved_content": [
                {
                    "campaign": "Fall Collection Launch",
                    "start_date": today.strftime("%Y-%m-%d"),
                    "end_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
                    "platforms": ["Instagram", "TikTok", "Twitter"],
                    "budget": 15000,
                    "status": "approved",
                    "kpis": ["Reach: 500K", "Engagement: 5%", "Conversions: 200"]
                },
                {
                    "campaign": "Influencer Collaboration Series",
                    "start_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "end_date": (today + timedelta(days=21)).strftime("%Y-%m-%d"),
                    "platforms": ["Instagram", "YouTube"],
                    "budget": 25000,
                    "status": "in_planning",
                    "kpis": ["Reach: 1M", "Engagement: 7%", "Brand Mentions: 500"]
                }
            ],
            "content_opportunities": [
                {
                    "opportunity": "Halloween Campaign",
                    "timeline": "October 15-31",
                    "potential_reach": "750K",
                    "estimated_budget": 12000,
                    "priority": "high",
                    "description": "Spooky streetwear theme with limited edition pieces"
                },
                {
                    "opportunity": "Black Friday Prep",
                    "timeline": "November 1-29",
                    "potential_reach": "1.2M",
                    "estimated_budget": 30000,
                    "priority": "critical",
                    "description": "Major sales event with exclusive drops"
                }
            ],
            "completion_tracking": {
                "total_campaigns": 4,
                "completed": 1,
                "in_progress": 2,
                "planned": 1,
                "completion_rate": 25.0,
                "on_track": True
            }
        }
        
        return strategic_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load strategic data: {str(e)}"
        }

@router.get("/strategic60")
async def get_strategic_60day():
    """Get 60-day planning view with holidays and cultural moments"""
    try:
        today = datetime.now()
        planning_data = {
            "success": True,
            "view_type": "60-day planning",
            "date_range": {
                "start": today.strftime("%Y-%m-%d"),
                "end": (today + timedelta(days=60)).strftime("%Y-%m-%d")
            },
            "upcoming_holidays": [
                {
                    "name": "Halloween",
                    "date": "2024-10-31",
                    "category": "Cultural",
                    "opportunity_score": 9,
                    "suggested_campaigns": ["Spooky Streetwear", "Costume Collaborations"],
                    "historical_performance": "High engagement, 15% sales boost"
                },
                {
                    "name": "Black Friday",
                    "date": "2024-11-29",
                    "category": "Commercial",
                    "opportunity_score": 10,
                    "suggested_campaigns": ["Mega Sale", "Exclusive Drops"],
                    "historical_performance": "Highest sales day, 300% traffic increase"
                },
                {
                    "name": "Thanksgiving",
                    "date": "2024-11-28",
                    "category": "Cultural",
                    "opportunity_score": 6,
                    "suggested_campaigns": ["Gratitude Campaign", "Community Focus"],
                    "historical_performance": "Moderate engagement, brand building"
                }
            ],
            "cultural_moments": [
                {
                    "moment": "Hip-Hop History Month",
                    "timeframe": "November 2024",
                    "relevance": "High",
                    "opportunity": "Collaborate with hip-hop artists and celebrate culture",
                    "potential_reach": "2M+",
                    "suggested_budget": 40000
                },
                {
                    "moment": "Streetwear Fashion Week",
                    "timeframe": "October 15-22, 2024",
                    "relevance": "Critical",
                    "opportunity": "Showcase new collections and establish industry presence",
                    "potential_reach": "5M+",
                    "suggested_budget": 75000
                }
            ],
            "campaign_themes": [
                {
                    "theme": "Urban Legends",
                    "description": "Celebrating street culture icons and their influence",
                    "duration": "October-November 2024",
                    "target_audience": "18-35 urban culture enthusiasts",
                    "key_messages": ["Authenticity", "Heritage", "Innovation"]
                },
                {
                    "theme": "Future Streets",
                    "description": "Tech-inspired streetwear for the digital generation",
                    "duration": "November-December 2024",
                    "target_audience": "16-28 tech-savvy consumers",
                    "key_messages": ["Innovation", "Digital Culture", "Next-Gen Style"]
                }
            ]
        }
        
        return planning_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load planning data: {str(e)}"
        }

@router.get("/strategic90")
async def get_strategic_90day():
    """Get 90+ day long-term strategic view"""
    try:
        today = datetime.now()
        longterm_data = {
            "success": True,
            "view_type": "90+ day long-term",
            "date_range": {
                "start": today.strftime("%Y-%m-%d"),
                "end": (today + timedelta(days=120)).strftime("%Y-%m-%d")
            },
            "important_birthdays": [
                {
                    "name": "Tupac Shakur",
                    "date": "2024-06-16",
                    "significance": "Hip-hop legend, major cultural influence",
                    "campaign_opportunity": "Heritage collection tribute",
                    "estimated_reach": "3M+"
                },
                {
                    "name": "Notorious B.I.G.",
                    "date": "2024-05-21",
                    "significance": "East Coast hip-hop icon",
                    "campaign_opportunity": "Brooklyn-inspired streetwear line",
                    "estimated_reach": "2.5M+"
                }
            ],
            "album_drops": [
                {
                    "artist": "Travis Scott",
                    "album": "Utopia Deluxe",
                    "expected_date": "2024-12-15",
                    "collaboration_potential": "High",
                    "opportunity": "Limited edition merch collaboration",
                    "estimated_value": "$500K+"
                },
                {
                    "artist": "Kendrick Lamar",
                    "album": "TBA",
                    "expected_date": "2025-01-30",
                    "collaboration_potential": "Medium",
                    "opportunity": "Cultural moment activation",
                    "estimated_value": "$300K+"
                }
            ],
            "anniversaries": [
                {
                    "event": "Crooks & Castles 20th Anniversary",
                    "date": "2025-03-15",
                    "significance": "Major brand milestone",
                    "campaign_scope": "Global celebration campaign",
                    "budget_allocation": "$1M+",
                    "expected_impact": "Brand legacy reinforcement"
                },
                {
                    "event": "Hip-Hop 50th Anniversary",
                    "date": "2024-11-12",
                    "significance": "Cultural milestone",
                    "campaign_scope": "Heritage and culture celebration",
                    "budget_allocation": "$200K",
                    "expected_impact": "Cultural credibility boost"
                }
            ],
            "marketing_opportunities": [
                {
                    "opportunity": "Super Bowl LVIII Activation",
                    "date": "2025-02-09",
                    "type": "Event Marketing",
                    "investment_required": "$750K",
                    "potential_roi": "300%",
                    "target_audience": "25M+ viewers"
                },
                {
                    "opportunity": "Coachella Partnership",
                    "date": "2025-04-11",
                    "type": "Festival Sponsorship",
                    "investment_required": "$400K",
                    "potential_roi": "250%",
                    "target_audience": "Music festival attendees"
                }
            ]
        }
        
        return longterm_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load long-term data: {str(e)}"
        }

@router.post("/create-event")
async def create_calendar_event(event_data: dict):
    """Create a new calendar event"""
    try:
        # This would typically save to a database
        event = {
            "success": True,
            "event_id": f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": event_data.get("title"),
            "date": event_data.get("date"),
            "type": event_data.get("type", "campaign"),
            "description": event_data.get("description"),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return event
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create event: {str(e)}"
        }

@router.get("/events/{date}")
async def get_events_for_date(date: str):
    """Get all events for a specific date"""
    try:
        # This would typically query a database
        events_data = {
            "success": True,
            "date": date,
            "events": [
                {
                    "id": "evt_001",
                    "title": "Instagram Story Series Launch",
                    "time": "10:00 AM",
                    "type": "content",
                    "status": "scheduled",
                    "platform": "Instagram"
                },
                {
                    "id": "evt_002",
                    "title": "Influencer Meeting",
                    "time": "2:00 PM",
                    "type": "meeting",
                    "status": "confirmed",
                    "attendees": ["Marketing Team", "High Voltage Digital"]
                }
            ]
        }
        
        return events_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load events: {str(e)}"
        }
