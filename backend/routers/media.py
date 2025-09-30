# backend/routers/media.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List, Optional
import shutil
import uuid
from datetime import datetime

from backend.database import get_db
from backend.models import MediaFile

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_media(
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Upload media files and save to database"""
    upload_files = []
    if files:
        upload_files = files
    elif file:
        upload_files = [file]
    else:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded = []
    for upload_file in upload_files:
        if upload_file.filename:
            # Generate unique filename
            file_ext = Path(upload_file.filename).suffix
            unique_name = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_name
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            # Save to database
            db_file = MediaFile(
                filename=unique_name,
                original_filename=upload_file.filename,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                mime_type=upload_file.content_type,
                uploaded_at=datetime.now(),
                meta_data={}
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            uploaded.append({
                "id": db_file.id,
                "filename": upload_file.filename,
                "size": db_file.file_size,
                "uploaded_at": db_file.uploaded_at.isoformat()
            })
    
    return {"uploaded": uploaded, "count": len(uploaded), "status": "success"}

@router.get("/list")
async def list_media(limit: int = 50, db: Session = Depends(get_db)):
    """List all media files from database"""
    files = db.query(MediaFile).order_by(MediaFile.uploaded_at.desc()).limit(limit).all()
    
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "size": f.file_size,
                "uploaded_at": f.uploaded_at.isoformat(),
                "mime_type": f.mime_type
            } for f in files
        ],
        "total": db.query(MediaFile).count()
    }

@router.get("/assets")
async def get_assets(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Get assets from database"""
    query = db.query(MediaFile)
    if category:
        query = query.filter(MediaFile.category == category)
    
    assets = query.all()
    
    return {
        "assets": [
            {
                "id": a.id,
                "filename": a.original_filename,
                "category": a.category,
                "size": a.file_size
            } for a in assets
        ],
        "categories": ["images", "videos", "documents"],
        "total": len(assets)
    }
