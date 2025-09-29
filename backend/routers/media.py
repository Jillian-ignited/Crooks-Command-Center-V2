# backend/routers/media.py
from pathlib import Path
import shutil
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

# Use the new storage path (must match main.py)
MEDIA_ROOT = Path(__file__).resolve().parents[2] / "backend" / "storage" / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

def _collect_assets():
    items = []
    for p in MEDIA_ROOT.rglob("*"):
        if p.is_file():
            rel = p.relative_to(MEDIA_ROOT).as_posix()
            items.append({"name": p.name, "path": f"/media/{rel}", "size": p.stat().st_size})
    return items

@router.get("/", name="media_root")
def media_root():
    return {"ok": True, "message": "Media API root"}

@router.get("/library", name="media_library")
def media_library():
    return JSONResponse({"assets": _collect_assets()})

@router.get("/assets", name="media_assets")  # alias for frontend
def media_assets():
    return media_library()

@router.get("/analytics", name="media_analytics")
def media_analytics():
    assets = _collect_assets()
    total_size = sum(a["size"] for a in assets)
    exts = {".jpg",".jpeg",".png",".gif",".webp",".svg",".mp4",".mov",".pdf"}
    by_ext = {e: 0 for e in exts}
    for a in assets:
        n = a["name"].lower()
        for e in exts:
            if n.endswith(e):
                by_ext[e] += 1
                break
    return {"count": len(assets), "total_size": total_size, "by_ext": by_ext}

@router.post("/upload", name="media_upload")
async def media_upload(file: UploadFile = File(...)):
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    target = MEDIA_ROOT / file.filename
    with target.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return {"ok": True, "filename": file.filename, "path": f"/media/{file.filename}"}
