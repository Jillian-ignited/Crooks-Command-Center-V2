from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timezone, timedelta
from typing import Optional
import json
import csv
from io import StringIO
import os
import re
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

def extract_brand_from_url(url: str) -> str:
    """Extract brand name from Instagram URL"""
    if not url:
        return None
    
    # Match instagram.com/BRANDNAME/
    match = re.search(r'instagram\.com/([^/\?]+)', url)
    if match:
        username = match.group(1)
        # Filter out Instagram path segments
        if username.lower() in ['p', 'reel', 'tv', 'stories', 'explore']:
            return None
        # Clean up the username
        username = username.replace('_', ' ').replace('.', ' ').strip()
        return username.title()
    
    return None

def extract_competitor_name_from_data(data: list, filename: str) -> str:
    """Extract competitor name from Apify data or filename"""
    
    # Try to find URL in the data (Apify Instagram scrapes have this)
    if data and isinstance(data, list):
        for item in data[:5]:  # Check first few items
            if isinstance(item, dict):
                # Check for Instagram URL
                if 'url' in item and item['url'] and 'instagram.com' in str(item['url']):
                    brand = extract_brand_from_url(item['url'])
                    if brand:
                        return brand
                
                # Check for ownerUsername
                if 'ownerUsername' in item and item['ownerUsername']:
                    username = item['ownerUsername'].replace('_', ' ').replace('.', ' ').strip()
                    return username.title()
                
                # Check for displayName or name fields
                for field in ['displayName', 'name', 'username', 'accountName']:
                    if field in item and item[field]:
                        name = str(item[field]).replace('_', ' ').replace('.', ' ').strip()
                        return name.title()
    
    # Fallback to filename extraction
    name = filename
    
    # Remove file extensions
    name = re.sub(r'\.(jsonl|json|csv|txt)$', '', name, flags=re.IGNORECASE)
    
    # Remove common Apify/timestamp patterns
    # Matches patterns like: 2025-10-06, 11-58-18, 20251006, etc.
    name = re.sub(r'[-_]\d{4}[-_]\d{2}[-_]\d{2}', '', name)  # Date: 2025-10-06
    name = re.sub(r'[-_]\d{2}[-_]\d{2}[-_]\d{2}', '', name)  # Time: 11-58-18
    name = re.sub(r'[-_]\d{3,}', '', name)  # Milliseconds or long numbers
    name = re.sub(r'\d{8,}', '', name)  # Long timestamp strings
    
    # Replace separators with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Remove common prefixes/suffixes
    remove_terms = ['instagram', 'scrape', 'data', 'competitor', 'intel', 'apify', 
                    'export', 'dataset', 'posts', 'feed', 'profile', 'set', 'hashtag', 'r']
    for term in remove_terms:
        name = re.sub(r'\b' + term + r'\b', '', name, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    name = ' '.join(name.split())
    
    # If nothing left, return Unknown
    if not name or len(name) < 2:
        return 'Unknown Competitor'
    
    return name.title()

def is_own_brand(competitor_name: str) -> bool:
    """Check if the competitor name is actually our own brand"""
    if not competitor_name:
        return False
    
    own_brand_keywords = ['crooks', 'castles', 'crooks and castles', 'crooks & castles', 
                          'crooks brand', 'deliverables', 'deliverable']
    
    name_lower = competitor_name.lower()
    return any(keyword in name_lower for keyword in own_brand_keywords)

def determine_threat_level(intel_count: int) -> str:
    """Determine threat level based on intel count"""
    if intel_count >= 10:
        return 'high'
    elif intel_count >= 5:
        return 'medium'
    else:
        return 'low'

@router.post("/upload")
async def upload_competitive_intel(
    file: UploadFile = File(...),
    competitor_name: Optional[str] = Form(None),
    category: str = Form('social_media'),
    source: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload competitive intelligence file (JSONL, JSON, CSV) - ONE entry per file"""
    
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
        competitor_name = extract_competitor_name_from_data(parsed_data, file.filename)
    
    # Validate that it's not our own brand
    if is_own_brand(competitor_name):
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot add '{competitor_name}' as a competitor - this appears to be your own brand. Please rename the file or provide a competitor name."
        )
    
    # Validate competitor name is not generic/invalid
    if competitor_name in ['Unknown Competitor', 'Set', 'Hashtag', 'R'] or len(competitor_name) < 3:
        raise HTTPException(
            status_code=400,
            detail=f"Could not determine competitor name from file '{file.filename}'. Please provide a competitor name manually."
        )
    
    # Determine source
    if not source:
        if 'instagram' in file.filename.lower():
            source = 'instagram'
        elif 'facebook' in file.filename.lower():
            source = 'facebook'
        elif 'tiktok' in file.filename.lower():
            source = 'tiktok'
        else:
            source = 'apify'
    
    # Check if this competitor already has an entry - if so, update it
    existing = db.query(CompetitorIntel).filter(
        CompetitorIntel.competitor_name == competitor_name,
        CompetitorIntel.data_type == source
    ).first()
    
    # Count posts for summary
    post_count = len(parsed_data) if parsed_data else 0
    
    # Generate AI summary and insights
    summary = ai_processor.generate_summary(raw_content[:5000])  # Limit to first 5000 chars for AI
    insights = ai_processor.extract_insights(raw_content[:5000])
    
    # Add post count to summary
    summary_with_count = f"{post_count} posts analyzed. {summary}"
    
    if existing:
        # Update existing entry
        existing.content = raw_content
        existing.ai_analysis = summary_with_count
        existing.tags = insights
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        
        return {
            "success": True,
            "message": f"Updated competitive intelligence for {competitor_name}",
            "id": existing.id,
            "competitor_name": competitor_name,
            "summary": summary_with_count,
            "insights": insights,
            "records_parsed": post_count,
            "action": "updated"
        }
    else:
        # Create new intel entry - ONE per competitor/source
        intel_entry = CompetitorIntel(
            competitor_name=competitor_name,
            category=category,
            data_type=source,
            content=raw_content,
            ai_analysis=summary_with_count,
            tags=insights,
            source_url=file_path,
            priority='medium',
            sentiment='neutral'
        )
        
        db.add(intel_entry)
        db.commit()
        db.refresh(intel_entry)
        
        return {
            "success": True,
            "message": f"Competitive intelligence uploaded for {competitor_name}",
            "id": intel_entry.id,
            "competitor_name": competitor_name,
            "summary": summary_with_count,
            "insights": insights,
            "records_parsed": post_count,
            "action": "created"
        }

@router.post("/import-json")
async def import_json_competitive(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import competitive intelligence from JSON/JSONL (used by frontend)"""
    return await upload_competitive_intel(
        file=file,
        competitor_name=None,
        category='social_media',
        source=None,
        notes=None,
        db=db
    )

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
    
    # Validate not own brand
    if is_own_brand(competitor_name):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot add '{competitor_name}' as a competitor - this is your own brand."
        )
    
    summary = ai_processor.generate_summary(content)
    insights = ai_processor.extract_insights(content)
    
    intel = CompetitorIntel(
        competitor_name=competitor_name,
        category=category,
        data_type=source,
        content=content,
        ai_analysis=summary,
        tags=insights,
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
                "key_insights": i.tags if isinstance(i.tags, (list, dict)) else (json.loads(i.tags) if i.tags else []),
                "created_at": i.created_at.isoformat()
            }
            for i in intel
        ],
        "total": len(intel)
    }

@router.get("/data")
def get_competitive_data(
    limit: int = 50,
    competitor: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get competitive data - returns in format expected by frontend"""
    
    query = db.query(CompetitorIntel)
    
    if competitor:
        query = query.filter(CompetitorIntel.competitor_name == competitor)
    
    if category:
        query = query.filter(CompetitorIntel.category == category)
    
    intel = query.order_by(desc(CompetitorIntel.created_at)).limit(limit).all()
    
    # Parse post count from content
    def get_post_count(content_str):
        try:
            data = json.loads(content_str)
            if isinstance(data, list):
                return len(data)
            return 1
        except:
            return 1
    
    return {
        "data": [
            {
                "id": i.id,
                "competitor": i.competitor_name,
                "category": i.category,
                "source": i.data_type,
                "post_count": get_post_count(i.content),
                "content": i.content[:500] if i.content else "",
                "summary": i.ai_analysis,
                "insights": i.tags if isinstance(i.tags, (list, dict)) else (json.loads(i.tags) if i.tags else []),
                "created_at": i.created_at.isoformat(),
                "priority": i.priority,
                "sentiment": i.sentiment
            }
            for i in intel
        ],
        "total": len(intel)
    }

@router.get("/brands")
def get_competitive_brands(db: Session = Depends(get_db)):
    """Get list of tracked brands categorized by threat level"""
    
    # Get all competitors with their intel counts
    competitors = db.query(
        CompetitorIntel.competitor_name,
        func.count(CompetitorIntel.id).label('intel_count')
    ).group_by(CompetitorIntel.competitor_name).all()
    
    # Categorize by threat level
    high_threat = []
    medium_threat = []
    low_threat = []
    
    for comp in competitors:
        threat_level = determine_threat_level(comp.intel_count)
        if threat_level == 'high':
            high_threat.append(comp.competitor_name)
        elif threat_level == 'medium':
            medium_threat.append(comp.competitor_name)
        else:
            low_threat.append(comp.competitor_name)
    
    return {
        "total": len(competitors),
        "threat_levels": {
            "high": len(high_threat),
            "medium": len(medium_threat),
            "low": len(low_threat)
        },
        "brands": {
            "high_threat": high_threat,
            "medium_threat": medium_threat,
            "low_threat": low_threat
        }
    }

@router.get("/dashboard")
def get_competitive_dashboard(
    days: int = 30, 
    threat_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get competitive dashboard summary in format expected by frontend"""
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get all intel entries
    intel_entries = db.query(CompetitorIntel).filter(
        CompetitorIntel.created_at >= start_date
    ).all()
    
    # Count posts per competitor
    competitor_posts = {}
    total_posts = 0
    
    for entry in intel_entries:
        # Parse post count from content
        try:
            data = json.loads(entry.content)
            post_count = len(data) if isinstance(data, list) else 1
        except:
            post_count = 1
        
        if entry.competitor_name not in competitor_posts:
            competitor_posts[entry.competitor_name] = {
                'total_posts': 0,
                'entries': 0
            }
        
        competitor_posts[entry.competitor_name]['total_posts'] += post_count
        competitor_posts[entry.competitor_name]['entries'] += 1
        total_posts += post_count
    
    # Build competitor list with threat levels
    competitors_list = []
    for comp_name, data in competitor_posts.items():
        threat = determine_threat_level(data['entries'])
        
        # Filter by threat level if specified
        if threat_level and threat != threat_level:
            continue
        
        competitors_list.append({
            "competitor": comp_name,
            "total_posts": data['total_posts'],
            "avg_engagement": data['total_posts'] * 50,  # Placeholder calculation
            "threat_level": threat
        })
    
    # Sort by total_posts descending
    competitors_list.sort(key=lambda x: x['total_posts'], reverse=True)
    
    return {
        "total_data_points": total_posts,
        "competitors_tracked": len(competitors_list),
        "competitors": competitors_list,
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
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
        "key_insights": intel.tags if isinstance(intel.tags, (list, dict)) else (json.loads(intel.tags) if intel.tags else []),
        "priority": intel.priority,
        "sentiment": intel.sentiment,
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
    
    competitors_with_threat = []
    for comp in competitors:
        threat_level = determine_threat_level(comp.intel_count)
        competitors_with_threat.append({
            "name": comp.competitor_name,
            "intel_count": comp.intel_count,
            "threat_level": threat_level
        })
    
    return {
        "competitors": competitors_with_threat,
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
