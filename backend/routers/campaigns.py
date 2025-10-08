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


@router.get("/cultural-calendar")
def get_cultural_calendar(
    days_ahead: int = 90,
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """Get THE LEGENDARY cultural calendar - most comprehensive streetwear culture moments"""
    
    # THE MOST LEGENDARY STREETWEAR CULTURE CALENDAR EVER CREATED
    annual_events = [
        # ═══════════════════════════════════════════════════════════
        # JANUARY - NEW YEAR ENERGY
        # ═══════════════════════════════════════════════════════════
        {"month": 1, "day": 1, "name": "New Year Drop Season", "category": "streetwear", "relevance": "Fresh year = fresh fits. Major drop season begins. New Year New Me energy."},
        {"month": 1, "day": 8, "name": "Elvis Presley Birthday", "category": "music", "relevance": "OG rebel before hip-hop, rockabilly aesthetic, Memphis legend"},
        {"month": 1, "day": 15, "name": "MLK Day", "category": "cultural", "relevance": "Civil rights legacy, resist authority, fight for community, Black excellence"},
        {"month": 1, "day": 17, "name": "Kid Cudi Birthday", "category": "hip-hop", "relevance": "Man on the Moon aesthetic, outsider anthem, mental health in hip-hop, Cleveland rebel"},
        {"month": 1, "day": 19, "name": "Dr. Dre 'The Chronic 2001' Anniversary (1999)", "category": "album", "relevance": "West Coast G-Funk perfection, lowrider culture, Death Row aftermath, Compton king"},
        {"month": 1, "day": 28, "name": "J. Cole Birthday", "category": "hip-hop", "relevance": "Dreamville boss, conscious rap, indie hustle mentality, Fayetteville to platinum"},
        
        # ═══════════════════════════════════════════════════════════
        # FEBRUARY - ALL-STAR & BLACK EXCELLENCE
        # ═══════════════════════════════════════════════════════════
        {"month": 2, "day": 1, "name": "Black History Month", "category": "cultural", "relevance": "Celebrate Black creators who BUILT streetwear, hip-hop culture, sneaker game"},
        {"month": 2, "day": 6, "name": "Nas 'Illmatic' Anniversary (1994)", "category": "album", "relevance": "GREATEST ALBUM EVER debate, Queensbridge projects, street poetry, timeless"},
        {"month": 2, "day": 7, "name": "2Pac Birthday", "category": "hip-hop", "relevance": "Thug Life code, bandana culture, West Coast OG, makaveli energy, outlaw authenticity"},
        {"month": 2, "day": 9, "name": "Super Bowl", "category": "sports", "relevance": "Halftime show culture, tailgate flex, jersey season, biggest TV moment of year"},
        {"month": 2, "day": 14, "name": "Valentine's Day", "category": "lifestyle", "relevance": "Couples drops, gift season for the crew, red/pink colorways"},
        {"month": 2, "day": 16, "name": "NBA All-Star Weekend", "category": "sports", "relevance": "SNEAKER RELEASES PEAK, courtside flex, celebrity sightings, basketball culture summit"},
        {"month": 2, "day": 18, "name": "Air Jordan Birthday (Feb 17, 1963 / Jordan 1 Released 1985)", "category": "streetwear", "relevance": "MJ born, Jordan 1 banned - the shoe that started EVERYTHING, sneaker royalty"},
        {"month": 2, "day": 21, "name": "Biggie Smalls Birthday", "category": "hip-hop", "relevance": "Coogi sweaters, Versace frames, Brooklyn king, Ready to Die, rap royalty"},
        
        # ═══════════════════════════════════════════════════════════
        # MARCH - SPRING SNEAKER SEASON & MADNESS
        # ═══════════════════════════════════════════════════════════
        {"month": 3, "day": 1, "name": "March Madness", "category": "sports", "relevance": "College hoops peak, bracket culture, Nike campus energy, underdog stories"},
        {"month": 3, "day": 8, "name": "International Women's Day", "category": "cultural", "relevance": "Queens in streetwear, female founders, women who built the culture"},
        {"month": 3, "day": 9, "name": "Biggie 'Ready to Die' Anniversary (1994)", "category": "album", "relevance": "Brooklyn crowned, Coogi aesthetic born, Versace frames, East Coast king"},
        {"month": 3, "day": 17, "name": "St. Patrick's Day", "category": "culture", "relevance": "Green drops, limited colorways, Irish mob aesthetics, Guinness and fits"},
        {"month": 3, "day": 25, "name": "Outkast 'Aquemini' Anniversary (1998)", "category": "album", "relevance": "Southern playalistic, Atlanta officially took over, Dungeon Family, rosa parks"},
        {"month": 3, "day": 26, "name": "Air Max Day", "category": "streetwear", "relevance": "Nike Air Max 1 (3.26.87) - SNEAKERHEAD HOLIDAY, visible air revolution, Tinker Hatfield legend"},
        {"month": 3, "day": 27, "name": "Quavo Birthday", "category": "hip-hop", "relevance": "Migos drip architect, trap fashion, Atlanta takeover, ice out everything"},
        {"month": 3, "day": 31, "name": "Eazy-E Death Anniversary (1995)", "category": "hip-hop", "relevance": "N.W.A founder, Compton legend, gangsta rap pioneer, jheri curl icon"},
        
        # ═══════════════════════════════════════════════════════════
        # APRIL - SPRING AWAKENING
        # ═══════════════════════════════════════════════════════════
        {"month": 4, "day": 1, "name": "April Fools", "category": "culture", "relevance": "Troll drops, surprise releases, chaos marketing, fake collabs that break internet"},
        {"month": 4, "day": 4, "name": "Beyoncé Birthday", "category": "culture", "relevance": "Ivy Park queen, athleisure royalty, Black excellence personified, Texas Hold'em"},
        {"month": 4, "day": 7, "name": "MLB Opening Day", "category": "sports", "relevance": "Fitted cap season BEGINS, New Era culture, stadium flex, baseball jerseys"},
        {"month": 4, "day": 13, "name": "Record Store Day", "category": "music", "relevance": "Vinyl culture, crate diggers, independent record shops, music purists"},
        {"month": 4, "day": 14, "name": "Coachella Weekend 1", "category": "festival", "relevance": "Festival fashion (though mainstream now), influencer marketing, desert vibes"},
        {"month": 4, "day": 16, "name": "Selena Day", "category": "latino-culture", "relevance": "Tejano queen, Latino streetwear icon, Corpus Christi legend"},
        {"month": 4, "day": 19, "name": "Nas 'Stillmatic' Anniversary (2001)", "category": "album", "relevance": "Ether diss destroyed Jay-Z, Queensbridge forever, comeback king"},
        {"month": 4, "day": 20, "name": "4/20", "category": "culture", "relevance": "Cannabis culture peak, stoner aesthetics, counterculture codes, green everything"},
        {"month": 4, "day": 29, "name": "A Tribe Called Quest 'The Low End Theory' Anniversary (1991)", "category": "album", "relevance": "Jazz rap perfection, Native Tongues, conscious hip-hop, timeless production"},
        
        # ═══════════════════════════════════════════════════════════
        # MAY - SUMMER PREP & MEMORIAL
        # ═══════════════════════════════════════════════════════════
        {"month": 5, "day": 1, "name": "May Day", "category": "culture", "relevance": "Workers' rights, hustle culture, independent grind, labor movement"},
        {"month": 5, "day": 5, "name": "Cinco de Mayo", "category": "latino-culture", "relevance": "Latino pride peak, street party culture, Mexican heritage"},
        {"month": 5, "day": 6, "name": "Travis Scott Birthday", "category": "hip-hop", "relevance": "Cactus Jack empire, rage culture, Nike SB Dunk collabs, Astroworld energy"},
        {"month": 5, "day": 12, "name": "Mother's Day", "category": "lifestyle", "relevance": "Honor the queens who raised us, gift season, family love"},
        {"month": 5, "day": 19, "name": "Malcolm X Birthday", "category": "cultural", "relevance": "By any means necessary, Black empowerment, Detroit Red legacy"},
        {"month": 5, "day": 21, "name": "Biggie Death Anniversary", "category": "hip-hop", "relevance": "March 9, 1997 - Brooklyn remembers, rap royalty fallen, conspiracy theories"},
        {"month": 5, "day": 23, "name": "Jordan 1 Release Anniversary (1985)", "category": "streetwear", "relevance": "OG Chicago colorway dropped, NBA banned them, most iconic sneaker EVER"},
        {"month": 5, "day": 25, "name": "Memorial Day Weekend", "category": "culture", "relevance": "Summer OFFICIALLY starts, long weekend drops, white tee season, BBQs"},
        {"month": 5, "day": 25, "name": "Lauryn Hill 'Miseducation' Anniversary (1998)", "category": "album", "relevance": "Female rap excellence, neo-soul fusion, conscious lyrics, Fugees legacy"},
        
        # ═══════════════════════════════════════════════════════════
        # JUNE - PRIDE & CHAMPIONSHIPS
        # ═══════════════════════════════════════════════════════════
        {"month": 6, "day": 1, "name": "Pride Month", "category": "cultural", "relevance": "LGBTQ+ in streetwear, inclusive crew culture, rainbow everything"},
        {"month": 6, "day": 1, "name": "NBA Finals Begin", "category": "sports", "relevance": "Championship energy, peak sneaker season, courtside fashion, legends made"},
        {"month": 6, "day": 6, "name": "BET Awards", "category": "entertainment", "relevance": "Black entertainment peak, red carpet street style, culture on display"},
        {"month": 6, "day": 7, "name": "Lil Baby Birthday", "category": "hip-hop", "relevance": "My Turn era, Atlanta trap king, street to success story, 4PF"},
        {"month": 6, "day": 7, "name": "Prince Death Anniversary (2016)", "category": "music", "relevance": "Purple Rain legend, Minneapolis genius, fashion icon, RIP"},
        {"month": 6, "day": 13, "name": "Tupac 'All Eyez On Me' Anniversary (1996)", "category": "album", "relevance": "Double album CLASSIC, Death Row peak, Thug Life manifesto, West Coast bible"},
        {"month": 6, "day": 16, "name": "2Pac Death Anniversary", "category": "hip-hop", "relevance": "September 13, 1996 - West Coast mourns, conspiracy lives on, All Eyez On Me forever"},
        {"month": 6, "day": 18, "name": "XXXTentacion Death Anniversary (2018)", "category": "hip-hop", "relevance": "SoundCloud pioneer, emo rap, Gen Z mourning, Florida legend, LLJ"},
        {"month": 6, "day": 19, "name": "Juneteenth", "category": "cultural", "relevance": "Freedom Day - Black liberation, Texas roots, independence celebration"},
        {"month": 6, "day": 21, "name": "Father's Day", "category": "lifestyle", "relevance": "OG appreciation, generational codes, dads who hustled"},
        {"month": 6, "day": 25, "name": "Kanye West 'Late Registration' Anniversary (2005)", "category": "album", "relevance": "Preppy meets street, polo bear era, college dropout sequel, strings and samples"},
        {"month": 6, "day": 27, "name": "XXXTentacion Death Anniversary", "category": "hip-hop", "relevance": "Jahseh Onfroy, SoundCloud era icon, emo rap pioneer, Gen Z heartbreak"},
        
        # ═══════════════════════════════════════════════════════════
        # JULY - INDEPENDENCE & SUMMER PEAK
        # ═══════════════════════════════════════════════════════════
        {"month": 7, "day": 4, "name": "Independence Day", "category": "culture", "relevance": "Red/white/blue colorways, American flags everywhere, BBQs and fireworks"},
        {"month": 7, "day": 6, "name": "50 Cent Birthday", "category": "hip-hop", "relevance": "G-Unit empire builder, Get Rich or Die Tryin', entrepreneur mogul, Queens legend"},
        {"month": 7, "day": 8, "name": "Mac Miller Birthday", "category": "hip-hop", "relevance": "Swimming aesthetic, artistic authenticity, Pittsburgh hero, RIP legend"},
        {"month": 7, "day": 18, "name": "Jay-Z 'Reasonable Doubt' Anniversary (1996)", "category": "album", "relevance": "Debut CLASSIC, Roc-A-Fella birth, Brooklyn hustler, Marcy Projects to billionaire"},
        {"month": 7, "day": 21, "name": "Rolling Loud Miami", "category": "festival", "relevance": "Hip-hop festival PEAK, rage culture, mosh pit energy, Miami heat"},
        {"month": 7, "day": 28, "name": "Lil Wayne 'Tha Carter III' Anniversary (2008)", "category": "album", "relevance": "Skateboard Wayne era, Trukfit incoming, A Milli, Lollipop, New Orleans king"},
        
        # ═══════════════════════════════════════════════════════════
        # AUGUST - BACK TO SCHOOL & HIP-HOP BIRTHDAY
        # ═══════════════════════════════════════════════════════════
        {"month": 8, "day": 4, "name": "Megan Thee Stallion Birthday", "category": "hip-hop", "relevance": "Hot Girl Summer CREATOR, female rap power, Houston hottie, knee megan knee"},
        {"month": 8, "day": 11, "name": "Hip-Hop Birthday (August 11, 1973)", "category": "hip-hop", "relevance": "1520 Sedgwick Ave Bronx - DJ Kool Herc - THE CULTURE WAS BORN"},
        {"month": 8, "day": 11, "name": "Kanye West 'The College Dropout' Anniversary (2004)", "category": "album", "relevance": "Changed the GAME, polo bear aesthetic, backpack rap goes mainstream, through the wire"},
        {"month": 8, "day": 15, "name": "Back to School Season", "category": "culture", "relevance": "MAJOR buying period - fresh fits for new semester, campus flex"},
        {"month": 8, "day": 25, "name": "Aaliyah Death Anniversary (2001)", "category": "culture", "relevance": "Timberland collabs, tomboy chic pioneer, R&B fashion icon, one in a million"},
        {"month": 8, "day": 25, "name": "N.W.A 'Straight Outta Compton' Anniversary (1988)", "category": "album", "relevance": "Gangsta rap INVENTED, Raiders gear, Compton pride, Fuck Tha Police, changed everything"},
        {"month": 8, "day": 25, "name": "MTV VMAs", "category": "entertainment", "relevance": "Music video culture, viral moments, Kanye interrupts Taylor, iconic fashion"},
        
        # ═══════════════════════════════════════════════════════════
        # SEPTEMBER - FALL RESET & FASHION WEEK
        # ═══════════════════════════════════════════════════════════
        {"month": 9, "day": 4, "name": "Beyoncé Birthday", "category": "culture", "relevance": "Queen B energy, luxury meets street, Houston raised, Destiny fulfilled"},
        {"month": 9, "day": 7, "name": "Labor Day", "category": "culture", "relevance": "End of summer sales, workers' pride, hustle appreciation, last long weekend"},
        {"month": 9, "day": 8, "name": "NFL Season Kicks Off", "category": "sports", "relevance": "Jersey season BEGINS, tailgate culture, football Sundays, fantasy draft"},
        {"month": 9, "day": 8, "name": "New York Fashion Week", "category": "fashion", "relevance": "Streetwear runway shows, brands debut, runway to streets pipeline, NYFW energy"},
        {"month": 9, "day": 11, "name": "Jay-Z 'The Blueprint' Anniversary (2001)", "category": "album", "relevance": "Released ON 9/11, instant classic, Rocawear peak, Roc-A-Fella dynasty"},
        {"month": 9, "day": 13, "name": "Tupac Death Anniversary (Sept 13, 1996)", "category": "hip-hop", "relevance": "Makaveli conspiracy theories, West Coast icon, 7 Day Theory, legend never dies"},
        {"month": 9, "day": 13, "name": "Lil Wayne 'Tha Carter II' Anniversary (2005)", "category": "album", "relevance": "Fireman era, mixtape Wayne rising, Cash Money peak"},
        {"month": 9, "day": 24, "name": "DMX 'It's Dark and Hell Is Hot' Anniversary (1998)", "category": "album", "relevance": "Ruff Ryders anthem, raw energy, Timbs and bandanas, Yonkers legend"},
        {"month": 9, "day": 25, "name": "Pharrell Birthday", "category": "culture", "relevance": "BBC/Ice Cream founder, Nigo collabs, Neptunes producer king, Virginia genius"},
        {"month": 9, "day": 26, "name": "Lil Wayne Birthday", "category": "hip-hop", "relevance": "Weezy F Baby, Trukfit founder, skateboard culture crossover, New Orleans god"},
        
        # ═══════════════════════════════════════════════════════════
        # OCTOBER - SPOOKY SEASON & NBA TIPS OFF
        # ═══════════════════════════════════════════════════════════
        {"month": 10, "day": 1, "name": "NBA Season Tips Off", "category": "sports", "relevance": "Basketball returns, sneaker release season RAMPS UP, courtside fits"},
        {"month": 10, "day": 3, "name": "Mean Girls Day", "category": "pop-culture", "relevance": "On Wednesdays we wear pink - meme culture, Gen Z nostalgia"},
        {"month": 10, "day": 8, "name": "Bella Hadid Birthday", "category": "culture", "relevance": "Model off-duty style, streetwear tastemaker, Palestinian pride"},
        {"month": 10, "day": 17, "name": "Eminem Birthday", "category": "hip-hop", "relevance": "8 Mile grit, Detroit underdog, Slim Shady, white tee culture, battle rap king"},
        {"month": 10, "day": 21, "name": "21 Savage Birthday", "category": "hip-hop", "relevance": "Zone 6 Atlanta, knife emoji aesthetic, trap culture, British twist"},
        {"month": 10, "day": 22, "name": "A$AP Rocky 'LONG.LIVE.A$AP' Anniversary (2013)", "category": "album", "relevance": "A$AP Mob takeover, Harlem renaissance, high fashion streetwear, Pretty Flacko"},
        {"month": 10, "day": 24, "name": "Drake Birthday", "category": "hip-hop", "relevance": "OVO owl empire, Toronto takeover, NOCTA Nike line, champagne papi"},
        {"month": 10, "day": 31, "name": "Halloween", "category": "culture", "relevance": "Dark aesthetics peak, costume culture, spooky limited drops, orange and black"},
        {"month": 10, "day": 31, "name": "Future 'DS2' Anniversary (2015)", "category": "album", "relevance": "Trap god coronation, Atlanta sound defined, lean culture, Freebandz"},
        
        # ═══════════════════════════════════════════════════════════
        # NOVEMBER - HOLIDAY PREP & BLACK FRIDAY CHAOS
        # ═══════════════════════════════════════════════════════════
        {"month": 11, "day": 1, "name": "Día de los Muertos", "category": "latino-culture", "relevance": "Skull graphics, Mexican heritage celebration, remembrance art, marigolds"},
        {"month": 11, "day": 3, "name": "Kendrick Lamar Birthday", "category": "hip-hop", "relevance": "TDE king, Compton storyteller, pgLang founder, Pulitzer Prize, GOAT debate"},
        {"month": 11, "day": 8, "name": "SZA Birthday", "category": "music", "relevance": "R&B queen, TDE, vulnerable authentic style, SOS album"},
        {"month": 11, "day": 9, "name": "Wu-Tang Clan '36 Chambers' Anniversary (1993)", "category": "album", "relevance": "Staten Island warriors unleashed, Shaolin style, martial arts aesthetic, LEGENDARY"},
        {"month": 11, "day": 11, "name": "Veterans Day", "category": "culture", "relevance": "Camo culture, military aesthetics, MA-1 bomber jackets, respect the troops"},
        {"month": 11, "day": 12, "name": "Kanye West 'MBDTF' Anniversary (2010)", "category": "album", "relevance": "My Beautiful Dark Twisted Fantasy - MASTERPIECE, high fashion era, G.O.O.D Music peak"},
        {"month": 11, "day": 15, "name": "50 Cent 'Get Rich or Die Tryin' Anniversary (2003)", "category": "album", "relevance": "G-Unit empire launched, bulletproof vest icon, In Da Club, Shady/Aftermath"},
        {"month": 11, "day": 19, "name": "Jordan 11 Season Begins", "category": "streetwear", "relevance": "Holiday 11s tradition - Concords, Space Jams, Breds - BIGGEST sneaker moment of year"},
        {"month": 11, "day": 24, "name": "Black Friday", "category": "retail", "relevance": "BIGGEST drop day of year, camp out culture, ABSOLUTE CHAOS, retail warfare"},
        {"month": 11, "day": 27, "name": "Cyber Monday", "category": "retail", "relevance": "Online cop wars, bot culture wars, digital hustle, refresh refresh refresh"},
        {"month": 11, "day": 30, "name": "Juice WRLD Birthday", "category": "hip-hop", "relevance": "999 forever, emo rap pioneer, SoundCloud generation, Chicago legend"},
        
        # ═══════════════════════════════════════════════════════════
        # DECEMBER - HOLIDAY SEASON & YEAR END
        # ═══════════════════════════════════════════════════════════
        {"month": 12, "day": 4, "name": "Jay-Z Birthday", "category": "hip-hop", "relevance": "Hov the GOAT, Roc-A-Fella dynasty, Rocawear founder, Brooklyn to billionaire blueprint"},
        {"month": 12, "day": 5, "name": "Offset Birthday", "category": "hip-hop", "relevance": "Migos architect, luxury streetwear obsessed, Atlanta culture, married Cardi"},
        {"month": 12, "day": 8, "name": "Juice WRLD Death Anniversary (2019)", "category": "hip-hop", "relevance": "Legends Never Die, Gen Z mourning rituals, 999 forever, Chicago remembers"},
        {"month": 12, "day": 15, "name": "Dr. Dre 'The Chronic' Anniversary (1992)", "category": "album", "relevance": "G-Funk CREATED here, West Coast takeover, Death Row dynasty begins, Compton king crowned"},
        {"month": 12, "day": 18, "name": "DMX Birthday", "category": "hip-hop", "relevance": "Ruff Ryders legend, raw power personified, Timbs and camo uniform, Yonkers forever"},
        {"month": 12, "day": 18, "name": "Travis Scott 'Rodeo' Anniversary (2015)", "category": "album", "relevance": "Cactus Jack BORN, rage culture defined, Nike collabs incoming, Houston to Astroworld"},
        {"month": 12, "day": 25, "name": "Christmas", "category": "culture", "relevance": "Gift season PEAK, NBA Christmas games tradition, holiday Jordan 11s, family flex"},
        {"month": 12, "day": 26, "name": "Kwanzaa Begins", "category": "cultural", "relevance": "Black unity, seven principles, African heritage celebration, community over commerce"},
        {"month": 12, "day": 31, "name": "New Year's Eve", "category": "culture", "relevance": "Countdown fits, NYE drip, year-end flex, resolutions incoming"},
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
    
    prompt = f"""You are a streetwear and hip-hop culture marketing expert for Crooks & Castles, a heritage streetwear brand born in 2002.

Campaign: {name}
Description: {description}
Target Audience: {target_audience or "Urban youth 18-34, hip-hop fans, streetwear collectors - The Rebel, Ruler, and Creator archetypes"}
Channels: {', '.join(channels) if channels else "Instagram, TikTok, Email"}

CROOKS & CASTLES DNA:
- Heritage: 2002 LA streetwear OGs, not a fast fashion clone
- Community: Crew culture from streets to castles
- Code: Loyalty, legacy, authenticity - earned not bought
- Aesthetic: High-contrast, urban grit meets polish, never soft

TARGET CUSTOMER PROFILE:
- Ages 18-34, urban hubs (NYC, LA, London, Paris, Tokyo)
- Status seekers who want credibility badges, not mass hype
- Cultural architects: Hip-hop/skate/gaming shapes their worldview
- Digital rebels: Instagram/TikTok natives but skeptical of clout-chasing
- Already own Supreme, BAPE, Purple Brand, Kith - want heritage that feels EARNED
- Shop StockX, Grailed, TikTok Shop - resale validation matters
- Badge-driven: Flex the Castle/Medusa/Chains because icon = street code
- Crew-oriented: Loyalty to their circle, rep brand as belonging marker

THREE CUSTOMER ARCHETYPES:
1. THE REBEL - Skate kids, hustlers, independent thinkers. Anti-institution, pro-crew.
2. THE RULER - Aspiring bosses, brand-builders, entrepreneurs. Respect discipline × disruption.
3. THE CREATOR - Designers, musicians, gamers. Remix culture into their identity.

WHAT THEY'RE REALLY BUYING:
- Heritage: A brand born in 2002, not a fast-fashion imposter
- Community: A crew that spans streets to castles
- Code: A badge money can't buy - loyalty, legacy, authenticity
- Aesthetic: High-contrast, urban, grit × polish (never soft)

Generate campaign strategy that CONVERTS these customers:

1. THREE content concepts that resonate with Rebels, Rulers, and Creators
   - Make it VISUAL, make it STORY-driven
   - Reference street codes they'll recognize
   - Show don't tell the heritage

2. THREE social media tactics (Instagram/TikTok) 
   - Feel earned, never corporate
   - Leverage cultural moments from our calendar
   - Build FOMO without being obvious

3. KEY MESSAGING pillars
   - Honor street codes
   - NO clout-chasing language
   - Speak to loyalty, legacy, crew

4. HASHTAG strategy that signals credibility
   - Mix of branded and culture tags
   - Nothing that screams "marketing"

Keep it 100. Real street talk. No corporate BS. This is for ONE person (the founder) to execute with their team. Make it ACTIONABLE and INSPIRED."""

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a streetwear marketing expert who deeply understands hip-hop culture, sneaker culture, and authentic street codes. You speak the language of the streets while driving business results. You inspire solo founders and small teams to create legendary campaigns."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.75
    )
    
    suggestions_text = response.choices[0].message.content
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suggestions": suggestions_text,
        "model": "gpt-4"
    }
