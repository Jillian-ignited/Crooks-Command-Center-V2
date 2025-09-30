from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import datetime

router = APIRouter()

class BriefRequest(BaseModel):
    brand: str
    objective: Optional[str] = ""
    audience: Optional[str] = ""
    tone: Optional[str] = ""
    channels: Optional[str] = ""

class IdeaRequest(BaseModel):
    brand: str
    theme: Optional[str] = ""
    count: Optional[int] = 10

@router.post("/brief")
def create_brief(request: BriefRequest) -> Dict[str, Any]:
    """Create a content brief"""
    if not request.brand or request.brand.strip() == "":
        raise HTTPException(status_code=400, detail="Brand name is required")
    
    # Generate a mock brief
    brief = {
        "id": f"brief_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "brand": request.brand,
        "objective": request.objective or "Drive brand awareness and engagement",
        "audience": request.audience or "Gen Z streetwear enthusiasts",
        "tone": request.tone or "Authentic and edgy",
        "channels": request.channels or "Instagram, TikTok, Email",
        "created_at": datetime.datetime.now().isoformat(),
        "status": "draft",
        "content_pillars": [
            "Street Culture",
            "Authenticity", 
            "Community",
            "Style Innovation"
        ],
        "key_messages": [
            f"{request.brand} represents authentic street culture",
            "Quality meets style in every piece",
            "Built for the streets, worn by legends"
        ],
        "campaign_themes": [
            "Urban Legends",
            "Street Royalty", 
            "Authentic Vibes",
            "Culture Creators"
        ]
    }
    
    return {
        "success": True,
        "brief": brief,
        "message": "Content brief created successfully"
    }

@router.post("/ideas")
def generate_ideas(request: IdeaRequest) -> Dict[str, Any]:
    """Generate content ideas"""
    if not request.brand or request.brand.strip() == "":
        raise HTTPException(status_code=400, detail="Brand name is required")
    
    count = min(request.count or 10, 50)  # Limit to 50 ideas max
    theme = request.theme or "Street Culture"
    
    # Generate mock content ideas
    idea_templates = [
        f"{request.brand} x {theme}: Behind the scenes of our latest drop",
        f"Style spotlight: How to rock {request.brand} pieces",
        f"{theme} meets fashion: {request.brand} inspiration",
        f"Community feature: {request.brand} fans share their style",
        f"Throwback Thursday: {request.brand} classic pieces",
        f"New arrival alert: Fresh {request.brand} drops",
        f"Street style photography featuring {request.brand}",
        f"Designer interview: The story behind {request.brand}",
        f"Styling tips: Mixing {request.brand} with vintage pieces",
        f"Culture spotlight: {theme} influences in fashion",
        f"{request.brand} lookbook: Spring/Summer vibes",
        f"Customer stories: Why they choose {request.brand}",
        f"Trend alert: {theme} is taking over",
        f"Collaboration announcement: {request.brand} x Artist",
        f"Sustainability focus: {request.brand}'s eco initiatives"
    ]
    
    ideas = []
    for i in range(count):
        template_index = i % len(idea_templates)
        idea = {
            "id": f"idea_{i+1:03d}",
            "title": idea_templates[template_index],
            "theme": theme,
            "content_type": ["Instagram Post", "TikTok Video", "Story", "Reel", "Email"][i % 5],
            "platform": ["Instagram", "TikTok", "Twitter", "Email", "Blog"][i % 5],
            "engagement_potential": ["High", "Medium", "High", "Medium", "Low"][i % 5],
            "effort_level": ["Low", "Medium", "High", "Medium", "Low"][i % 5],
            "suggested_hashtags": [
                f"#{request.brand.lower().replace(' ', '').replace('&', '')}",
                f"#{theme.lower().replace(' ', '')}",
                "#streetwear",
                "#fashion",
                "#style"
            ][:3],
            "call_to_action": [
                "Shop the look",
                "Tag a friend",
                "Share your style", 
                "Join the community",
                "Get inspired"
            ][i % 5]
        }
        ideas.append(idea)
    
    return {
        "success": True,
        "ideas": ideas,
        "total_count": len(ideas),
        "theme": theme,
        "brand": request.brand,
        "generated_at": datetime.datetime.now().isoformat()
    }

@router.get("/briefs")
def get_briefs(limit: int = 20) -> Dict[str, Any]:
    """Get existing content briefs"""
    # Mock briefs data
    briefs = [
        {
            "id": "brief_001",
            "brand": "Crooks & Castles",
            "objective": "Drive Q1 sales",
            "status": "active",
            "created_at": "2024-01-10T10:00:00",
            "channels": "Instagram, TikTok"
        },
        {
            "id": "brief_002", 
            "brand": "Crooks & Castles",
            "objective": "Brand awareness campaign",
            "status": "draft",
            "created_at": "2024-01-08T14:30:00",
            "channels": "All social platforms"
        }
    ]
    
    return {
        "success": True,
        "briefs": briefs[:limit],
        "total_count": len(briefs)
    }

@router.get("/briefs/{brief_id}")
def get_brief(brief_id: str) -> Dict[str, Any]:
    """Get a specific brief by ID"""
    # Mock brief data
    brief = {
        "id": brief_id,
        "brand": "Crooks & Castles",
        "objective": "Drive Q1 sales and brand awareness",
        "audience": "Gen Z streetwear enthusiasts aged 16-24",
        "tone": "Authentic, edgy, community-focused",
        "channels": "Instagram, TikTok, Email, Website",
        "created_at": "2024-01-10T10:00:00",
        "status": "active",
        "content_pillars": [
            "Street Culture",
            "Authenticity",
            "Community", 
            "Style Innovation"
        ],
        "key_messages": [
            "Crooks & Castles represents authentic street culture",
            "Quality meets style in every piece",
            "Built for the streets, worn by legends"
        ]
    }
    
    return {
        "success": True,
        "brief": brief
    }

@router.get("/templates")
def get_content_templates() -> Dict[str, Any]:
    """Get content templates"""
    templates = [
        {
            "id": "template_001",
            "name": "Product Showcase",
            "type": "Instagram Post",
            "description": "Highlight new product drops with lifestyle imagery",
            "structure": {
                "image": "Product in lifestyle setting",
                "caption": "Product description + brand story + CTA",
                "hashtags": "Brand + product + lifestyle tags"
            }
        },
        {
            "id": "template_002",
            "name": "Behind the Scenes",
            "type": "TikTok Video", 
            "description": "Show the creative process and brand culture",
            "structure": {
                "video": "15-30 second behind-the-scenes footage",
                "audio": "Trending sound or original audio",
                "text_overlay": "Process explanation + brand message"
            }
        },
        {
            "id": "template_003",
            "name": "User Generated Content",
            "type": "Story",
            "description": "Feature customer styling and reviews",
            "structure": {
                "content": "Customer photo/video",
                "overlay": "Brand sticker + thank you message",
                "cta": "Swipe up to shop or tag friends"
            }
        }
    ]
    
    return {
        "success": True,
        "templates": templates,
        "total_count": len(templates)
    }

@router.get("/analytics")
def get_content_analytics() -> Dict[str, Any]:
    """Get content performance analytics"""
    analytics = {
        "total_posts": 156,
        "total_engagement": 45230,
        "avg_engagement_rate": 4.2,
        "top_performing_content": [
            {
                "id": "post_001",
                "title": "New hoodie drop behind the scenes",
                "platform": "TikTok",
                "engagement": 12450,
                "engagement_rate": 8.7
            },
            {
                "id": "post_002",
                "title": "Customer styling feature",
                "platform": "Instagram", 
                "engagement": 8920,
                "engagement_rate": 6.3
            }
        ],
        "content_by_type": {
            "video": 45,
            "image": 89,
            "carousel": 22
        },
        "engagement_by_platform": {
            "instagram": 28450,
            "tiktok": 12340,
            "twitter": 4440
        }
    }
    
    return {
        "success": True,
        "analytics": analytics,
        "period": "last_30_days",
        "generated_at": datetime.datetime.now().isoformat()
    }
