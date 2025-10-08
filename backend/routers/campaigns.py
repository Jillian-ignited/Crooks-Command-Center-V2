from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta
from typing import Optional
import os
from openai import OpenAI

from ..database import get_db
from ..models import Campaign

router = APIRouter()

# Initialize OpenAI client
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("[Campaigns] ✅ OpenAI available for content suggestions")
except Exception as e:
    openai_client = None
    print(f"[Campaigns] ⚠️ OpenAI not available: {e}")


@router.get("/")
def get_campaigns(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all campaigns with optional status filter"""
    
    query = db.query(Campaign)
    
    if status:
        query = query.filter(Campaign.status == status)
    
    total = query.count()
    campaigns = query.order_by(desc(Campaign.created_at)).limit(limit).offset(offset).all()
    
    return {
        "campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "status": c.status,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "budget": c.budget,
                "target_audience": c.target_audience,
                "channels": c.channels,
                "kpis": c.kpis,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in campaigns
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/")
async def create_campaign(
    name: str,
    description: str,
    start_date: str,
    end_date: Optional[str] = None,
    budget: Optional[float] = None,
    target_audience: Optional[str] = None,
    channels: Optional[list] = None,
    kpis: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Create a new campaign with AI-generated suggestions"""
    
    # Parse dates
    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
    
    # Generate AI suggestions
    ai_suggestions = None
    if openai_client:
        try:
            ai_suggestions = await generate_campaign_suggestions(
                name, description, target_audience, channels
            )
        except Exception as e:
            print(f"[Campaigns] AI suggestion failed: {e}")
    
    campaign = Campaign(
        name=name,
        description=description,
        status="planning",
        start_date=start,
        end_date=end,
        budget=budget,
        target_audience=target_audience,
        channels=channels,
        kpis=kpis,
        ai_suggestions=ai_suggestions
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "status": campaign.status,
        "ai_suggestions": campaign.ai_suggestions,
        "created_at": campaign.created_at.isoformat()
    }


@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get detailed campaign information"""
    
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "status": campaign.status,
        "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "budget": campaign.budget,
        "target_audience": campaign.target_audience,
        "channels": campaign.channels,
        "kpis": campaign.kpis,
        "ai_suggestions": campaign.ai_suggestions,
        "created_at": campaign.created_at.isoformat(),
        "updated_at": campaign.updated_at.isoformat()
    }


@router.put("/{campaign_id}")
def update_campaign(
    campaign_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    budget: Optional[float] = None,
    target_audience: Optional[str] = None,
    channels: Optional[list] = None,
    kpis: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Update campaign details"""
    
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    if name:
        campaign.name = name
    if description:
        campaign.description = description
    if status:
        campaign.status = status
    if start_date:
        campaign.start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if end_date:
        campaign.end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    if budget is not None:
        campaign.budget = budget
    if target_audience:
        campaign.target_audience = target_audience
    if channels:
        campaign.channels = channels
    if kpis:
        campaign.kpis = kpis
    
    campaign.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(campaign)
    
    return {"success": True, "campaign_id": campaign.id}


@router.post("/{campaign_id}/generate-suggestions")
async def regenerate_suggestions(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Regenerate AI suggestions for a campaign"""
    
    if not openai_client:
        raise HTTPException(503, "AI service not available")
    
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    try:
        ai_suggestions = await generate_campaign_suggestions(
            campaign.name,
            campaign.description,
            campaign.target_audience,
            campaign.channels
        )
        
        campaign.ai_suggestions = ai_suggestions
        campaign.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(campaign)
        
        return {
            "success": True,
            "ai_suggestions": ai_suggestions
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to generate suggestions: {str(e)}")


async def generate_campaign_suggestions(
    name: str,
    description: str,
    target_audience: Optional[str],
    channels: Optional[list]
):
    """Generate AI-powered campaign suggestions using OpenAI"""
    
    prompt = f"""You are a streetwear and hip-hop culture marketing expert for Crooks & Castles.

Campaign: {name}
Description: {description}
Target Audience: {target_audience or "Urban youth 18-34, hip-hop fans, streetwear collectors, rebels/rulers/creators"}
Channels: {', '.join(channels) if channels else "Instagram, TikTok, Email"}

Generate creative campaign suggestions for authentic street culture:
1. 3 content ideas that resonate with hustlers, rebels, and cultural architects
2. 3 social media post concepts that feel earned, not corporate
3. Key messaging that honors legacy + authenticity
4. Hashtag recommendations that signal credibility

Keep suggestions real to the streets. No clout-chasing. Crooks & Castles = heritage, code, loyalty."""

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a streetwear marketing expert who understands hip-hop culture authenticity."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    suggestions_text = response.choices[0].message.content
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suggestions": suggestions_text,
        "model": "gpt-4"
    }


@router.get("/cultural-calendar")
def get_cultural_calendar(
    days_ahead: int = 90,
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """Get cultural calendar events - shows next 90 days by default for planning"""
    
    # Authentic cultural calendar for Crooks & Castles customers
    annual_events = [
        # JANUARY - New Year Hustle
        {"month": 1, "day": 1, "name": "New Year Reset", "category": "culture", "relevance": "Fresh start drops, New Year's resolutions for hustlers"},
        {"month": 1, "day": 8, "name": "Elvis Presley Birthday", "category": "music", "relevance": "OG rebel, rock meets street culture"},
        {"month": 1, "day": 15, "name": "MLK Day", "category": "cultural", "relevance": "Civil rights legacy, resist authority, fight for community"},
        {"month": 1, "day": 17, "name": "Kid Cudi Birthday", "category": "hip-hop", "relevance": "Man on the Moon - outsider anthem, mental health in hip-hop"},
        {"month": 1, "day": 28, "name": "J. Cole Birthday", "category": "hip-hop", "relevance": "Dreamville, conscious rap, indie hustle mindset"},
        
        # FEBRUARY - Black Excellence
        {"month": 2, "day": 1, "name": "Black History Month", "category": "cultural", "relevance": "Celebrate Black creators, founders, and street culture architects"},
        {"month": 2, "day": 7, "name": "2Pac Birthday", "category": "hip-hop", "relevance": "West Coast legend, Thug Life code, outlaw authenticity"},
        {"month": 2, "day": 9, "name": "Super Bowl", "category": "sports", "relevance": "Halftime show culture, tailgate flex, athleisure crossover"},
        {"month": 2, "day": 14, "name": "Valentine's Day", "category": "lifestyle", "relevance": "Couples flex, gift drops for the crew"},
        {"month": 2, "day": 16, "name": "NBA All-Star Weekend", "category": "sports", "relevance": "Sneaker culture peak, celebrity courtside flex, basketball meets fashion"},
        {"month": 2, "day": 18, "name": "Air Jordan Birthday", "category": "streetwear", "relevance": "Jordan 1 release anniversary - sneaker royalty"},
        {"month": 2, "day": 21, "name": "Biggie Birthday", "category": "hip-hop", "relevance": "Notorious B.I.G., Brooklyn king, East Coast crown"},
        
        # MARCH - Madness & Drops
        {"month": 3, "day": 1, "name": "March Madness Begins", "category": "sports", "relevance": "College basketball culture, bracket betting, underdog stories"},
        {"month": 3, "day": 8, "name": "International Women's Day", "category": "cultural", "relevance": "Women in streetwear, female hustlers, queens in the game"},
        {"month": 3, "day": 17, "name": "St. Patrick's Day", "category": "culture", "relevance": "Green drops, Irish mob aesthetics, working-class pride"},
        {"month": 3, "day": 26, "name": "Air Max Day", "category": "streetwear", "relevance": "Nike Air Max 1 anniversary, sneakerhead holiday"},
        {"month": 3, "day": 27, "name": "Quavo Birthday", "category": "hip-hop", "relevance": "Migos, trap culture, Atlanta influence"},
        
        # APRIL - Spring Drops
        {"month": 4, "day": 1, "name": "April Fools", "category": "culture", "relevance": "Surprise drops, troll marketing, chaos energy"},
        {"month": 4, "day": 4, "name": "Beyoncé Birthday", "category": "culture", "relevance": "Queen B, Black excellence, luxury streetwear crossover"},
        {"month": 4, "day": 7, "name": "MLB Opening Day", "category": "sports", "relevance": "Fitted cap culture, baseball heritage, stadium flex"},
        {"month": 4, "day": 13, "name": "Record Store Day", "category": "music", "relevance": "Vinyl culture, crate diggers, music heritage"},
        {"month": 4, "day": 14, "name": "Coachella Weekend 1", "category": "festival", "relevance": "Festival fashion, influencer culture, desert flex"},
        {"month": 4, "day": 16, "name": "Selena Birthday", "category": "latino-culture", "relevance": "Tejano queen, Latino streetwear influence"},
        {"month": 4, "day": 20, "name": "4/20", "category": "culture", "relevance": "Cannabis culture, counterculture codes, stoner aesthetics"},
        
        # MAY - Summer Season Kickoff
        {"month": 5, "day": 1, "name": "May Day", "category": "culture", "relevance": "Workers' rights, hustle culture, independent grind"},
        {"month": 5, "day": 5, "name": "Cinco de Mayo", "category": "latino-culture", "relevance": "Latino heritage, street party culture"},
        {"month": 5, "day": 6, "name": "Travis Scott Birthday", "category": "hip-hop", "relevance": "Cactus Jack, Astroworld, rage culture"},
        {"month": 5, "day": 12, "name": "Mother's Day", "category": "lifestyle", "relevance": "Honor the queens, gift season"},
        {"month": 5, "day": 21, "name": "Biggie Death Anniversary", "category": "hip-hop", "relevance": "Remembrance, Brooklyn tribute, rap royalty"},
        {"month": 5, "day": 23, "name": "Jordan 1 Anniversary", "category": "streetwear", "relevance": "Most iconic sneaker ever, banned story"},
        {"month": 5, "day": 25, "name": "Memorial Day", "category": "culture", "relevance": "Summer kickoff, long weekend drops, camo heritage"},
        
        # JUNE - Pride & Finals
        {"month": 6, "day": 1, "name": "Pride Month", "category": "cultural", "relevance": "LGBTQ+ representation in streetwear, inclusive crew"},
        {"month": 6, "day": 1, "name": "NBA Finals Begin", "category": "sports", "relevance": "Championship culture, peak sneaker season, courtside fashion"},
        {"month": 6, "day": 6, "name": "BET Awards", "category": "entertainment", "relevance": "Black entertainment celebration, red carpet street style"},
        {"month": 6, "day": 7, "name": "Lil Baby Birthday", "category": "hip-hop", "relevance": "My Turn era, Atlanta trap, street to success"},
        {"month": 6, "day": 13, "name": "Tupac Death Anniversary", "category": "hip-hop", "relevance": "West Coast legend, All Eyez On Me legacy"},
        {"month": 6, "day": 16, "name": "2Pac Death Anniversary", "category": "hip-hop", "relevance": "Remembrance, outlaw code"},
        {"month": 6, "day": 19, "name": "Juneteenth", "category": "cultural", "relevance": "Freedom Day, Black liberation, independent hustle"},
        {"month": 6, "day": 21, "name": "Father's Day", "category": "lifestyle", "relevance": "Kings and OGs, generational codes"},
        {"month": 6, "day": 27, "name": "XXXTentacion Death Anniversary", "category": "hip-hop", "relevance": "SoundCloud era, emo rap, Gen Z icon"},
        
        # JULY - Independence & Summer
        {"month": 7, "day": 4, "name": "Independence Day", "category": "culture", "relevance": "American rebel spirit, fireworks, red/white/blue drops"},
        {"month": 7, "day": 6, "name": "50 Cent Birthday", "category": "hip-hop", "relevance": "G-Unit, Get Rich or Die Tryin', entrepreneur code"},
        {"month": 7, "day": 8, "name": "Mac Miller Birthday", "category": "hip-hop", "relevance": "Pittsburgh legend, artist authenticity, indie creativity"},
        {"month": 7, "day": 21, "name": "Rolling Loud", "category": "festival", "relevance": "Hip-hop festival, rage culture, youth energy"},
        {"month": 7, "day": 26, "name": "Mick Jagger Birthday", "category": "music", "relevance": "Rock rebel, Stones legacy, outlaw aesthetic"},
        
        # AUGUST - Back to Streets
        {"month": 8, "day": 4, "name": "Megan Thee Stallion Birthday", "category": "hip-hop", "relevance": "Hot Girl Summer, female rap royalty"},
        {"month": 8, "day": 11, "name": "Hip-Hop Birthday", "category": "hip-hop", "relevance": "1973 - Birth at 1520 Sedgwick, culture foundation"},
        {"month": 8, "day": 15, "name": "Back to School", "category": "culture", "relevance": "Fresh gear season, youth marketing, new semester flex"},
        {"month": 8, "day": 25, "name": "Aaliyah Death Anniversary", "category": "culture", "relevance": "R&B icon, Timberland collaboration, tomboy chic"},
        {"month": 8, "day": 25, "name": "MTV VMAs", "category": "entertainment", "relevance": "Music video culture, viral moments, red carpet rebellion"},
        
        # SEPTEMBER - Fall Reset
        {"month": 9, "day": 4, "name": "Beyoncé Birthday", "category": "culture", "relevance": "Queen energy, luxury streetwear, Black excellence"},
        {"month": 9, "day": 7, "name": "Labor Day", "category": "culture", "relevance": "End of summer sales, hustle appreciation, workers' pride"},
        {"month": 9, "day": 8, "name": "NFL Season Kickoff", "category": "sports", "relevance": "Football culture, tailgate fits, team pride"},
        {"month": 9, "day": 8, "name": "NYFW", "category": "fashion", "relevance": "Fashion Week, streetwear shows, runway to streets"},
        {"month": 9, "day": 13, "name": "Tupac Death", "category": "hip-hop", "relevance": "Makaveli legacy, conspiracy culture"},
        {"month": 9, "day": 25, "name": "Pharrell Birthday", "category": "culture", "relevance": "Billionaire Boys Club, Ice Cream, producer king"},
        {"month": 9, "day": 26, "name": "Lil Wayne Birthday", "category": "hip-hop", "relevance": "Weezy F Baby, Trukfit, New Orleans legend"},
        
        # OCTOBER - Spooky Season
        {"month": 10, "day": 1, "name": "NBA Season Begins", "category": "sports", "relevance": "Basketball returns, sneaker releases ramp up"},
        {"month": 10, "day": 3, "name": "Mean Girls Day", "category": "pop-culture", "relevance": "On Wednesdays we wear pink - meme culture"},
        {"month": 10, "day": 8, "name": "Bella Hadid Birthday", "category": "culture", "relevance": "Model off-duty style, streetwear influence"},
        {"month": 10, "day": 17, "name": "Eminem Birthday", "category": "hip-hop", "relevance": "8 Mile, Detroit grit, underdog story"},
        {"month": 10, "day": 21, "name": "21 Savage Birthday", "category": "hip-hop", "relevance": "Zone 6, Atlanta trap, immigration story"},
        {"month": 10, "day": 24, "name": "Drake Birthday", "category": "hip-hop", "relevance": "OVO, Toronto influence, emotional gangster"},
        {"month": 10, "day": 31, "name": "Halloween", "category": "culture", "relevance": "Costume culture, dark aesthetics, limited drops"},
        
        # NOVEMBER - Gratitude & Grind
        {"month": 11, "day": 1, "name": "Día de los Muertos", "category": "latino-culture", "relevance": "Mexican heritage, skull aesthetics, remembrance"},
        {"month": 11, "day": 3, "name": "Kendrick Lamar Birthday", "category": "hip-hop", "relevance": "TDE, Compton king, conscious rebel"},
        {"month": 11, "day": 8, "name": "SZA Birthday", "category": "music", "relevance": "R&B queen, TDE, vulnerable authenticity"},
        {"month": 11, "day": 11, "name": "Veterans Day", "category": "culture", "relevance": "Military heritage, camo culture, discipline codes"},
        {"month": 11, "day": 19, "name": "Jordan 11 Concord Season", "category": "streetwear", "relevance": "Holiday 11s tradition, December prep"},
        {"month": 11, "day": 23, "name": "Thanksgiving", "category": "culture", "relevance": "Gratitude, family flex, Black Friday prep"},
        {"month": 11, "day": 24, "name": "Black Friday", "category": "retail", "relevance": "Drop culture, deals, sneaker releases, chaos"},
        {"month": 11, "day": 27, "name": "Cyber Monday", "category": "retail", "relevance": "Online cop day, digital hustle"},
        {"month": 11, "day": 30, "name": "Juice WRLD Birthday", "category": "hip-hop", "relevance": "999, emo rap, SoundCloud legend"},
        
        # DECEMBER - Holiday Hustle
        {"month": 12, "day": 4, "name": "Jay-Z Birthday", "category": "hip-hop", "relevance": "Hov, Roc-A-Fella, blueprint entrepreneur"},
        {"month": 12, "day": 5, "name": "Offset Birthday", "category": "hip-hop", "relevance": "Migos, luxury streetwear, Atlanta culture"},
        {"month": 12, "day": 8, "name": "Juice WRLD Death Anniversary", "category": "hip-hop", "relevance": "Legends Never Die, Gen Z mourning"},
        {"month": 12, "day": 18, "name": "DMX Birthday", "category": "hip-hop", "relevance": "Ruff Ryders, raw energy, Yonkers legend"},
        {"month": 12, "day": 25, "name": "Christmas", "category": "culture", "relevance": "Gift culture, NBA games, family flex"},
        {"month": 12, "day": 26, "name": "Kwanzaa", "category": "cultural", "relevance": "Black unity, African heritage, seven principles"},
        {"month": 12, "day": 31, "name": "New Year's Eve", "category": "culture", "relevance": "Party season, year reflection, countdown culture"},
    ]
    
    # Get today and calculate date range
    today = datetime.now(timezone.utc).date()
    end_date = today + timedelta(days=days_ahead)
    
    # Convert annual events to actual dates in the rolling window
    upcoming_events = []
    
    for event in annual_events:
        # Check this year and next year to capture rolling window
        for year_offset in [0, 1]:
            event_year = today.year + year_offset
            try:
                event_date = datetime(event_year, event["month"], event["day"]).date()
                
                # Only include if within our date range
                if today <= event_date <= end_date:
                    days_until = (event_date - today).days
                    
                    upcoming_events.append({
                        **event,
                        "year": event_year,
                        "date": event_date.isoformat(),
                        "days_until": days_until,
                        "planning_window": "immediate" if days_until <= 7 else "week" if days_until <= 14 else "two_weeks" if days_until <= 30 else "month" if days_until <= 60 else "future"
                    })
            except ValueError:
                # Handle invalid dates
                continue
    
    # Sort by date
    upcoming_events.sort(key=lambda x: x["date"])
    
    # If month filter specified, filter by month
    if month:
        upcoming_events = [e for e in upcoming_events if e["month"] == month]
    
    # If year filter specified, filter by year
    if year:
        upcoming_events = [e for e in upcoming_events if e["year"] == year]
    
    # Calculate category counts
    categories = {}
    for event in upcoming_events:
        cat = event["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "start_date": today.isoformat(),
        "end_date": end_date.isoformat(),
        "days_ahead": days_ahead,
        "total_events": len(upcoming_events),
        "events": upcoming_events,
        "categories": categories,
        "planning_windows": {
            "immediate": len([e for e in upcoming_events if e["planning_window"] == "immediate"]),
            "week": len([e for e in upcoming_events if e["planning_window"] == "week"]),
            "two_weeks": len([e for e in upcoming_events if e["planning_window"] == "two_weeks"]),
            "month": len([e for e in upcoming_events if e["planning_window"] == "month"]),
            "future": len([e for e in upcoming_events if e["planning_window"] == "future"])
        }
    }