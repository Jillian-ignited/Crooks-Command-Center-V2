# backend/routers/intelligence.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
import shutil
import uuid
import traceback

from backend.database import get_db
from backend.models import IntelligenceFile

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads/intelligence")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def process_file_async(file_id: int, file_path: str):
    """Background task to process uploaded file with AI"""
    from backend.database import SessionLocal
    from backend.file_parser import parse_uploaded_file
    from backend.ai_processor import analyze_social_data
    
    db = SessionLocal()
    try:
        # Parse file
        data, source_type = parse_uploaded_file(file_path)
        
        if not data:
            print(f"[intelligence] No data parsed from file {file_id}")
            return
        
        print(f"[intelligence] Parsed {len(data)} records from file {file_id}")
        
        # Analyze with AI
        insights = analyze_social_data(data, source_type)
        
        print(f"[intelligence] Generated insights for file {file_id}")
        
        # Update database
        db_file = db.query(IntelligenceFile).filter(IntelligenceFile.id == file_id).first()
        if db_file:
            db_file.processed = True
            db_file.insights = insights
            db.commit()
            print(f"[intelligence] Successfully processed file {file_id}")
    
    except Exception as e:
        print(f"[intelligence] Error processing file {file_id}: {e}")
        traceback.print_exc()
    finally:
        db.close()

@router.get("/summary")
async def get_intelligence_summary(db: Session = Depends(get_db)):
    try:
        total_files = db.query(IntelligenceFile).count()
        processed = db.query(IntelligenceFile).filter(IntelligenceFile.processed == True).count()
        
        latest = db.query(IntelligenceFile).filter(
            IntelligenceFile.processed == True
        ).order_by(IntelligenceFile.uploaded_at.desc()).first()
        
        return {
            "files_processed": processed,
            "total_files": total_files,
            "insights": latest.insights if latest and latest.insights else {},
            "last_updated": latest.uploaded_at.isoformat() if latest else None
        }
    except Exception as e:
        print(f"[intelligence] Error in summary: {e}")
        return {
            "files_processed": 0,
            "total_files": 0,
            "insights": {},
            "last_updated": None,
            "error": str(e)
        }

@router.post("/upload")
async def upload_intelligence(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload intelligence file and process with AI in background"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.csv', '.json', '.jsonl', '.xlsx', '.xls']:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_name
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"[intelligence] Saved file to {file_path}")
        
        # Save to database
        db_file = IntelligenceFile(
            filename=file.filename,
            source=source or "apify_scrape",
            brand=brand or "Crooks & Castles",
            file_path=str(file_path),
            processed=False
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        print(f"[intelligence] Created database record ID {db_file.id}")
        
        # Process in background
        background_tasks.add_task(process_file_async, db_file.id, str(file_path))
        
        return {
            "id": db_file.id,
            "filename": file.filename,
            "source": source,
            "brand": brand,
            "status": "processing",
            "message": "File uploaded successfully. AI analysis in progress..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[intelligence] Upload error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/files")
async def list_intelligence_files(db: Session = Depends(get_db)):
    try:
        files = db.query(IntelligenceFile).order_by(IntelligenceFile.uploaded_at.desc()).all()
        return {
            "files": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "source": f.source,
                    "brand": f.brand,
                    "processed": f.processed,
                    "uploaded_at": f.uploaded_at.isoformat(),
                    "has_insights": bool(f.insights)
                } for f in files
            ]
        }
    except Exception as e:
        print(f"[intelligence] Error listing files: {e}")
        return {"files": [], "error": str(e)}

@router.get("/files/{file_id}")
async def get_intelligence_file(file_id: int, db: Session = Depends(get_db)):
    try:
        file = db.query(IntelligenceFile).filter(IntelligenceFile.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "id": file.id,
            "filename": file.filename,
            "source": file.source,
            "brand": file.brand,
            "processed": file.processed,
            "insights": file.insights,
            "uploaded_at": file.uploaded_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[intelligence] Error getting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upload")
async def intelligence_upload_page():
    return {"message": "Use POST to upload files"}

@router.get("/sources")
async def get_intelligence_sources():
    return {
        "sources": [
            {"id": "apify_instagram", "name": "Instagram (Apify)"},
            {"id": "apify_tiktok", "name": "TikTok (Apify)"},
            {"id": "apify_hashtag", "name": "Hashtag Analysis (Apify)"},
            {"id": "manual", "name": "Manual Upload"}
        ]
    }
