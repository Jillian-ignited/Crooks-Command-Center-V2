# backend/routers/media.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter()
_ASSETS = {}  # in-memory for now

@router.get("/assets")
def list_assets() -> List[dict]:
    return list(_ASSETS.values())

@router.post("/assets")
async def upload_asset(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    asset_id = f"a_{len(_ASSETS)+1}"
    _ASSETS[asset_id] = {"id": asset_id, "name": file.filename, "type": file.content_type, "size": len(data), "url": f"/media/{file.filename}"}
    return _ASSETS[asset_id]

@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: str):
    if asset_id in _ASSETS:
        del _ASSETS[asset_id]
        return {"ok": True, "deleted": asset_id}
    raise HTTPException(status_code=404, detail="Not found")
