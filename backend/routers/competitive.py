from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timezone
from typing import Optional
import json
import csv
from io import StringIO
import os
from backend.database import get_db
from backend.models import CompetitorIntel
from backend.ai_processor import AIProcessor

router = APIRouter()
ai_processor = AIProcessor()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "competitive")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def parse_jsonl(content: str) -> list:
    """Parse JSONL format (one JSON object per line)"""
    lines = content.strip().split('\n')
    data = []
    for line in lines:
        if line.strip():
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data

def parse_csv(content: str) -> list:
    """Parse CSV format"""
    reader = csv.DictReader(StringIO(content))
    return list(reader)

def extract_competitor_name_from_data(data: dict, filename: str) -> str:
    """Extract competitor name from data object or filename"""
    # Try common field names
    for field in ['competitor', 'brand', 'account_name', 'username', 'company', 'competitor_name']:
        if field in data and data[field]:
            return str(data[field])
    
    # Extract from filename
    name = filename.replace('.jsonl', '').replace('.json', '').replace('.csv', '').replace('.txt', '')
    name = name.replace('_', ' ').replace('-', ' ')
    
    for prefix in ['instagram', 'scrape', 'data', 'competitor', 'intel']:
        name = name.replace(prefix, '').strip()
    
    return name.title() if name else 'Unknown Competitor'

@router.post("/upload")
async def upload_competitive_intel(
    file: UploadFile = File(...),
    competitor_name: Optional[str] = Form(None),
    category: str = Form('social_media'),
    source: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload competitive intelligence file (JSONL, JSON, CSV)"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read file content
    content = await file.read()
    raw_content = content.decode('utf-8')
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Parse based on file type
    parsed_data = None
    if file.filename.endswith('.jsonl'):
        parsed_data = parse_jsonl(raw_content)
    elif file.filename.endswith('.json'):
        try:
            parsed_data = json.loads(raw_content)
            if not isinstance(parsed_data, list):
                parsed_data = [parsed_data]
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
    elif file.filename.endswith('.csv'):
        parsed_data = parse_csv(raw_content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .jsonl, .json, or .csv")
    
    # Determine competitor name
    if not competitor_name:
        if parsed_data and len(parsed_data) > 0:
            competitor_name = extract_competitor_name_from_data(parsed_data[0], file.filename)
        else:
            competitor_name = extract_competitor_name_from_data({}, file.filename)
    
    # Generate AI summary and insights
    summary = ai_processor.generate_summary(raw_content)
    insights = ai_processor.extract_insights(raw_content)
    
    # Determine source
    if not source:
        if 'instagram' in file.filename.lower():
            source = 'instagram'
        elif 'facebook' in file.filename.lower():
            source = 'facebook'
        elif 'tiktok' in file.filename.lower():
            source = 'tiktok'
        else:
            source = 'manual_upload'
    
    # Create competitive intel entry
    intel_entry = CompetitorIntel(
        competitor_name=competitor_name,
        category=category,
        data_type=source,
        content=raw_content,
        ai_analysis=summary,
        tags=insights if isinstance(insights, list) else [],
        source_url=file_path,
        priority='medium',
        sentiment='neutral'
    )
    
    db.add(intel_entry)
    db.commit()
    db.refresh(intel_entry)
    
    return {
        "success": True,
        "message": "Competitive intelligence uploaded successfully",
        "id": intel_entry.id,
        "competitor_name": competitor_name,
        "summary": summary,
        "insights": insights,
        "records_parsed": len(parsed_data) if parsed_data else 0
    }

@router.post("/manual")
def add_competitive_intel(
    competitor_name: str,
    category: str,
    source: str,
    content: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Manually add competitive intelligence entry"""
    
    summary = ai_processor.generate_summary(content)
    insights = ai_processor.extract_insights(content)
    
    intel = CompetitorIntel(
        competitor_name=competitor_name,
        category=category,
        data_type=source,
        content=content,
        ai_analysis=summary,
        tags=insights if isinstance(insights, list) else [],
        priority='medium',
        sentiment='neutral'
    )
    
    db.add(intel)
    db.commit()
    db.refresh(intel)
    
    return {
        "success": True,
        "message": "Competitive intel added successfully",
        "id": intel.id,
        "summary": summary,
        "insights": insights
    }

@router.get("/intel")
def get_competitive_intel(
    limit: int = 50,
    competitor: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get competitive intelligence entries"""
    
    query = db.query(CompetitorIntel)
    
    if competitor:
        query = query.filter(CompetitorIntel.competitor_name == competitor)
    
    if category:
        query = query.filter(CompetitorIntel.category == category)
    
    intel = query.order_by(desc(CompetitorIntel.created_at)).limit(limit).all()
    
    return {
        "intel": [
            {
                "id": i.id,
                "competitor_name": i.competitor_name,
                "category": i.category,
                "source": i.data_type,
                "summary": i.ai_analysis,
                "key_insights": i.tags if isinstance(i.tags, list) else [],
                "created_at": i.created_at.isoformat()
            }
            for i in intel
        ],
        "total": len(intel)
    }

@router.get("/intel/{intel_id}")
def get_intel_detail(intel_id: int, db: Session = Depends(get_db)):
    """Get detailed competitive intel entry"""
    
    intel = db.query(CompetitorIntel).filter(CompetitorIntel.id == intel_id).first()
    
    if not intel:
        raise HTTPException(status_code=404, detail="Competitive intel entry not found")
    
    return {
        "id": intel.id,
        "competitor_name": intel.competitor_name,
        "category": intel.category,
        "source": intel.data_type,
        "content": intel.content,
        "summary": intel.ai_analysis,
        "key_insights": intel.tags if isinstance(intel.tags, list) else [],
        "created_at": intel.created_at.isoformat()
    }

@router.delete("/intel/{intel_id}")
def delete_competitive_intel(intel_id: int, db: Session = Depends(get_db)):
    """Delete competitive intel entry"""
    
    intel = db.query(CompetitorIntel).filter(CompetitorIntel.id == intel_id).first()
    
    if not intel:
        raise HTTPException(status_code=404, detail="Competitive intel entry not found")
    
    # Delete file if exists
    if intel.source_url and os.path.exists(intel.source_url):
        os.remove(intel.source_url)
    
    db.delete(intel)
    db.commit()
    
    return {"success": True, "message": "Competitive intel entry deleted"}

@router.get("/competitors/list")
def get_competitors_list(db: Session = Depends(get_db)):
    """Get list of all tracked competitors with intel counts"""
    
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
