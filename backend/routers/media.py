from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Dict, Any, Optional
from uuid import uuid4

router = APIRouter(tags=["media"])
_ASSETS: Dict[str, Dict[str, Any]] = {}

@router.get("")
@router.get("/")
def root():
    return {"ok": True, "router": "media"}

@router.get("/assets")
def list_assets() -> List[Dict[str, Any]]:
    return list(_ASSETS.values())

@router.post("/assets")
async def upload_asset(file: UploadFile = File(...), kind: Optional[str] = Form(None)) -> Dict[str, Any]:
    data = await file.read()
    if not data: raise HTTPException(status_code=400, detail="Empty file")
    asset_id = f"a_{uuid4().hex[:10]}"
    item = {"id": asset_id, "name": file.filename, "mime": file.content_type or "application/octet-stream", "size": len(data), "kind": kind or "unknown", "url": f"/media/{file.filename}"}
    _ASSETS[asset_id] = item
    return item

@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: str) -> Dict[str, Any]:
    if asset_id in _ASSETS:
        del _ASSETS[asset_id]
        return {"ok": True, "deleted": asset_id}
    raise HTTPException(status_code=404, detail="Asset not found")
