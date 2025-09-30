from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

router = APIRouter()

# Request models
class ContentBriefRequest(BaseModel):
    brand: str
    campaign_type: Optional[str] = "general"
    target_audience: Optional[str] = "streetwear enthusiasts"
    tone: Optional[str] = "rebellious, authentic"
    objectives: Optional[List[str]] = ["brand awareness", "engagement"]
    platforms: Optional[List[str]] = ["instagram", "tiktok"]

class ContentIdeasRequest(BaseModel):
    brand: str
    theme: Optional[str] = "streetwear culture"
    count: Optional[int] = 5
    format: Optional[str] = "mixed"  # post, story, video, mixed

# Response models
class ContentBrief(BaseModel):
    id: str
    brand: str
    title: str
    overview: str
    target_audience: str
    key_messages: List[str]
    tone_guidelines: str
    content_pillars: List[str]
    success_metrics: List[str]
    created_at: str

class ContentIdea(BaseModel):
    id: str
    title: str
    description: str
    format: str
    platform: str
    engagement_potential: str
    difficulty: str

@router.post("/brief")
async def create_content_brief(request: ContentBriefRequest):
    """Create a comprehensive content brief for brand campaigns"""
    
    try:
        # Generate content brief based on brand and requirements
        brief_id = str(uuid.uuid4())[:8]
        
        # Customize content based on brand
        if "crooks" in request.brand.lower():
            brand_voice = "Rebellious, street-smart, authentic. No compromise on quality or attitude."
            content_pillars = [
                "Street Culture Authenticity",
                "Premium Quality Craftsmanship", 
                "Community & Brotherhood",
                "Urban Lifestyle Excellence"
            ]
            key_messages = [
                "Crooks & Castles represents authentic street culture",
                "Premium streetwear for those who demand excellence",
                "Built by the streets, for the streets",
                "Quality that speaks louder than words"
            ]
        else:
            brand_voice = f"Authentic, engaging, and true to {request.brand}'s core values"
            content_pillars = [
                "Brand Authenticity",
                "Quality & Craftsmanship",
                "Community Engagement", 
                "Lifestyle Integration"
            ]
            key_messages = [
                f"{request.brand} delivers exceptional quality",
                f"Authentic style that defines {request.brand}",
                "Built for those who appreciate excellence",
                "Where style meets substance"
            ]
        
        brief = ContentBrief(
            id=brief_id,
            brand=request.brand,
            title=f"{request.brand} {request.campaign_type.title()} Campaign Brief",
            overview=f"Comprehensive content strategy for {request.brand} targeting {request.target_audience}. This brief outlines key messaging, content pillars, and success metrics for authentic brand storytelling across digital platforms.",
            target_audience=request.target_audience,
            key_messages=key_messages,
            tone_guidelines=brand_voice,
            content_pillars=content_pillars,
            success_metrics=[
                "Engagement Rate: >4.5%",
                "Brand Mention Sentiment: >75% positive",
                "Content Saves: >2% of reach",
                "Story Completion Rate: >70%",
                "Community Growth: >5% monthly"
            ],
            created_at=datetime.now().isoformat()
        )
        
        return {
            "success": True,
            "brief": brief,
            "message": f"Content brief created successfully for {request.brand}",
            "next_steps": [
                "Review and approve content pillars",
                "Generate specific content ideas",
                "Create content calendar",
                "Begin asset production"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content brief: {str(e)}")

@router.post("/ideas")
async def generate_content_ideas(request: ContentIdeasRequest):
    """Generate creative content ideas based on brand and theme"""
    
    try:
        ideas = []
        
        # Generate ideas based on brand and theme
        if "crooks" in request.brand.lower():
            base_ideas = [
                {
                    "title": "Behind the Seams: Craftsmanship Stories",
                    "description": "Showcase the detailed craftsmanship that goes into each piece, from fabric selection to final stitching",
                    "format": "video",
                    "platform": "instagram",
                    "engagement_potential": "high",
                    "difficulty": "medium"
                },
                {
                    "title": "Street Culture Chronicles", 
                    "description": "Feature real community members wearing Crooks & Castles in their authentic environments",
                    "format": "photo_series",
                    "platform": "instagram",
                    "engagement_potential": "very_high",
                    "difficulty": "low"
                },
                {
                    "title": "Heritage Moments",
                    "description": "Celebrate cultural heritage months with authentic storytelling and community spotlights",
                    "format": "carousel",
                    "platform": "instagram",
                    "engagement_potential": "high", 
                    "difficulty": "medium"
                },
                {
                    "title": "Quality Check Challenge",
                    "description": "TikTok series showing the durability and quality of pieces through real-world tests",
                    "format": "video",
                    "platform": "tiktok",
                    "engagement_potential": "viral_potential",
                    "difficulty": "low"
                },
                {
                    "title": "Community Spotlight Series",
                    "description": "Feature customers and their stories, showing how Crooks & Castles fits into their lifestyle",
                    "format": "story_highlight",
                    "platform": "instagram",
                    "engagement_potential": "medium",
                    "difficulty": "low"
                },
                {
                    "title": "Design Process Deep Dive",
                    "description": "Take followers behind the scenes of how new designs come to life",
                    "format": "video",
                    "platform": "youtube",
                    "engagement_potential": "high",
                    "difficulty": "high"
                },
                {
                    "title": "Street Style Inspiration",
                    "description": "Curated looks and styling tips featuring latest pieces in urban settings",
                    "format": "photo",
                    "platform": "instagram",
                    "engagement_potential": "medium",
                    "difficulty": "low"
                }
            ]
        else:
            base_ideas = [
                {
                    "title": f"{request.brand} Lifestyle Moments",
                    "description": f"Showcase how {request.brand} fits into everyday life with authentic customer stories",
                    "format": "photo_series",
                    "platform": "instagram", 
                    "engagement_potential": "high",
                    "difficulty": "low"
                },
                {
                    "title": "Product Spotlight Series",
                    "description": "Deep dive into key products with detailed features and benefits",
                    "format": "carousel",
                    "platform": "instagram",
                    "engagement_potential": "medium",
                    "difficulty": "medium"
                },
                {
                    "title": "Behind the Brand",
                    "description": "Share the story, values, and people behind the brand",
                    "format": "video",
                    "platform": "instagram",
                    "engagement_potential": "high",
                    "difficulty": "medium"
                },
                {
                    "title": "Community Features",
                    "description": "Highlight customers and their unique style interpretations",
                    "format": "story_highlight",
                    "platform": "instagram",
                    "engagement_potential": "medium",
                    "difficulty": "low"
                },
                {
                    "title": "Trend Integration",
                    "description": "Show how brand pieces work with current fashion and cultural trends",
                    "format": "video",
                    "platform": "tiktok",
                    "engagement_potential": "high",
                    "difficulty": "medium"
                }
            ]
        
        # Select and customize ideas based on request
        selected_ideas = base_ideas[:request.count]
        
        for i, idea in enumerate(selected_ideas):
            content_idea = ContentIdea(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                title=idea["title"],
                description=idea["description"],
                format=idea["format"],
                platform=idea["platform"],
                engagement_potential=idea["engagement_potential"],
                difficulty=idea["difficulty"]
            )
            ideas.append(content_idea)
        
        return {
            "success": True,
            "ideas": ideas,
            "brand": request.brand,
            "theme": request.theme,
            "total_generated": len(ideas),
            "message": f"Generated {len(ideas)} content ideas for {request.brand}",
            "recommendations": [
                "Start with low-difficulty, high-engagement ideas",
                "Test different formats to see what resonates",
                "Maintain consistent brand voice across all content",
                "Track performance metrics for optimization"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content ideas: {str(e)}")

@router.get("/briefs")
async def list_content_briefs():
    """List all created content briefs"""
    
    # Mock data for existing briefs
    briefs = [
        {
            "id": "brief_001",
            "brand": "Crooks & Castles",
            "title": "Q1 Brand Campaign Brief",
            "status": "active",
            "created_at": "2025-09-25T10:00:00",
            "last_updated": "2025-09-30T15:30:00"
        },
        {
            "id": "brief_002", 
            "brand": "Crooks & Castles",
            "title": "Holiday Collection Brief",
            "status": "draft",
            "created_at": "2025-09-28T14:20:00",
            "last_updated": "2025-09-29T09:15:00"
        }
    ]
    
    return {
        "success": True,
        "briefs": briefs,
        "total_count": len(briefs),
        "active_count": len([b for b in briefs if b["status"] == "active"]),
        "draft_count": len([b for b in briefs if b["status"] == "draft"])
    }
