# backend/routers/intelligence.py
from __future__ import annotations
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse, FileResponse

from backend.services import intelligence_store as store

ROOT = Path(__file__).resolve().parents[2]
INTEL_DIR = ROOT / "backend" / "storage" / "intelligence"
INTEL_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

@router.get("/brands", name="brands")
def brands():
    return {"ok": True, "items": store.list_brands()}

@router.get("/summary", name="summary")
def summary():
    ov = store.executive_overview()
    return {"ok": True, **ov}

@router.post("/upload", name="intelligence_upload")
async def intelligence_upload(file: UploadFile = File(...), parse: bool = Query(True)):
    safe = os.path.basename(file.filename) or "upload.bin"
    target = INTEL_DIR / safe

    size = 0
    with target.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk: break
            out.write(chunk); size += len(chunk)

    # If it's a CSV, parse it into the store
    summary = None
    if parse and safe.lower().endswith(".csv"):
        summary = store.import_csv(target)

    return {"ok": True, "filename": safe, "size": size, "path": f"/api/intelligence/files/{safe}", "parsed": bool(summary), "import": summary}

@router.post("/upload/", include_in_schema=False)
async def intelligence_upload_alias(file: UploadFile = File(...), parse: bool = Query(True)):
    return await intelligence_upload(file, parse)

@router.get("/upload", include_in_schema=False)
def intelligence_upload_get_hint():
    return JSONResponse({"detail":"Use POST multipart/form-data to /api/intelligence/upload (field 'file')."}, status_code=405)

@router.get("/files", name="intelligence_files")
def intelligence_files():
    items = []
    for p in INTEL_DIR.glob("*"):
        if p.is_file():
            items.append({"name": p.name, "size": p.stat().st_size, "href": f"/api/intelligence/files/{p.name}"})
    items.sort(key=lambda x: x["name"].lower())
    return {"ok": True, "items": items}

@router.get("/files/{name}", name="intelligence_file_get")
def intelligence_file_get(name: str):
    safe = os.path.basename(name)
    target = INTEL_DIR / safe
    if not target.is_file():
        return JSONResponse({"detail":"Not Found"}, status_code=404)
    return FileResponse(str(target), filename=safe)
