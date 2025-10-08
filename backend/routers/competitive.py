from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import Optional
import json
import csv
from io import StringIO

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


@router.post("/upload")
async def upload_competitive_intel(
    file: UploadFile = File(...),
    competitor_name: str = Form(...),
    category: str = Form(None),
    tags: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload competitive intelligence file (CSV, JSON, JSONL, TXT)"""
    
    try:
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        print(f"[Competitive] Received file: {file.filename} ({file_extension})")
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        created_count = 0
        
        # Handle JSONL/JSON files
        if file_extension in ['jsonl', 'json']:
            text_content = content.decode('utf-8')
            entries = []
            
            # Try parsing as JSONL
            for line in text_content.strip().split('\n'):
                if line.strip():
                    try:
                        entries.append(json.loads(line.strip()))
                    except:
                        continue
            
            if not entries:
                # Try as single JSON
                try:
                    entries = json.loads(text_content)
                    if not isinstance(entries, list):
                        entries = [entries]
                except:
                    raise HTTPException(400, "Could not parse JSON/JSONL")
            
            print(f"[Competitive] Found {len(entries)} entries")
            
            # Process each entry
            for idx, entry in enumerate(entries, 1):
                try:
                    # Extract content
                    content_parts = []
                    url = entry.get('url', '')
                    
                    if url:
                        content_parts.append(f"URL: {url}")
                    
                    for key in ['text', 'content', 'description', 'caption']:
                        if entry.get(key):
                            content_parts.append(str(entry[key]))
                    
                    entry_content = "\n\n".join(content_parts)
                    
                    if not entry_content.strip():
                        continue
                    
                    # Create competitor intel entry
                    intel = CompetitorIntel(
                        competitor_name=competitor_name,
                        category=category or "social_media",
                        data_type="social_post" if url else "data",
                        content=entry_content[:10000],
                        source_url=url or None,
                        sentiment="neutral",
                        ai_analysis=None,
                        priority="medium",
                        tags=tag_list + ["file_upload"]
                    )
                    
                    db.add(intel)
                    created_count += 1
                    
                except Exception as e:
                    print(f"[Competitive] Entry {idx} error: {e}")
                    continue
            
            db.commit()
            
            return {
                "success": True,
                "message": f"✅ Imported {created_count} competitive intel entries",
                "created": created_count
            }
        
        # Handle CSV files
        elif file_extension == 'csv':
            text_content = content.decode('utf-8')
            csv_file = StringIO(text_content)
            reader = csv.DictReader(csv_file)
            
            for idx, row in enumerate(reader, 1):
                try:
                    # Try to extract content from common CSV columns
                    content_text = (
                        row.get('content') or 
                        row.get('text') or 
                        row.get('description') or 
                        row.get('caption') or 
                        ""
                    )
                    
                    url = row.get('url') or row.get('link') or row.get('source_url')
                    
                    if not content_text.strip():
                        continue
                    
                    intel = CompetitorIntel(
                        competitor_name=competitor_name,
                        category=category or "data",
                        data_type="csv_import",
                        content=content_text[:10000],
                        source_url=url,
                        sentiment="neutral",
                        priority="medium",
                        tags=tag_list + ["csv_upload"]
                    )
                    
                    db.add(intel)
                    created_count += 1
                    
                except Exception as e:
                    print(f"[Competitive] CSV row {idx} error: {e}")
                    continue
            
            db.commit()
            
            return {
                "success": True,
                "message": f"✅ Imported {created_count} entries from CSV",
                "created": created_count
            }
        
        # Handle TXT files
        elif file_extension in ['txt', 'md']:
            text_content = content.decode('utf-8')
            
            intel = CompetitorIntel(
                competitor_name=competitor_name,
                category=category or "document",
                data_type=file_extension,
                content=text_content[:10000],
                source_url=None,
                sentiment="neutral",
                priority="medium",
                tags=tag_list + ["file_upload"]
            )
            
            db.add(intel)
            db.commit()
            
            return {
                "success": True,
                "message": f"✅ Imported competitive intel document",
                "created": 1
            }
        
        else:
            raise HTTPException(400, f"Unsupported file type: {file_extension}. Use JSON, JSONL, CSV, or TXT")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Upload failed: {str(e)}")


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
    """Create a new competitive intelligence entry manually"""
    
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
    """Get list of all tracked competitors with intel counts"""
    
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
        ],
        "total_competitors": len(competitors)
    }


@router.get("/summary/by-competitor")
def get_competitive_summary(db: Session = Depends(get_db)):
    """Get competitive intelligence summary grouped by competitor"""
    
    from sqlalchemy import func
    
    summary = db.query(
        CompetitorIntel.competitor_name,
        CompetitorIntel.category,
        func.count(CompetitorIntel.id).label('count'),
        func.max(CompetitorIntel.created_at).label('latest_intel')
    ).group_by(
        CompetitorIntel.competitor_name,
        CompetitorIntel.category
    ).all()
    
    # Group by competitor
    competitors_data = {}
    for row in summary:
        if row.competitor_name not in competitors_data:
            competitors_data[row.competitor_name] = {
                "name": row.competitor_name,
                "total_intel": 0,
                "categories": {},
                "latest_update": None
            }
        
        competitors_data[row.competitor_name]["total_intel"] += row.count
        competitors_data[row.competitor_name]["categories"][row.category] = row.count
        
        if not competitors_data[row.competitor_name]["latest_update"] or row.latest_intel > competitors_data[row.competitor_name]["latest_update"]:
            competitors_data[row.competitor_name]["latest_update"] = row.latest_intel.isoformat() if row.latest_intel else None
    
    return {
        "competitors": list(competitors_data.values()),
        "total_competitors": len(competitors_data),
        "total_intel_entries": sum(c["total_intel"] for c in competitors_data.values())
    }
