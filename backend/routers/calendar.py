# backend/routers/calendar.py
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import List, Dict

router = APIRouter()

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
