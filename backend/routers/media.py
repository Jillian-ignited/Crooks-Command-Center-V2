# backend/routers/media.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import List, Optional
import shutil
import json
from datetime import datetime

router = APIRouter()

MEDIA_STORAGE = Path("backend/media_storage")
MEDIA_STORAGE.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_media(files: List[UploadFile] = File(...)):
    """Upload media files"""
    uploaded = []
    for file in files:
        file_path = MEDIA_STORAGE / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded.append({
            "filename": file.filename,
            "size": file_path.stat().st_size,
            "uploaded_at": datetime.now().isoformat()
        })
    return {"uploaded": uploaded, "count": len(uploaded)}

@router.get("/list")
async def list_media(limit: int = 50):
    """List all media files"""
    files = []
    for file_path in MEDIA_STORAGE.glob("*"):
        if file_path.is_file():
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    return {"files": files[:limit], "total": len(files)}

@router.get("/assets")
async def get_assets(category: Optional[str] = None):
    """Get assets, optionally filtered by category"""
    return {
        "assets": [],
        "categories": ["images", "videos", "documents"],
        "total": 0
    }
