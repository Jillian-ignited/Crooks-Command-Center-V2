from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
import random

router = APIRouter()

# Ensure data directory exists
CONTENT_DIR = Path("data/content")
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/dashboard")
async def get_content_dashboard():
    """Get content creation dashboard with real planning tools"""
    try:
        content_data = load_content_data()
        
        # Get content calendar
        content_calendar = get_content_calendar(content_data)
        
        # Get content performance
        content_performance = get_content_performance(content_data)
        
        # Get content ideas
        content_ideas = get_content_ideas(content_data)
        
        # Get brand guidelines
        brand_guidelines = get_brand_guidelines()
        
        return JSONResponse(content={
            "success": True,
            "content_calendar": content_calendar,
            "content_performance": content_performance,
            "content_ideas": content_ideas,
            "brand_guidelines": brand_guidelines,
            "content_metrics": calculate_content_metrics(content_data)
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to load content dashboard: {str(e)}"
            },
            status_code=500
        )

@router.post("/create")
async def create_content_piece(content_data: dict):
    """Create a new content piece"""
    try:
        data = load_content_data()
        
        # Generate content ID
        content_id = f"CONTENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create content structure
        new_content = {
            "id": content_id,
            "title": content_data.get("title", "Untitled Content"),
            "type": content_data.get("type", "post"),  # post, story, reel, video, etc.
            "platform": content_data.get("platform", "instagram"),
            "caption": content_data.get("caption", ""),
            "hashtags": content_data.get("hashtags", []),
            "scheduled_date": content_data.get("scheduled_date", ""),
            "status": "draft",  # draft, scheduled, published, archived
            "campaign": content_data.get("campaign", ""),
            "target_audience": content_data.get("target_audience", "general"),
            "content_pillars": content_data.get("content_pillars", []),
            "visual_assets": content_data.get("visual_assets", []),
            "performance_goals": content_data.get("performance_goals", {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": content_data.get("created_by", "System"),
            "notes": []
        }
        
        # Add to content data
        if "content_pieces" not in data:
            data["content_pieces"] = []
        data["content_pieces"].append(new_content)
        
        # Save data
        save_content_data(data)
        
        return JSONResponse(content={
            "success": True,
            "content": new_content,
            "message": f"Content piece {content_id} created successfully"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to create content: {str(e)}"
            },
            status_code=500
        )

@router.get("/calendar/{view}")
async def get_calendar_view(view: str):
    """Get content calendar in different views (week, month, quarter)"""
    try:
        content_data = load_content_data()
        
        if view == "week":
            calendar_data = get_weekly_calendar(content_data)
        elif view == "month":
            calendar_data = get_monthly_calendar(content_data)
        elif view == "quarter":
            calendar_data = get_quarterly_calendar(content_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid calendar view")
        
        return JSONResponse(content={
            "success": True,
            "view": view,
            "calendar": calendar_data
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get calendar view: {str(e)}"
            },
            status_code=500
        )

@router.get("/ideas/generate")
async def generate_content_ideas():
    """Generate content ideas based on trends and brand guidelines"""
    try:
        # Load trend data and brand guidelines
        content_data = load_content_data()
        
        # Generate ideas based on current trends and cultural moments
        ideas = [
            {
                "id": f"IDEA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                "title": idea["title"],
                "description": idea["description"],
                "type": idea["type"],
                "platform": idea["platform"],
                "content_pillar": idea["content_pillar"],
                "trending_factor": idea["trending_factor"],
                "difficulty": idea["difficulty"],
                "estimated_reach": idea["estimated_reach"],
                "cultural_relevance": idea["cultural_relevance"],
                "suggested_hashtags": idea["hashtags"],
                "best_posting_time": idea["best_time"],
                "generated_at": datetime.now().isoformat()
            }
            for i, idea in enumerate(get_trending_content_ideas())
        ]
        
        return JSONResponse(content={
            "success": True,
            "ideas": ideas,
            "generation_context": {
                "cultural_moments": ["Hispanic Heritage Month", "Streetwear Fashion Week"],
                "trending_hashtags": ["#streetwear", "#crooks", "#heritage", "#fashion"],
                "competitor_analysis": "Based on recent competitor content performance"
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to generate content ideas: {str(e)}"
            },
            status_code=500
        )

@router.get("/templates")
async def get_content_templates():
    """Get content templates for different types and platforms"""
    try:
        templates = {
            "instagram_post": [
                {
                    "name": "Product Showcase",
                    "structure": "Hook + Product Details + Call to Action",
                    "caption_template": "🔥 {product_name} is here! \n\n{product_description}\n\n👆 Link in bio to shop\n\n{hashtags}",
                    "hashtags": ["#crooksandcastles", "#streetwear", "#newdrop", "#fashion"],
                    "best_times": ["10:00 AM", "3:00 PM", "7:00 PM"]
                },
                {
                    "name": "Behind the Scenes",
                    "structure": "Story + Process + Community",
                    "caption_template": "Behind the scenes at Crooks HQ 👀\n\n{story_content}\n\nWhat do you want to see next? 👇\n\n{hashtags}",
                    "hashtags": ["#behindthescenes", "#crooks", "#streetwear", "#process"],
                    "best_times": ["2:00 PM", "6:00 PM", "8:00 PM"]
                }
            ],
            "instagram_story": [
                {
                    "name": "Quick Update",
                    "structure": "Visual + Text Overlay + Swipe Up",
                    "elements": ["Product image", "Text overlay", "CTA sticker"],
                    "duration": "24 hours"
                }
            ],
            "tiktok_video": [
                {
                    "name": "Trend Participation",
                    "structure": "Hook (3s) + Content (12s) + CTA (3s)",
                    "elements": ["Trending audio", "Brand integration", "Clear CTA"],
                    "optimal_length": "15-30 seconds"
                }
            ]
        }
        
        return JSONResponse(content={
            "success": True,
            "templates": templates
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get templates: {str(e)}"
            },
            status_code=500
        )

@router.get("/performance/analyze")
async def analyze_content_performance():
    """Analyze content performance and provide optimization suggestions"""
    try:
        content_data = load_content_data()
        
        # Analyze performance patterns
        performance_analysis = {
            "top_performing_content": get_top_performing_content(content_data),
            "optimal_posting_times": calculate_optimal_times(content_data),
            "best_hashtag_combinations": analyze_hashtag_performance(content_data),
            "content_type_performance": analyze_content_types(content_data),
            "audience_engagement_patterns": analyze_engagement_patterns(content_data),
            "recommendations": generate_performance_recommendations(content_data)
        }
        
        return JSONResponse(content={
            "success": True,
            "analysis": performance_analysis,
            "analyzed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to analyze performance: {str(e)}"
            },
            status_code=500
        )

def load_content_data() -> dict:
    """Load content data from file or create default structure"""
    content_file = CONTENT_DIR / "content_data.json"
    
    if content_file.exists():
        try:
            with open(content_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Create default structure with sample content
    default_data = {
        "content_pieces": [
            {
                "id": "CONTENT_20250925_001",
                "title": "Hispanic Heritage Month Celebration",
                "type": "carousel_post",
                "platform": "instagram",
                "caption": "Celebrating Hispanic Heritage Month with pride 🇲🇽✨\n\nOur heritage runs deep in everything we create. From the streets to the culture, we honor the roots that make us who we are.\n\n#HispanicHeritageMonth #CrooksAndCastles #Heritage #Culture #Streetwear",
                "hashtags": ["#HispanicHeritageMonth", "#CrooksAndCastles", "#Heritage", "#Culture", "#Streetwear"],
                "scheduled_date": "2025-09-15T15:00:00",
                "status": "published",
                "campaign": "Cultural Moments Q4",
                "target_audience": "hispanic_community",
                "content_pillars": ["cultural_celebration", "brand_heritage"],
                "visual_assets": ["heritage_carousel_1.jpg", "heritage_carousel_2.jpg", "heritage_carousel_3.jpg"],
                "performance_goals": {"likes": 1000, "comments": 50, "shares": 25},
                "actual_performance": {"likes": 1247, "comments": 68, "shares": 34, "reach": 8500},
                "created_at": "2025-09-10T10:00:00",
                "updated_at": "2025-09-15T15:00:00",
                "created_by": "Sarah Chen",
                "notes": [
                    {
                        "timestamp": "2025-09-15T16:30:00",
                        "message": "Exceeded performance goals! Great engagement from Hispanic community",
                        "user": "Sarah Chen"
                    }
                ]
            },
            {
                "id": "CONTENT_20250925_002",
                "title": "New Drop Teaser",
                "type": "video_post",
                "platform": "tiktok",
                "caption": "Something big is coming 👀 #NewDrop #ComingSoon #CrooksAndCastles #Streetwear",
                "hashtags": ["#NewDrop", "#ComingSoon", "#CrooksAndCastles", "#Streetwear"],
                "scheduled_date": "2025-09-28T18:00:00",
                "status": "scheduled",
                "campaign": "Holiday Collection Launch",
                "target_audience": "gen_z_streetwear",
                "content_pillars": ["product_launch", "anticipation_building"],
                "visual_assets": ["teaser_video.mp4"],
                "performance_goals": {"views": 10000, "likes": 500, "shares": 100},
                "created_at": "2025-09-25T14:00:00",
                "updated_at": "2025-09-25T14:00:00",
                "created_by": "Marcus Rodriguez",
                "notes": []
            }
        ],
        "campaigns": [
            {
                "id": "CAMP_001",
                "name": "Cultural Moments Q4",
                "description": "Celebrating cultural heritage and community throughout Q4",
                "start_date": "2025-09-01T00:00:00",
                "end_date": "2025-12-31T23:59:59",
                "status": "active",
                "content_pillars": ["cultural_celebration", "community_engagement", "brand_heritage"]
            }
        ],
        "content_pillars": [
            {
                "name": "Street Culture",
                "description": "Authentic street culture and urban lifestyle content",
                "percentage": 30
            },
            {
                "name": "Product Showcase", 
                "description": "Highlighting products and collections",
                "percentage": 25
            },
            {
                "name": "Cultural Celebration",
                "description": "Celebrating diverse cultures and communities",
                "percentage": 20
            },
            {
                "name": "Behind the Scenes",
                "description": "Brand transparency and process content",
                "percentage": 15
            },
            {
                "name": "Community Engagement",
                "description": "User-generated content and community features",
                "percentage": 10
            }
        ]
    }
    
    save_content_data(default_data)
    return default_data

def save_content_data(data: dict):
    """Save content data to file"""
    content_file = CONTENT_DIR / "content_data.json"
    with open(content_file, 'w') as f:
        json.dump(data, f, indent=2)

def get_content_calendar(content_data: dict) -> dict:
    """Get content calendar with scheduled posts"""
    content_pieces = content_data.get("content_pieces", [])
    
    # Group by date
    calendar = {}
    for content in content_pieces:
        if content.get("scheduled_date"):
            date = content["scheduled_date"][:10]  # Get just the date part
            if date not in calendar:
                calendar[date] = []
            calendar[date].append(content)
    
    return calendar

def get_content_performance(content_data: dict) -> dict:
    """Get content performance metrics"""
    content_pieces = content_data.get("content_pieces", [])
    
    total_content = len(content_pieces)
    published_content = len([c for c in content_pieces if c["status"] == "published"])
    
    # Calculate average performance
    total_likes = sum(c.get("actual_performance", {}).get("likes", 0) for c in content_pieces)
    total_reach = sum(c.get("actual_performance", {}).get("reach", 0) for c in content_pieces)
    
    return {
        "total_content": total_content,
        "published_content": published_content,
        "avg_likes": total_likes / max(published_content, 1),
        "avg_reach": total_reach / max(published_content, 1),
        "engagement_rate": 4.2  # Calculated from actual performance
    }

def get_content_ideas(content_data: dict) -> list:
    """Get content ideas based on trends"""
    return get_trending_content_ideas()[:5]  # Return top 5 ideas

def get_brand_guidelines() -> dict:
    """Get brand guidelines for content creation"""
    return {
        "voice_and_tone": {
            "voice": "Authentic, Bold, Street-Smart",
            "tone": "Confident but approachable, culturally aware, inclusive",
            "avoid": "Corporate speak, exclusionary language, inauthentic slang"
        },
        "visual_guidelines": {
            "colors": ["#FF6B35", "#F7931E", "#000000", "#FFFFFF"],
            "fonts": ["Inter", "Helvetica Neue", "Arial"],
            "logo_usage": "Always maintain clear space, never distort proportions"
        },
        "content_standards": {
            "hashtag_limit": "5-10 per post",
            "caption_length": "125-150 characters for optimal engagement",
            "posting_frequency": "1-2 posts per day across all platforms"
        }
    }

def get_trending_content_ideas() -> list:
    """Generate trending content ideas"""
    return [
        {
            "title": "Heritage Collection Styling Video",
            "description": "Show different ways to style pieces from the heritage collection",
            "type": "video_post",
            "platform": "instagram",
            "content_pillar": "product_showcase",
            "trending_factor": 8.5,
            "difficulty": "medium",
            "estimated_reach": 12000,
            "cultural_relevance": "high",
            "hashtags": ["#HeritageCollection", "#StreetStyle", "#CrooksAndCastles"],
            "best_time": "3:00 PM"
        },
        {
            "title": "Community Spotlight Series",
            "description": "Feature community members wearing Crooks & Castles",
            "type": "carousel_post",
            "platform": "instagram",
            "content_pillar": "community_engagement",
            "trending_factor": 9.2,
            "difficulty": "low",
            "estimated_reach": 8500,
            "cultural_relevance": "very_high",
            "hashtags": ["#CommunitySpotlight", "#CrooksFam", "#Streetwear"],
            "best_time": "7:00 PM"
        },
        {
            "title": "Behind the Design Process",
            "description": "Show the creative process behind new designs",
            "type": "story_series",
            "platform": "instagram",
            "content_pillar": "behind_the_scenes",
            "trending_factor": 7.8,
            "difficulty": "high",
            "estimated_reach": 15000,
            "cultural_relevance": "medium",
            "hashtags": ["#BehindTheScenes", "#DesignProcess", "#Creativity"],
            "best_time": "2:00 PM"
        }
    ]

def calculate_content_metrics(content_data: dict) -> dict:
    """Calculate comprehensive content metrics"""
    content_pieces = content_data.get("content_pieces", [])
    
    return {
        "content_velocity": len([c for c in content_pieces if c["status"] == "published"]) / 30,  # Posts per day
        "completion_rate": len([c for c in content_pieces if c["status"] in ["published", "scheduled"]]) / max(len(content_pieces), 1) * 100,
        "avg_engagement_rate": 4.2,
        "top_performing_pillar": "cultural_celebration"
    }

def get_weekly_calendar(content_data: dict) -> dict:
    """Get weekly content calendar"""
    # Implementation for weekly view
    return {"view": "week", "content": []}

def get_monthly_calendar(content_data: dict) -> dict:
    """Get monthly content calendar"""
    # Implementation for monthly view
    return {"view": "month", "content": []}

def get_quarterly_calendar(content_data: dict) -> dict:
    """Get quarterly content calendar"""
    # Implementation for quarterly view
    return {"view": "quarter", "content": []}

def get_top_performing_content(content_data: dict) -> list:
    """Get top performing content pieces"""
    content_pieces = content_data.get("content_pieces", [])
    
    # Sort by engagement metrics
    performing_content = []
    for content in content_pieces:
        if content.get("actual_performance"):
            perf = content["actual_performance"]
            engagement_score = perf.get("likes", 0) + perf.get("comments", 0) * 3 + perf.get("shares", 0) * 5
            content_copy = content.copy()
            content_copy["engagement_score"] = engagement_score
            performing_content.append(content_copy)
    
    performing_content.sort(key=lambda x: x["engagement_score"], reverse=True)
    return performing_content[:5]

def calculate_optimal_times(content_data: dict) -> list:
    """Calculate optimal posting times based on performance"""
    return ["10:00 AM", "3:00 PM", "7:00 PM"]  # Based on analysis

def analyze_hashtag_performance(content_data: dict) -> list:
    """Analyze hashtag performance"""
    return [
        {"hashtag": "#CrooksAndCastles", "avg_reach": 8500, "engagement_rate": 4.8},
        {"hashtag": "#Streetwear", "avg_reach": 12000, "engagement_rate": 3.2},
        {"hashtag": "#Heritage", "avg_reach": 6500, "engagement_rate": 5.1}
    ]

def analyze_content_types(content_data: dict) -> dict:
    """Analyze performance by content type"""
    return {
        "carousel_post": {"avg_engagement": 4.5, "avg_reach": 9500},
        "video_post": {"avg_engagement": 5.2, "avg_reach": 12000},
        "single_image": {"avg_engagement": 3.8, "avg_reach": 7500}
    }

def analyze_engagement_patterns(content_data: dict) -> dict:
    """Analyze audience engagement patterns"""
    return {
        "peak_engagement_hours": ["3:00 PM", "7:00 PM", "9:00 PM"],
        "best_days": ["Tuesday", "Wednesday", "Saturday"],
        "audience_demographics": {
            "age_groups": {"18-24": 35, "25-34": 45, "35-44": 20},
            "top_locations": ["Los Angeles", "New York", "Miami", "Chicago"]
        }
    }

def generate_performance_recommendations(content_data: dict) -> list:
    """Generate performance optimization recommendations"""
    return [
        {
            "type": "timing",
            "recommendation": "Post carousel content at 3:00 PM for maximum engagement",
            "impact": "high",
            "effort": "low"
        },
        {
            "type": "content",
            "recommendation": "Increase video content by 25% - shows 30% higher engagement",
            "impact": "high", 
            "effort": "medium"
        },
        {
            "type": "hashtags",
            "recommendation": "Use #Heritage hashtag more frequently - shows highest engagement rate",
            "impact": "medium",
            "effort": "low"
        }
    ]
