# backend/routers/content.py
# Content creation and management router with real data processing

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse

# Fixed OpenAI client initialization (no proxies parameter)
try:
    from openai import OpenAI
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )
    AI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
    print("[content] OpenAI client initialized successfully")
except ImportError:
    print("[content] OpenAI not available - install with: pip install openai")
    openai_client = None
    AI_AVAILABLE = False
except Exception as e:
    print(f"[content] OpenAI initialization error: {e}")
    openai_client = None
    AI_AVAILABLE = False

router = APIRouter()

# Content storage directory
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
os.makedirs(CONTENT_DIR, exist_ok=True)

# Database setup
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
    else:
        DB_AVAILABLE = False
except Exception as e:
    print(f"[content] Database setup error: {e}")
    DB_AVAILABLE = False

@router.get("/overview")
async def get_content_overview():
    """Get comprehensive content creation overview"""
    
    try:
        print("[content] Generating content overview")
        
        # Get created content files
        content_files = []
        if os.path.exists(CONTENT_DIR):
            for filename in os.listdir(CONTENT_DIR):
                file_path = os.path.join(CONTENT_DIR, filename)
                if os.path.isfile(file_path) and filename.endswith('.json'):
                    try:
                        with open(file_path, 'r') as f:
                            content_data = json.load(f)
                        content_files.append(content_data)
                    except Exception as e:
                        print(f"[content] Error reading {filename}: {e}")
        
        # Generate overview metrics
        overview = {
            "content_summary": {
                "total_briefs": len([c for c in content_files if c.get("type") == "brief"]),
                "total_ideas": len([c for c in content_files if c.get("type") == "ideas"]),
                "total_campaigns": len([c for c in content_files if c.get("type") == "campaign"]),
                "last_created": max([c.get("created_at", "") for c in content_files]) if content_files else None
            },
            "content_types": {
                "social_media": len([c for c in content_files if "social" in str(c.get("content", {}))]),
                "email_campaigns": len([c for c in content_files if "email" in str(c.get("content", {}))]),
                "product_descriptions": len([c for c in content_files if "product" in str(c.get("content", {}))]),
                "blog_posts": len([c for c in content_files if "blog" in str(c.get("content", {}))])
            },
            "brand_focus": {
                "crooks_castles": len([c for c in content_files if "crooks" in str(c).lower()]),
                "streetwear": len([c for c in content_files if "streetwear" in str(c).lower()]),
                "hip_hop": len([c for c in content_files if "hip hop" in str(c).lower()])
            },
            "ai_capabilities": {
                "ai_available": AI_AVAILABLE,
                "content_generation": AI_AVAILABLE,
                "idea_brainstorming": AI_AVAILABLE,
                "trend_analysis": AI_AVAILABLE
            },
            "recent_content": content_files[-5:] if content_files else [],
            "storage_location": CONTENT_DIR,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "overview": overview
        }
        
    except Exception as e:
        print(f"[content] Overview error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate overview: {str(e)}")

@router.post("/brief")
async def create_content_brief(
    brand: str = Form(...),
    campaign_type: str = Form("social_media"),
    target_audience: str = Form("streetwear enthusiasts"),
    objectives: str = Form("increase brand awareness"),
    tone: str = Form("authentic, urban, confident"),
    channels: str = Form("Instagram, TikTok"),
    timeline: str = Form("30 days"),
    budget: Optional[str] = Form(None),
    additional_notes: Optional[str] = Form(None)
):
    """Create comprehensive content brief with AI assistance"""
    
    try:
        print(f"[content] Creating brief for {brand}")
        
        # Generate unique brief ID
        brief_id = str(uuid.uuid4())
        
        # Create base brief structure
        brief = {
            "id": brief_id,
            "type": "brief",
            "brand": brand,
            "campaign_type": campaign_type,
            "target_audience": target_audience,
            "objectives": objectives,
            "tone": tone,
            "channels": channels.split(",") if channels else [],
            "timeline": timeline,
            "budget": budget,
            "additional_notes": additional_notes,
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        # Generate AI-enhanced brief content
        if AI_AVAILABLE and openai_client:
            try:
                ai_content = await generate_ai_brief_content(brief)
                brief["ai_generated_content"] = ai_content
                brief["ai_enhanced"] = True
            except Exception as e:
                print(f"[content] AI brief generation error: {e}")
                brief["ai_enhanced"] = False
                brief["ai_error"] = str(e)
        else:
            brief["ai_enhanced"] = False
            brief["ai_note"] = "AI content generation not available"
        
        # Add manual content structure
        brief["content_structure"] = generate_manual_brief_structure(brief)
        
        # Save brief to file
        brief_filename = f"brief_{brief_id}.json"
        brief_path = os.path.join(CONTENT_DIR, brief_filename)
        
        with open(brief_path, 'w') as f:
            json.dump(brief, f, indent=2)
        
        # Save to database if available
        if DB_AVAILABLE:
            try:
                save_content_to_database(brief)
            except Exception as db_error:
                print(f"[content] Database save error: {db_error}")
        
        return {
            "success": True,
            "message": f"Content brief created successfully for {brand}",
            "brief_id": brief_id,
            "brief": brief,
            "ai_enhanced": brief.get("ai_enhanced", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[content] Brief creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create brief: {str(e)}")

@router.post("/ideas")
async def generate_content_ideas(
    brand: str = Form(...),
    theme: str = Form("streetwear culture"),
    content_type: str = Form("social_media"),
    quantity: int = Form(10),
    target_audience: str = Form("Gen Z streetwear enthusiasts"),
    current_trends: Optional[str] = Form(None)
):
    """Generate creative content ideas with AI assistance"""
    
    try:
        print(f"[content] Generating {quantity} ideas for {brand}")
        
        # Generate unique ideas ID
        ideas_id = str(uuid.uuid4())
        
        # Create base ideas structure
        ideas_request = {
            "id": ideas_id,
            "type": "ideas",
            "brand": brand,
            "theme": theme,
            "content_type": content_type,
            "quantity": quantity,
            "target_audience": target_audience,
            "current_trends": current_trends,
            "created_at": datetime.now().isoformat()
        }
        
        # Generate AI-powered ideas
        if AI_AVAILABLE and openai_client:
            try:
                ai_ideas = await generate_ai_content_ideas(ideas_request)
                ideas_request["ai_generated_ideas"] = ai_ideas
                ideas_request["ai_enhanced"] = True
            except Exception as e:
                print(f"[content] AI ideas generation error: {e}")
                ideas_request["ai_enhanced"] = False
                ideas_request["ai_error"] = str(e)
        else:
            ideas_request["ai_enhanced"] = False
            ideas_request["ai_note"] = "AI idea generation not available"
        
        # Add manual ideas as fallback
        ideas_request["manual_ideas"] = generate_manual_content_ideas(ideas_request)
        
        # Save ideas to file
        ideas_filename = f"ideas_{ideas_id}.json"
        ideas_path = os.path.join(CONTENT_DIR, ideas_filename)
        
        with open(ideas_path, 'w') as f:
            json.dump(ideas_request, f, indent=2)
        
        # Save to database if available
        if DB_AVAILABLE:
            try:
                save_content_to_database(ideas_request)
            except Exception as db_error:
                print(f"[content] Database save error: {db_error}")
        
        return {
            "success": True,
            "message": f"Generated {quantity} content ideas for {brand}",
            "ideas_id": ideas_id,
            "ideas": ideas_request,
            "ai_enhanced": ideas_request.get("ai_enhanced", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[content] Ideas generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {str(e)}")

@router.get("/briefs")
async def get_content_briefs(limit: int = 20):
    """Get list of created content briefs"""
    
    try:
        briefs = []
        
        if os.path.exists(CONTENT_DIR):
            for filename in os.listdir(CONTENT_DIR):
                if filename.startswith("brief_") and filename.endswith(".json"):
                    file_path = os.path.join(CONTENT_DIR, filename)
                    try:
                        with open(file_path, 'r') as f:
                            brief = json.load(f)
                        briefs.append(brief)
                    except Exception as e:
                        print(f"[content] Error reading brief {filename}: {e}")
        
        # Sort by creation date (newest first) and limit
        briefs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        briefs = briefs[:limit]
        
        return {
            "success": True,
            "briefs": briefs,
            "total_briefs": len(briefs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get briefs: {str(e)}")

@router.get("/ideas")
async def get_content_ideas(limit: int = 20):
    """Get list of generated content ideas"""
    
    try:
        ideas_list = []
        
        if os.path.exists(CONTENT_DIR):
            for filename in os.listdir(CONTENT_DIR):
                if filename.startswith("ideas_") and filename.endswith(".json"):
                    file_path = os.path.join(CONTENT_DIR, filename)
                    try:
                        with open(file_path, 'r') as f:
                            ideas = json.load(f)
                        ideas_list.append(ideas)
                    except Exception as e:
                        print(f"[content] Error reading ideas {filename}: {e}")
        
        # Sort by creation date (newest first) and limit
        ideas_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        ideas_list = ideas_list[:limit]
        
        return {
            "success": True,
            "ideas": ideas_list,
            "total_idea_sets": len(ideas_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ideas: {str(e)}")

async def generate_ai_brief_content(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-enhanced brief content"""
    
    if not AI_AVAILABLE or not openai_client:
        return {"note": "AI content generation not available"}
    
    try:
        prompt = f"""
        Create a comprehensive content brief for {brief['brand']} with these details:
        - Campaign Type: {brief['campaign_type']}
        - Target Audience: {brief['target_audience']}
        - Objectives: {brief['objectives']}
        - Tone: {brief['tone']}
        - Channels: {', '.join(brief['channels'])}
        - Timeline: {brief['timeline']}
        
        Provide a detailed brief in JSON format with:
        1. executive_summary: Brief overview of the campaign
        2. content_pillars: 3-5 key content themes
        3. messaging_framework: Key messages and value propositions
        4. content_calendar: Suggested posting schedule
        5. success_metrics: KPIs to track
        6. creative_guidelines: Visual and copy guidelines
        7. hashtag_strategy: Relevant hashtags for each platform
        
        Focus on streetwear culture, authenticity, and urban lifestyle.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a content strategist specializing in streetwear brands and urban culture, creating briefs for {brief['brand']}."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse JSON response
        try:
            ai_content = json.loads(ai_response)
        except:
            ai_content = {"content": ai_response}
        
        return {
            "ai_brief": ai_content,
            "model": "gpt-3.5-turbo",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[content] AI brief generation error: {e}")
        return {"ai_error": f"AI brief generation failed: {str(e)}"}

async def generate_ai_content_ideas(ideas_request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-powered content ideas"""
    
    if not AI_AVAILABLE or not openai_client:
        return {"note": "AI idea generation not available"}
    
    try:
        prompt = f"""
        Generate {ideas_request['quantity']} creative content ideas for {ideas_request['brand']} with these parameters:
        - Theme: {ideas_request['theme']}
        - Content Type: {ideas_request['content_type']}
        - Target Audience: {ideas_request['target_audience']}
        - Current Trends: {ideas_request.get('current_trends', 'streetwear, urban culture')}
        
        For each idea, provide:
        1. title: Catchy title for the content
        2. description: Detailed description of the content
        3. platform: Best platform for this content
        4. format: Content format (post, story, reel, etc.)
        5. hashtags: Relevant hashtags
        6. call_to_action: Suggested CTA
        7. visual_concept: Description of visual elements
        
        Focus on authentic streetwear culture, urban lifestyle, and current trends.
        Return as JSON array of ideas.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a creative content strategist for {ideas_request['brand']}, specializing in streetwear and urban culture content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse JSON response
        try:
            ai_ideas = json.loads(ai_response)
        except:
            # If JSON parsing fails, create structured response
            ai_ideas = [{"title": "AI Generated Ideas", "description": ai_response}]
        
        return {
            "ai_ideas": ai_ideas,
            "model": "gpt-3.5-turbo",
            "generated_at": datetime.now().isoformat(),
            "total_ideas": len(ai_ideas) if isinstance(ai_ideas, list) else 1
        }
        
    except Exception as e:
        print(f"[content] AI ideas generation error: {e}")
        return {"ai_error": f"AI idea generation failed: {str(e)}"}

def generate_manual_brief_structure(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Generate manual brief structure as fallback"""
    
    return {
        "executive_summary": f"Content campaign for {brief['brand']} targeting {brief['target_audience']} with {brief['campaign_type']} content.",
        "content_pillars": [
            "Brand Authenticity",
            "Streetwear Culture",
            "Urban Lifestyle",
            "Community Engagement"
        ],
        "messaging_framework": {
            "primary_message": f"Authentic {brief['brand']} represents true streetwear culture",
            "supporting_messages": [
                "Quality craftsmanship meets urban style",
                "Built for the streets, worn by the culture",
                "Authentic since day one"
            ]
        },
        "content_calendar": {
            "posting_frequency": "Daily posts, 3-4 stories per day",
            "optimal_times": "12PM, 6PM, 9PM",
            "content_mix": "60% product, 25% lifestyle, 15% community"
        },
        "success_metrics": [
            "Engagement rate",
            "Reach and impressions",
            "Website traffic",
            "Conversion rate"
        ],
        "hashtag_strategy": {
            "brand_hashtags": ["#CrooksAndCastles", "#StreetCulture"],
            "community_hashtags": ["#Streetwear", "#UrbanStyle", "#HipHopFashion"],
            "trending_hashtags": ["#OOTD", "#StreetStyle", "#FashionDaily"]
        }
    }

def generate_manual_content_ideas(ideas_request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate manual content ideas as fallback"""
    
    base_ideas = [
        {
            "title": "Behind the Scenes: Design Process",
            "description": f"Show the creative process behind {ideas_request['brand']} designs",
            "platform": "Instagram",
            "format": "Carousel post",
            "hashtags": ["#BehindTheScenes", "#DesignProcess", "#Streetwear"],
            "call_to_action": "What design would you like to see next?",
            "visual_concept": "Designer sketches, fabric selection, production shots"
        },
        {
            "title": "Street Style Spotlight",
            "description": "Feature customers wearing the brand in their daily lives",
            "platform": "TikTok",
            "format": "Short video",
            "hashtags": ["#StreetStyle", "#OOTD", "#CustomerSpotlight"],
            "call_to_action": "Tag us in your fit!",
            "visual_concept": "Real customers in urban environments"
        },
        {
            "title": "Culture Connection",
            "description": f"Connect {ideas_request['brand']} to hip-hop and street culture",
            "platform": "Instagram",
            "format": "Story series",
            "hashtags": ["#HipHopCulture", "#StreetCulture", "#Authenticity"],
            "call_to_action": "Share your culture story",
            "visual_concept": "Music, art, and fashion intersection"
        },
        {
            "title": "Product Drop Teaser",
            "description": "Build anticipation for new product releases",
            "platform": "Instagram",
            "format": "Reel",
            "hashtags": ["#ComingSoon", "#NewDrop", "#Exclusive"],
            "call_to_action": "Turn on notifications for the drop",
            "visual_concept": "Product reveals, countdown timers"
        },
        {
            "title": "Community Challenges",
            "description": "Engage audience with brand-related challenges",
            "platform": "TikTok",
            "format": "Challenge video",
            "hashtags": ["#Challenge", "#Community", "#StreetChallenge"],
            "call_to_action": "Show us your version!",
            "visual_concept": "User-generated content, creative challenges"
        }
    ]
    
    # Customize ideas based on request
    customized_ideas = []
    for i, idea in enumerate(base_ideas):
        if i < ideas_request['quantity']:
            idea['brand'] = ideas_request['brand']
            idea['theme'] = ideas_request['theme']
            customized_ideas.append(idea)
    
    return customized_ideas

def save_content_to_database(content: Dict[str, Any]):
    """Save content to database"""
    
    if not DB_AVAILABLE:
        return
    
    try:
        with SessionLocal() as session:
            query = text("""
                INSERT INTO content_items 
                (content_id, content_type, brand, data, created_at)
                VALUES (:content_id, :content_type, :brand, :data, :created_at)
            """)
            
            session.execute(query, {
                "content_id": content["id"],
                "content_type": content["type"],
                "brand": content["brand"],
                "data": json.dumps(content),
                "created_at": datetime.now()
            })
            session.commit()
            
    except Exception as e:
        print(f"[content] Database save error: {e}")

@router.get("/health")
async def content_health():
    """Health check for content module"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "database_available": DB_AVAILABLE,
        "content_directory": CONTENT_DIR,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "supported_content_types": ["brief", "ideas", "campaign"]
    }
