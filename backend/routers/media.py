# backend/routers/media.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

router = APIRouter()

# Define the media root directory
MEDIA_ROOT = Path(__file__).resolve().parents[2] / "backend" / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


def _collect_assets():
    """Walk the MEDIA_ROOT and return all file metadata as a list."""
    assets = []
    for p in MEDIA_ROOT.rglob("*"):
        if p.is_file():
            rel = p.relative_to(MEDIA_ROOT).as_posix()
            assets.append({
                "name": p.name,
                "path": f"/media/{rel}",   # URL path (served by StaticFiles in main.py)
                "size": p.stat().st_size,
            })
    return assets


@router.get("/", name="media_root")
def media_root():
    return {"ok": True, "message": "Media API root"}


@router.get("/library", name="media_library")
def media_library():
    """Canonical endpoint to list assets."""
    return JSONResponse({"assets": _collect_assets()})


@router.get("/assets", name="media_assets")
def media_assets():
    """Alias endpoint for compatibility (same output as /library)."""
    return media_library()


@router.get("/analytics", name="media_analytics")
def media_analytics():
    """Placeholder: return basic analytics on media files."""
    assets = _collect_assets()
    total_size = sum(a["size"] for a in assets)
    return {
        "count": len(assets),
        "total_size": total_size,
        "extensions": {
            ext: len([a for a in assets if a["name"].lower().endswith(ext)])
            for ext in {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".pdf"}
        }
    }


@router.post("/upload", name="media_upload")
async def media_upload(file: UploadFile = File(...)):
    """Save an uploaded file into MEDIA_ROOT."""
    target = MEDIA_ROOT / file.filename
    with target.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"ok": True, "filename": file.filename, "path": f"/media/{file.filename}"}
