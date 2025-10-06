from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
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

# OpenAI v0.28.1 setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[Intelligence] ⚠️ No OPENAI_API_KEY - AI analysis disabled")
    AI_AVAILABLE = False
else:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        models = openai.Model.list()
        AI_AVAILABLE = True
        print("[Intelligence] ✅ OpenAI v0.28.1 initialized successfully")
    except Exception as e:
        print(f"[Intelligence] ❌ OpenAI initialization failed: {e}")
        AI_AVAILABLE = False

# File storage setup
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/intelligence")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# File validation
ALLOWED_EXTENSIONS = {'.jsonl', '.json', '.csv', '.txt', '.xlsx', '.xls'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Rate limiting
upload_attempts = {}

def check_rate_limit(request: Request) -> bool:
    """Simple rate limiting - 10 uploads per hour per IP"""
    client_ip = request.client.host
    current_time = datetime.utcnow()
    
    if client_ip not in upload_attempts:
        upload_attempts[client_ip] = []
    
    upload_attempts[client_ip] = [
        attempt for attempt in upload_attempts[client_ip]
        if (current_time - attempt).seconds < 3600
    ]
    
    if len(upload_attempts[client_ip]) >= 10:
        return False
    
    upload_attempts[client_ip].append(current_time)
    return True

def sanitize_filename(filename: str) -> str:
    """Secure filename sanitization"""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\-.]', '_', filename)
    return filename

def get_table_columns(db: Session) -> list:
    """Get the actual columns that exist in the intelligence_files table"""
    try:
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'intelligence_files'
            ORDER BY ordinal_position;
        """))
        columns = [row[0] for row in result]
        print(f"[Intelligence] 📊 Available table columns: {columns}")
        return columns
    except Exception as e:
        print(f"[Intelligence] ❌ Failed to get table columns: {e}")
        return []

def create_adaptive_record(db: Session, file_data: dict) -> dict:
    """Create a database record using only the columns that actually exist"""
    try:
        # Get available columns
        available_columns = get_table_columns(db)
        
        if not available_columns:
            raise Exception("Could not determine table structure")
        
        # Map our data to available columns
        column_mapping = {
            'filename': file_data.get('filename'),
            'original_filename': file_data.get('original_filename'),
            'source': file_data.get('source', 'manual_upload'),
            'brand': file_data.get('brand', 'Crooks & Castles'),
            'file_path': file_data.get('file_path'),
            'file_size': file_data.get('file_size'),
            'file_type': file_data.get('file_type'),
            'description': file_data.get('description', ''),
            'analysis_results': file_data.get('analysis_results'),
            'status': file_data.get('status', 'uploaded'),
            'uploaded_at': file_data.get('uploaded_at', datetime.utcnow()),
            'processed_at': file_data.get('processed_at'),
            'created_by': file_data.get('created_by')
        }
        
        # Filter to only include columns that exist in the table
        filtered_data = {
            col: value for col, value in column_mapping.items() 
            if col in available_columns and value is not None
        }
        
        print(f"[Intelligence] 📝 Inserting data: {list(filtered_data.keys())}")
        
        # Build dynamic SQL
        columns = list(filtered_data.keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"""
            INSERT INTO intelligence_files ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        result = db.execute(text(sql), filtered_data)
        db.commit()
        
        record_id = result.scalar()
        print(f"[Intelligence] ✅ Created record with ID: {record_id}")
        
        return {"id": record_id, "columns_used": columns}
        
    except Exception as e:
        db.rollback()
        print(f"[Intelligence] ❌ Failed to create record: {e}")
        raise

def generate_ai_analysis(file_path: str, filename: str) -> dict:
    """Generate AI analysis using OpenAI v0.28.1"""
    if not AI_AVAILABLE:
        return {"error": "AI analysis not available", "analysis": "Manual review required"}
    
    try:
        import openai
        
        # Sample file content
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            sample_size = min(10, len(all_lines))
            if len(all_lines) > 10:
                sample_lines = random.sample(all_lines, sample_size)
            else:
                sample_lines = all_lines
            
            sample_data = []
            for line in sample_lines:
                try:
                    sample_data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        if not sample_data:
            return {"error": "No valid JSON data found", "analysis": "File format issue"}
        
        # OpenAI v0.28.1 API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert competitive intelligence analyst for fashion and streetwear brands. Analyze the provided social media data and extract key insights about trends, engagement patterns, content themes, and strategic opportunities."
                },
                {
                    "role": "user",
                    "content": f"Analyze this competitive intelligence data from {filename}. Provide insights on:\n1. Content themes and trends\n2. Engagement patterns\n3. Audience preferences\n4. Strategic opportunities\n5. Competitive positioning\n\nSample data: {json.dumps(sample_data[:3], indent=2)}"
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        analysis_text = response.choices[0].message.content
        
        return {
            "analysis": analysis_text,
            "sample_size": len(sample_data),
            "total_records": len(all_lines),
            "model_used": "gpt-3.5-turbo",
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
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "api_version": "0.28.1"
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
    """Upload and analyze intelligence file - ADAPTIVE VERSION"""
    
    # Rate limiting
    if not check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # File validation
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file_ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate secure filename
    file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file_hash}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        # Save file
        total_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(status_code=413, detail="File too large")
                await f.write(chunk)
        
        # Prepare file data
        file_data = {
            'filename': safe_filename,
            'original_filename': sanitize_filename(file.filename),
            'source': source,
            'brand': brand,
            'description': description,
            'file_path': file_path,
            'file_size': total_size,
            'file_type': file_ext,
            'status': 'uploaded',
            'uploaded_at': datetime.utcnow()
        }
        
        # Create database record using adaptive method
        record_info = create_adaptive_record(db, file_data)
        
        # Queue AI analysis if available
        if AI_AVAILABLE:
            background_tasks.add_task(
                process_ai_analysis_adaptive,
                record_info['id'],
                file_path,
                file.filename,
                db
            )
            message = "File uploaded successfully. AI analysis in progress."
        else:
            message = "File uploaded successfully. AI analysis not available."
        
        return {
            "success": True,
            "message": message,
            "file_id": record_info['id'],
            "filename": file_data['original_filename'],
            "size": total_size,
            "columns_used": record_info['columns_used'],
            "ai_analysis_queued": AI_AVAILABLE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        
        print(f"[Intelligence] Upload error: {e}")
        print(f"[Intelligence] Traceback: {traceback.format_exc()}")
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def process_ai_analysis_adaptive(file_id: int, file_path: str, original_filename: str, db: Session):
    """Background task for AI analysis - adaptive version"""
    try:
        # Generate AI analysis
        ai_analysis = generate_ai_analysis(file_path, original_filename)
        
        # Update record with analysis (if analysis_results column exists)
        available_columns = get_table_columns(db)
        
        if 'analysis_results' in available_columns:
            db.execute(
                text("UPDATE intelligence_files SET analysis_results = :analysis WHERE id = :id"),
                {"analysis": json.dumps(ai_analysis), "id": file_id}
            )
        
        if 'status' in available_columns:
            db.execute(
                text("UPDATE intelligence_files SET status = :status WHERE id = :id"),
                {"status": "processed", "id": file_id}
            )
        
        if 'processed_at' in available_columns:
            db.execute(
                text("UPDATE intelligence_files SET processed_at = :processed_at WHERE id = :id"),
                {"processed_at": datetime.utcnow(), "id": file_id}
            )
        
        db.commit()
        print(f"[Intelligence] ✅ AI analysis completed for file {file_id}")
        
    except Exception as e:
        print(f"[Intelligence] ❌ Background AI analysis failed: {e}")

@router.get("/files")
def list_intelligence_files(db: Session = Depends(get_db)):
    """List all uploaded intelligence files - adaptive version"""
    try:
        # Get available columns
        available_columns = get_table_columns(db)
        
        # Build dynamic query based on available columns
        select_columns = []
        if 'id' in available_columns:
            select_columns.append('id')
        if 'original_filename' in available_columns:
            select_columns.append('original_filename')
        elif 'filename' in available_columns:
            select_columns.append('filename')
        if 'source' in available_columns:
            select_columns.append('source')
        if 'brand' in available_columns:
            select_columns.append('brand')
        if 'file_size' in available_columns:
            select_columns.append('file_size')
        if 'status' in available_columns:
            select_columns.append('status')
        if 'uploaded_at' in available_columns:
            select_columns.append('uploaded_at')
        if 'processed_at' in available_columns:
            select_columns.append('processed_at')
        if 'analysis_results' in available_columns:
            select_columns.append('analysis_results')
        
        if not select_columns:
            return {"files": [], "total": 0, "error": "No readable columns found"}
        
        sql = f"SELECT {', '.join(select_columns)} FROM intelligence_files ORDER BY id DESC"
        result = db.execute(text(sql))
        
        files = []
        for row in result:
            file_data = dict(zip(select_columns, row))
            files.append({
                "id": file_data.get('id'),
                "filename": file_data.get('original_filename') or file_data.get('filename'),
                "source": file_data.get('source'),
                "brand": file_data.get('brand'),
                "size": file_data.get('file_size'),
                "status": file_data.get('status'),
                "uploaded_at": file_data.get('uploaded_at').isoformat() if file_data.get('uploaded_at') else None,
                "processed_at": file_data.get('processed_at').isoformat() if file_data.get('processed_at') else None,
                "has_analysis": bool(file_data.get('analysis_results'))
            })
        
        return {
            "files": files,
            "total": len(files),
            "available_columns": available_columns
        }
        
    except Exception as e:
        print(f"[Intelligence] Error listing files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")

@router.get("/files/{file_id}")
def get_intelligence_file(file_id: int, db: Session = Depends(get_db)):
    """Get specific intelligence file - adaptive version"""
    try:
        available_columns = get_table_columns(db)
        
        if not available_columns:
            raise HTTPException(status_code=500, detail="Cannot read table structure")
        
        sql = f"SELECT * FROM intelligence_files WHERE id = :file_id"
        result = db.execute(text(sql), {"file_id": file_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_data = dict(zip(available_columns, row))
        
        return {
            "id": file_data.get('id'),
            "filename": file_data.get('original_filename') or file_data.get('filename'),
            "source": file_data.get('source'),
            "brand": file_data.get('brand'),
            "description": file_data.get('description'),
            "size": file_data.get('file_size'),
            "status": file_data.get('status'),
            "uploaded_at": file_data.get('uploaded_at').isoformat() if file_data.get('uploaded_at') else None,
            "processed_at": file_data.get('processed_at').isoformat() if file_data.get('processed_at') else None,
            "analysis": file_data.get('analysis_results'),
            "available_columns": available_columns
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Intelligence] Error getting file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file")
