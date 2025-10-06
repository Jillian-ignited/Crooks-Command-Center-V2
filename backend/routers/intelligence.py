from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session
from pathlib import Path
import os
import json
import hashlib
import aiofiles
from datetime import datetime
import tempfile
import traceback
import re
import random

# Import centralized database components
from ..database import get_db, DB_AVAILABLE
from ..models import IntelligenceFile

# Initialize router
router = APIRouter()

# CRITICAL FIX #18: Proper OpenAI setup with validation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[Intelligence] ⚠️ No OPENAI_API_KEY - AI analysis disabled")
    AI_AVAILABLE = False
    client = None
else:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Test the key works
        client.models.list()
        AI_AVAILABLE = True
        print("[Intelligence] ✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"[Intelligence] ❌ OpenAI initialization failed: {e}")
        AI_AVAILABLE = False
        client = None

# CRITICAL FIX #13: Use persistent storage, not /tmp
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/intelligence")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# CRITICAL FIX #3: File type validation
ALLOWED_EXTENSIONS = {'.jsonl', '.json', '.csv', '.txt', '.xlsx', '.xls'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Simple rate limiting storage (in production, use Redis)
upload_attempts = {}

def check_rate_limit(request: Request) -> bool:
    """Simple rate limiting - 10 uploads per hour per IP"""
    client_ip = request.client.host
    current_time = datetime.utcnow()
    
    if client_ip not in upload_attempts:
        upload_attempts[client_ip] = []
    
    # Remove attempts older than 1 hour
    upload_attempts[client_ip] = [
        attempt for attempt in upload_attempts[client_ip]
        if (current_time - attempt).seconds < 3600
    ]
    
    # Check if under limit
    if len(upload_attempts[client_ip]) >= 10:
        return False
    
    # Add current attempt
    upload_attempts[client_ip].append(current_time)
    return True

def sanitize_filename(filename: str) -> str:
    """CRITICAL FIX #15: Secure filename sanitization"""
    # Remove any path components
    filename = os.path.basename(filename)
    # Keep only alphanumeric, dash, underscore, dot
    filename = re.sub(r'[^\w\-.]', '_', filename)
    return filename

def generate_ai_analysis(file_path: str, filename: str) -> dict:
    """CRITICAL FIX #17 & #19: Fixed OpenAI model and better sampling"""
    if not AI_AVAILABLE or not client:
        return {"error": "AI analysis not available", "analysis": "Manual review required"}
    
    try:
        # Better file sampling
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            
            # Take random sample from entire file
            sample_size = min(10, len(all_lines))
            if len(all_lines) > 10:
                sample_lines = random.sample(all_lines, sample_size)
            else:
                sample_lines = all_lines
            
            # Parse JSON lines safely
            sample_data = []
            for line in sample_lines:
                try:
                    sample_data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        if not sample_data:
            return {"error": "No valid JSON data found", "analysis": "File format issue"}
        
        # CRITICAL FIX #17: Use correct OpenAI model
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # FIXED: was gpt-4.1-mini (doesn't exist)
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert competitive intelligence analyst. Analyze the provided data and extract key insights about trends, engagement patterns, content themes, and strategic opportunities."
                },
                {
                    "role": "user",
                    "content": f"Analyze this competitive intelligence data from {filename}. Sample data: {json.dumps(sample_data[:3], indent=2)}"
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        analysis_text = response.choices[0].message.content
        
        return {
            "analysis": analysis_text,
            "sample_size": len(sample_data),
            "total_records": len(all_lines),
            "model_used": "gpt-4o-mini",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[Intelligence] AI analysis error: {e}")
        return {
            "error": str(e),
            "analysis": "AI analysis failed - manual review required",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/health")
def intelligence_health_check():
    """Health check for intelligence module"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "openai_configured": OPENAI_API_KEY is not None,
        "database_available": DB_AVAILABLE,
        "upload_directory": UPLOAD_DIR,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }

@router.post("/upload")
async def upload_intelligence_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: str = "manual_upload",
    brand: str = "Crooks & Castles",
    description: str = "",
    db: Session = Depends(get_db)
):
    """Upload and analyze intelligence file with security fixes"""
    
    # CRITICAL FIX #7: Rate limiting (simplified version)
    if not check_rate_limit(request):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 10 uploads per hour."
        )
    
    # CRITICAL FIX #3: Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file_ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # CRITICAL FIX #15: Secure filename generation
    file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file_hash}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # CRITICAL FIX #16: Proper cleanup on failure
    try:
        # Stream file with size validation
        total_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    # Clean up partial file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
                    )
                await f.write(chunk)
        
        # CRITICAL FIX #12: Use ORM for better transaction management
        intelligence_file = IntelligenceFile(
            filename=safe_filename,
            original_filename=sanitize_filename(file.filename),
            source=source,
            brand=brand,
            description=description,
            file_path=file_path,
            file_size=total_size,
            file_type=file_ext,
            status="uploaded",
            uploaded_at=datetime.utcnow()
        )
        
        db.add(intelligence_file)
        db.commit()
        db.refresh(intelligence_file)
        
        # CRITICAL FIX #20: Run AI analysis in background
        if AI_AVAILABLE:
            background_tasks.add_task(
                process_ai_analysis,
                intelligence_file.id,
                file_path,
                file.filename
            )
            message = "File uploaded successfully. AI analysis in progress."
        else:
            message = "File uploaded successfully. AI analysis not available."
        
        return {
            "success": True,
            "message": message,
            "file_id": intelligence_file.id,
            "filename": intelligence_file.original_filename,
            "size": total_size,
            "ai_analysis_queued": AI_AVAILABLE
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like file too large)
        raise
    except Exception as e:
        # CRITICAL FIX #16: Clean up file on any error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        print(f"[Intelligence] Upload error: {e}")
        print(f"[Intelligence] Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

def process_ai_analysis(file_id: int, file_path: str, original_filename: str):
    """Background task to process AI analysis"""
    from ..database import SessionLocal
    
    db = SessionLocal()
    try:
        # Generate AI analysis
        ai_analysis = generate_ai_analysis(file_path, original_filename)
        
        # Update database record
        intelligence_file = db.query(IntelligenceFile).filter(
            IntelligenceFile.id == file_id
        ).first()
        
        if intelligence_file:
            intelligence_file.analysis_results = ai_analysis
            intelligence_file.status = "processed"
            intelligence_file.processed_at = datetime.utcnow()
            db.commit()
            
        print(f"[Intelligence] ✅ AI analysis completed for file {file_id}")
        
    except Exception as e:
        print(f"[Intelligence] ❌ Background AI analysis failed: {e}")
        
        # Update status to failed
        try:
            intelligence_file = db.query(IntelligenceFile).filter(
                IntelligenceFile.id == file_id
            ).first()
            if intelligence_file:
                intelligence_file.status = "analysis_failed"
                intelligence_file.analysis_results = {"error": str(e)}
                db.commit()
        except:
            pass
    finally:
        db.close()

@router.get("/files")
def list_intelligence_files(db: Session = Depends(get_db)):
    """List all uploaded intelligence files"""
    try:
        files = db.query(IntelligenceFile).order_by(
            IntelligenceFile.uploaded_at.desc()
        ).all()
        
        return {
            "files": [
                {
                    "id": file.id,
                    "filename": file.original_filename,
                    "source": file.source,
                    "brand": file.brand,
                    "size": file.file_size,
                    "status": file.status,
                    "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None,
                    "processed_at": file.processed_at.isoformat() if file.processed_at else None,
                    "has_analysis": bool(file.analysis_results)
                }
                for file in files
            ],
            "total": len(files)
        }
        
    except Exception as e:
        print(f"[Intelligence] Error listing files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")

@router.get("/files/{file_id}")
def get_intelligence_file(file_id: int, db: Session = Depends(get_db)):
    """Get specific intelligence file with analysis"""
    try:
        file = db.query(IntelligenceFile).filter(
            IntelligenceFile.id == file_id
        ).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "id": file.id,
            "filename": file.original_filename,
            "source": file.source,
            "brand": file.brand,
            "description": file.description,
            "size": file.file_size,
            "status": file.status,
            "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None,
            "processed_at": file.processed_at.isoformat() if file.processed_at else None,
            "analysis": file.analysis_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Intelligence] Error getting file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file")
