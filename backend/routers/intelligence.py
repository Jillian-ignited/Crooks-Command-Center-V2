from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import Optional
import os
import json
import PyPDF2
from anthropic import Anthropic

from ..database import get_db
from ..models import Intelligence, CompetitorIntel

router = APIRouter()

# File upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Anthropic client
try:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    print("[Intelligence] ✅ Claude AI available for intelligence analysis")
except Exception as e:
    client = None
    print(f"[Intelligence] ⚠️ Claude AI not available: {e}")

# Competitor brands to auto-detect
COMPETITOR_BRANDS = [
    "supreme", "palace", "bape", "stussy", "diamond supply", "the hundreds",
    "huf", "obey", "hundreds", "undefeated", "kith", "anti social social club",
    "assc", "off white", "fear of god", "essentials", "chrome hearts",
    "purple brand", "true religion", "ed hardy", "affliction", "tap out"
]


def detect_competitor(content: str, url: str = None) -> Optional[str]:
    """Detect if content is about a competitor brand"""
    content_lower = content.lower() if content else ""
    url_lower = url.lower() if url else ""
    
    for brand in COMPETITOR_BRANDS:
        if brand in content_lower or brand in url_lower:
            return brand.title()
    
    return None


async def analyze_intelligence(text_content: str, filename: str):
    """Analyze intelligence content using Claude AI"""
    
    if not client:
        return {
            "summary": "AI analysis not available - Claude API key not configured",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model": "none"
        }
    
    try:
        prompt = f"""Analyze this intelligence for Crooks & Castles streetwear brand.

Source: {filename}

Content:
{text_content[:8000]}

Provide a brief analysis covering:
1. Key insights and trends
2. Competitive intelligence (if any)
3. Market opportunities
4. Actionable recommendations

Keep it concise (2-3 paragraphs)."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        analysis_text = message.content[0].text
        
        return {
            "summary": analysis_text,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model": "claude-sonnet-4-20250514"
        }
    
    except Exception as e:
        print(f"[Intelligence] Claude analysis error: {e}")
        return {
            "summary": f"Analysis failed: {str(e)}",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model": "error"
        }


@router.post("/upload")
async def upload_intelligence(
    file: UploadFile = File(...),
    category: str = Form(None),
    tags: str = Form(None),
    analyze_with_ai: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Upload intelligence file and analyze with Claude - auto-feeds to competitive"""
    
    try:
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        print(f"[Intelligence] Received file: {file.filename} ({file_extension})")
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        created_count = 0
        competitor_count = 0
        
        # Handle JSONL files (Apify scrapes)
        if file_extension in ['jsonl', 'json']:
            print(f"[Intelligence] Processing JSONL/JSON file")
            
            text_content = content.decode('utf-8')
            entries = []
            
            # Try parsing as JSONL (one JSON object per line)
            try:
                for line_num, line in enumerate(text_content.strip().split('\n'), 1):
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            entries.append(entry)
                        except json.JSONDecodeError:
                            print(f"[Intelligence] Line {line_num}: Invalid JSON, skipping")
                            continue
                
                if not entries:
                    # Try parsing as single JSON array
                    try:
                        entries = json.loads(text_content)
                        if not isinstance(entries, list):
                            entries = [entries]
                    except:
                        raise HTTPException(400, "Could not parse JSON/JSONL file")
                
                print(f"[Intelligence] Found {len(entries)} entries to process")
                
                # Process each entry
                for idx, entry in enumerate(entries, 1):
                    try:
                        # Extract title and content from Apify scrape format
                        title = entry.get('title') or entry.get('name') or entry.get('url') or f"Entry {idx}"
                        url = entry.get('url', '')
                        
                        # Build content from various fields
                        content_parts = []
                        
                        if url:
                            content_parts.append(f"URL: {url}")
                        
                        if entry.get('text'):
                            content_parts.append(entry['text'])
                        elif entry.get('content'):
                            content_parts.append(entry['content'])
                        elif entry.get('description'):
                            content_parts.append(entry['description'])
                        
                        # Add any other text fields
                        for key in ['caption', 'snippet', 'summary', 'body']:
                            if entry.get(key):
                                content_parts.append(f"{key.title()}: {entry[key]}")
                        
                        entry_content = "\n\n".join(content_parts)
                        
                        if not entry_content.strip():
                            print(f"[Intelligence] Entry {idx}: No content, skipping")
                            continue
                        
                        # Detect if this is competitor intelligence
                        competitor_name = detect_competitor(entry_content, url)
                        
                        # Optional AI analysis (only first 5 to save time/cost)
                        ai_summary = None
                        ai_insights = {"raw_data": entry}
                        
                        if analyze_with_ai and idx <= 5:
                            print(f"[Intelligence] Analyzing entry {idx} with AI...")
                            analysis = await analyze_intelligence(entry_content, f"{file.filename} - {title}")
                            ai_summary = analysis.get("summary")
                            ai_insights = {"analysis": analysis, "raw_data": entry}
                        
                        # Create intelligence entry
                        intelligence = Intelligence(
                            title=title[:255],
                            content=entry_content[:50000],
                            source_type="apify_scrape" if 'url' in entry else "json",
                            category=category or ("competitor" if competitor_name else "scrape_data"),
                            tags=tag_list,
                            ai_summary=ai_summary,
                            ai_insights=ai_insights,
                            sentiment="neutral",
                            priority="medium",
                            status="new",
                            file_url=url
                        )
                        
                        db.add(intelligence)
                        created_count += 1
                        
                        # AUTO-FEED TO COMPETITIVE if competitor detected
                        if competitor_name:
                            competitor_intel = CompetitorIntel(
                                competitor_name=competitor_name,
                                category="social_media" if "instagram" in url.lower() or "tiktok" in url.lower() else "content",
                                data_type="social_post" if url else "data",
                                content=entry_content[:10000],
                                source_url=url,
                                sentiment="neutral",
                                ai_analysis=ai_summary,
                                priority="medium",
                                tags=tag_list + ["auto_imported"]
                            )
                            db.add(competitor_intel)
                            competitor_count += 1
                            print(f"[Intelligence] Entry {idx}: Auto-created competitive intel for {competitor_name}")
                        
                        print(f"[Intelligence] Entry {idx}: Created - {title[:50]}")
                        
                    except Exception as e:
                        print(f"[Intelligence] Entry {idx} error: {e}")
                        continue
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"✅ Processed {created_count} entries, {competitor_count} auto-fed to competitive intel",
                    "entries_processed": created_count,
                    "competitor_intel_created": competitor_count,
                    "ai_analyzed": min(created_count, 5) if analyze_with_ai else 0
                }
            
            except Exception as e:
                db.rollback()
                raise HTTPException(400, f"JSONL processing failed: {str(e)}")
        
        # Handle other file types (PDF, TXT, etc.)
        else:
            if file_extension == 'pdf':
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            elif file_extension in ['txt', 'md']:
                text_content = content.decode('utf-8')
            else:
                text_content = content.decode('utf-8', errors='ignore')
            
            # Detect competitor
            competitor_name = detect_competitor(text_content)
            
            # Analyze with Claude
            analysis = None
            if analyze_with_ai:
                analysis = await analyze_intelligence(text_content, file.filename)
            
            # Create intelligence entry
            intelligence = Intelligence(
                title=file.filename,
                content=text_content[:50000],
                source_type=file_extension,
                category=category or ("competitor" if competitor_name else "uploaded_file"),
                tags=tag_list,
                ai_summary=analysis.get("summary") if analysis else None,
                ai_insights={"analysis": analysis} if analysis else {},
                sentiment="neutral",
                priority="medium",
                status="new",
                file_url=f"/uploads/{file.filename}"
            )
            
            db.add(intelligence)
            
            # AUTO-FEED TO COMPETITIVE if competitor detected
            if competitor_name:
                competitor_intel = CompetitorIntel(
                    competitor_name=competitor_name,
                    category="document",
                    data_type=file_extension,
                    content=text_content[:10000],
                    source_url=f"/uploads/{file.filename}",
                    sentiment="neutral",
                    ai_analysis=analysis.get("summary") if analysis else None,
                    priority="medium",
                    tags=tag_list + ["auto_imported"]
                )
                db.add(competitor_intel)
                competitor_count = 1
            
            db.commit()
            db.refresh(intelligence)
            
            return {
                "success": True,
                "id": intelligence.id,
                "title": intelligence.title,
                "analysis": analysis,
                "competitor_intel_created": competitor_count,
                "created_at": intelligence.created_at.isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/")
def get_intelligence(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all intelligence entries"""
    
    query = db.query(Intelligence)
    
    if category:
        query = query.filter(Intelligence.category == category)
    
    if status:
        query = query.filter(Intelligence.status == status)
    
    total = query.count()
    items = query.order_by(desc(Intelligence.created_at)).limit(limit).offset(offset).all()
    
    return {
        "intelligence": [
            {
                "id": i.id,
                "title": i.title,
                "content": i.content[:200] + "..." if i.content and len(i.content) > 200 else i.content,
                "source_type": i.source_type,
                "category": i.category,
                "tags": i.tags,
                "ai_summary": i.ai_summary[:300] + "..." if i.ai_summary and len(i.ai_summary) > 300 else i.ai_summary,
                "sentiment": i.sentiment,
                "priority": i.priority,
                "status": i.status,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/files")
def get_intelligence_files(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all intelligence files - frontend-compatible format"""
    
    query = db.query(Intelligence)
    
    if category:
        query = query.filter(Intelligence.category == category)
    
    if status:
        query = query.filter(Intelligence.status == status)
    
    total = query.count()
    items = query.order_by(desc(Intelligence.created_at)).limit(limit).offset(offset).all()
    
    # Map to frontend expected format
    return {
        "files": [
            {
                "id": i.id,
                "filename": i.title,
                "source": i.source_type or "upload",
                "brand": i.category or "general",
                "size_mb": 0.1,
                "uploaded_at": i.created_at.isoformat() if i.created_at else None,
                "status": "processed",
                "has_analysis": bool(i.ai_summary),
                "content": i.content[:200] + "..." if i.content and len(i.content) > 200 else i.content,
                "tags": i.tags,
                "sentiment": i.sentiment,
                "priority": i.priority,
                "file_url": i.file_url
            }
            for i in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/files/{file_id}")
def get_intelligence_file_detail(file_id: int, db: Session = Depends(get_db)):
    """Get detailed intelligence file - frontend-compatible format"""
    
    intel = db.query(Intelligence).filter(Intelligence.id == file_id).first()
    
    if not intel:
        raise HTTPException(404, "Intelligence file not found")
    
    # Extract analysis data
    analysis_data = {}
    if intel.ai_insights:
        if isinstance(intel.ai_insights, dict):
            analysis_obj = intel.ai_insights.get("analysis", {})
            if isinstance(analysis_obj, dict):
                analysis_data = {
                    "analysis": intel.ai_summary or "No analysis available",
                    "model": analysis_obj.get("model", "unknown"),
                    "sample_size": 5,
                    "total_records": 1
                }
            else:
                analysis_data = {
                    "analysis": intel.ai_summary or "No analysis available",
                    "model": "unknown",
                    "sample_size": 1,
                    "total_records": 1
                }
        else:
            analysis_data = {
                "analysis": intel.ai_summary or "No analysis available",
                "model": "unknown"
            }
    elif intel.ai_summary:
        analysis_data = {
            "analysis": intel.ai_summary,
            "model": "claude-sonnet-4-20250514"
        }
    
    return {
        "id": intel.id,
        "filename": intel.title,
        "source": intel.source_type or "upload",
        "brand": intel.category or "general",
        "size_mb": 0.1,
        "uploaded_at": intel.created_at.isoformat(),
        "status": "processed",
        "has_analysis": bool(intel.ai_summary),
        "analysis": analysis_data,
        "content": intel.content,
        "tags": intel.tags,
        "file_url": intel.file_url
    }


@router.get("/{intelligence_id}")
def get_intelligence_detail(intelligence_id: int, db: Session = Depends(get_db)):
    """Get detailed intelligence entry"""
    
    intel = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    
    if not intel:
        raise HTTPException(404, "Intelligence entry not found")
    
    return {
        "id": intel.id,
        "title": intel.title,
        "content": intel.content,
        "source_type": intel.source_type,
        "category": intel.category,
        "tags": intel.tags,
        "ai_summary": intel.ai_summary,
        "ai_insights": intel.ai_insights,
        "sentiment": intel.sentiment,
        "priority": intel.priority,
        "status": intel.status,
        "file_url": intel.file_url,
        "created_at": intel.created_at.isoformat(),
        "updated_at": intel.updated_at.isoformat()
    }


@router.put("/{intelligence_id}")
def update_intelligence(
    intelligence_id: int,
    title: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[list] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update intelligence entry"""
    
    intel = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    
    if not intel:
        raise HTTPException(404, "Intelligence entry not found")
    
    if title:
        intel.title = title
    if category:
        intel.category = category
    if tags is not None:
        intel.tags = tags
    if status:
        intel.status = status
    if priority:
        intel.priority = priority
    if sentiment:
        intel.sentiment = sentiment
    
    intel.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(intel)
    
    return {"success": True, "intelligence_id": intel.id}


@router.delete("/{intelligence_id}")
def delete_intelligence(intelligence_id: int, db: Session = Depends(get_db)):
    """Delete intelligence entry"""
    
    intel = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    
    if not intel:
        raise HTTPException(404, "Intelligence entry not found")
    
    db.delete(intel)
    db.commit()
    
    return {"success": True, "message": "Intelligence entry deleted"}


@router.post("/analyze/{intelligence_id}")
async def reanalyze_intelligence(intelligence_id: int, db: Session = Depends(get_db)):
    """Re-analyze an existing intelligence entry with Claude"""
    
    intel = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    
    if not intel:
        raise HTTPException(404, "Intelligence entry not found")
    
    if not intel.content:
        raise HTTPException(400, "No content to analyze")
    
    # Re-analyze with Claude
    analysis = await analyze_intelligence(intel.content, intel.title)
    
    intel.ai_summary = analysis.get("summary")
    intel.ai_insights = {"analysis": analysis}
    intel.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(intel)
    
    return {
        "success": True,
        "analysis": analysis,
        "updated_at": intel.updated_at.isoformat()
    }


@router.post("/migrate-table")
def migrate_intelligence_table(db: Session = Depends(get_db)):
    """DANGER: Recreate intelligence table - will delete all data!"""
    
    from sqlalchemy import text
    
    try:
        db.execute(text("DROP TABLE IF EXISTS intelligence CASCADE"))
        db.commit()
        
        db.execute(text("""
            CREATE TABLE intelligence (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                content TEXT NOT NULL,
                source_type VARCHAR,
                category VARCHAR,
                tags JSONB,
                ai_summary TEXT,
                ai_insights JSONB,
                sentiment VARCHAR,
                priority VARCHAR DEFAULT 'medium',
                status VARCHAR DEFAULT 'new',
                file_url VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.commit()
        
        db.execute(text("CREATE INDEX ix_intelligence_id ON intelligence(id)"))
        db.execute(text("CREATE INDEX ix_intelligence_title ON intelligence(title)"))
        db.execute(text("CREATE INDEX ix_intelligence_category ON intelligence(category)"))
        db.execute(text("CREATE INDEX ix_intelligence_created_at ON intelligence(created_at)"))
        db.commit()
        
        return {
            "success": True,
            "message": "✅ Intelligence table recreated successfully!"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Migration failed: {str(e)}")
