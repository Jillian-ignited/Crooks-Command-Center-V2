# backend/routers/intelligence.py
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

# Storage folder for intelligence uploads
ROOT = Path(__file__).resolve().parents[2]  # project root
INTEL_DIR = ROOT / "backend" / "storage" / "intelligence"
INTEL_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()


# ---------- Simple info endpoints (optional) ----------
@router.get("/brands", name="brands")
def brands():
    return {"ok": True, "brands": []}

@router.get("/summary", name="summary")
def summary():
    return {"ok": True, "summary": "No data yet."}


# ---------- Upload endpoints ----------
@router.post("/upload", name="intelligence_upload")
async def intelligence_upload(file: UploadFile = File(...)):
    """
    Accepts multipart/form-data with field name 'file'.
    Saves to backend/storage/intelligence/<filename>.
    """
    # Normalize filename (avoid path traversal)
    safe_name = os.path.basename(file.filename) or "upload.bin"
    target = INTEL_DIR / safe_name

    size = 0
    # Write in chunks to avoid loading entire file into memory
    with target.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            out.write(chunk)
            size += len(chunk)

    return {
        "ok": True,
        "filename": safe_name,
        "size": size,
        # This is a local server path for your backend; you can serve from here if you expose a route.
        "path": f"/api/intelligence/files/{safe_name}"
    }

# Accept trailing slash too
@router.post("/upload/", include_in_schema=False)
async def intelligence_upload_alias(file: UploadFile = File(...)):
    return await intelligence_upload(file)

# Helpful GET so accidental GETs don’t 404
@router.get("/upload", include_in_schema=False)
def intelligence_upload_get_hint():
    return JSONResponse(
        {"detail": "Use POST multipart/form-data to /api/intelligence/upload with field name 'file'."},
        status_code=405
    )


# ---------- Simple file browsing ----------
@router.get("/files", name="intelligence_files")
def intelligence_files() -> dict:
    """List uploaded files (name, size, href)."""
    items: List[dict] = []
    for p in INTEL_DIR.glob("*"):
        if p.is_file():
            items.append({
                "name": p.name,
                "size": p.stat().st_size,
                "href": f"/api/intelligence/files/{p.name}",
            })
    items.sort(key=lambda x: x["name"].lower())
    return {"ok": True, "items": items}

@router.get("/files/{name}", name="intelligence_file_get")
def intelligence_file_get(name: str):
    """Serve a specific uploaded file back."""
    safe_name = os.path.basename(name)
    target = INTEL_DIR / safe_name
    if not target.is_file():
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    # Let Starlette infer content-type from filename
    return FileResponse(path=str(target), filename=safe_name)
