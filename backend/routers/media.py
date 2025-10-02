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

# --- New --- 
from fastapi.staticfiles import StaticFiles

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- New: Mount the uploads directory to be served statically ---
router.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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

    if not upload_files:
        raise HTTPException(status_code=400, detail="No files sent")

    saved_files = []
    for upload_file in upload_files:
        # Generate a unique filename
        unique_id = uuid.uuid4()
        file_extension = Path(upload_file.filename).suffix
        unique_filename = f"{unique_id}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        # --- New: Generate a public URL for the file ---
        public_url = f"/api/media/uploads/{unique_filename}"

        # Save file metadata to the database
        db_file = MediaFile(
            original_filename=upload_file.filename,
            file_path=str(file_path),
            public_url=public_url,  # Save the public URL
            file_size=file_path.stat().st_size,
            mime_type=upload_file.content_type,
            uploaded_at=datetime.utcnow()
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        saved_files.append(db_file)

    return {
        "message": f"{len(saved_files)} files uploaded successfully",
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "size": f.file_size,
                "url": f.public_url  # Return the public URL
            } for f in saved_files
        ]
    }

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
                "mime_type": f.mime_type,
                "url": f.public_url  # Return the public URL
            }
            for f in files
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
                "size": a.file_size,
                "url": a.public_url  # Return the public URL
            } for a in assets
        ],
        "categories": ["images", "videos", "documents"],
        "total": len(assets)
    }


