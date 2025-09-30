# backend/routers/content_creation.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class ContentBrief(BaseModel):
    brand: str
    objective: str
    audience: str
    tone: str
    channels: List[str]

class IdeaRequest(BaseModel):
    brand: str
    theme: Optional[str] = None
    count: int = 5

@router.post("/brief")
async def create_content_brief(brief: ContentBrief):
    """Create content brief"""
    return {
        "brief_id": "brief_123",
        "status": "created",
        "brief": brief.dict()
    }

@router.post("/ideas")
async def generate_content_ideas(request: IdeaRequest):
    """Generate content ideas"""
    return {
        "brand": request.brand,
        "theme": request.theme,
        "ideas": [
            {"title": f"Idea {i+1}", "description": f"Content idea for {request.brand}", "channels": ["instagram", "tiktok"]}
            for i in range(request.count)
        ]
    }

@router.post("/generate")
async def generate_content(prompt: str, brand: str):
    """Generate content based on prompt"""
    return {
        "content": f"Generated content for {brand}",
        "prompt": prompt,
        "word_count": 250
    }
