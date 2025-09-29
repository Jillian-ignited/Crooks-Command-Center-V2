# backend/routers/upload_sidecar.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter()

_JOBS: Dict[str, Dict[str, Any]] = {}

@router.get("/")
def status():
    return {"ok": True, "module": "upload_sidecar", "jobs": len(_JOBS)}

@router.get("/jobs")
def list_jobs():
    return {"ok": True, "count": len(_JOBS), "jobs": list(_JOBS.values())[:50]}

@router.post("/webhook")
async def webhook(request: Request):
    """Generic webhook for storage/CDN callbacks."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    job_id = body.get("job_id") or body.get("id") or f"job-{len(_JOBS)+1}"
    _JOBS[job_id] = {"id": job_id, "payload": body, "received_at": datetime.utcnow().isoformat()}
    return {"ok": True, "stored": job_id}

@router.post("/upload")
async def upload(file: UploadFile = File(...), bucket: Optional[str] = Form(None)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    job_id = f"sidecar-{len(_JOBS)+1}"
    _JOBS[job_id] = {
        "id": job_id,
        "filename": file.filename,
        "size": len(data),
        "bucket": bucket or "default",
        "ts": datetime.utcnow().isoformat(),
    }
    return {"ok": True, "job_id": job_id, "filename": file.filename, "size": len(data), "bucket": bucket or "default"}
