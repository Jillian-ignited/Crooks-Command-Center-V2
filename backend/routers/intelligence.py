from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pathlib import Path
import os
import json
import hashlib
import aiofiles
from datetime import datetime
import traceback
import re

from ..database import get_db, DB_AVAILABLE
from ..models import IntelligenceFile

router = APIRouter()

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_AVAILABLE = bool(OPENAI_API_KEY)

if AI_AVAILABLE:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        print("[Intelligence] ✅ OpenAI initialized")
    except Exception as e:
        print(f"[Intelligence] ❌ OpenAI init failed: {e}")
        AI_AVAILABLE = False

# File storage
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/intelligence")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jsonl', '.json', '.csv', '.txt', '.xlsx', '.xls'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def sanitize_filename(filename: str) -> str:
    """Secure filename"""
    return re.sub(r'[^\w\-.]', '_', os.path.basename(filename))

def generate_ai_analysis(file_path: str, filename: str, source: str) -> dict:
    """Generate AI analysis with streetwear focus"""
    if not AI_AVAILABLE:
        return {"error": "AI not available", "analysis": "Manual review required"}
    
    try:
        import openai
        
        # Read sample data
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]  # Sample first 10 lines
            sample_data = []
            for line in lines:
                try:
                    sample_data.append(json.loads(line.strip()))
                except:
                    continue
        
        if not sample_data:
            return {"error": "No valid data", "analysis": "Could not parse file"}
        
        # Streetwear-specific AI prompt
        system_prompt = """You are a streetwear brand strategist analyzing competitive intelligence.
        
Focus on:
1. Cultural moments & trends (music, sports, art, subcultures)
2. Product drops & release strategies  
3. Influencer/celebrity mentions
4. Aesthetic trends (Y2K, techwear, vintage, etc.)
5. Engagement tactics (giveaways, limited drops, community)
6. Sentiment and audience reactions

Provide actionable insights for Crooks & Castles."""

        user_prompt = f"""Analyze this {source} data from {filename}.

Sample data: {json.dumps(sample_data[:3], indent=2)}

Provide:
1. Key trends & cultural moments
2. Top performing content themes
3. Engagement patterns
4. Strategic opportunities for Crooks & Castles
5. Sentiment overview"""

        # OpenAI v0.28.1 API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        analysis_text = response.choices[0].message.content
        
        return {
            "analysis": analysis_text,
            "sample_size": len(sample_data),
            "total_records": len(lines),
            "model": "gpt-3.5-turbo",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[Intelligence] AI error: {e}")
        return {"error": str(e), "analysis": "AI analysis failed"}


@router.get("/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "database_available": DB_AVAILABLE
    }


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    source: str = "manual_upload",  # apify, shopify, manus, manual_upload
    brand: str = "Crooks & Castles",
    description: str = "",
    db: Session = Depends(get_db)
):
    """Upload intelligence file - SIMPLIFIED VERSION"""
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Invalid file type: {file_ext}")
    
    # Generate secure filename
    file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{file_hash}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    
    try:
        # Save file
        total_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    os.remove(file_path)
                    raise HTTPException(413, "File too large")
                await f.write(chunk)
        
        # Generate AI analysis (synchronous - no background task needed)
        analysis_results = None
        if AI_AVAILABLE:
            analysis_results = generate_ai_analysis(file_path, file.filename, source)
        
        # Create database record using ORM
        file_record = IntelligenceFile(
            filename=safe_name,
            original_filename=sanitize_filename(file.filename),
            source=source,
            brand=brand,
            description=description,
            file_path=file_path,
            file_size=total_size,
            file_type=file_ext,
            analysis_results=analysis_results,  # Store as JSON
            status="processed" if analysis_results else "uploaded",
            processed_at=datetime.utcnow() if analysis_results else None
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        return {
            "success": True,
            "file_id": file_record.id,
            "filename": file_record.original_filename,
            "size": total_size,
            "source": source,
            "ai_analysis_complete": bool(analysis_results),
            "status": file_record.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"[Intelligence] Upload error: {e}")
        print(traceback.format_exc())
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/files")
def list_files(
    source: str = None,  # Filter: apify, shopify, manus
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List uploaded files"""
    query = db.query(IntelligenceFile)
    
    if source:
        query = query.filter(IntelligenceFile.source == source)
    
    files = query.order_by(IntelligenceFile.uploaded_at.desc()).limit(limit).all()
    
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "source": f.source,
                "brand": f.brand,
                "size": f.file_size,
                "status": f.status,
                "uploaded_at": f.uploaded_at.isoformat(),
                "has_analysis": bool(f.analysis_results)
            }
            for f in files
        ],
        "total": len(files)
    }


@router.get("/files/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db)):
    """Get file details with AI analysis"""
    file_record = db.query(IntelligenceFile).filter(
        IntelligenceFile.id == file_id
    ).first()
    
    if not file_record:
        raise HTTPException(404, "File not found")
    
    return {
        "id": file_record.id,
        "filename": file_record.original_filename,
        "source": file_record.source,
        "brand": file_record.brand,
        "description": file_record.description,
        "size": file_record.file_size,
        "status": file_record.status,
        "uploaded_at": file_record.uploaded_at.isoformat(),
        "processed_at": file_record.processed_at.isoformat() if file_record.processed_at else None,
        "analysis": file_record.analysis_results
    }


@router.get("/insights")
def get_insights(
    source: str = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get aggregated insights from all files"""
    from datetime import timedelta
    
    since = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(IntelligenceFile).filter(
        IntelligenceFile.uploaded_at >= since,
        IntelligenceFile.analysis_results.isnot(None)
    )
    
    if source:
        query = query.filter(IntelligenceFile.source == source)
    
    files = query.all()
    
    # Aggregate insights
    all_analyses = [f.analysis_results for f in files if f.analysis_results]
    
    return {
        "period": f"Last {days} days",
        "total_files": len(files),
        "sources": list(set(f.source for f in files)),
        "files_analyzed": len(all_analyses),
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "source": f.source,
                "uploaded_at": f.uploaded_at.isoformat(),
                "analysis_preview": (
                    f.analysis_results.get("analysis", "")[:200] + "..."
                    if isinstance(f.analysis_results, dict)
                    else str(f.analysis_results)[:200] + "..."
                )
            }
            for f in files
        ]
    }