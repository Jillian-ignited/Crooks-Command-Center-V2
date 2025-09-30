# backend/routers/content.py
from fastapi import APIRouter, HTTPException, Form
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter()

# Content templates and data for Crooks & Castles
CONTENT_TEMPLATES = {
    "streetwear": {
        "themes": ["Urban Luxury", "Street Culture", "Hip-Hop Heritage", "Rebel Aesthetic"],
        "tones": ["Bold & Confident", "Authentic & Raw", "Aspirational", "Rebellious"],
        "platforms": {
            "instagram": ["Feed Post", "Stories", "Reels", "IGTV"],
            "tiktok": ["Short Video", "Trend Participation", "Challenge", "Behind-the-Scenes"],
            "twitter": ["Thread", "Quote Tweet", "Announcement", "Community"],
            "youtube": ["Product Showcase", "Brand Story", "Collaboration", "Tutorial"]
        }
    },
    "campaigns": {
        "product_launch": {
            "phases": ["Teaser", "Reveal", "Launch", "Social Proof"],
            "content_types": ["Hero Video", "Product Photography", "Lifestyle Shots", "UGC Campaign"]
        },
        "seasonal": {
            "fall_winter": ["Layering Guides", "Street Style", "Holiday Collections", "Year-End Drops"],
            "spring_summer": ["Fresh Drops", "Festival Wear", "Vacation Vibes", "Summer Essentials"]
        },
        "cultural_moments": ["Hip-Hop Anniversaries", "Fashion Week", "Music Festivals", "Sports Events"]
    }
}

RECENT_CONTENT = [
    {
        "id": "content_001",
        "title": "Medusa Chain Hoodie Launch Campaign",
        "type": "Product Launch",
        "status": "Published",
        "platform": "Instagram",
        "created_at": "2025-09-28T10:00:00Z",
        "performance": {
            "reach": 45678,
            "engagement": 3421,
            "clicks": 892,
            "conversions": 67
        },
        "content": {
            "caption": "The streets have spoken. Medusa Chain Hoodie drops tomorrow. 🐍⛓️ #CrooksAndCastles #StreetLuxury",
            "hashtags": ["#CrooksAndCastles", "#StreetLuxury", "#NewDrop", "#Streetwear"],
            "visual": "Hero product shot with urban backdrop"
        }
    },
    {
        "id": "content_002", 
        "title": "Hip-Hop Heritage Series - Biggie Tribute",
        "type": "Cultural Content",
        "status": "Scheduled",
        "platform": "TikTok",
        "created_at": "2025-09-29T14:30:00Z",
        "scheduled_for": "2025-10-01T18:00:00Z",
        "content": {
            "concept": "90s streetwear evolution featuring Biggie-inspired pieces",
            "audio": "Trending hip-hop audio with Biggie sample",
            "visual": "Transition video showing 90s to now styling"
        }
    },
    {
        "id": "content_003",
        "title": "Customer Spotlight - Street Style Feature", 
        "type": "UGC Campaign",
        "status": "In Review",
        "platform": "Instagram Stories",
        "created_at": "2025-09-30T09:15:00Z",
        "content": {
            "concept": "Featuring customer street style with C&C pieces",
            "cta": "Tag us in your fits for a chance to be featured",
            "visual": "UGC reshare with branded overlay"
        }
    }
]

@router.get("/overview")
async def get_content_overview():
    """Get comprehensive content overview and performance metrics"""
    
    try:
        # Calculate performance metrics
        total_content = len(RECENT_CONTENT)
        published_content = len([c for c in RECENT_CONTENT if c["status"] == "Published"])
        scheduled_content = len([c for c in RECENT_CONTENT if c["status"] == "Scheduled"])
        
        # Calculate engagement metrics from published content
        total_reach = sum(c.get("performance", {}).get("reach", 0) for c in RECENT_CONTENT if c["status"] == "Published")
        total_engagement = sum(c.get("performance", {}).get("engagement", 0) for c in RECENT_CONTENT if c["status"] == "Published")
        total_conversions = sum(c.get("performance", {}).get("conversions", 0) for c in RECENT_CONTENT if c["status"] == "Published")
        
        engagement_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0
        
        overview_data = {
            "summary": {
                "total_content_pieces": total_content,
                "published_this_month": published_content,
                "scheduled_content": scheduled_content,
                "content_in_review": len([c for c in RECENT_CONTENT if c["status"] == "In Review"]),
                "avg_engagement_rate": round(engagement_rate, 2),
                "total_reach_30d": total_reach,
                "total_conversions_30d": total_conversions
            },
            "platform_breakdown": {
                "instagram": {
                    "posts": len([c for c in RECENT_CONTENT if c["platform"] == "Instagram"]),
                    "avg_engagement": 7.8,
                    "top_performing": "Product launches and lifestyle content"
                },
                "tiktok": {
                    "posts": len([c for c in RECENT_CONTENT if c["platform"] == "TikTok"]),
                    "avg_engagement": 12.3,
                    "top_performing": "Trend participation and cultural moments"
                },
                "twitter": {
                    "posts": 0,
                    "avg_engagement": 0,
                    "top_performing": "Community engagement and announcements"
                }
            },
            "content_types": {
                "product_launches": {
                    "count": len([c for c in RECENT_CONTENT if c["type"] == "Product Launch"]),
                    "performance": "High conversion rate (7.5%)"
                },
                "cultural_content": {
                    "count": len([c for c in RECENT_CONTENT if c["type"] == "Cultural Content"]),
                    "performance": "Strong engagement and brand affinity"
                },
                "ugc_campaigns": {
                    "count": len([c for c in RECENT_CONTENT if c["type"] == "UGC Campaign"]),
                    "performance": "Excellent community building"
                }
            },
            "recent_content": RECENT_CONTENT,
            "upcoming_opportunities": [
                {
                    "date": "2025-10-05",
                    "event": "NBA Season Opener",
                    "content_idea": "Tunnel walk fits breakdown series",
                    "priority": "high"
                },
                {
                    "date": "2025-10-15", 
                    "event": "Hip-Hop History Month",
                    "content_idea": "90s streetwear evolution series",
                    "priority": "medium"
                },
                {
                    "date": "2025-10-31",
                    "event": "Halloween",
                    "content_idea": "Dark aesthetic collection showcase",
                    "priority": "high"
                }
            ],
            "performance_insights": [
                "Product launch content drives highest conversion rates (7.5% avg)",
                "Cultural moment content generates 40% higher engagement",
                "UGC campaigns increase brand mention by 65%",
                "Video content outperforms static posts by 3.2x"
            ]
        }
        
        return overview_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load content overview: {str(e)}")

@router.post("/brief")
async def create_content_brief(
    brand: str = Form("Crooks & Castles"),
    campaign_type: str = Form("product_launch"),
    target_audience: str = Form("streetwear_enthusiasts"),
    platform: str = Form("instagram"),
    tone: str = Form("bold_confident"),
    objectives: Optional[str] = Form(None)
):
    """Generate comprehensive content brief for campaigns"""
    
    try:
        # Generate brief ID
        brief_id = f"brief_{uuid.uuid4().hex[:8]}"
        
        # Select appropriate templates based on inputs
        campaign_templates = CONTENT_TEMPLATES["campaigns"].get(campaign_type, {})
        platform_formats = CONTENT_TEMPLATES["streetwear"]["platforms"].get(platform, [])
        
        # Generate content strategy
        content_strategy = generate_content_strategy(campaign_type, platform, tone, target_audience)
        
        # Create comprehensive brief
        brief = {
            "brief_id": brief_id,
            "created_at": datetime.now().isoformat(),
            "brand": brand,
            "campaign_details": {
                "type": campaign_type,
                "platform": platform,
                "target_audience": target_audience,
                "tone": tone,
                "objectives": objectives or f"Drive awareness and engagement for {brand} {campaign_type}"
            },
            "content_strategy": content_strategy,
            "creative_direction": {
                "visual_style": get_visual_style(campaign_type, tone),
                "color_palette": ["#000000", "#FFFFFF", "#C9A96E", "#8B0000"],  # C&C brand colors
                "typography": "Bold, street-inspired fonts with luxury touches",
                "photography_style": "Urban lifestyle with high contrast and dramatic lighting"
            },
            "content_calendar": generate_content_calendar(campaign_type, platform),
            "success_metrics": {
                "primary_kpis": ["Reach", "Engagement Rate", "Click-through Rate", "Conversions"],
                "engagement_target": "8%+ engagement rate",
                "reach_target": "50K+ unique accounts",
                "conversion_target": "5%+ click-to-purchase rate"
            },
            "budget_allocation": {
                "content_creation": "40%",
                "paid_promotion": "35%", 
                "influencer_partnerships": "15%",
                "production": "10%"
            },
            "deliverables": generate_deliverables(campaign_type, platform),
            "timeline": generate_timeline(campaign_type),
            "brand_guidelines": {
                "voice": "Authentic, confident, street-smart with luxury aspirations",
                "messaging": "Quality you can feel, style you can see",
                "hashtags": ["#CrooksAndCastles", "#StreetLuxury", "#QualityYouCanFeel"],
                "mentions": "@crookscastles",
                "legal_requirements": "Include FTC disclosures for paid partnerships"
            }
        }
        
        return {
            "success": True,
            "brief": brief,
            "message": f"Content brief created successfully for {campaign_type} campaign"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content brief: {str(e)}")

@router.post("/ideas")
async def generate_content_ideas(
    brand: str = Form("Crooks & Castles"),
    theme: str = Form("streetwear"),
    platform: str = Form("instagram"),
    count: int = Form(5)
):
    """Generate creative content ideas based on brand and theme"""
    
    try:
        ideas = []
        
        # Generate ideas based on theme and platform
        for i in range(count):
            idea = generate_single_idea(brand, theme, platform, i)
            ideas.append(idea)
        
        return {
            "success": True,
            "brand": brand,
            "theme": theme,
            "platform": platform,
            "ideas": ideas,
            "generated_at": datetime.now().isoformat(),
            "total_ideas": len(ideas)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content ideas: {str(e)}")

@router.get("/briefs")
async def get_content_briefs(limit: int = 20):
    """Get list of all created content briefs"""
    
    try:
        # Mock briefs data
        briefs = [
            {
                "brief_id": "brief_a1b2c3d4",
                "title": "Fall Collection Launch Campaign",
                "campaign_type": "product_launch",
                "platform": "instagram",
                "status": "approved",
                "created_at": "2025-09-28T10:00:00Z",
                "budget": "$15,000",
                "timeline": "2 weeks"
            },
            {
                "brief_id": "brief_e5f6g7h8",
                "title": "Hip-Hop Heritage Series",
                "campaign_type": "cultural_content",
                "platform": "tiktok", 
                "status": "in_progress",
                "created_at": "2025-09-25T14:30:00Z",
                "budget": "$8,000",
                "timeline": "3 weeks"
            },
            {
                "brief_id": "brief_i9j0k1l2",
                "title": "Holiday Gift Guide Campaign",
                "campaign_type": "seasonal",
                "platform": "multi_platform",
                "status": "draft",
                "created_at": "2025-09-30T09:15:00Z",
                "budget": "$25,000",
                "timeline": "4 weeks"
            }
        ]
        
        return {
            "briefs": briefs[:limit],
            "total_briefs": len(briefs),
            "summary": {
                "approved": len([b for b in briefs if b["status"] == "approved"]),
                "in_progress": len([b for b in briefs if b["status"] == "in_progress"]),
                "draft": len([b for b in briefs if b["status"] == "draft"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content briefs: {str(e)}")

def generate_content_strategy(campaign_type: str, platform: str, tone: str, audience: str) -> Dict[str, Any]:
    """Generate content strategy based on inputs"""
    
    strategies = {
        "product_launch": {
            "approach": "Build anticipation through teaser content, showcase product features, leverage social proof",
            "content_pillars": ["Product Hero Shots", "Lifestyle Integration", "Behind-the-Scenes", "Customer Stories"],
            "posting_frequency": "Daily during launch week, 3x/week pre-launch",
            "engagement_tactics": ["Countdown posts", "Exclusive previews", "User-generated content campaigns"]
        },
        "cultural_content": {
            "approach": "Connect brand heritage with current culture, educate and inspire audience",
            "content_pillars": ["Hip-Hop History", "Street Culture", "Brand Legacy", "Community Stories"],
            "posting_frequency": "2-3x/week with cultural moment tie-ins",
            "engagement_tactics": ["Educational carousels", "Story polls", "Community challenges"]
        },
        "seasonal": {
            "approach": "Align with seasonal trends while maintaining brand identity",
            "content_pillars": ["Seasonal Styling", "Holiday Collections", "Gift Guides", "Trend Forecasting"],
            "posting_frequency": "4-5x/week during peak season",
            "engagement_tactics": ["Seasonal lookbooks", "Holiday contests", "Gift recommendations"]
        }
    }
    
    return strategies.get(campaign_type, strategies["product_launch"])

def get_visual_style(campaign_type: str, tone: str) -> str:
    """Get visual style recommendations"""
    
    styles = {
        "product_launch": "Clean, high-contrast product photography with urban backdrops",
        "cultural_content": "Vintage-inspired visuals with modern streetwear aesthetic",
        "seasonal": "Lifestyle photography showcasing seasonal styling and environments"
    }
    
    return styles.get(campaign_type, "Bold, street-inspired visuals with luxury touches")

def generate_content_calendar(campaign_type: str, platform: str) -> List[Dict[str, Any]]:
    """Generate content calendar for campaign"""
    
    calendar = []
    base_date = datetime.now()
    
    for i in range(7):  # 7-day calendar
        date = base_date + timedelta(days=i)
        
        if campaign_type == "product_launch":
            content_types = ["Teaser", "Product Feature", "Lifestyle Shot", "Behind-the-Scenes", "Launch Day", "Social Proof", "Follow-up"]
        elif campaign_type == "cultural_content":
            content_types = ["Educational", "Heritage Story", "Modern Connection", "Community Feature", "Throwback", "Current Culture", "Brand Legacy"]
        else:
            content_types = ["Awareness", "Consideration", "Product Focus", "Lifestyle", "Community", "Promotion", "Engagement"]
        
        calendar.append({
            "date": date.strftime("%Y-%m-%d"),
            "content_type": content_types[i % len(content_types)],
            "platform": platform,
            "post_time": "6:00 PM EST" if platform == "instagram" else "7:00 PM EST",
            "content_focus": f"Day {i+1} - {content_types[i % len(content_types)]}"
        })
    
    return calendar

def generate_deliverables(campaign_type: str, platform: str) -> List[str]:
    """Generate list of deliverables for campaign"""
    
    base_deliverables = [
        "Content strategy document",
        "Creative brief and guidelines",
        "Content calendar (7-14 days)",
        "Performance tracking setup"
    ]
    
    if platform == "instagram":
        base_deliverables.extend([
            "Feed posts (1080x1080)",
            "Stories content (1080x1920)",
            "Reels video content",
            "Caption copy and hashtags"
        ])
    elif platform == "tiktok":
        base_deliverables.extend([
            "Short-form video content (9:16)",
            "Trending audio integration",
            "Video captions and effects",
            "Hashtag strategy"
        ])
    
    if campaign_type == "product_launch":
        base_deliverables.extend([
            "Product photography",
            "Launch announcement graphics",
            "Email marketing assets",
            "Paid advertising creatives"
        ])
    
    return base_deliverables

def generate_timeline(campaign_type: str) -> Dict[str, str]:
    """Generate campaign timeline"""
    
    timelines = {
        "product_launch": {
            "Week 1": "Strategy development and content creation",
            "Week 2": "Pre-launch teasers and audience building", 
            "Week 3": "Launch execution and real-time optimization",
            "Week 4": "Post-launch analysis and follow-up content"
        },
        "cultural_content": {
            "Week 1": "Research and content planning",
            "Week 2": "Content creation and review",
            "Week 3": "Publishing and community engagement",
            "Week 4": "Performance analysis and optimization"
        },
        "seasonal": {
            "Week 1-2": "Seasonal trend research and planning",
            "Week 3-4": "Content creation and asset development",
            "Week 5-6": "Campaign execution and optimization",
            "Week 7-8": "Performance analysis and next season planning"
        }
    }
    
    return timelines.get(campaign_type, timelines["product_launch"])

def generate_single_idea(brand: str, theme: str, platform: str, index: int) -> Dict[str, Any]:
    """Generate a single content idea"""
    
    idea_templates = {
        "streetwear": [
            {
                "title": "Street Style Evolution",
                "concept": "Show the evolution of streetwear from 90s to now using brand pieces",
                "format": "Carousel post or video transition",
                "hook": "From the streets to the runway - streetwear evolution"
            },
            {
                "title": "Behind the Design",
                "concept": "Take followers behind the scenes of the design process",
                "format": "Story series or Reels",
                "hook": "Ever wondered how your favorite pieces come to life?"
            },
            {
                "title": "Customer Spotlight",
                "concept": "Feature real customers styling brand pieces their way",
                "format": "UGC reshare with branded overlay",
                "hook": "Our community, our inspiration"
            },
            {
                "title": "Cultural Moment Tie-in",
                "concept": "Connect current cultural events with brand heritage",
                "format": "Educational carousel or video",
                "hook": "Where culture meets fashion"
            },
            {
                "title": "Styling Challenge",
                "concept": "Challenge followers to style one piece multiple ways",
                "format": "Interactive post with user participation",
                "hook": "One piece, endless possibilities"
            }
        ]
    }
    
    templates = idea_templates.get(theme, idea_templates["streetwear"])
    template = templates[index % len(templates)]
    
    return {
        "id": f"idea_{uuid.uuid4().hex[:8]}",
        "title": template["title"],
        "concept": template["concept"],
        "format": template["format"],
        "hook": template["hook"],
        "platform": platform,
        "theme": theme,
        "estimated_reach": random.randint(10000, 50000),
        "difficulty": random.choice(["Easy", "Medium", "Advanced"]),
        "resources_needed": random.choice([
            "Photography, Graphic Design",
            "Video Production, Editing",
            "Community Management, UGC",
            "Research, Copywriting"
        ])
    }
