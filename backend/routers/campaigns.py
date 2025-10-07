from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import Optional
import os
import json

from ..database import get_db
from ..models import Campaign, IntelligenceFile

router = APIRouter()

# OpenAI for content suggestions
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_AVAILABLE = bool(OPENAI_API_KEY)

if AI_AVAILABLE:
    from openai import OpenAI as OpenAIClient
    print("[Campaigns] ✅ OpenAI available for content suggestions")


@router.get("/")
def get_campaigns(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all campaigns"""
    query = db.query(Campaign)
    
    if status:
        query = query.filter(Campaign.status == status)
    
    campaigns = query.order_by(desc(Campaign.created_at)).all()
    
    return {
        "campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "theme": c.theme,
                "launch_date": c.launch_date.isoformat() if c.launch_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "status": c.status,
                "cultural_moment": c.cultural_moment,
                "has_suggestions": bool(c.content_suggestions)
            }
            for c in campaigns
        ],
        "total": len(campaigns)
    }


@router.post("/")
def create_campaign(
    name: str,
    description: str = "",
    theme: str = "",
    launch_date: Optional[str] = None,
    end_date: Optional[str] = None,
    cultural_moment: str = "",
    target_audience: str = "",
    generate_suggestions: bool = True,
    db: Session = Depends(get_db)
):
    """Create a new campaign"""
    
    # Parse dates
    launch_dt = datetime.fromisoformat(launch_date) if launch_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    # Create campaign
    campaign = Campaign(
        name=name,
        description=description,
        theme=theme,
        launch_date=launch_dt,
        end_date=end_dt,
        cultural_moment=cultural_moment,
        target_audience=target_audience,
        status="planning"
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Generate AI content suggestions
    if generate_suggestions and AI_AVAILABLE:
        suggestions = generate_content_suggestions(campaign, db)
        campaign.content_suggestions = suggestions
        db.commit()
    
    return {
        "success": True,
        "campaign_id": campaign.id,
        "name": campaign.name,
        "has_suggestions": bool(campaign.content_suggestions)
    }


@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign details with content suggestions"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "theme": campaign.theme,
        "launch_date": campaign.launch_date.isoformat() if campaign.launch_date else None,
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "status": campaign.status,
        "cultural_moment": campaign.cultural_moment,
        "target_audience": campaign.target_audience,
        "content_suggestions": campaign.content_suggestions,
        "notes": campaign.notes,
        "created_at": campaign.created_at.isoformat()
    }


@router.post("/{campaign_id}/generate-suggestions")
def regenerate_suggestions(campaign_id: int, db: Session = Depends(get_db)):
    """Regenerate AI content suggestions for a campaign"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    if not AI_AVAILABLE:
        raise HTTPException(503, "AI suggestions unavailable - OpenAI not configured")
    
    suggestions = generate_content_suggestions(campaign, db)
    campaign.content_suggestions = suggestions
    db.commit()
    
    return {
        "success": True,
        "suggestions": suggestions
    }


@router.put("/{campaign_id}")
def update_campaign(
    campaign_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update campaign"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    if name:
        campaign.name = name
    if description:
        campaign.description = description
    if status:
        campaign.status = status
    if notes:
        campaign.notes = notes
    
    db.commit()
    
    return {"success": True}


@router.get("/cultural-calendar")
def get_cultural_calendar(days_ahead: int = 120, db: Session = Depends(get_db)):
    """Get rolling cultural calendar - upcoming moments for the next 90-120 days
    
    Always shows relevant hip hop, urban, and streetwear moments ahead
    """
    
    from datetime import datetime, timedelta
    import calendar as cal
    
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)
    
    # Helper function for calculating Monday holidays
    def third_monday(year, month):
        """Get third Monday of month"""
        first_day = datetime(year, month, 1)
        first_monday = 1 + (7 - first_day.weekday()) % 7
        return first_monday + 14
    
    # Generate ALL potential cultural moments dynamically
    def get_all_moments_in_range(start_date, end_date):
        moments = []
        current = start_date
        
        while current <= end_date:
            year = current.year
            month = current.month
            
            # === MONTHLY RECURRING MOMENTS ===
            
            # January
            if month == 1:
                moments.append({
                    "name": "New Year Fresh Fits Season",
                    "date": f"{year}-01-01",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "New year, new wardrobe - fresh drop campaign",
                    "duration_days": 14
                })
                moments.append({
                    "name": "MLK Day",
                    "date": f"{year}-01-{third_monday(year, 1):02d}",
                    "category": "cultural",
                    "type": "annual",
                    "opportunity": "Honor legacy with authentic content, community focus",
                    "duration_days": 3
                })
                
            # February
            elif month == 2:
                moments.append({
                    "name": "Black History Month",
                    "date": f"{year}-02-01",
                    "category": "cultural",
                    "type": "recurring",
                    "opportunity": "Month-long celebration of Black culture in streetwear & hip hop",
                    "duration_days": 28
                })
                moments.append({
                    "name": "NBA All-Star Weekend",
                    "date": f"{year}-02-14",
                    "category": "sports",
                    "type": "annual",
                    "opportunity": "Basketball culture x streetwear, celebrity fits, watch parties",
                    "duration_days": 3
                })
                moments.append({
                    "name": "Grammy Awards",
                    "date": f"{year}-02-02",
                    "category": "hip_hop",
                    "type": "annual",
                    "opportunity": "Hip hop fashion moments, red carpet street style",
                    "duration_days": 1
                })
                
            # March
            elif month == 3:
                moments.append({
                    "name": "March Madness",
                    "date": f"{year}-03-17",
                    "category": "sports",
                    "type": "recurring",
                    "opportunity": "College basketball culture, campus style, tournament parties",
                    "duration_days": 21
                })
                moments.append({
                    "name": "Spring Break Season",
                    "date": f"{year}-03-10",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Travel fits, spring collection drop",
                    "duration_days": 14
                })
                
            # April
            elif month == 4:
                moments.append({
                    "name": "Coachella Season",
                    "date": f"{year}-04-11",
                    "category": "music",
                    "type": "annual",
                    "opportunity": "Festival fits (even if not attending), spring style",
                    "duration_days": 7
                })
                moments.append({
                    "name": "NBA Playoffs Begin",
                    "date": f"{year}-04-15",
                    "category": "sports",
                    "type": "annual",
                    "opportunity": "Playoff energy, team pride content, watch party fits",
                    "duration_days": 60
                })
                moments.append({
                    "name": "Record Store Day",
                    "date": f"{year}-04-19",
                    "category": "hip_hop",
                    "type": "annual",
                    "opportunity": "Music culture celebration, vinyl drops, nostalgia",
                    "duration_days": 1
                })
                
            # May
            elif month == 5:
                moments.append({
                    "name": "Memorial Day Weekend",
                    "date": f"{year}-05-26",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Unofficial start of summer, cookout season kickoff",
                    "duration_days": 3
                })
                moments.append({
                    "name": "Summer Drop Season",
                    "date": f"{year}-05-15",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Summer collection launch, lighter fabrics, bright colors",
                    "duration_days": 30
                })
                
            # June
            elif month == 6:
                moments.append({
                    "name": "Juneteenth",
                    "date": f"{year}-06-19",
                    "category": "cultural",
                    "type": "annual",
                    "opportunity": "Celebrate freedom, Black culture, authentic storytelling",
                    "duration_days": 3
                })
                moments.append({
                    "name": "BET Awards",
                    "date": f"{year}-06-29",
                    "category": "hip_hop",
                    "type": "annual",
                    "opportunity": "Hip hop's biggest night, fashion moments, artist features",
                    "duration_days": 1
                })
                moments.append({
                    "name": "NBA Finals",
                    "date": f"{year}-06-05",
                    "category": "sports",
                    "type": "annual",
                    "opportunity": "Championship energy, watch parties, team gear",
                    "duration_days": 14
                })
                moments.append({
                    "name": "Pride Month (Urban Lens)",
                    "date": f"{year}-06-01",
                    "category": "cultural",
                    "type": "recurring",
                    "opportunity": "LGBTQ+ representation in streetwear, inclusive marketing",
                    "duration_days": 30
                })
                
            # July
            elif month == 7:
                moments.append({
                    "name": "Fourth of July Parties",
                    "date": f"{year}-07-04",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Summer party fits, cookouts, day parties",
                    "duration_days": 3
                })
                moments.append({
                    "name": "Rolling Loud",
                    "date": f"{year}-07-25",
                    "category": "music",
                    "type": "annual",
                    "opportunity": "Hip hop festival fits, artist spotlights, street style",
                    "duration_days": 3
                })
                moments.append({
                    "name": "Summer Concert Season Peak",
                    "date": f"{year}-07-01",
                    "category": "music",
                    "type": "recurring",
                    "opportunity": "Tour merch, concert fits, artist collabs",
                    "duration_days": 60
                })
                
            # August
            elif month == 8:
                moments.append({
                    "name": "Back to School Season",
                    "date": f"{year}-08-15",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "College move-in, campus style, fresh semester energy",
                    "duration_days": 21
                })
                moments.append({
                    "name": "Hip Hop Anniversary (Aug 11, 1973)",
                    "date": f"{year}-08-11",
                    "category": "hip_hop",
                    "type": "annual",
                    "opportunity": "Celebrate hip hop's birthday, throwback content, history",
                    "duration_days": 3
                })
                
            # September
            elif month == 9:
                moments.append({
                    "name": "Fashion Week Season",
                    "date": f"{year}-09-08",
                    "category": "streetwear",
                    "type": "annual",
                    "opportunity": "Street style (not runway), trend spotting, influencer content",
                    "duration_days": 21
                })
                moments.append({
                    "name": "Labor Day Weekend",
                    "date": f"{year}-09-01",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "End of summer sales, last summer fits",
                    "duration_days": 3
                })
                moments.append({
                    "name": "Hispanic Heritage Month",
                    "date": f"{year}-09-15",
                    "category": "cultural",
                    "type": "recurring",
                    "opportunity": "Celebrate Latino streetwear culture, reggaeton influence",
                    "duration_days": 45
                })
                
            # October
            elif month == 10:
                moments.append({
                    "name": "NBA Season Tip-Off",
                    "date": f"{year}-10-22",
                    "category": "sports",
                    "type": "annual",
                    "opportunity": "Basketball season returns, team pride, new season energy",
                    "duration_days": 7
                })
                moments.append({
                    "name": "Halloween Urban Style",
                    "date": f"{year}-10-31",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Costume culture, nightlife fits, party szn",
                    "duration_days": 7
                })
                
            # November
            elif month == 11:
                moments.append({
                    "name": "Day of the Dead",
                    "date": f"{year}-11-01",
                    "category": "cultural",
                    "type": "annual",
                    "opportunity": "Latino culture celebration, artistic storytelling",
                    "duration_days": 2
                })
                moments.append({
                    "name": "Hip Hop History Month",
                    "date": f"{year}-11-01",
                    "category": "hip_hop",
                    "type": "recurring",
                    "opportunity": "Celebrate rap pioneers, throwback content, education",
                    "duration_days": 30
                })
                moments.append({
                    "name": "Thanksgiving Weekend",
                    "date": f"{year}-11-28",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Family fits, Black Friday alternative drops",
                    "duration_days": 4
                })
                moments.append({
                    "name": "Black Friday (Anti-Corporate)",
                    "date": f"{year}-11-29",
                    "category": "retail",
                    "type": "recurring",
                    "opportunity": "Limited street drops, exclusive releases (not corporate sales)",
                    "duration_days": 1
                })
                
            # December
            elif month == 12:
                moments.append({
                    "name": "Holiday Party Season",
                    "date": f"{year}-12-10",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Party fits, nightlife style, NYE prep",
                    "duration_days": 21
                })
                moments.append({
                    "name": "Winter Collection Drop",
                    "date": f"{year}-12-01",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Cold weather essentials, hoodies, jackets, layering",
                    "duration_days": 30
                })
                moments.append({
                    "name": "Christmas Week",
                    "date": f"{year}-12-25",
                    "category": "seasonal",
                    "type": "recurring",
                    "opportunity": "Gift ideas, last-minute drops, family gathering fits",
                    "duration_days": 7
                })
                
            # Move to next month
            current = current + timedelta(days=32)
            current = current.replace(day=1)
        
        return moments
    
    # Get all moments
    all_moments = get_all_moments_in_range(now, end_date)
    
    # Filter to only upcoming moments
    upcoming = []
    for moment in all_moments:
        moment_date = datetime.fromisoformat(moment["date"])
        if moment_date >= now:
            days_away = (moment_date - now).days
            end_of_moment = moment_date + timedelta(days=moment.get("duration_days", 1))
            
            upcoming.append({
                **moment,
                "days_away": days_away,
                "month": moment_date.strftime("%B"),
                "formatted_date": moment_date.strftime("%B %d, %Y"),
                "day_of_week": moment_date.strftime("%A"),
                "end_date": end_of_moment.strftime("%B %d, %Y"),
                "is_upcoming_soon": days_away <= 30,
                "planning_window": "Plan now!" if days_away <= 30 else "Start planning" if days_away <= 60 else "On radar"
            })
    
    # Sort by date
    upcoming.sort(key=lambda x: x["days_away"])
    
    # Group by timeframe
    next_30_days = [m for m in upcoming if m["days_away"] <= 30]
    next_60_days = [m for m in upcoming if 30 < m["days_away"] <= 60]
    next_90_days = [m for m in upcoming if 60 < m["days_away"] <= 90]
    beyond_90_days = [m for m in upcoming if m["days_away"] > 90]
    
    # Group by category
    by_category = {
        "hip_hop": [m for m in upcoming if m["category"] == "hip_hop"],
        "sports": [m for m in upcoming if m["category"] == "sports"],
        "cultural": [m for m in upcoming if m["category"] == "cultural"],
        "music": [m for m in upcoming if m["category"] == "music"],
        "seasonal": [m for m in upcoming if m["category"] == "seasonal"],
        "streetwear": [m for m in upcoming if m["category"] == "streetwear"],
        "retail": [m for m in upcoming if m["category"] == "retail"]
    }
    
    return {
        "all_upcoming": upcoming,
        "by_timeframe": {
            "next_30_days": next_30_days,
            "next_60_days": next_60_days,
            "next_90_days": next_90_days,
            "beyond_90_days": beyond_90_days
        },
        "by_category": by_category,
        "total_moments": len(upcoming),
        "planning_summary": {
            "urgent": len(next_30_days),
            "coming_soon": len(next_60_days),
            "on_radar": len(next_90_days) + len(beyond_90_days)
        }
    }


def generate_content_suggestions(campaign: Campaign, db: Session):
    """Generate AI content suggestions based on campaign and intelligence data
    
    Focuses on hip hop culture, urban moments, and authentic streetwear marketing
    """
    
    if not AI_AVAILABLE:
        return {"error": "OpenAI not configured"}
    
    try:
        # Get recent intelligence data for context
        recent_intel = db.query(IntelligenceFile).filter(
            IntelligenceFile.status == "processed",
            IntelligenceFile.analysis_results.isnot(None)
        ).order_by(desc(IntelligenceFile.uploaded_at)).limit(3).all()
        
        # Build context from intelligence
        intel_context = ""
        if recent_intel:
            intel_context = "\n\nRecent competitive intelligence insights:\n"
            for file in recent_intel:
                if isinstance(file.analysis_results, dict) and "analysis" in file.analysis_results:
                    analysis = file.analysis_results["analysis"]
                    intel_context += f"- {analysis[:500]}...\n"
        
        # Create AI prompt with STREETWEAR/HIP HOP FOCUS
        client = OpenAIClient(api_key=OPENAI_API_KEY)
        
        system_prompt = """You are a streetwear marketing strategist for Crooks & Castles, deeply embedded in hip hop and urban culture.

BRAND CONTEXT:
- Crooks & Castles is an authentic streetwear brand rooted in hip hop culture
- Target: Gen Z and millennial streetwear enthusiasts who live and breathe hip hop
- Values: Authenticity, rebellion, street credibility, cultural relevance

CULTURAL FOCUS AREAS (prioritize these):
**Hip Hop Culture:**
- Album drops, mixtape releases, artist collaborations
- Hip hop award shows (BET Awards, Hip Hop Awards, Grammys)
- Rap battles, cyphers, freestyle culture
- Producer beats, sampling culture
- Hip hop fashion moments

**Urban Culture & Events:**
- Sneaker releases and drops
- Basketball culture (NBA playoffs, All-Star, streetball)
- Graffiti/street art exhibitions
- Underground music scenes
- Block parties, day parties, concert culture

**National/Cultural Moments:**
- Black History Month (authentic celebration, not performative)
- Juneteenth
- NBA Finals, March Madness
- Fashion weeks (with street lens, not high fashion)
- Music festival season (Rolling Loud, Day N Vegas, etc.)

**Seasonal Urban Moments:**
- Back to school (college move-in culture)
- Summer cookout season
- Winter coat season (fitted, puffer culture)
- Holiday parties (not traditional, but urban nightlife)

AVOID:
- Generic corporate holidays
- Inauthentic "brand voice" 
- Surface-level trend chasing
- Anything that feels forced or disconnected from street culture

Generate content that CONNECTS to what the Crooks & Castles customer actually cares about."""

        user_prompt = f"""Create content marketing suggestions for this Crooks & Castles campaign:

**Campaign Details:**
Name: {campaign.name}
Description: {campaign.description}
Theme: {campaign.theme}
Launch Date: {campaign.launch_date.strftime('%B %d, %Y') if campaign.launch_date else 'TBD'}
Cultural Moment: {campaign.cultural_moment}
Target Audience: {campaign.target_audience}

**Intelligence Context:**
{intel_context}

Provide 5-7 SPECIFIC content ideas that leverage hip hop culture, urban moments, and authentic street marketing opportunities.

Return in JSON format:
{{
  "suggestions": [
    {{
      "title": "Specific content idea",
      "description": "Detailed tactical execution (not vague)",
      "platform": "Instagram/TikTok/Email/Twitter/IRL",
      "content_type": "Reel/Story/Email/Event/Collab/etc",
      "timing": "Exact timing relative to cultural moment",
      "why_it_works": "Why this resonates with streetwear/hip hop audience",
      "cultural_connection": "Specific hip hop/urban/cultural moment it taps into",
      "execution_notes": "How to execute authentically"
    }}
  ],
  "key_opportunities": [
    "Upcoming hip hop moments to leverage",
    "Urban culture connections to tap into",
    "Authentic engagement tactics"
  ],
  "timing_strategy": "When and why to activate this campaign based on culture",
  "authenticity_notes": "How to stay true to street culture and avoid looking corporate"
}}

CRITICAL: Every suggestion must connect to real hip hop/urban culture, not generic marketing."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2500,
            temperature=0.75
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            suggestions_text = suggestions_text.replace("```json", "").replace("```", "").strip()
            suggestions = json.loads(suggestions_text)
        except:
            suggestions = {"raw_suggestions": suggestions_text}
        
        suggestions["generated_at"] = datetime.utcnow().isoformat()
        suggestions["intelligence_sources_used"] = len(recent_intel)
        
        return suggestions
        
    except Exception as e:
        print(f"[Campaigns] AI suggestion error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Failed to generate suggestions - check OpenAI configuration"
        }
