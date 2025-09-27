from fastapi import APIRouter, HTTPException
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

class Brief(BaseModel):
    title: str
    key_message: str
    hooks: List[str]
    cta: str
    deliverables: List[str]

class IdeasRequest(BaseModel):
    brand: str
    theme: str
    count: int = 10

@router.post("/brief")
def create_brief(req: BriefRequest) -> Dict[str, Any]:
    title = f"{req.brand}: {req.objective}".strip()
    brief = Brief(
        title=title,
        key_message=f"{req.brand} stands for {req.objective}.",
        hooks=[
            f"What {req.brand} knows about {req.audience}",
            f"{req.objective} without the noise",
        ],
        cta="Shop now at crooksncastles.com",
        deliverables=[f"IG Reel ({req.tone})", "TikTok (15s)", "Email hero", "PD image x3"],
    )
    return {"ok": True, "brief": brief.model_dump(), "channels": req.channels, "ts": datetime.now().isoformat()}

@router.post("/ideas")
def generate_ideas(req: IdeasRequest) -> Dict[str, Any]:
    ideas = [f"{req.brand} × {req.theme} — Concept #{i+1}" for i in range(max(1, min(req.count, 50)))]
    return {"ok": True, "ideas": ideas, "ts": datetime.now().isoformat()}

class MapAssetRequest(BaseModel):
    asset_id: str
    deliverable: str
    usage: str  # e.g., "primary", "alt", "thumbnail"

@router.post("/map-asset")
def map_asset(req: MapAssetRequest) -> Dict[str, Any]:
    # Stub: persist mapping later
    return {"ok": True, "mapping": req.model_dump(), "ts": datetime.now().isoformat()}
