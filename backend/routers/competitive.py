from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import json

from ..database import get_db
from ..models import CompetitiveIntel

router = APIRouter()

# Competitor brands organized by threat level
COMPETITOR_BRANDS = {
    "high_threat": [
        "Hellstar",
        "Memory Lane",
        "Smoke Rise",
        "Reason Clothing",
        "Purple Brand",
        "Amiri"
    ],
    "medium_threat": [
        "Aimé Leon Dore (ALD)",
        "Kith",
        "Supreme",
        "Fear of God",
        "Off-White",
        "BAPE",
        "Palace",
        "Godspeed"
    ],
    "low_threat": [
        "LRG",
        "Ecko Unlimited",
        "Sean John",
        "Rocawear",
        "Von Dutch",
        "Ed Hardy",
        "Affliction"
    ]
}

# Flat list of all competitors
ALL_COMPETITORS = (
    COMPETITOR_BRANDS["high_threat"] + 
    COMPETITOR_BRANDS["medium_threat"] + 
    COMPETITOR_BRANDS["low_threat"]
)


@router.get("/brands")
def get_competitor_brands():
    """Get list of tracked competitor brands organized by threat level"""
    return {
        "brands": COMPETITOR_BRANDS,
        "all_brands": ALL_COMPETITORS,
        "total": len(ALL_COMPETITORS),
        "threat_levels": {
            "high": len(COMPETITOR_BRANDS["high_threat"]),
            "medium": len(COMPETITOR_BRANDS["medium_threat"]),
            "low": len(COMPETITOR_BRANDS["low_threat"])
        }
    }


@router.get("/dashboard")
def get_competitive_dashboard(
    days: int = 30,
    threat_level: Optional[str] = None,  # high_threat, medium_threat, low_threat
    db: Session = Depends(get_db)
):
    """Get competitive intelligence dashboard overview"""
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    # Filter by threat level if specified
    if threat_level and threat_level in COMPETITOR_BRANDS:
        competitor_filter = COMPETITOR_BRANDS[threat_level]
        intel = db.query(CompetitiveIntel).filter(
            and_(
                CompetitiveIntel.collected_at >= start_date,
                CompetitiveIntel.competitor.in_(competitor_filter)
            )
        ).all()
    else:
        # Get all competitive data in period
        intel = db.query(CompetitiveIntel).filter(
            CompetitiveIntel.collected_at >= start_date
        ).all()
    
    # Aggregate by competitor
    by_competitor = {}
    for item in intel:
        comp = item.competitor
        if comp not in by_competitor:
            # Determine threat level
            threat = "unknown"
            if comp in COMPETITOR_BRANDS["high_threat"]:
                threat = "high"
            elif comp in COMPETITOR_BRANDS["medium_threat"]:
                threat = "medium"
            elif comp in COMPETITOR_BRANDS["low_threat"]:
                threat = "low"
            
            by_competitor[comp] = {
                "competitor": comp,
                "threat_level": threat,
                "total_posts": 0,
                "avg_engagement": 0,
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
                "sources": set(),
                "latest_activity": None
            }
        
        by_competitor[comp]["total_posts"] += 1
        by_competitor[comp]["sources"].add(item.data_source)
        
        if item.engagement_score:
            by_competitor[comp]["avg_engagement"] += item.engagement_score
        
        if item.sentiment:
            sentiment = item.sentiment.lower()
            if sentiment in by_competitor[comp]["sentiment_breakdown"]:
                by_competitor[comp]["sentiment_breakdown"][sentiment] += 1
        
        if not by_competitor[comp]["latest_activity"] or item.collected_at > by_competitor[comp]["latest_activity"]:
            by_competitor[comp]["latest_activity"] = item.collected_at
    
    # Calculate averages
    competitors_list = []
    for comp_data in by_competitor.values():
        if comp_data["total_posts"] > 0:
            comp_data["avg_engagement"] = round(comp_data["avg_engagement"] / comp_data["total_posts"], 2)
        comp_data["sources"] = list(comp_data["sources"])
        comp_data["latest_activity"] = comp_data["latest_activity"].isoformat() if comp_data["latest_activity"] else None
        competitors_list.append(comp_data)
    
    # Sort by threat level first, then by total posts
    threat_order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    competitors_list.sort(key=lambda x: (threat_order.get(x["threat_level"], 3), -x["total_posts"]))
    
    return {
        "period_days": days,
        "total_data_points": len(intel),
        "competitors_tracked": len(by_competitor),
        "competitors": competitors_list,
        "available_brands": COMPETITOR_BRANDS
    }


@router.get("/data")
def get_competitive_data(
    competitor: Optional[str] = None,
    data_source: Optional[str] = None,
    threat_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get competitive intelligence data with filters"""
    
    query = db.query(CompetitiveIntel)
    
    if competitor:
        query = query.filter(CompetitiveIntel.competitor == competitor)
    
    if data_source:
        query = query.filter(CompetitiveIntel.data_source == data_source)
    
    if threat_level and threat_level in COMPETITOR_BRANDS:
        competitor_filter = COMPETITOR_BRANDS[threat_level]
        query = query.filter(CompetitiveIntel.competitor.in_(competitor_filter))
    
    total = query.count()
    
    intel = query.order_by(desc(CompetitiveIntel.collected_at)).limit(limit).offset(offset).all()
    
    return {
        "data": [
            {
                "id": item.id,
                "competitor": item.competitor,
                "data_source": item.data_source,
                "content_type": item.content_type,
                "raw_data": item.raw_data,
                "analysis": item.analysis,
                "sentiment": item.sentiment,
                "engagement_score": item.engagement_score,
                "collected_at": item.collected_at.isoformat() if item.collected_at else None
            }
            for item in intel
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/import-json")
async def import_competitive_json(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import competitive intelligence from JSON (Apify exports)"""
    
    if not file.filename.endswith('.json'):
        raise HTTPException(400, "File must be a JSON")
    
    try:
        contents = await file.read()
        data = json.loads(contents)
        
        # Handle both single object and array
        if not isinstance(data, list):
            data = [data]
        
        imported = 0
        errors = []
        
        for item in data:
            try:
                # Extract competitor info
                competitor = item.get('competitor') or item.get('brand') or item.get('username') or 'Unknown'
                data_source = item.get('source') or item.get('platform') or 'manual_import'
                content_type = item.get('type') or item.get('contentType') or 'post'
                
                # Extract engagement metrics
                engagement_score = 0
                if 'likes' in item:
                    engagement_score += item.get('likes', 0)
                if 'comments' in item:
                    engagement_score += item.get('comments', 0) * 2  # Comments worth 2x
                if 'shares' in item:
                    engagement_score += item.get('shares', 0) * 3  # Shares worth 3x
                if 'engagement' in item:
                    engagement_score = item.get('engagement', 0)
                
                # Basic sentiment analysis from text
                sentiment = None
                text = item.get('text') or item.get('caption') or item.get('description') or ''
                if text:
                    text_lower = text.lower()
                    positive_words = ['great', 'love', 'amazing', 'awesome', 'excellent', 'best', 'fire', '🔥']
                    negative_words = ['bad', 'terrible', 'worst', 'hate', 'disappointing']
                    
                    pos_count = sum(1 for word in positive_words if word in text_lower)
                    neg_count = sum(1 for word in negative_words if word in text_lower)
                    
                    if pos_count > neg_count:
                        sentiment = "positive"
                    elif neg_count > pos_count:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"
                
                intel_data = CompetitiveIntel(
                    competitor=competitor,
                    data_source=data_source,
                    content_type=content_type,
                    raw_data=item,
                    sentiment=sentiment,
                    engagement_score=float(engagement_score) if engagement_score else None
                )
                
                db.add(intel_data)
                imported += 1
                
            except Exception as e:
                errors.append(f"Item error: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "imported": imported,
            "errors": errors[:10] if errors else [],
            "message": f"Imported {imported} competitive intelligence data points"
        }
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON file")
    except Exception as e:
        raise HTTPException(400, f"Error importing data: {str(e)}")


@router.post("/manual-entry")
def create_manual_entry(
    competitor: str,
    data_source: str,
    content_type: str,
    raw_data: dict,
    sentiment: Optional[str] = None,
    engagement_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Manually add competitive intelligence data point"""
    
    intel = CompetitiveIntel(
        competitor=competitor,
        data_source=data_source,
        content_type=content_type,
        raw_data=raw_data,
        sentiment=sentiment,
        engagement_score=engagement_score
    )
    
    db.add(intel)
    db.commit()
    db.refresh(intel)
    
    return {
        "success": True,
        "id": intel.id,
        "message": "Competitive intelligence data added"
    }


@router.get("/competitors")
def list_competitors(db: Session = Depends(get_db)):
    """Get list of all tracked competitors with data"""
    
    competitors = db.query(
        CompetitiveIntel.competitor,
        func.count(CompetitiveIntel.id).label('data_points')
    ).group_by(CompetitiveIntel.competitor).all()
    
    return {
        "competitors": [
            {
                "name": comp,
                "data_points": count
            }
            for comp, count in competitors
        ],
        "available_brands": COMPETITOR_BRANDS,
        "all_brands": ALL_COMPETITORS
    }


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    """Get list of all data sources"""
    
    sources = db.query(
        CompetitiveIntel.data_source,
        func.count(CompetitiveIntel.id).label('data_points')
    ).group_by(CompetitiveIntel.data_source).all()
    
    return {
        "sources": [
            {
                "name": source,
                "data_points": count
            }
            for source, count in sources
        ]
    }


@router.delete("/data/{intel_id}")
def delete_intel(intel_id: int, db: Session = Depends(get_db)):
    """Delete a competitive intelligence data point"""
    
    intel = db.query(CompetitiveIntel).filter(CompetitiveIntel.id == intel_id).first()
    
    if not intel:
        raise HTTPException(404, "Data point not found")
    
    db.delete(intel)
    db.commit()
    
    return {"success": True}
