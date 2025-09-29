from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional, Dict, Any

# NOTE: This is mounted under /api/intelligence by main.py’s prefix rules
router = APIRouter(tags=["intelligence"])

def _ok(payload: Dict[str, Any]) -> Dict[str, Any]:
    base = {"ok": True}; base.update(payload); return base

@router.get("")
@router.get("/")
def root():
    return {"ok": True, "router": "intelligence-upload-sidecar"}

@router.post("/upload")
async def upload(request: Request, file: Optional[UploadFile] = File(None), kind: Optional[str] = Form(None)):
    ctype = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" in ctype:
        if not file or not file.filename: raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data: raise HTTPException(status_code=400, detail="Empty file")
        return _ok({"mode":"multipart","filename":file.filename,"size":len(data),"mime":file.content_type or "application/octet-stream","kind":kind or "unknown"})
    if "application/json" in ctype:
        body = await request.json()
        content = body.get("content")
        if not isinstance(content, str) or not content: raise HTTPException(status_code=400, detail="Missing/invalid 'content'")
        return _ok({"mode":"json","filename":body.get("filename","payload.txt"),"size":len(content.encode("utf-8","ignore")),"mime":"text/plain","kind":body.get("kind") or "unknown"})
    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {ctype}")
