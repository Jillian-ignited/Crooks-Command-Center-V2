from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from typing import Optional, Dict, Any
from uuid import uuid4

router = APIRouter(tags=["ingest"])

@router.get("")
@router.get("/")
def root():
    return {"ok": True, "router": "ingest"}

@router.post("/upload")
async def upload(request: Request, file: Optional[UploadFile] = File(None), source: Optional[str] = Form(None), notes: Optional[str] = Form(None)) -> Dict[str, Any]:
    ctype = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" in ctype:
        if not file: raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data: raise HTTPException(status_code=400, detail="Empty file")
        return {"ok": True, "mode": "multipart", "job_id": f"ing_{uuid4().hex[:10]}", "filename": file.filename, "size": len(data), "mime": file.content_type or "application/octet-stream", "source": source, "notes": notes}
    if "application/json" in ctype:
        body = await request.json()
        content = body.get("content")
        if not isinstance(content, str) or not content: raise HTTPException(status_code=400, detail="Missing/invalid 'content'")
        return {"ok": True, "mode": "json", "job_id": f"ing_{uuid4().hex[:10]}", "size": len(content.encode()), "source": body.get("source"), "notes": body.get("notes")}
    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {ctype}")
