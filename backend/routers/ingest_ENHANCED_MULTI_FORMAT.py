from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from typing import Optional, Dict, Any, List
from uuid import uuid4

router = APIRouter(tags=["ingest"])

SUPPORTED: List[str] = ["text/csv", "application/json", "text/plain"]

@router.post("/upload")
async def upload(
    request: Request,
    file: Optional[UploadFile] = File(None),
    source: Optional[str] = Form(None),    # e.g., "exec", "catalog", "social"
    notes: Optional[str] = Form(None),
) -> Dict[str, Any]:
    ctype = request.headers.get("content-type", "")
    # multipart path
    if "multipart/form-data" in ctype:
        if not file:
            raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")
        mime = file.content_type or "application/octet-stream"
        if mime not in SUPPORTED:
            # still accept, just flag
            pass
        job_id = f"ing_{uuid4().hex[:10]}"
        # TODO: enqueue job with 'data', 'source', 'notes'
        return {"ok": True, "mode": "multipart", "job_id": job_id, "filename": file.filename, "size": len(data), "mime": mime, "source": source, "notes": notes}

    # JSON path
    if "application/json" in ctype:
        body = await request.json()
        payload = body.get("content")
        if not isinstance(payload, str) or not payload:
            raise HTTPException(status_code=400, detail="Missing/invalid 'content' string")
        job_id = f"ing_{uuid4().hex[:10]}"
        return {"ok": True, "mode": "json", "job_id": job_id, "size": len(payload.encode()), "source": body.get("source"), "notes": body.get("notes")}

    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {ctype}")

@router.get("/status/{job_id}")
def status(job_id: str) -> Dict[str, Any]:
    # Stub: return fake progressing status
    return {"job_id": job_id, "state": "queued", "progress": 5}

@router.get("/overview")
async def get_overview() -> Dict[str, Any]:
    """Get data ingestion overview"""
    try:
        from datetime import datetime
        
        # Mock data - replace with actual file analysis
        return {
            "success": True,
            "overview": {
                "total_files": 0,
                "total_records": 0,
                "processed_files": 0,
                "data_by_type": {
                    "instagram_data": 0,
                    "tiktok_data": 0,
                    "social_media_data": 0,
                    "shopify_data": 0,
                    "ecommerce_data": 0,
                    "agency_data": 0
                },
                "storage_used": 0,
                "last_upload": 0,
                "supported_formats": ["JSON", "JSONL", "CSV", "Excel (.xlsx, .xls)"],
                "data_sources": [
                    "Social Media (Instagram, TikTok, Twitter)",
                    "E-commerce (Shopify, WooCommerce)",
                    "Agency Reports (Projects, Deliverables)",
                    "Analytics (Google Analytics, Facebook Insights)"
                ],
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {e}")
