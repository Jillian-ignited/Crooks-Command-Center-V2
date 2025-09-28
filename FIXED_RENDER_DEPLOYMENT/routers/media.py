from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Dict, Any, Optional
from uuid import uuid4

router = APIRouter(tags=["media"])

# In-memory store for now; swap with DB/S3 later
_ASSETS: Dict[str, Dict[str, Any]] = {}

@router.get("/assets")
def list_assets() -> List[Dict[str, Any]]:
    return list(_ASSETS.values())

@router.post("/assets")
async def upload_asset(
    file: UploadFile = File(...),
    kind: Optional[str] = Form(None)  # image|video|doc|...
) -> Dict[str, Any]:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    asset_id = f"a_{uuid4().hex[:10]}"
    item = {
        "id": asset_id,
        "name": file.filename,
        "mime": file.content_type or "application/octet-stream",
        "size": len(data),
        "kind": kind or "unknown",
        "url": f"/media/{file.filename}",  # placeholder; replace with S3 URL later
    }
    _ASSETS[asset_id] = item
    return item

@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: str) -> Dict[str, Any]:
    if asset_id in _ASSETS:
        del _ASSETS[asset_id]
        return {"ok": True, "deleted": asset_id}
    raise HTTPException(status_code=404, detail="Asset not found")

# Optional presign flow (stubbed)
@router.post("/presign")
def presign(kind: Optional[str] = Form(None), filename: Optional[str] = Form(None)) -> Dict[str, Any]:
    # Replace with real S3/GCS presign. This just unblocks UI wiring.
    return {
        "provider": "stub",
        "url": "/media/upload-direct",
        "fields": {"key": filename or "file.bin", "kind": kind or "unknown"}
    }

@router.post("/commit")
def commit(key: str = Form(...), size: int = Form(...), mime: str = Form("application/octet-stream")) -> Dict[str, Any]:
    asset_id = f"a_{uuid4().hex[:10]}"
    item = {"id": asset_id, "name": key, "mime": mime, "size": size, "url": f"/media/{key}"}
    _ASSETS[asset_id] = item
    return item

@router.get("/library")
@router.get("/library/")
def media_library() -> Dict[str, Any]:
    """Media library endpoint with asset management"""
    return {
        "success": True,
        "library": {
            "total_assets": len(_ASSETS),
            "assets": list(_ASSETS.values()),
            "categories": {
                "images": len([a for a in _ASSETS.values() if a.get("kind") == "image"]),
                "videos": len([a for a in _ASSETS.values() if a.get("kind") == "video"]),
                "documents": len([a for a in _ASSETS.values() if a.get("kind") == "doc"]),
                "other": len([a for a in _ASSETS.values() if a.get("kind") not in ["image", "video", "doc"]])
            },
            "storage_used": sum(a.get("size", 0) for a in _ASSETS.values()),
            "recent_uploads": sorted(_ASSETS.values(), key=lambda x: x.get("id", ""), reverse=True)[:10]
        },
        "upload_info": {
            "max_file_size": "50MB",
            "supported_formats": ["JPG", "PNG", "GIF", "MP4", "MOV", "PDF", "DOC"],
            "storage_limit": "1GB"
        }
    }
