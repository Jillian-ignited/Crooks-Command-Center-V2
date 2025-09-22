import json
import os
from datetime import datetime, timedelta

DATA_PATH = os.path.join('data', 'calendar.json')

# Enhanced streetwear cultural calendar with detailed campaign planning
ENHANCED_STREETWEAR_CALENDAR = {
    "7_day_view": [
        {
            "date": "2025-09-23",
            "title": "Hip-Hop Heritage Story Series Launch",
            "description": "Launch authentic hip-hop heritage content series with street photography and cultural elements showcasing Crooks & Castles legacy in hip-hop culture",
            "budget_allocation": 500,
            "deliverables": ["Instagram post (1080x1080)", "Instagram story series (1080x1920)", "TikTok video (9:16)", "Community engagement"],
            "assets_mapped": ["sept_19_hiphop_anniversary.png", "model1_story.png"],
            "cultural_context": "Hip-Hop Anniversary celebration with authentic street culture positioning",
            "target_kpis": {"engagement_rate": "4.5%", "reach": "25K", "saves": "500"},
            "status": "assets_ready",
            "priority": "high",
            "campaign_type": "cultural_heritage"
        },
        {
            "date": "2025-09-25",
            "title": "Cultural Fusion Content Drop",
            "description": "Showcase cultural fusion in streetwear with diverse models and lifestyle context, emphasizing Crooks & Castles multicultural heritage",
            "budget_allocation": 750,
            "deliverables": ["Instagram carousel (5 slides)", "Story highlights series", "TikTok trend participation", "Community spotlights"],
            "assets_mapped": ["sept_16_cultural_fusion(3).png", "real_instagram_story_rebel_rooftop(1).png"],
            "cultural_context": "Multicultural streetwear positioning with authentic community representation",
            "target_kpis": {"engagement_rate": "5.2%", "reach": "35K", "shares": "200"},
            "status": "in_production",
            "priority": "high",
            "campaign_type": "cultural_fusion"
        },
        {
            "date": "2025-09-27",
            "title": "Weekly Intelligence Recap & Trend Analysis",
            "description": "Comprehensive competitive intelligence report with streetwear trend analysis and cultural moment identification",
            "budget_allocation": 300,
            "deliverables": ["Weekly intelligence report", "Trend briefing document", "Competitive positioning analysis", "Cultural calendar updates"],
            "assets_mapped": ["dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl", "dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl"],
            "cultural_context": "Data-driven insights for streetwear market positioning",
            "target_kpis": {"report_engagement": "150 views", "insights_generated": "12", "actionable_items": "8"},
            "status": "data_processing",
            "priority": "medium",
            "campaign_type": "intelligence"
        }
    ],
    "30_day_view": [
        {
            "date": "2025-10-02",
            "title": "Hispanic Heritage Month Celebration Campaign",
            "description": "Authentic celebration of Hispanic heritage in streetwear with community partnerships, featuring Latino artists and cultural elements in Crooks & Castles designs",
            "budget_allocation": 2000,
            "deliverables": ["Campaign hero creative (multiple formats)", "Community partnership content", "Educational heritage content", "Artist collaboration posts"],
            "assets_mapped": ["sept_15_hispanic_heritage_launch(3).png", "wordmark_story(1).png", "410f528c-980e-497b-bcf0-a6294a39631b.mp4"],
            "cultural_context": "Hispanic Heritage Month with authentic community representation and cultural sensitivity",
            "target_kpis": {"engagement_rate": "6.8%", "reach": "100K", "community_mentions": "50", "cultural_sentiment": "90%+"},
            "status": "community_outreach",
            "priority": "high",
            "campaign_type": "heritage_celebration"
        },
        {
            "date": "2025-10-15",
            "title": "Hip-Hop 52nd Anniversary Tribute",
            "description": "Documentary-style tribute to hip-hop anniversary showcasing Crooks & Castles role in hip-hop fashion evolution with historical timeline content",
            "budget_allocation": 1500,
            "deliverables": ["Anniversary tribute video", "Historical timeline graphics", "Artist testimonials", "Heritage brand storytelling"],
            "assets_mapped": ["sept_19_hiphop_anniversary.png", "castle_story.png", "medusa_story(1).png"],
            "cultural_context": "Hip-Hop Anniversary with brand heritage positioning in street culture",
            "target_kpis": {"engagement_rate": "7.2%", "reach": "75K", "video_completion": "65%", "brand_mentions": "25+"},
            "status": "content_development",
            "priority": "high",
            "campaign_type": "anniversary_tribute"
        },
        {
            "date": "2025-10-22",
            "title": "Streetwear Culture Documentation Series",
            "description": "Behind-the-scenes documentation of street culture and fashion with authentic community voices and Crooks & Castles cultural impact",
            "budget_allocation": 1200,
            "deliverables": ["Documentary series (3 episodes)", "Community interviews", "Street photography collection", "Cultural impact stories"],
            "assets_mapped": ["model2_story.png", "9dd8a1ec-8b07-460b-884d-8e0d8a0260d9.mov"],
            "cultural_context": "Authentic street culture documentation with community focus",
            "target_kpis": {"series_views": "50K", "community_engagement": "80%", "cultural_authenticity_score": "95%"},
            "status": "pre_production",
            "priority": "medium",
            "campaign_type": "documentary"
        }
    ],
    "60_day_view": [
        {
            "date": "2025-11-01",
            "title": "Pre-Black Friday Cultural Positioning",
            "description": "Strategic pre-BFCM campaign positioning Crooks & Castles as authentic streetwear choice with cultural heritage emphasis",
            "budget_allocation": 3000,
            "deliverables": ["Brand positioning campaign", "Heritage storytelling content", "Community testimonials", "Cultural authenticity messaging"],
            "assets_mapped": ["castle_story.png", "medusa_story(1).png", "wordmark_story(1).png"],
            "cultural_context": "Pre-commercial cultural positioning with authenticity emphasis",
            "target_kpis": {"brand_awareness": "+12%", "cultural_association": "+20%", "purchase_intent": "+15%"},
            "status": "strategy_development",
            "priority": "high",
            "campaign_type": "brand_positioning"
        },
        {
            "date": "2025-11-25",
            "title": "Black Friday Cultural Commerce Campaign",
            "description": "Strategic BFCM campaign balancing commercial goals with cultural authenticity, featuring community-driven content and heritage pieces",
            "budget_allocation": 5000,
            "deliverables": ["BFCM campaign creative suite", "Cultural commerce messaging", "Community-driven content", "Heritage collection spotlight"],
            "assets_mapped": ["sept_15_hispanic_heritage_launch(3).png", "sept_16_cultural_fusion(3).png"],
            "cultural_context": "Commercial campaign with maintained cultural authenticity and community respect",
            "target_kpis": {"conversion_rate": "3.5%", "roas": "4.2x", "cultural_sentiment": "85%+", "community_engagement": "70%"},
            "status": "creative_development",
            "priority": "critical",
            "campaign_type": "commercial"
        },
        {
            "date": "2025-12-15",
            "title": "Holiday Cultural Fusion Campaign",
            "description": "Holiday season campaign celebrating cultural diversity in streetwear with inclusive messaging and community representation",
            "budget_allocation": 2500,
            "deliverables": ["Holiday campaign creative", "Multicultural content series", "Community celebration content", "Year-end cultural recap"],
            "assets_mapped": ["model1_story.png", "model2_story.png", "real_instagram_story_rebel_rooftop(1).png"],
            "cultural_context": "Holiday inclusivity with multicultural streetwear celebration",
            "target_kpis": {"holiday_engagement": "60K interactions", "cultural_reach": "200K", "community_sentiment": "90%+"},
            "status": "concept_phase",
            "priority": "medium",
            "campaign_type": "holiday"
        }
    ],
    "90_day_view": [
        {
            "date": "2025-12-20",
            "title": "Year-End Cultural Impact Report",
            "description": "Comprehensive report on Crooks & Castles cultural impact and community engagement throughout the year with strategic insights",
            "budget_allocation": 1500,
            "deliverables": ["Cultural impact report", "Community engagement analysis", "Brand cultural positioning assessment", "Strategic recommendations"],
            "assets_mapped": ["dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl", "instagram_competitive_data.jsonl"],
            "cultural_context": "Year-end cultural assessment and strategic planning",
            "target_kpis": {"report_distribution": "500+", "industry_recognition": "5+ mentions", "strategic_insights": "20+"},
            "status": "data_collection",
            "priority": "medium",
            "campaign_type": "reporting"
        },
        {
            "date": "2026-01-15",
            "title": "Q1 2026 Cultural Brand Evolution",
            "description": "Strategic brand evolution for new year positioning with enhanced cultural authenticity and community-first approach to streetwear",
            "budget_allocation": 8000,
            "deliverables": ["Brand evolution strategy", "Cultural positioning manifesto", "Community partnership framework", "Q1 launch campaign"],
            "assets_mapped": ["castle_story.png", "medusa_story(1).png", "wordmark_story(1).png"],
            "cultural_context": "Strategic brand evolution with deepened cultural authenticity and community focus",
            "target_kpis": {"brand_evolution_awareness": "+25%", "cultural_authenticity_score": "95%+", "community_advocacy": "+30%"},
            "status": "strategic_planning",
            "priority": "critical",
            "campaign_type": "brand_evolution"
        },
        {
            "date": "2026-02-01",
            "title": "Community Partnership Expansion",
            "description": "Expansion of community partnerships with local artists, cultural organizations, and streetwear influencers for authentic brand representation",
            "budget_allocation": 4000,
            "deliverables": ["Partnership strategy", "Community ambassador program", "Local artist collaborations", "Cultural organization partnerships"],
            "assets_mapped": ["model1_story.png", "model2_story.png"],
            "cultural_context": "Community-first partnership expansion with authentic cultural representation",
            "target_kpis": {"partnership_growth": "+50%", "community_reach": "500K+", "authentic_advocacy": "80%+"},
            "status": "partnership_development",
            "priority": "high",
            "campaign_type": "partnerships"
        }
    ],
    "120_day_view": [
        {
            "date": "2026-02-14",
            "title": "Valentine's Day Street Love Campaign",
            "description": "Authentic street culture take on Valentine's Day with community love stories and relationship representation in streetwear",
            "budget_allocation": 1800,
            "deliverables": ["Community love stories", "Couple streetwear styling", "Valentine's street photography", "Love in the streets content"],
            "assets_mapped": ["real_instagram_story_rebel_rooftop(1).png", "sept_16_cultural_fusion(3).png"],
            "cultural_context": "Street culture authenticity in mainstream holiday with community focus",
            "target_kpis": {"engagement_rate": "6.5%", "reach": "80K", "community_stories": "25+"},
            "status": "concept_development",
            "priority": "medium",
            "campaign_type": "holiday_street"
        },
        {
            "date": "2026-03-01",
            "title": "Women's History Month in Streetwear",
            "description": "Celebrating women's contributions to street culture and hip-hop with female artist collaborations and historical recognition",
            "budget_allocation": 3500,
            "deliverables": ["Female artist spotlights", "Women in hip-hop timeline", "Female streetwear pioneers", "Community women leaders"],
            "assets_mapped": ["model2_story.png", "castle_story.png"],
            "cultural_context": "Women's empowerment in street culture with historical context and modern representation",
            "target_kpis": {"female_engagement": "+40%", "reach": "120K", "artist_collaborations": "8+"},
            "status": "research_phase",
            "priority": "high",
            "campaign_type": "empowerment"
        }
    ]
}

def get_calendar(view="7_day_view"):
    """Get calendar data for specified view with enhanced streetwear cultural intelligence"""
    if view in ENHANCED_STREETWEAR_CALENDAR:
        return ENHANCED_STREETWEAR_CALENDAR[view]
    return []

def add_calendar_event(event_data, view="7_day_view"):
    """Add new event to calendar with validation"""
    required_fields = ["date", "title", "description", "budget_allocation", "deliverables", "cultural_context", "target_kpis", "status", "priority", "campaign_type"]
    
    # Validate required fields
    for field in required_fields:
        if field not in event_data:
            return {"success": False, "error": f"Missing required field: {field}"}
    
    # Add to calendar
    if view not in ENHANCED_STREETWEAR_CALENDAR:
        ENHANCED_STREETWEAR_CALENDAR[view] = []
    
    # Add unique ID and timestamp
    event_data["id"] = f"event_{len(ENHANCED_STREETWEAR_CALENDAR[view]) + 1}_{view}"
    event_data["created_at"] = datetime.now().isoformat()
    event_data["assets_mapped"] = event_data.get("assets_mapped", [])
    
    ENHANCED_STREETWEAR_CALENDAR[view].append(event_data)
    
    # Save to file
    save_calendar_data()
    
    return {"success": True, "event_id": event_data["id"]}

def remove_calendar_event(event_id, view="7_day_view"):
    """Remove event from calendar"""
    if view not in ENHANCED_STREETWEAR_CALENDAR:
        return {"success": False, "error": "View not found"}
    
    events = ENHANCED_STREETWEAR_CALENDAR[view]
    for i, event in enumerate(events):
        if event.get("id") == event_id:
            removed_event = events.pop(i)
            save_calendar_data()
            return {"success": True, "removed_event": removed_event}
    
    return {"success": False, "error": "Event not found"}

def update_calendar_event(event_id, updated_data, view="7_day_view"):
    """Update existing calendar event"""
    if view not in ENHANCED_STREETWEAR_CALENDAR:
        return {"success": False, "error": "View not found"}
    
    events = ENHANCED_STREETWEAR_CALENDAR[view]
    for event in events:
        if event.get("id") == event_id:
            event.update(updated_data)
            event["updated_at"] = datetime.now().isoformat()
            save_calendar_data()
            return {"success": True, "updated_event": event}
    
    return {"success": False, "error": "Event not found"}

def map_asset_to_event(event_id, asset_filename, view="7_day_view"):
    """Map asset to calendar event"""
    if view not in ENHANCED_STREETWEAR_CALENDAR:
        return {"success": False, "error": "View not found"}
    
    events = ENHANCED_STREETWEAR_CALENDAR[view]
    for event in events:
        if event.get("id") == event_id:
            if "assets_mapped" not in event:
                event["assets_mapped"] = []
            
            if asset_filename not in event["assets_mapped"]:
                event["assets_mapped"].append(asset_filename)
                event["updated_at"] = datetime.now().isoformat()
                save_calendar_data()
                return {"success": True, "message": f"Asset {asset_filename} mapped to event {event_id}"}
            else:
                return {"success": False, "error": "Asset already mapped to this event"}
    
    return {"success": False, "error": "Event not found"}

def unmap_asset_from_event(event_id, asset_filename, view="7_day_view"):
    """Remove asset mapping from calendar event"""
    if view not in ENHANCED_STREETWEAR_CALENDAR:
        return {"success": False, "error": "View not found"}
    
    events = ENHANCED_STREETWEAR_CALENDAR[view]
    for event in events:
        if event.get("id") == event_id:
            if "assets_mapped" in event and asset_filename in event["assets_mapped"]:
                event["assets_mapped"].remove(asset_filename)
                event["updated_at"] = datetime.now().isoformat()
                save_calendar_data()
                return {"success": True, "message": f"Asset {asset_filename} unmapped from event {event_id}"}
            else:
                return {"success": False, "error": "Asset not mapped to this event"}
    
    return {"success": False, "error": "Event not found"}

def get_events_by_priority(priority="high"):
    """Get events filtered by priority across all views"""
    priority_events = []
    for view, events in ENHANCED_STREETWEAR_CALENDAR.items():
        for event in events:
            if event.get("priority") == priority:
                event["view"] = view
                priority_events.append(event)
    
    return priority_events

def get_events_by_campaign_type(campaign_type):
    """Get events filtered by campaign type across all views"""
    campaign_events = []
    for view, events in ENHANCED_STREETWEAR_CALENDAR.items():
        for event in events:
            if event.get("campaign_type") == campaign_type:
                event["view"] = view
                campaign_events.append(event)
    
    return campaign_events

def get_budget_summary():
    """Get budget allocation summary across all calendar views"""
    budget_summary = {
        "total_budget": 0,
        "by_view": {},
        "by_priority": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        "by_campaign_type": {}
    }
    
    for view, events in ENHANCED_STREETWEAR_CALENDAR.items():
        view_budget = 0
        for event in events:
            budget = event.get("budget_allocation", 0)
            view_budget += budget
            budget_summary["total_budget"] += budget
            
            # By priority
            priority = event.get("priority", "medium")
            budget_summary["by_priority"][priority] += budget
            
            # By campaign type
            campaign_type = event.get("campaign_type", "other")
            if campaign_type not in budget_summary["by_campaign_type"]:
                budget_summary["by_campaign_type"][campaign_type] = 0
            budget_summary["by_campaign_type"][campaign_type] += budget
        
        budget_summary["by_view"][view] = view_budget
    
    return budget_summary

def save_calendar_data():
    """Save calendar data to file"""
    try:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, 'w') as f:
            json.dump(ENHANCED_STREETWEAR_CALENDAR, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving calendar data: {e}")
        return False

def load_calendar_data():
    """Load calendar data from file"""
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                loaded_data = json.load(f)
                ENHANCED_STREETWEAR_CALENDAR.update(loaded_data)
        return True
    except Exception as e:
        print(f"Error loading calendar data: {e}")
        return False

# Load calendar data on import
load_calendar_data()
