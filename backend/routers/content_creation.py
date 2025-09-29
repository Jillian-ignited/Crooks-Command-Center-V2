from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter(tags=["content"])

class BriefRequest(BaseModel):
    brand: str
    objective: str
    audience: str
    tone: Optional[str] = "authentic"
    channels: List[str] = []

class IdeasRequest(BaseModel):
    brand: str
    theme: str
    count: int = 10

class MapAssetRequest(BaseModel):
    asset_id: str
    deliverable: str
    usage: str

@router.get("")
@router.get("/")
def root():
    return {"ok": True, "router": "content"}

@router.post("/brief")
def create_brief(req: BriefRequest) -> Dict[str, Any]:
    return {
        "ok": True,
        "brief": {
            "title": f"{req.brand}: {req.objective}",
            "key_message": f"{req.brand} stands for {req.objective}.",
            "hooks": [f"What {req.brand} knows about {req.audience}", f"{req.objective} without the noise"],
            "cta": "Shop now",
            "deliverables": ["IG Reel", "TikTok 15s", "Email hero", "PD image x3"],
        },
        "channels": req.channels,
        "ts": datetime.utcnow().isoformat(),
    }

@router.post("/ideas")
def generate_ideas(req: IdeasRequest) -> Dict[str, Any]:
    ideas = [f"{req.brand} × {req.theme} — #{i+1}" for i in range(max(1, min(req.count, 50)))]
    return {"ok": True, "ideas": ideas, "ts": datetime.utcnow().isoformat()}

@router.post("/map-asset")
def map_asset(req: MapAssetRequest) -> Dict[str, Any]:
    return {"ok": True, "mapping": req.model_dump(), "ts": datetime.utcnow().isoformat()}
