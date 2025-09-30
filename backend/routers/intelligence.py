# backend/routers/intelligence.py
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

router = APIRouter()

@router.get("/summary")
async def get_intelligence_summary():
    return {"files_processed": 0, "insights": [], "last_updated": None}

@router.post("/upload")
async def upload_intelligence(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    brand: Optional[str] = Form(None)
):
    """Upload intelligence file"""
    return {
        "filename": file.filename,
        "source": source,
        "brand": brand,
        "status": "processed",
        "insights_extracted": 0
    }

@router.get("/upload")
async def intelligence_upload_page():
    """GET endpoint for upload page"""
    return {"message": "Use POST to upload files"}

@router.get("/files")
async def list_intelligence_files():
    return {"files": []}

@router.get("/files/{name}")
async def get_intelligence_file(name: str):
    return {"filename": name, "content": "File content here"}

@router.get("/sources")
async def get_intelligence_sources():
    """Get available intelligence sources"""
    return {
        "sources": [
            {"id": "social", "name": "Social Media"},
            {"id": "news", "name": "News Articles"},
            {"id": "trends", "name": "Trend Reports"},
            {"id": "competitor", "name": "Competitor Analysis"}
        ]
    }
