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
from ..models import Intelligence  # CHANGED FROM IntelligenceFile

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


async def analyze_intelligence(text_content: str, filename: str):
    """Analyze intelligence content using Claude AI"""
    
    if not client:
        return {
            "summary": "AI analysis not available - Claude API key not configured",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model": "none"
        }
    
    try:
        prompt = f"""Analyze this intelligence file for Crooks & Castles streetwear brand.

Filename: {filename}

Content:
{text_content[:8000]}

Provide a structured analysis covering:
1. Key insights and trends
2. Competitive intelligence (if any)
3. Market opportunities
4. Customer/audience insights
5. Actionable recommendations

Focus on insights relevant to hip-hop culture, streetwear, and urban fashion."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
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
    db: Session = Depends(get_db)
):
    """Upload intelligence file and analyze with Claude"""
    
    try:
        # Read file content
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        # Extract text based on file type
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
        
        # Analyze with Claude
        analysis = await analyze_intelligence(text_content, file.filename)
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        # Create intelligence entry
        intelligence = Intelligence(
            title=file.filename,
            content=text_content[:10000],  # Store first 10k chars
            source_type=file_extension,
            category=category or "uploaded_file",
            tags=tag_list,
            ai_summary=analysis.get("summary"),
            ai_insights={"analysis": analysis},
            sentiment="neutral",
            priority="medium",
            status="new",
            file_url=f"/uploads/{file.filename}"
        )
        
        db.add(intelligence)
        db.commit()
        db.refresh(intelligence)
        
        return {
            "success": True,
            "id": intelligence.id,
            "title": intelligence.title,
            "analysis": analysis,
            "created_at": intelligence.created_at.isoformat()
        }
        
    except Exception as e:
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
        # Drop old table
        db.execute(text("DROP TABLE IF EXISTS intelligence CASCADE"))
        db.commit()
        
        # Create new table with correct schema
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
        
        # Create indexes
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
