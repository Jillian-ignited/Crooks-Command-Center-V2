# backend/routers/calendar.py
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
import uuid

router = APIRouter()

# NEW REQUEST MODELS FOR CREATE ENDPOINTS
class CalendarEventRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    start_date: str  # ISO format
    end_date: Optional[str] = None
    event_type: str = "campaign"  # campaign, launch, meeting, deadline, cultural
    priority: str = "medium"  # low, medium, high, critical
    brand: Optional[str] = "Crooks & Castles"
    assigned_to: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    location: Optional[str] = ""
    is_all_day: Optional[bool] = False

class BulkEventRequest(BaseModel):
    events: List[CalendarEventRequest]
    campaign_name: Optional[str] = "Bulk Campaign Events"

# NEW RESPONSE MODELS
class CalendarEvent(BaseModel):
    id: str
    title: str
    description: str
    start_date: str
    end_date: str
    event_type: str
    priority: str
    brand: str
    assigned_to: List[str]
    tags: List[str]
    location: str
    is_all_day: bool
    status: str
    created_at: str
    created_by: str

# EXISTING CULTURAL CONTENT (PRESERVED)
# Hip Hop History & Streetwear Culture
CULTURAL_MOMENTS = [
    {"date": "01-01", "name": "Grandmaster Flash's Birthday", "category": "hip_hop_history", "campaign_idea": "Pioneer tribute post series", "content_type": "educational"},
    {"date": "02-18", "name": "Run-DMC 'Walk This Way' Release Anniversary", "category": "hip_hop_history", "campaign_idea": "Crossover culture content", "content_type": "throwback"},
    {"date": "03-09", "name": "Notorious B.I.G. Birthday", "category": "hip_hop_legend", "campaign_idea": "Brooklyn streetwear tribute collection tease", "content_type": "commemorative"},
    {"date": "04-16", "name": "Tupac's Birthday", "category": "hip_hop_legend", "campaign_idea": "West Coast influence series", "content_type": "cultural"},
    {"date": "05-26", "name": "Lauryn Hill's Birthday", "category": "hip_hop_history", "campaign_idea": "90s style revival content", "content_type": "style_inspiration"},
    {"date": "08-11", "name": "Hip Hop's Birthday (1973)", "category": "hip_hop_history", "campaign_idea": "Major anniversary campaign - collab drop", "content_type": "major_event"},
    {"date": "09-07", "name": "Tupac Death Anniversary", "category": "commemorative", "campaign_idea": "Legacy tribute collection", "content_type": "commemorative"},
    {"date": "10-27", "name": "Nas 'Illmatic' Anniversary", "category": "hip_hop_history", "campaign_idea": "NY streetwear storytelling", "content_type": "cultural"},
    {"date": "01-15", "name": "Martin Luther King Jr. Day", "category": "cultural", "campaign_idea": "Social justice messaging + community initiative", "content_type": "values"},
    {"date": "02-01", "name": "Black History Month Begins", "category": "cultural", "campaign_idea": "Month-long Black culture in streetwear series", "content_type": "educational"},
    {"date": "06-19", "name": "Juneteenth", "category": "cultural", "campaign_idea": "Freedom + Black excellence campaign", "content_type": "commemorative"},
    {"date": "01-07", "name": "Tyler, The Creator's Birthday", "category": "contemporary_culture", "campaign_idea": "Golf Wang influence + color blocking content", "content_type": "style_inspiration"},
    {"date": "10-24", "name": "Drake's Birthday", "category": "contemporary_culture", "campaign_idea": "OVO aesthetic + Toronto culture", "content_type": "cultural"},
    {"date": "12-04", "name": "Jay-Z's Birthday", "category": "hip_hop_legend", "campaign_idea": "Business mogul style evolution", "content_type": "style_inspiration"},
]

# Pop Culture & Contemporary Events
POP_CULTURE_EVENTS = [
    {"date": "02-04", "name": "Grammy Awards Weekend", "category": "music", "campaign_idea": "Red carpet street style breakdown", "content_type": "trend_commentary"},
    {"date": "02-13", "name": "Super Bowl Sunday", "category": "sports", "campaign_idea": "Game day fits + halftime show reaction content", "content_type": "real_time"},
    {"date": "03-20", "name": "March Madness Begins", "category": "sports", "campaign_idea": "College basketball culture + jersey styling", "content_type": "sports_culture"},
    {"date": "04-13", "name": "Coachella Weekend 1", "category": "festival", "campaign_idea": "Festival fit guides + street style coverage", "content_type": "seasonal"},
    {"date": "05-06", "name": "Met Gala", "category": "fashion", "campaign_idea": "High fashion meets streetwear commentary", "content_type": "cultural"},
    {"date": "06-15", "name": "NBA Finals Begin", "category": "sports", "campaign_idea": "Basketball culture series + player style spotlights", "content_type": "sports_culture"},
    {"date": "08-27", "name": "MTV VMAs", "category": "music", "campaign_idea": "Music video fashion retrospective", "content_type": "nostalgia"},
    {"date": "09-08", "name": "New York Fashion Week", "category": "fashion", "campaign_idea": "Street style vs runway + trend predictions", "content_type": "fashion_week"},
    {"date": "10-01", "name": "NBA Season Opener", "category": "sports", "campaign_idea": "Tunnel walk fits breakdown series", "content_type": "sports_culture"},
    {"date": "03-26", "name": "Air Max Day", "category": "sneaker_culture", "campaign_idea": "Sneaker history + styling tips", "content_type": "product_tie_in"},
    {"date": "05-23", "name": "Jordan Brand Anniversary", "category": "sneaker_culture", "campaign_idea": "MJ influence on streetwear", "content_type": "cultural"},
    {"date": "06-10", "name": "Summer Game Fest", "category": "gaming", "campaign_idea": "Gaming x streetwear crossover content", "content_type": "subculture"},
    {"date": "07-03", "name": "Anime Expo", "category": "anime", "campaign_idea": "Anime-inspired streetwear styling", "content_type": "subculture"},
    {"date": "10-02", "name": "New York Comic Con", "category": "pop_culture", "campaign_idea": "Comic/anime streetwear mashup", "content_type": "subculture"},
    {"date": "06-21", "name": "Go Skateboarding Day", "category": "skate_culture", "campaign_idea": "Skate heritage in streetwear", "content_type": "cultural"},
    {"date": "02-14", "name": "Valentine's Day", "category": "holiday", "campaign_idea": "Couples streetwear campaign", "content_type": "seasonal"},
    {"date": "07-04", "name": "Independence Day", "category": "holiday", "campaign_idea": "Americana streetwear reinterpretation", "content_type": "seasonal"},
    {"date": "10-31", "name": "Halloween", "category": "holiday", "campaign_idea": "Dark aesthetic limited pieces", "content_type": "seasonal"},
    {"date": "11-29", "name": "Black Friday", "category": "retail", "campaign_idea": "Exclusive streetwear drop", "content_type": "sales_event"},
    {"date": "12-25", "name": "Christmas", "category": "holiday", "campaign_idea": "Holiday gift guide campaign", "content_type": "seasonal"},
]

# EXISTING HELPER FUNCTIONS (PRESERVED)
def get_cultural_events_for_range(start_date: datetime, end_date: datetime) -> List[Dict]:
    """Get cultural events within date range with campaign suggestions"""
    events = []
    current = start_date
    all_moments = CULTURAL_MOMENTS + POP_CULTURE_EVENTS
    
    while current <= end_date:
        month_day = current.strftime("%m-%d")
        for moment in all_moments:
            if moment["date"] == month_day:
                events.append({
                    "date": current.isoformat(),
                    "title": moment["name"],
                    "category": moment["category"],
                    "campaign_idea": moment["campaign_idea"],
                    "content_type": moment["content_type"],
                    "type": "cultural_moment"
                })
        current += timedelta(days=1)
    
    return sorted(events, key=lambda x: x["date"])

def get_detailed_posts_for_week(start_date: datetime) -> List[Dict]:
    """Generate detailed post suggestions for 7-day view"""
    posts = []
    
    for i in range(7):
        current = start_date + timedelta(days=i)
        day_name = current.strftime("%A")
        
        # Morning product post
        if i in [0, 2, 4]:  # Mon, Wed, Fri
            posts.append({
                "date": current.isoformat(),
                "time": "10:00 AM",
                "platform": "Instagram Feed",
                "post_type": "Product Showcase",
                "content": f"New arrival feature - {day_name} drop",
                "caption": "New heat just landed. Quality you can feel. 🔥",
                "hashtags": ["#StreetStyle", "#CrooksAndCastles", "#NewDrop", "#Streetwear"],
                "visual": "Flat lay or lifestyle product shot",
                "cta": "Link in bio to shop"
            })
        
        # Midday engagement
        if i in [1, 3, 5]:  # Tue, Thu, Sat
            posts.append({
                "date": current.isoformat(),
                "time": "2:00 PM",
                "platform": "TikTok",
                "post_type": "Trend/Challenge",
                "content": f"Trending audio participation - {day_name}",
                "caption": "POV: Your style is unmatched",
                "hashtags": ["#OOTD", "#StreetStyleTikTok", "#Fashion"],
                "visual": "Transition video or fit check",
                "cta": "Follow for daily style"
            })
        
        # Evening stories
        posts.append({
            "date": current.isoformat(),
            "time": "6:00 PM",
            "platform": "Instagram Stories",
            "post_type": "Community",
            "content": f"{day_name} community feature",
            "visual": "UGC reshare or poll/question sticker",
            "cta": "Tag us in your fits"
        })
    
    return posts

def generate_event_recommendations(event_type: str, priority: str) -> List[str]:
    """Generate contextual recommendations based on event type and priority"""
    
    recommendations = []
    
    if event_type == "campaign":
        recommendations.extend([
            "Prepare campaign assets and creative materials",
            "Coordinate with marketing team for launch strategy",
            "Set up tracking and analytics for campaign performance",
            "Schedule social media posts and content calendar"
        ])
    elif event_type == "launch":
        recommendations.extend([
            "Finalize product photography and descriptions",
            "Coordinate with inventory and fulfillment teams",
            "Prepare press releases and media outreach",
            "Set up landing pages and promotional materials"
        ])
    elif event_type == "meeting":
        recommendations.extend([
            "Prepare agenda and meeting materials",
            "Send calendar invites to all participants",
            "Book meeting room or set up video conference",
            "Gather relevant documents and reports"
        ])
    elif event_type == "deadline":
        recommendations.extend([
            "Create task breakdown and assign responsibilities",
            "Set up progress tracking and check-in points",
            "Identify potential blockers and mitigation strategies",
            "Prepare backup plans for critical deliverables"
        ])
    elif event_type == "cultural":
        recommendations.extend([
            "Research cultural significance and appropriate messaging",
            "Prepare authentic and respectful content",
            "Coordinate with community partners if applicable",
            "Plan special promotions or community engagement"
        ])
    
    # Add priority-specific recommendations
    if priority == "critical":
        recommendations.append("Assign dedicated project manager for oversight")
        recommendations.append("Set up daily check-ins and progress reports")
    elif priority == "high":
        recommendations.append("Schedule regular progress updates")
        recommendations.append("Identify key stakeholders for approval process")
    
    return recommendations[:4]  # Return top 4 recommendations

# EXISTING ENDPOINTS (PRESERVED)
@router.get("/status")
async def calendar_status():
    return {"status": "active", "events_count": len(CULTURAL_MOMENTS + POP_CULTURE_EVENTS)}

@router.get("/events")
async def get_calendar_events(days: int = Query(7)):
    """Get calendar events with campaign suggestions"""
    today = datetime.now()
    end_date = today + timedelta(days=days)
    
    cultural_events = get_cultural_events_for_range(today, end_date)
    detailed_posts = get_detailed_posts_for_week(today) if days <= 7 else []
    
    return {
        "period_days": days,
        "start_date": today.isoformat(),
        "end_date": end_date.isoformat(),
        "cultural_moments": cultural_events,
        "detailed_posts": detailed_posts,
        "total_events": len(cultural_events) + len(detailed_posts)
    }

@router.get("/cultural")
async def get_cultural_calendar():
    """Get full cultural calendar for planning"""
    today = datetime.now()
    year_end = datetime(today.year, 12, 31)
    events = get_cultural_events_for_range(today, year_end)
    
    return {
        "cultural_moments": events,
        "total": len(events)
    }

@router.get("/periods")
async def get_calendar_periods():
    """Get calendar periods with strategic recommendations"""
    today = datetime.now()
    
    return {
        "periods": {
            "7d": {
                "days": 7,
                "focus": "Detailed daily posts - execution ready",
                "posts_per_day": "2-3 across platforms"
            },
            "30d": {
                "days": 30,
                "focus": "Weekly themes + cultural moments",
                "campaigns": "2-3 mini campaigns"
            },
            "60d": {
                "days": 60,
                "focus": "Major campaigns + seasonal transitions",
                "campaigns": "1-2 major + ongoing content"
            },
            "90d": {
                "days": 90,
                "focus": "Quarterly planning + collection launches",
                "campaigns": "Seasonal campaign + fashion week"
            }
        }
    }

# NEW CREATE ENDPOINTS (ADDED)
@router.post("/create")
async def create_calendar_event(request: CalendarEventRequest):
    """Create a new calendar event"""
    
    try:
        # Generate event ID
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        
        # Parse and validate dates
        try:
            start_dt = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
            if request.end_date:
                end_dt = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
            else:
                # Default to 1 hour duration for non-all-day events
                if request.is_all_day:
                    end_dt = start_dt.replace(hour=23, minute=59, second=59)
                else:
                    end_dt = start_dt + timedelta(hours=1)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
        
        # Validate end date is after start date
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Create event object
        event = CalendarEvent(
            id=event_id,
            title=request.title,
            description=request.description or f"{request.event_type.title()} event for {request.brand}",
            start_date=start_dt.isoformat(),
            end_date=end_dt.isoformat(),
            event_type=request.event_type,
            priority=request.priority,
            brand=request.brand or "Crooks & Castles",
            assigned_to=request.assigned_to or [],
            tags=request.tags or [request.event_type, request.brand or "crooks-castles"],
            location=request.location or "",
            is_all_day=request.is_all_day or False,
            status="scheduled",
            created_at=datetime.now().isoformat(),
            created_by="system"
        )
        
        # Generate contextual recommendations based on event type
        recommendations = generate_event_recommendations(request.event_type, request.priority)
        
        return {
            "success": True,
            "event": event,
            "message": f"Calendar event '{request.title}' created successfully",
            "recommendations": recommendations,
            "next_steps": [
                "Add event to team calendars",
                "Set up reminder notifications", 
                "Prepare necessary materials",
                "Coordinate with assigned team members"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")

@router.post("/create/bulk")
async def create_bulk_events(request: BulkEventRequest):
    """Create multiple calendar events at once"""
    
    try:
        created_events = []
        failed_events = []
        
        for i, event_request in enumerate(request.events):
            try:
                # Create individual event
                event_id = f"evt_{uuid.uuid4().hex[:8]}"
                
                # Parse dates
                start_dt = datetime.fromisoformat(event_request.start_date.replace('Z', '+00:00'))
                if event_request.end_date:
                    end_dt = datetime.fromisoformat(event_request.end_date.replace('Z', '+00:00'))
                else:
                    if event_request.is_all_day:
                        end_dt = start_dt.replace(hour=23, minute=59, second=59)
                    else:
                        end_dt = start_dt + timedelta(hours=1)
                
                event = CalendarEvent(
                    id=event_id,
                    title=event_request.title,
                    description=event_request.description or f"{event_request.event_type.title()} event",
                    start_date=start_dt.isoformat(),
                    end_date=end_dt.isoformat(),
                    event_type=event_request.event_type,
                    priority=event_request.priority,
                    brand=event_request.brand or "Crooks & Castles",
                    assigned_to=event_request.assigned_to or [],
                    tags=event_request.tags or [event_request.event_type],
                    location=event_request.location or "",
                    is_all_day=event_request.is_all_day or False,
                    status="scheduled",
                    created_at=datetime.now().isoformat(),
                    created_by="system"
                )
                
                created_events.append(event)
                
            except Exception as e:
                failed_events.append({
                    "index": i,
                    "title": event_request.title,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "campaign_name": request.campaign_name,
            "created_events": created_events,
            "failed_events": failed_events,
            "summary": {
                "total_requested": len(request.events),
                "successfully_created": len(created_events),
                "failed": len(failed_events)
            },
            "message": f"Bulk creation completed: {len(created_events)} events created, {len(failed_events)} failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bulk events: {str(e)}")

@router.post("/create/campaign")
async def create_campaign_timeline(
    campaign_name: str,
    start_date: str,
    end_date: str,
    brand: str = "Crooks & Castles"
):
    """Create a complete campaign timeline with standard milestones"""
    
    try:
        # Parse campaign dates
        campaign_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        campaign_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Calculate campaign duration
        duration = (campaign_end - campaign_start).days
        
        # Generate standard campaign events
        campaign_events = []
        
        # Campaign kickoff (start date)
        campaign_events.append(CalendarEventRequest(
            title=f"{campaign_name} - Campaign Kickoff",
            description=f"Official launch of {campaign_name} campaign for {brand}",
            start_date=campaign_start.isoformat(),
            event_type="campaign",
            priority="high",
            brand=brand,
            tags=["campaign", "kickoff", brand.lower().replace(" ", "-")]
        ))
        
        # Content creation phase (25% into campaign)
        content_date = campaign_start + timedelta(days=int(duration * 0.25))
        campaign_events.append(CalendarEventRequest(
            title=f"{campaign_name} - Content Creation Deadline",
            description="All campaign content must be finalized and approved",
            start_date=content_date.isoformat(),
            event_type="deadline",
            priority="high",
            brand=brand,
            tags=["content", "deadline", brand.lower().replace(" ", "-")]
        ))
        
        # Mid-campaign review (50% into campaign)
        review_date = campaign_start + timedelta(days=int(duration * 0.5))
        campaign_events.append(CalendarEventRequest(
            title=f"{campaign_name} - Mid-Campaign Review",
            description="Review campaign performance and make adjustments",
            start_date=review_date.isoformat(),
            event_type="meeting",
            priority="medium",
            brand=brand,
            tags=["review", "meeting", brand.lower().replace(" ", "-")]
        ))
        
        # Final push (75% into campaign)
        push_date = campaign_start + timedelta(days=int(duration * 0.75))
        campaign_events.append(CalendarEventRequest(
            title=f"{campaign_name} - Final Push Phase",
            description="Intensify campaign efforts for maximum impact",
            start_date=push_date.isoformat(),
            event_type="campaign",
            priority="high",
            brand=brand,
            tags=["final-push", "campaign", brand.lower().replace(" ", "-")]
        ))
        
        # Campaign wrap-up (end date)
        campaign_events.append(CalendarEventRequest(
            title=f"{campaign_name} - Campaign Wrap-up",
            description=f"Official end of {campaign_name} campaign and results analysis",
            start_date=campaign_end.isoformat(),
            event_type="campaign",
            priority="medium",
            brand=brand,
            tags=["wrap-up", "analysis", brand.lower().replace(" ", "-")]
        ))
        
        # Create bulk events
        bulk_request = BulkEventRequest(
            events=campaign_events,
            campaign_name=campaign_name
        )
        
        # Use the bulk creation endpoint
        result = await create_bulk_events(bulk_request)
        
        return {
            "success": True,
            "campaign_name": campaign_name,
            "campaign_timeline": result,
            "duration_days": duration,
            "message": f"Campaign timeline created for {campaign_name}",
            "timeline_overview": {
                "kickoff": campaign_start.strftime("%Y-%m-%d"),
                "content_deadline": content_date.strftime("%Y-%m-%d"),
                "mid_review": review_date.strftime("%Y-%m-%d"),
                "final_push": push_date.strftime("%Y-%m-%d"),
                "wrap_up": campaign_end.strftime("%Y-%m-%d")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create campaign timeline: {str(e)}")

@router.get("/templates")
async def get_event_templates():
    """Get predefined event templates for common campaign types"""
    
    templates = {
        "product_launch": {
            "name": "Product Launch Campaign",
            "duration_days": 30,
            "events": [
                {"title": "Pre-Launch Teasers", "offset_days": 0, "type": "campaign"},
                {"title": "Content Creation Deadline", "offset_days": 7, "type": "deadline"},
                {"title": "Influencer Outreach", "offset_days": 10, "type": "campaign"},
                {"title": "Launch Day", "offset_days": 21, "type": "launch"},
                {"title": "Post-Launch Analysis", "offset_days": 30, "type": "meeting"}
            ]
        },
        "seasonal_campaign": {
            "name": "Seasonal Marketing Campaign", 
            "duration_days": 45,
            "events": [
                {"title": "Campaign Planning", "offset_days": 0, "type": "meeting"},
                {"title": "Creative Development", "offset_days": 7, "type": "deadline"},
                {"title": "Campaign Soft Launch", "offset_days": 21, "type": "campaign"},
                {"title": "Full Campaign Launch", "offset_days": 28, "type": "campaign"},
                {"title": "Campaign Wrap-up", "offset_days": 45, "type": "meeting"}
            ]
        },
        "cultural_moment": {
            "name": "Cultural Moment Campaign",
            "duration_days": 14,
            "events": [
                {"title": "Cultural Research & Planning", "offset_days": 0, "type": "meeting"},
                {"title": "Content Creation", "offset_days": 3, "type": "deadline"},
                {"title": "Community Outreach", "offset_days": 7, "type": "campaign"},
                {"title": "Cultural Moment Activation", "offset_days": 10, "type": "cultural"},
                {"title": "Impact Assessment", "offset_days": 14, "type": "meeting"}
            ]
        }
    }
    
    return {
        "success": True,
        "templates": templates,
        "message": "Available event templates for campaign planning"
    }
