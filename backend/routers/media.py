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
                "id": file.id,
                "filename": file.original_filename,
                "url": file.public_url,
                "size": file.file_size,
                "uploaded_at": file.uploaded_at
            }
            for file in saved_files
        ]
    }

@router.get("/assets")
async def get_media_assets(db: Session = Depends(get_db)):
    """Get all media assets from database"""
    
    try:
        # Query all media files from database
        media_files = db.query(MediaFile).order_by(MediaFile.uploaded_at.desc()).all()
        
        assets = []
        for media_file in media_files:
            assets.append({
                "id": media_file.id,
                "filename": media_file.original_filename,
                "url": media_file.public_url,
                "file_path": media_file.file_path,
                "file_size": media_file.file_size,
                "mime_type": media_file.mime_type,
                "uploaded_at": media_file.uploaded_at.isoformat() if media_file.uploaded_at else None,
                "is_clickable": True,
                "download_url": media_file.public_url
            })
        
        return {
            "assets": assets,
            "total_assets": len(assets),
            "data_source": "database",
            "status": "success"
        }
        
    except Exception as e:
        print(f"[Media] Assets query error: {e}")
        return {
            "assets": [],
            "total_assets": 0,
            "data_source": "error",
            "status": "error",
            "error": str(e)
        }

@router.get("/list")
async def list_media_files(db: Session = Depends(get_db)):
    """List all media files with metadata"""
    
    try:
        media_files = db.query(MediaFile).order_by(MediaFile.uploaded_at.desc()).all()
        
        files = []
        for media_file in media_files:
            files.append({
                "id": media_file.id,
                "original_filename": media_file.original_filename,
                "public_url": media_file.public_url,
                "file_size": media_file.file_size,
                "mime_type": media_file.mime_type,
                "uploaded_at": media_file.uploaded_at.isoformat() if media_file.uploaded_at else None
            })
        
        return {
            "files": files,
            "total_files": len(files),
            "upload_directory": str(UPLOAD_DIR),
            "status": "success"
        }
        
    except Exception as e:
        print(f"[Media] File list error: {e}")
        return {
            "files": [],
            "total_files": 0,
            "status": "error",
            "error": str(e)
        }

@router.get("/health")
def media_health_check():
    """Health check for media module"""
    return {
        "status": "healthy",
        "upload_directory": str(UPLOAD_DIR),
        "directory_exists": UPLOAD_DIR.exists(),
        "directory_writable": UPLOAD_DIR.is_dir()
    }
