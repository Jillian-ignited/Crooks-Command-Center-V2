# backend/routers/intelligence.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
import shutil
import uuid

from backend.database import get_db
from backend.models import IntelligenceFile
from backend.file_parser import parse_uploaded_file
from backend.ai_processor import analyze_social_data

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads/intelligence")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def process_file_async(file_id: int, file_path: str, db: Session):
    """Background task to process uploaded file with AI"""
    try:
        # Parse file
        data, source_type = parse_uploaded_file(file_path)
        
        if not data:
            return
        
        # Analyze with AI
        insights = analyze_social_data(data, source_type)
        
        # Update database
        db_file = db.query(IntelligenceFile).filter(IntelligenceFile.id == file_id).first()
        if db_file:
            db_file.processed = True
            db_file.insights = insights
            db.commit()
            print(f"[intelligence] Processed file {file_id} with {len(data)} records")
    
    except Exception as e:
        print(f"[intelligence] Error processing file {file_id}: {e}")

@router.get("/summary")
async def get_intelligence_summary(db: Session = Depends(get_db)):
    total_files = db.query(IntelligenceFile).count()
    processed = db.query(IntelligenceFile).filter(IntelligenceFile.processed == True).count()
    
    # Get latest insights
    latest = db.query(IntelligenceFile).filter(
        IntelligenceFile.processed == True
    ).order_by(IntelligenceFile.uploaded_at.desc()).first()
    
    return {
        "files_processed": processed,
        "total_files": total_files,
        "insights": latest.insights if latest else {},
        "last_updated": latest.uploaded_at.isoformat() if latest else None
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
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_name
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
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
    
    # Process in background
    background_tasks.add_task(process_file_async, db_file.id, str(file_path), db)
    
    return {
        "id": db_file.id,
        "filename": file.filename,
        "source": source,
        "brand": brand,
        "status": "processing",
        "message": "File uploaded successfully. AI analysis in progress..."
    }

@router.get("/files")
async def list_intelligence_files(db: Session = Depends(get_db)):
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

@router.get("/files/{file_id}")
async def get_intelligence_file(file_id: int, db: Session = Depends(get_db)):
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
