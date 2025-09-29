from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def content_root():
    """Content root endpoint"""
    return {
        "success": True,
        "message": "Content API operational",
        "endpoints": ["/dashboard", "/ideas/generate", "/calendar", "/analytics"]
    }

@router.get("/dashboard")
async def content_dashboard():
    """Get content dashboard data"""
    return {
        "success": True,
        "content_performance": {
            "total_content": 87,
            "published": 72,
            "scheduled": 15,
            "top_performing": {
                "title": "Behind the Scenes: Fall Collection",
                "platform": "Instagram",
                "engagement_rate": "8.7%",
                "reach": 45000
            }
        },
        "content_metrics": {
            "avg_engagement_rate": 4.8,
            "content_velocity": 2.5,
            "top_performing_pillar": "Product Showcases",
            "platform_performance": {
                "instagram": {
                    "posts": 35,
                    "avg_engagement": "5.2%",
                    "best_time": "6-8 PM"
                },
                "tiktok": {
                    "posts": 22,
                    "avg_engagement": "7.8%",
                    "best_time": "7-9 PM"
                },
                "twitter": {
                    "posts": 15,
                    "avg_engagement": "3.1%",
                    "best_time": "12-2 PM"
                }
            }
        },
        "content_ideas": [
            {
                "title": "Streetwear Styling Tips",
                "description": "Quick video series showing how to style key pieces from the new collection",
                "platform": "TikTok",
                "trending_factor": 9.2
            },
            {
                "title": "Designer Interview",
                "description": "Behind-the-scenes interview with head designer about inspiration",
                "platform": "Instagram",
                "trending_factor": 8.5
            },
            {
                "title": "Limited Edition Unboxing",
                "description": "Influencer unboxing of limited edition collaboration pieces",
                "platform": "YouTube",
                "trending_factor": 8.8
            },
            {
                "title": "Streetwear History",
                "description": "Educational carousel post about the evolution of streetwear",
                "platform": "Instagram",
                "trending_factor": 7.5
            },
            {
                "title": "Customer Style Showcase",
                "description": "Featuring real customers styling Crooks & Castles pieces",
                "platform": "Instagram",
                "trending_factor": 8.2
            },
            {
                "title": "Design Process Timelapse",
                "description": "Showing the creation process from sketch to final product",
                "platform": "TikTok",
                "trending_factor": 7.8
            }
        ]
    }

@router.post("/ideas/generate")
async def generate_content_ideas():
    """Generate new content ideas"""
    return {
        "success": True,
        "ideas": [
            {
                "title": "Day in the Life: Streetwear Designer",
                "description": "Follow our lead designer through their creative process for a day",
                "platform": "Instagram Stories",
                "trending_factor": 8.7
            },
            {
                "title": "Streetwear Essentials Challenge",
                "description": "Community challenge to style 3 essential pieces 3 different ways",
                "platform": "TikTok",
                "trending_factor": 9.1
            },
            {
                "title": "Material Spotlight Series",
                "description": "Educational series highlighting quality and sustainability of materials",
                "platform": "Instagram",
                "trending_factor": 7.9
            },
            {
                "title": "Collaboration Announcement Teaser",
                "description": "Mysterious teaser for upcoming artist collaboration",
                "platform": "All Platforms",
                "trending_factor": 9.5
            }
        ]
    }

@router.get("/calendar")
async def content_calendar():
    """Get content calendar"""
    return {
        "success": True,
        "calendar": {
            "upcoming": [
                {
                    "date": "2023-09-30",
                    "platform": "Instagram",
                    "content_type": "Carousel Post",
                    "title": "Fall Collection Highlights",
                    "status": "Scheduled"
                },
                {
                    "date": "2023-10-02",
                    "platform": "TikTok",
                    "content_type": "Video",
                    "title": "Styling Challenge",
                    "status": "In Production"
                },
                {
                    "date": "2023-10-05",
                    "platform": "Instagram",
                    "content_type": "Reel",
                    "title": "Behind the Scenes",
                    "status": "Planned"
                }
            ],
            "published": [
                {
                    "date": "2023-09-25",
                    "platform": "Instagram",
                    "content_type": "Post",
                    "title": "New Arrival Announcement",
                    "performance": {
                        "engagement_rate": "5.2%",
                        "reach": 32500,
                        "saves": 450
                    }
                },
                {
                    "date": "2023-09-22",
                    "platform": "TikTok",
                    "content_type": "Video",
                    "title": "Outfit Transition",
                    "performance": {
                        "engagement_rate": "7.8%",
                        "views": 45000,
                        "shares": 320
                    }
                }
            ]
        }
    }

@router.get("/analytics")
async def content_analytics():
    """Get content analytics"""
    return {
        "success": True,
        "analytics": {
            "performance_by_platform": {
                "instagram": {
                    "followers": 125000,
                    "growth_rate": "+2.5%",
                    "engagement_rate": "5.2%",
                    "top_post": "Behind the Scenes: Fall Collection"
                },
                "tiktok": {
                    "followers": 85000,
                    "growth_rate": "+4.8%",
                    "engagement_rate": "7.8%",
                    "top_post": "Outfit Transition Challenge"
                },
                "twitter": {
                    "followers": 45000,
                    "growth_rate": "+1.2%",
                    "engagement_rate": "3.1%",
                    "top_post": "Limited Edition Drop Announcement"
                }
            },
            "content_type_performance": {
                "video": {
                    "engagement_rate": "6.8%",
                    "avg_watch_time": "15.5 seconds",
                    "completion_rate": "62%"
                },
                "carousel": {
                    "engagement_rate": "5.2%",
                    "avg_swipe_through": "3.2 slides",
                    "save_rate": "3.5%"
                },
                "static_image": {
                    "engagement_rate": "4.1%",
                    "save_rate": "2.8%",
                    "share_rate": "1.2%"
                }
            },
            "audience_insights": {
                "age_distribution": {
                    "18-24": "35%",
                    "25-34": "42%",
                    "35-44": "18%",
                    "45+": "5%"
                },
                "gender_distribution": {
                    "male": "65%",
                    "female": "32%",
                    "non_binary": "3%"
                },
                "top_locations": [
                    "Los Angeles",
                    "New York",
                    "Chicago",
                    "Atlanta",
                    "Toronto"
                ],
                "active_hours": {
                    "peak": "6-9 PM EST",
                    "secondary": "12-2 PM EST"
                }
            }
        }
    }
