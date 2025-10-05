from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy import text
import os
import json
import aiofiles
from datetime import datetime
import hashlib
from typing import Optional
import tempfile
import traceback

# Import centralized database components
from ..database import engine, DB_AVAILABLE

# Initialize router
router = APIRouter()

# OpenAI setup
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
    print("[Intelligence] OpenAI client initialized successfully")
except Exception as e:
    print(f"[Intelligence] OpenAI initialization failed: {e}")
    AI_AVAILABLE = False

UPLOAD_DIR = "/tmp/intelligence_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_ai_analysis(file_path: str):
    """
    Reads a sample of a JSONL file, sends it to the OpenAI API for analysis,
    and returns a structured dictionary of the analysis.
    """
    try:
        with open(file_path, 'r') as f:
            # Read the first 5 lines for a sample
            sample_lines = [next(f) for _ in range(5)]
            sample_data = [json.loads(line) for line in sample_lines]
    except Exception as e:
        return {
            "error": f"Failed to read or parse file: {e}",
            "status": "error"
        }

    prompt = f'''
    Analyze the following sample of a JSONL file containing Instagram hashtag data.
    Provide a brief summary of the data, identify 3-5 key insights, and suggest 3-5 actionable recommendations for the streetwear brand "Crooks & Castles".

    Sample data:
    {json.dumps(sample_data, indent=2)}

    Your response should be a JSON object with three keys: "summary", "insights", and "recommendations".
    The "insights" and "recommendations" keys should contain a list of strings.
    '''

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes data for a streetwear brand and returns responses in JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        analysis_json = response.choices[0].message.content
        analysis_data = json.loads(analysis_json)
        analysis_data["analysis_timestamp"] = datetime.now().isoformat()
        return analysis_data

    except Exception as e:
        return {
            "error": f"Failed to get AI analysis: {e}",
            "status": "error"
        }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "database_available": DB_AVAILABLE,
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "upload_directory": os.path.exists(UPLOAD_DIR),
        "max_file_size_mb": 100
    }

@router.post("/upload")
async def upload_intelligence_file(
    file: UploadFile = File(...),
    source: str = Form("manual_upload"),
    brand: str = Form("Crooks & Castles"),
    description: Optional[str] = Form(None)
):
    """Upload with DETAILED DIAGNOSTICS"""
    
    upload_log = []
    
    try:
        upload_log.append("Starting upload process...")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        upload_log.append(f"File received: {file.filename}")
        
        # Stream file to disk safely
        max_size = 100 * 1024 * 1024  # 100MB
        file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_hash}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        upload_log.append(f"Saving to: {file_path}")
        
        total_size = 0
        with open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > max_size:
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail=f"File too large (max 100MB)")
                f.write(chunk)
        
        upload_log.append(f"File saved successfully: {total_size:,} bytes")
        
        # Generate AI analysis
        upload_log.append("Generating AI analysis...")
        ai_analysis = generate_ai_analysis(file_path)
        upload_log.append(f"AI analysis generated: {len(ai_analysis.get('insights', []))} insights")
        
        # Database save with detailed diagnostics
        database_saved = False
        database_error = None
        inserted_id = None
        database_log = []
        
        try:
            upload_log.append("Starting database save...")
            
            if not DB_AVAILABLE:
                database_error = "Database not available"
                database_log.append("DB_AVAILABLE is False")
            elif not engine:
                database_error = "Database engine not created"
                database_log.append("Engine is None")
            else:
                database_log.append("Database connection available")
                
                # Convert analysis to JSON string
                analysis_json = json.dumps(ai_analysis, ensure_ascii=False, indent=None)
                database_log.append(f"Analysis JSON created: {len(analysis_json)} characters")
                
                with engine.connect() as db:
                    database_log.append("Database connection opened")
                    
                    with db.begin():
                        database_log.append("Transaction started")
                        
                        result = db.execute(text("""
                            INSERT INTO intelligence_files 
                            (filename, source, brand, file_path, insights, uploaded_at)
                            VALUES (:filename, :source, :brand, :file_path, :insights, :uploaded_at)
                            RETURNING id
                        """), {
                            "filename": file.filename,
                            "source": source,
                            "brand": brand,
                            "file_path": file_path,
                            "insights": analysis_json,
                            "uploaded_at": datetime.now()
                        })
                        
                        database_log.append("INSERT executed")
                        
                        inserted_id = result.fetchone()[0]
                        database_saved = True
                        database_log.append(f"Record inserted with ID: {inserted_id}")
                        
                database_log.append("Transaction committed successfully")
                        
        except Exception as db_error:
            database_error = str(db_error)
            database_log.append(f"DATABASE ERROR: {database_error}")
            database_log.append(f"TRACEBACK: {traceback.format_exc()}")
            upload_log.append(f"Database save failed: {database_error}")
        
        upload_log.append("Upload process completed")
        
        return {
            "message": "File uploaded and AI analysis completed",
            "filename": file.filename,
            "file_size": total_size,
            "file_size_mb": round(total_size / (1024 * 1024), 1),
            "file_path": file_path,
            "database_saved": database_saved,
            "database_error": database_error,
            "database_id": inserted_id,
            "ai_analysis": ai_analysis,
            "upload_timestamp": datetime.now().isoformat(),
            "upload_log": upload_log,
            "database_log": database_log
        }
        
    except Exception as e:
        upload_log.append(f"UPLOAD ERROR: {str(e)}")
        upload_log.append(f"TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={
            "error": f"Upload failed: {str(e)}",
            "upload_log": upload_log
        })




@router.get("/files")
async def list_intelligence_files():
    """List all intelligence files from the database."""
    if not DB_AVAILABLE or not engine:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        with engine.connect() as db:
            result = db.execute(text("SELECT id, filename, source, brand, file_path, insights, uploaded_at FROM intelligence_files ORDER BY uploaded_at DESC"))
            files = result.fetchall()
            return [
                {
                    "id": row[0],
                    "filename": row[1],
                    "source": row[2],
                    "brand": row[3],
                    "file_path": row[4],
                    "insights": json.loads(row[5]),
                    "uploaded_at": row[6],
                }
                for row in files
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {e}")

