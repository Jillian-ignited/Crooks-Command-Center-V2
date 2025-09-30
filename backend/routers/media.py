# backend/routers/media.py
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Where to store uploaded media (must be mounted in main.py at /media)
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "backend/media")).resolve()
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

router = APIRouter()

def _asset_url(name: str) -> str:
    # Served by StaticFiles mounted at /media in main.py
    return f"/media/{name}"

@router.get("/", summary="Media root")
def media_root():
    return {"ok": True, "media_root": str(MEDIA_ROOT)}

@router.get("/library", summary="(deprecated) list assets")
def media_library():
    return media_assets()

@router.get("/assets", summary="List uploaded assets")
def media_assets():
    if not MEDIA_ROOT.exists():
        return {"ok": True, "assets": []}
    items: List[dict] = []
    for p in sorted(MEDIA_ROOT.iterdir()):
        if p.is_file():
            st = p.stat()
            items.append({
                "filename": p.name,
                "size": st.st_size,
                "modified": int(st.st_mtime),
                "url": _asset_url(p.name),
            })
    return {"ok": True, "count": len(items), "assets": items}

@router.post("/upload", summary="Upload a media file (multipart field name = file)")
async def media_upload(file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    # Normalize filename (very light)
    safe_name = Path(file.filename).name.replace("..", "_")
    dest = MEDIA_ROOT / safe_name
    data = await file.read()
    dest.write_bytes(data)
    return JSONResponse({
        "ok": True,
        "filename": safe_name,
        "size": len(data),
        "url": _asset_url(safe_name),
    })
