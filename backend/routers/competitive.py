from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import Optional

from ..database import get_db
from ..models import CompetitorIntel

router = APIRouter()


@router.get("/")
def get_competitive_intel(
    competitor: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get competitive intelligence entries"""
    
    query = db.query(CompetitorIntel)
    
    if competitor:
        query = query.filter(CompetitorIntel.competitor_name.ilike(f"%{competitor}%"))
    
    if category:
        query = query.filter(CompetitorIntel.category == category)
    
    if sentiment:
        query = query.filter(CompetitorIntel.sentiment == sentiment)
    
    total = query.count()
    intel = query.order_by(desc(CompetitorIntel.created_at)).limit(limit).offset(offset).all()
    
    return {
        "competitive_intel": [
            {
                "id": i.id,
                "competitor_name": i.competitor_name,
                "category": i.category,
                "data_type": i.data_type,
                "content": i.content[:200] + "..." if i.content and len(i.content) > 200 else i.content,
                "source_url": i.source_url,
                "sentiment": i.sentiment,
                "priority": i.priority,
                "tags": i.tags,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in intel
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/")
def create_competitive_intel(
    competitor_name: str,
    content: str,
    category: Optional[str] = None,
    data_type: Optional[str] = None,
    source_url: Optional[str] = None,
    sentiment: Optional[str] = "neutral",
    priority: Optional[str] = "medium",
    tags: Optional[list] = None,
    db: Session = Depends(get_db)
):
    """Create a new competitive intelligence entry"""
    
    intel = CompetitorIntel(
        competitor_name=competitor_name,
        category=category,
        data_type=data_type,
        content=content,
        source_url=source_url,
        sentiment=sentiment,
        priority=priority,
        tags=tags
    )
    
    db.add(intel)
    db.commit()
    db.refresh(intel)
    
    return {
        "id": intel.id,
        "competitor_name": intel.competitor_name,
        "sentiment": intel.sentiment,
        "created_at": intel.created_at.isoformat()
    }


@router.get("/{intel_id}")
def get_competitive_intel_detail(intel_id: int, db: Session = Depends(get_db)):
    """Get detailed competitive intelligence entry"""
    
    intel = db.query(CompetitorIntel).filter(CompetitorIntel.id == intel_id).first()
    
    if not intel:
        raise HTTPException(404, "Competitive intel entry not found")
    
    return {
        "id": intel.id,
        "competitor_name": intel.competitor_name,
        "category": intel.category,
        "data_type": intel.data_type,
        "content": intel.content,
        "source_url": intel.source_url,
        "sentiment": intel.sentiment,
        "ai_analysis": intel.ai_analysis,
        "priority": intel.priority,
        "tags": intel.tags,
        "created_at": intel.created_at.isoformat(),
        "updated_at": intel.updated_at.isoformat()
    }


@router.put("/{intel_id}")
def update_competitive_intel(
    intel_id: int,
    competitor_name: Optional[str] = None,
    category: Optional[str] = None,
    content: Optional[str] = None,
    sentiment: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list] = None,
    db: Session = Depends(get_db)
):
    """Update competitive intelligence entry"""
    
    intel = db.query(CompetitorIntel).filter(CompetitorIntel.id == intel_id).first()
    
    if not intel:
        raise HTTPException(404, "Competitive intel entry not found")
    
    if competitor_name:
        intel.competitor_name = competitor_name
    if category:
        intel.category = category
    if content:
        intel.content = content
    if sentiment:
        intel.sentiment = sentiment
    if priority:
        intel.priority = priority
    if tags is not None:
        intel.tags = tags
    
    intel.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(intel)
    
    return {"success": True, "intel_id": intel.id}


@router.delete("/{intel_id}")
def delete_competitive_intel(intel_id: int, db: Session = Depends(get_db)):
    """Delete competitive intelligence entry"""
    
    intel = db.query(CompetitorIntel).filter(CompetitorIntel.id == intel_id).first()
    
    if not intel:
        raise HTTPException(404, "Competitive intel entry not found")
    
    db.delete(intel)
    db.commit()
    
    return {"success": True, "message": "Competitive intel entry deleted"}


@router.get("/competitors/list")
def get_competitors_list(db: Session = Depends(get_db)):
    """Get list of all tracked competitors"""
    
    from sqlalchemy import func
    
    competitors = db.query(
        CompetitorIntel.competitor_name,
        func.count(CompetitorIntel.id).label('intel_count')
    ).group_by(CompetitorIntel.competitor_name).all()
    
    return {
        "competitors": [
            {
                "name": c.competitor_name,
                "intel_count": c.intel_count
            }
            for c in competitors
        ]
    }
