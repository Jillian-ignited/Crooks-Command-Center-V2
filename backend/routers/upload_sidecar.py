# backend/routers/upload_sidecar.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional

router = APIRouter()

@router.post("/upload")
async def upload_data(
    request: Request,
    file: Optional[UploadFile] = File(None),   # supports FormData
    kind: Optional[str] = Form(None),          # optional metadata
):
    """
    Accepts either:
      1) multipart/form-data  -> file=<UploadFile>, kind=<str>
      2) application/json     -> {"content": "<base64 or raw text>", "filename": "...", "kind": "..."}
    Returns a minimal receipt; delegate heavy lifting to your existing pipeline.
    """
    ctype = request.headers.get("content-type", "")

    # Case 1: multipart/form-data
    if "multipart/form-data" in ctype:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")

        # >>> Hook into your existing pipeline here <<<
        # e.g., job_id = await pipeline.ingest_bytes(data, filename=file.filename, kind=kind)
        job_id = None

        return {
            "ok": True,
            "ingest_mode": "multipart",
            "filename": file.filename,
            "size": len(data),
            "kind": kind,
            "job_id": job_id,
        }

    # Case 2: JSON body (fallback)
    if "application/json" in ctype:
        body = await request.json()
        content = body.get("content")
        filename = body.get("filename", "payload.txt")
        kind_json = body.get("kind")
        if content is None:
            raise HTTPException(status_code=400, detail="Missing 'content' in JSON body")
        if isinstance(content, str):
            data = content.encode("utf-8", errors="ignore")
        else:
            raise HTTPException(status_code=400, detail="'content' must be a string")

        # >>> Hook into your existing pipeline here <<<
        # job_id = await pipeline.ingest_bytes(data, filename=filename, kind=kind_json)
        job_id = None

        return {
            "ok": True,
            "ingest_mode": "json",
            "filename": filename,
            "size": len(data),
            "kind": kind_json,
            "job_id": job_id,
        }

    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {ctype}")
