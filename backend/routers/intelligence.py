# backend/routers/intelligence.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/brands", name="brands")
def brands():
    return {"ok": True, "brands": []}

@router.get("/summary", name="summary")
def summary():
    return {"ok": True, "summary": "No data yet."}

# === Upload endpoints ===

# Primary POST handler (multipart file)
@router.post("/upload", name="upload")
async def upload(file: UploadFile = File(...)):
    # Read to count bytes; replace with real processing as needed
    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
    return {"ok": True, "filename": file.filename, "size": size}

# Accept trailing slash too
@router.post("/upload/", include_in_schema=False)
async def upload_alias(file: UploadFile = File(...)):
    return await upload(file)

# Helpful GET so accidental GETs don’t 404
@router.get("/upload", include_in_schema=False)
def upload_get_hint():
    return JSONResponse(
        {"detail": "Use POST multipart/form-data to /api/intelligence/upload with field name 'file'."},
        status_code=405
    )
