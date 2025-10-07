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
import random

from ..database import get_db, DB_AVAILABLE
from ..models import IntelligenceFile

router = APIRouter()

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_AVAILABLE = bool(OPENAI_API_KEY)

if AI_AVAILABLE:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Test connection
        client.models.list()
        print("[Intelligence] ✅ OpenAI v1.x initialized")
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


def analyze_large_file(file_path: str, filename: str, source: str) -> dict:
    """
    Optimized AI analysis for large files (up to 70MB)
    Uses intelligent sampling instead of reading entire file
    """
    if not AI_AVAILABLE:
        return {"error": "OpenAI not configured", "analysis": "AI analysis unavailable"}
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        print(f"[Analysis] Reading file: {filename}")
        
        # OPTIMIZED SAMPLING for large files
        with open(file_path, 'r', encoding='utf-8') as f:
            # Count total lines
            all_lines = f.readlines()
            total_lines = len(all_lines)
            print(f"[Analysis] Total records: {total_lines}")
            
            # Intelligent sampling: beginning, middle, end
            sample_lines = []
            
            # First 5 records
            for line in all_lines[:5]:
                try:
                    sample_lines.append(json.loads(line.strip()))
                except:
                    continue
            
            # Middle 5 records
            if total_lines > 20:
                middle_start = total_lines // 2
                for line in all_lines[middle_start:middle_start+5]:
                    try:
                        sample_lines.append(json.loads(line.strip()))
                    except:
                        continue
            
            # Last 5 records
            if total_lines > 10:
                for line in all_lines[-5:]:
                    try:
                        sample_lines.append(json.loads(line.strip()))
                    except:
                        continue
        
        if not sample_lines:
            return {"error": "No valid JSON data", "analysis": "File format issue"}
        
        print(f"[Analysis] Sampled {len(sample_lines)} records from {total_lines} total")
        
        # Streetwear-specific AI prompt
        system_prompt = """You are a streetwear brand strategist analyzing competitive intelligence data.

Focus on:
1. Cultural moments & trends (music, sports, art, subcultures)
2. Product drops & release strategies
3. Influencer/celebrity mentions
4. Aesthetic trends (Y2K, techwear, vintage, gorpcore, etc.)
5. Engagement tactics (giveaways, limited drops, community building)
6. Sentiment and audience reactions
7. Pricing strategies and positioning

Provide actionable insights for Crooks & Castles to compete effectively."""

        user_prompt = f"""Analyze this {source} competitive intelligence data from {filename}.

Dataset: {total_lines} total records (sampled {len(sample_lines)} for analysis)

Sample data:
{json.dumps(sample_lines[:5], indent=2)}

Provide:
1. **Key Cultural Trends**: What's resonating in streetwear culture?
2. **Top Content Themes**: What content performs best?
3. **Engagement Patterns**: When/how is audience most engaged?
4. **Competitive Moves**: What are competitors doing well?
5. **Strategic Opportunities**: Specific actions for Crooks & Castles
6. **Sentiment Overview**: Brand perception and audience mood
7. **Timing Insights**: Best times for content and campaigns"""

        # Call OpenAI
        print(f"[Analysis] Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",  # 16k model for larger context
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        analysis_text = response.choices[0].message.content
        
        print(f"[Analysis] ✅ AI analysis complete")
        
        return {
            "analysis": analysis_text,
            "sample_size": len(sample_lines),
            "total_records": total_lines,
            "sampling_method": "intelligent (beginning, middle, end)",
            "model": "gpt-3.5-turbo-16k",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[Analysis] AI error: {e}")
        traceback.print_exc()
        return {
            "error": str(e),
            "analysis": "AI analysis failed - please try again"
        }


@router.get("/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "database_available": DB_AVAILABLE,
        "upload_directory": UPLOAD_DIR,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    source: str = "manual_upload",  # apify, shopify, manus
    brand: str = "Crooks & Castles",
    description: str = "",
    db: Session = Depends(get_db)
):
    """
    Upload intelligence file (up to 100MB)
    Analysis runs synchronously - will take 30-60 seconds for large files
    """
    
    # Validate
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
        print(f"[Upload] Receiving: {file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    os.remove(file_path)
                    raise HTTPException(413, "File exceeds 100MB limit")
                await f.write(chunk)
        
        print(f"[Upload] Saved: {total_size / 1024 / 1024:.2f} MB")
        
        # Generate AI analysis (synchronous - user waits)
        analysis_results = None
        if AI_AVAILABLE:
            print(f"[Upload] Starting AI analysis...")
            analysis_results = analyze_large_file(file_path, file.filename, source)
            print(f"[Upload] AI analysis complete")
        
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
            analysis_results=analysis_results,
            status="processed" if analysis_results else "uploaded",
            processed_at=datetime.utcnow() if analysis_results else None
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        print(f"[Upload] ✅ Complete - ID: {file_record.id}")
        
        return {
            "success": True,
            "file_id": file_record.id,
            "filename": file_record.original_filename,
            "size_mb": round(total_size / 1024 / 1024, 2),
            "source": source,
            "status": file_record.status,
            "ai_analysis_complete": bool(analysis_results),
            "message": "Upload and analysis complete!" if analysis_results else "Upload complete (AI unavailable)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"[Upload] ❌ Error: {e}")
        traceback.print_exc()
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/files")
def list_files(
    source: str = None,
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
                "size_mb": round(f.file_size / 1024 / 1024, 2) if f.file_size else 0,
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
        "size_mb": round(file_record.file_size / 1024 / 1024, 2) if file_record.file_size else 0,
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
    """Get aggregated insights from recent files"""
    from datetime import timedelta
    
    since = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(IntelligenceFile).filter(
        IntelligenceFile.uploaded_at >= since,
        IntelligenceFile.analysis_results.isnot(None)
    )
    
    if source:
        query = query.filter(IntelligenceFile.source == source)
    
    files = query.order_by(IntelligenceFile.uploaded_at.desc()).all()
    
    return {
        "period": f"Last {days} days",
        "total_files": len(files),
        "sources": list(set(f.source for f in files)),
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "source": f.source,
                "uploaded_at": f.uploaded_at.isoformat(),
                "analysis_preview": (
                    f.analysis_results.get("analysis", "")[:200] + "..."
                    if isinstance(f.analysis_results, dict) and "analysis" in f.analysis_results
                    else str(f.analysis_results)[:200] + "..."
                    if f.analysis_results
                    else "No analysis available"
                )
            }
            for f in files
        ]
    }