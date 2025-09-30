# backend/routers/intelligence.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
import shutil
import uuid

from backend.database import get_db
from backend.models import IntelligenceFile

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads/intelligence")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/summary")
async def get_intelligence_summary(db: Session = Depends(get_db)):
    total_files = db.query(IntelligenceFile).count()
    processed = db.query(IntelligenceFile).filter(IntelligenceFile.processed == True).count()
    
    return {
        "files_processed": processed,
        "total_files": total_files,
        "insights": [],
        "last_updated": None
    }

@router.post("/upload")
async def upload_intelligence(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload intelligence file and save to database"""
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
        source=source,
        brand=brand,
        file_path=str(file_path),
        processed=False
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return {
        "id": db_file.id,
        "filename": file.filename,
        "source": source,
        "brand": brand,
        "status": "uploaded",
        "insights_extracted": 0
    }

@router.get("/files")
async def list_intelligence_files(db: Session = Depends(get_db)):
    files = db.query(IntelligenceFile).all()
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "source": f.source,
                "brand": f.brand,
                "processed": f.processed,
                "uploaded_at": f.uploaded_at.isoformat()
            } for f in files
        ]
    }

@router.get("/upload")
async def intelligence_upload_page():
    return {"message": "Use POST to upload files"}

@router.get("/files/{name}")
async def get_intelligence_file(name: str):
    return {"filename": name, "content": "File content here"}

@router.get("/sources")
async def get_intelligence_sources():
    return {
        "sources": [
            {"id": "social", "name": "Social Media"},
            {"id": "news", "name": "News Articles"},
            {"id": "trends", "name": "Trend Reports"},
            {"id": "competitor", "name": "Competitor Analysis"}
        ]
    }
