# backend/routers/media.py
from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

# MEDIA_ROOT relative to project layout
MEDIA_ROOT = Path(__file__).resolve().parents[2] / "backend" / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

def _collect_assets():
    items = []
    for p in MEDIA_ROOT.rglob("*"):
        if p.is_file():
            rel = p.relative_to(MEDIA_ROOT).as_posix()
            items.append({
                "name": p.name,
                "path": f"/media/{rel}",   # served by StaticFiles in main.py
                "size": p.stat().st_size,
            })
    return items

@router.get("/", name="media_root")
def media_root():
    return {"ok": True, "message": "Media API root"}

@router.get("/library", name="media_library")
def media_library():
    """Canonical endpoint to list assets."""
    return JSONResponse({"assets": _collect_assets()})

@router.get("/assets", name="media_assets")
def media_assets():
    """Alias for compatibility with existing UI expecting /assets."""
    return media_library()

@router.get("/analytics", name="media_analytics")
def media_analytics():
    assets = _collect_assets()
    total_size = sum(a["size"] for a in assets)
    ext_set = {".jpg",".jpeg",".png",".gif",".mp4",".pdf",".webp",".svg",".mov"}
    ext_counts = {ext: 0 for ext in ext_set}
    for a in assets:
        lower = a["name"].lower()
        for ext in ext_set:
            if lower.endswith(ext):
                ext_counts[ext] += 1
                break
    return {"count": len(assets), "total_size": total_size, "by_ext": ext_counts}

@router.post("/upload", name="media_upload")
async def media_upload(file: UploadFile = File(...)):
    target = MEDIA_ROOT / file.filename
    with target.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return {"ok": True, "filename": file.filename, "path": f"/media/{file.filename}"}
