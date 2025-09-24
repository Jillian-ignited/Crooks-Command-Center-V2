import os
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form
from ..models.schemas import UploadAck, IntelligenceRequest, IntelligenceReport
from ..services.scraper import save_uploads
from ..services.analyzer import brand_intelligence

router = APIRouter()

UPLOAD_DIR = "data/uploads"

@router.post("/upload", response_model=UploadAck)
async def upload_files(files: List[UploadFile] = File(...)):
    saved = []
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for f in files:
        dest = os.path.join(UPLOAD_DIR, f.filename)
        content = await f.read()
        with open(dest, "wb") as out:
            out.write(content)
        saved.append(dest)
    save_uploads(saved)
    return {"saved_files": [os.path.basename(s) for s in saved]}

@router.post("/report", response_model=IntelligenceReport)
async def report(req: IntelligenceRequest):
    rep = brand_intelligence(req.brands, req.lookback_days)
    return rep
