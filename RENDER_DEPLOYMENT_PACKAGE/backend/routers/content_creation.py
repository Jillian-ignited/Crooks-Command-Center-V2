from fastapi import APIRouter, HTTPException, Query
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

@router.get("/ideas/generate")
async def generate_ideas_get(
    brand: str = Query("crooks & castles", description="Brand name"),
    theme: str = Query("streetwear", description="Content theme"),
    count: int = Query(10, description="Number of ideas to generate")
) -> Dict[str, Any]:
    """Generate content ideas via GET request"""
    try:
        # Generate creative content ideas based on brand and theme
        streetwear_ideas = [
            f"Heritage Month: {brand} celebrates cultural roots through authentic streetwear storytelling",
            f"Behind the Scenes: The craftsmanship and attention to detail that goes into every {brand} piece",
            f"Community Spotlight: Real customers wearing {brand} in their daily lives and environments",
            f"Vintage Vibes: How {brand} draws inspiration from classic streetwear and hip-hop culture",
            f"Collaboration Tease: Sneak peek at upcoming {brand} partnerships and limited drops",
            f"Street Style Guide: How to style {brand} pieces for different occasions and seasons",
            f"Brand Evolution: The journey of {brand} from underground to mainstream streetwear icon",
            f"Cultural Impact: How {brand} influences and is influenced by music, art, and street culture",
            f"Sustainability Story: {brand}'s commitment to responsible fashion and ethical production",
            f"Limited Edition Launch: Building anticipation for exclusive {brand} releases"
        ]
        
        # Select random ideas based on count
        import random
        selected_ideas = random.sample(streetwear_ideas, min(count, len(streetwear_ideas)))
        
        return {
            "success": True,
            "ideas": selected_ideas,
            "brand": brand,
            "theme": theme,
            "count": len(selected_ideas),
            "ts": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content ideas: {e}")

@router.get("/dashboard")
async def get_dashboard() -> Dict[str, Any]:
    """Get content dashboard data"""
    try:
        return {
            "success": True,
            "content_performance": {
                "total_content": 156
            },
            "content_metrics": {
                "avg_engagement_rate": 4.2,
                "content_velocity": 3.5,
                "top_performing_pillar": "Streetwear"
            },
            "content_ideas": [
                {
                    "title": "Heritage Month Campaign",
                    "description": "Celebrate cultural heritage with authentic streetwear storytelling",
                    "trending_factor": 9,
                    "platform": "Instagram"
                },
                {
                    "title": "Behind the Scenes",
                    "description": "Show the craftsmanship behind Crooks & Castles designs",
                    "trending_factor": 7,
                    "platform": "TikTok"
                },
                {
                    "title": "Community Spotlight",
                    "description": "Feature real customers wearing C&C in their daily lives",
                    "trending_factor": 8,
                    "platform": "Instagram"
                },
                {
                    "title": "Vintage Aesthetic",
                    "description": "Showcase how C&C draws from classic streetwear heritage",
                    "trending_factor": 6,
                    "platform": "Pinterest"
                },
                {
                    "title": "Collaboration Tease",
                    "description": "Build anticipation for upcoming brand partnerships",
                    "trending_factor": 9,
                    "platform": "TikTok"
                },
                {
                    "title": "Street Style Guide",
                    "description": "How to style C&C pieces for different occasions",
                    "trending_factor": 7,
                    "platform": "Instagram"
                }
            ],
            "recent_performance": {
                "top_post_engagement": 8.7,
                "avg_reach": 12500,
                "best_performing_content_type": "Video",
                "optimal_posting_time": "6-9 PM EST"
            },
            "content_calendar_preview": [
                {
                    "date": "2025-10-01",
                    "content_type": "Instagram Post",
                    "theme": "Heritage Celebration",
                    "status": "Scheduled"
                },
                {
                    "date": "2025-10-03",
                    "content_type": "TikTok Video",
                    "theme": "Behind the Scenes",
                    "status": "In Review"
                },
                {
                    "date": "2025-10-05",
                    "content_type": "Instagram Story",
                    "theme": "Community Spotlight",
                    "status": "Draft"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load content dashboard: {e}")

class MapAssetRequest(BaseModel):
    asset_id: str
    deliverable: str
    usage: str  # e.g., "primary", "alt", "thumbnail"

@router.post("/map-asset")
def map_asset(req: MapAssetRequest) -> Dict[str, Any]:
    # Stub: persist mapping later
    return {"ok": True, "mapping": req.model_dump(), "ts": datetime.now().isoformat()}
