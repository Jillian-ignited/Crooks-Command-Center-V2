from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional

router = APIRouter(tags=["intelligence"])

@router.post("/upload")
async def upload_data(
    request: Request,
    file: Optional[UploadFile] = File(None),
    kind: Optional[str] = Form(None),
):
    ctype = request.headers.get("content-type", "")
    # multipart
    if "multipart/form-data" in ctype:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")
        return {"ok": True, "mode": "multipart", "filename": file.filename, "size": len(data), "kind": kind}

    # JSON
    if "application/json" in ctype:
        body = await request.json()
        content = body.get("content")
        if content is None or not isinstance(content, str):
            raise HTTPException(status_code=400, detail="Missing/invalid 'content'")
        data = content.encode("utf-8", errors="ignore")
        return {"ok": True, "mode": "json", "filename": body.get("filename", "payload.txt"), "size": len(data), "kind": body.get("kind")}

    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {ctype}")
