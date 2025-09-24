from pathlib import Path
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict
from models.schemas import UploadAck, IntelligenceRequest, IntelligenceReport
from services.scraper import save_uploads
from services.analyzer import brand_intelligence

router = APIRouter()   # <-- this line must come BEFORE any @router decorators

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

# ✅ New endpoints go *below* router = APIRouter()

@router.get("/uploads")
async def list_uploads() -> Dict[str, list]:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return {"files": files}

@router.delete("/upload/{filename}")
async def delete_upload(filename: str) -> Dict[str, str]:
    dest = Path(UPLOAD_DIR) / filename
    try:
        dest = dest.resolve(strict=False)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not str(dest).startswith(str(Path(UPLOAD_DIR).resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not dest.exists():
        raise HTTPException(status_code=404, detail="File not found")
    dest.unlink()
    return {"deleted": filename}

@router.post("/report", response_model=IntelligenceReport)
async def report(req: IntelligenceRequest):
    rep = brand_intelligence(req.brands, req.lookback_days)
    return rep
