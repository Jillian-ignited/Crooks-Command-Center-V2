from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import Optional
import os
import json
import PyPDF2
from backend.database import get_db
from backend.models import Intelligence, CompetitorIntel
from backend.ai_processor import AIProcessor

router = APIRouter()
ai_processor = AIProcessor()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "intelligence")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def detect_competitor_data(content: str, filename: str) -> Optional[dict]:
    """Detect if content contains competitor intelligence data"""
    content_lower = content.lower()
    
    # Check for Instagram scrape patterns
    if any(term in content_lower for term in ['instagram', 'followers', 'engagement_rate', 'post_content']):
        return {
            'source': 'instagram',
            'category': 'social_media'
        }
    
    # Check for product/pricing data
    if any(term in content_lower for term in ['product', 'price', 'sku', 'inventory']):
        return {
            'source': 'product_data',
            'category': 'product'
        }
    
    # Check for marketing data
    if any(term in content_lower for term in ['campaign', 'ad_spend', 'cpc', 'ctr']):
        return {
            'source': 'marketing',
            'category': 'marketing'
        }
    
    return None

def extract_competitor_name(content: str, filename: str) -> str:
    """Extract competitor name from content or filename"""
    # Try to parse as JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            # Look for common competitor name fields
            for field in ['competitor', 'brand', 'account_name', 'username', 'company']:
                if field in data and data[field]:
                    return str(data[field])
            
            # For Instagram scrapes, check profile info
            if 'profile' in data and isinstance(data['profile'], dict):
                if 'username' in data['profile']:
                    return data['profile']['username']
        
        # If it's a list, check first item
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            for field in ['competitor', 'brand', 'account_name', 'username']:
                if field in data[0] and data[0][field]:
                    return str(data[0][field])
    except json.JSONDecodeError:
        pass
    
    # Extract from filename as fallback
    name = filename.replace('.jsonl', '').replace('.json', '').replace('.txt', '')
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Remove common prefixes
    for prefix in ['instagram', 'scrape', 'data', 'competitor', 'intel']:
        name = name.replace(prefix, '').strip()
    
    return name.title() if name else 'Unknown Competitor'

@router.post("/upload")
async def upload_intelligence(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload intelligence file with auto-competitive population"""
    
    # Use defaults if not provided
    if not source:
        source = "manual_upload"
    
    # Infer category from source
    if not category:
        category_map = {
            'apify': 'social_media',
            'shopify': 'sales_data',
            'manus': 'agency_report',
            'manual_upload': 'general'
        }
        category = category_map.get(source, 'general')
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Read content for processing
    try:
        if file.filename.endswith('.pdf'):
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                raw_content = ""
                for page in pdf_reader.pages:
                    raw_content += page.extract_text()
        else:
            raw_content = content.decode('utf-8')
    except Exception as e:
        raw_content = ""
    
    # Generate AI summary
    summary = ai_processor.generate_summary(raw_content)
    insights = ai_processor.extract_insights(raw_content)
    
    # Create Intelligence entry
    intel_entry = Intelligence(
        title=file.filename,
        source_type=source,
        category=category,
        content=raw_content,
        ai_summary=summary,
        ai_insights=insights,  # PostgreSQL JSONB handles this automatically
        file_url=file_path,
        tags=[description] if description else [],
        status='new'
    )
    
    db.add(intel_entry)
    db.flush()  # Get the ID without committing yet
    
    db.add(intel_entry)
    db.flush()  # Get the ID without committing yet
    
    # Auto-populate Competitive Intelligence if detected
    competitor_info = detect_competitor_data(raw_content, file.filename)
    if competitor_info:
        competitor_name = extract_competitor_name(raw_content, file.filename)
        
        competitor_entry = CompetitorIntel(
            competitor_name=competitor_name,
            category=competitor_info['category'],
            data_type=competitor_info['source'],
            content=raw_content,
            ai_analysis=summary,
            tags=insights,  # PostgreSQL JSONB handles this automatically
            source_url=file_path,
            priority='medium',
            sentiment='neutral'
        )
        
        db.add(competitor_entry)
    
    db.commit()
    db.refresh(intel_entry)
    
    # Get file size
    file_size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    
    return {
        "success": True,
        "message": "Intelligence uploaded successfully",
        "id": intel_entry.id,
        "filename": file.filename,
        "size_mb": file_size_mb,
        "source": source,
        "status": intel_entry.status,
        "summary": summary,
        "insights": insights,
        "ai_analysis_complete": bool(summary and insights),
        "competitor_auto_populated": competitor_info is not None
    }

@router.get("/files")
def list_intelligence_files(
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all intelligence entries"""
    
    query = db.query(Intelligence)
    
    if category:
        query = query.filter(Intelligence.category == category)
    
    entries = query.order_by(desc(Intelligence.created_at)).limit(limit).all()
    
    return {
        "files": [
            {
                "id": e.id,
                "title": e.title,
                "source": e.source_type,
                "category": e.category,
                "summary": e.ai_summary,
                "key_insights": e.ai_insights if isinstance(e.ai_insights, (list, dict)) else (json.loads(e.ai_insights) if e.ai_insights else []),
                "created_at": e.created_at.isoformat(),
                "status": e.status
            }
            for e in entries
        ],
        "total": len(entries)
    }

@router.get("/summary")
def get_intelligence_summary(db: Session = Depends(get_db)):
    """Get intelligence summary statistics"""
    
    from sqlalchemy import func
    
    total = db.query(func.count(Intelligence.id)).scalar()
    
    by_category = db.query(
        Intelligence.category,
        func.count(Intelligence.id)
    ).group_by(Intelligence.category).all()
    
    by_source = db.query(
        Intelligence.source_type,
        func.count(Intelligence.id)
    ).group_by(Intelligence.source_type).all()
    
    recent = db.query(Intelligence).order_by(
        desc(Intelligence.created_at)
    ).limit(5).all()
    
    return {
        "total_entries": total,
        "by_category": {cat: count for cat, count in by_category},
        "by_source": {src: count for src, count in by_source},
        "recent_uploads": [
            {
                "id": e.id,
                "title": e.title,
                "source": e.source_type,
                "category": e.category,
                "created_at": e.created_at.isoformat()
            }
            for e in recent
        ]
    }

@router.delete("/{entry_id}")
def delete_intelligence(entry_id: int, db: Session = Depends(get_db)):
    """Delete intelligence entry"""
    
    entry = db.query(Intelligence).filter(Intelligence.id == entry_id).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Intelligence entry not found")
    
    # Delete file if exists
    if entry.file_url and os.path.exists(entry.file_url):
        os.remove(entry.file_url)
    
    db.delete(entry)
    db.commit()
    
    return {"success": True, "message": "Intelligence entry deleted"}
