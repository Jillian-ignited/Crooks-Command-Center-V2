from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import datetime

router = APIRouter()

# Mock executive data
MOCK_EXECUTIVE_DATA = {
    "orders": {
        "7d": 450,
        "30d": 1850,
        "60d": 3200,
        "quarter": 8500,
        "wow_change": -9.7,
        "mom_change": 12.3
    },
    "net_sales": {
        "7d": 105993,
        "30d": 425000,
        "60d": 780000,
        "quarter": 1950000,
        "wow_change": -11.5,
        "mom_change": 8.7
    },
    "aov": {
        "7d": 236,
        "30d": 229,
        "60d": 244,
        "quarter": 229,
        "wow_change": 2.7,
        "mom_change": -1.2
    },
    "conversion": {
        "7d": 3.90,
        "30d": 4.15,
        "60d": 3.85,
        "quarter": 4.02,
        "wow_change": -4.5,
        "mom_change": 2.1
    },
    "sessions": {
        "7d": 26718,
        "30d": 115000,
        "60d": 225000,
        "quarter": 580000,
        "wow_change": 9.9,
        "mom_change": 15.2
    },
    "social_plays": {
        "7d": 37628,
        "30d": 145000,
        "60d": 290000,
        "quarter": 750000,
        "wow_change": 30.9,
        "mom_change": 22.5
    },
    "social_likes": {
        "7d": 11900,
        "30d": 48500,
        "60d": 95000,
        "quarter": 245000,
        "wow_change": 5.3,
        "mom_change": 18.7
    },
    "social_comments": {
        "7d": 263,
        "30d": 1150,
        "60d": 2300,
        "quarter": 5800,
        "wow_change": 29.5,
        "mom_change": 12.8
    }
}

MOCK_HASHTAGS = {
    "combined": [
        {"tag": "#crooksandcastles", "count": 15420, "engagement": 89500},
        {"tag": "#streetwear", "count": 8930, "engagement": 45200},
        {"tag": "#crooks", "count": 6780, "engagement": 32100},
        {"tag": "#streetstyle", "count": 5640, "engagement": 28900},
        {"tag": "#fashion", "count": 4520, "engagement": 22100}
    ],
    "tiktok": [
        {"tag": "#crooksandcastles", "count": 8920, "engagement": 125000},
        {"tag": "#streetwear", "count": 5430, "engagement": 78000},
        {"tag": "#ootd", "count": 3210, "engagement": 45000},
        {"tag": "#style", "count": 2890, "engagement": 38000},
        {"tag": "#fashion", "count": 2340, "engagement": 32000}
    ],
    "instagram": [
        {"tag": "#crooksandcastles", "count": 6500, "engagement": 54000},
        {"tag": "#streetwear", "count": 3500, "engagement": 29000},
        {"tag": "#crooks", "count": 3470, "engagement": 28500},
        {"tag": "#streetstyle", "count": 2350, "engagement": 19800},
        {"tag": "#fashion", "count": 2180, "engagement": 18200}
    ]
}

@router.get("/overview")
def get_executive_overview(period: str = "7d") -> Dict[str, Any]:
    """Get executive overview data"""
    if period not in ["7d", "30d", "60d", "quarter"]:
        period = "7d"
    
    # Extract data for the requested period
    overview_data = {}
    for metric, data in MOCK_EXECUTIVE_DATA.items():
        overview_data[metric] = {
            "value": data[period],
            "wow_change": data.get("wow_change", 0),
            "mom_change": data.get("mom_change", 0)
        }
    
    return {
        "success": True,
        "period": period,
        "data": overview_data,
        "last_updated": datetime.datetime.now().isoformat(),
        "data_freshness": "real-time"
    }

@router.get("/hashtags")
def get_hashtags(platform: str = "combined", period: str = "7d") -> Dict[str, Any]:
    """Get top hashtag performance"""
    if platform not in ["combined", "tiktok", "instagram"]:
        platform = "combined"
    
    hashtags = MOCK_HASHTAGS.get(platform, MOCK_HASHTAGS["combined"])
    
    return {
        "success": True,
        "platform": platform,
        "period": period,
        "hashtags": hashtags,
        "total_count": len(hashtags),
        "last_updated": datetime.datetime.now().isoformat()
    }

@router.get("/priorities")
def get_priorities() -> Dict[str, Any]:
    """Get executive priorities and recommendations"""
    priorities = [
        {
            "id": "priority_001",
            "title": "Improve Conversion Rate",
            "description": "Current conversion rate is below target. Focus on checkout optimization.",
            "priority": "high",
            "impact": "revenue",
            "timeline": "2 weeks",
            "owner": "E-commerce Team"
        },
        {
            "id": "priority_002", 
            "title": "Increase Social Engagement",
            "description": "Social comments are trending up. Capitalize with more interactive content.",
            "priority": "medium",
            "impact": "brand_awareness",
            "timeline": "1 week",
            "owner": "Social Team"
        },
        {
            "id": "priority_003",
            "title": "Optimize TikTok Strategy",
            "description": "TikTok engagement is outperforming other platforms. Increase investment.",
            "priority": "medium", 
            "impact": "reach",
            "timeline": "3 weeks",
            "owner": "Content Team"
        }
    ]
    
    return {
        "success": True,
        "priorities": priorities,
        "total_count": len(priorities),
        "high_priority_count": len([p for p in priorities if p["priority"] == "high"])
    }

@router.get("/trends")
def get_trends(period: str = "30d") -> Dict[str, Any]:
    """Get trending metrics and insights"""
    trends = {
        "positive_trends": [
            {
                "metric": "Social Plays",
                "change": "+30.9%",
                "description": "Significant increase in video content engagement"
            },
            {
                "metric": "Sessions", 
                "change": "+9.9%",
                "description": "Growing website traffic from organic sources"
            },
            {
                "metric": "Social Comments",
                "change": "+29.5%",
                "description": "Higher community engagement and interaction"
            }
        ],
        "negative_trends": [
            {
                "metric": "Orders",
                "change": "-9.7%",
                "description": "Decline in order volume, investigate conversion funnel"
            },
            {
                "metric": "Net Sales",
                "change": "-11.5%", 
                "description": "Revenue impact from reduced order volume"
            },
            {
                "metric": "Conversion Rate",
                "change": "-4.5%",
                "description": "Checkout optimization needed"
            }
        ],
        "stable_metrics": [
            {
                "metric": "AOV",
                "change": "+2.7%",
                "description": "Average order value remains healthy"
            }
        ]
    }
    
    return {
        "success": True,
        "period": period,
        "trends": trends,
        "analysis_date": datetime.datetime.now().isoformat()
    }

@router.get("/competitive")
def get_competitive_summary() -> Dict[str, Any]:
    """Get competitive intelligence summary"""
    competitive_data = {
        "vs_supreme": {
            "orders": {"us": 450, "them": 473, "difference": -23},
            "revenue": {"us": 105993, "them": 104369, "difference": 1624},
            "aov": {"us": 236, "them": 221, "difference": 15},
            "conversion": {"us": 3.90, "them": 4.80, "difference": -0.90}
        },
        "market_position": {
            "rank": 10,
            "total_brands": 30,
            "category": "Streetwear",
            "market_share": 3.2
        },
        "key_insights": [
            "Revenue ahead of Supreme despite fewer orders",
            "Higher AOV indicates premium positioning success", 
            "Conversion rate gap is primary growth opportunity",
            "Social engagement significantly outperforming competitors"
        ]
    }
    
    return {
        "success": True,
        "competitive_data": competitive_data,
        "last_updated": datetime.datetime.now().isoformat(),
        "data_source": "competitive_intelligence"
    }

@router.post("/refresh")
def refresh_executive_data() -> Dict[str, Any]:
    """Trigger a refresh of executive dashboard data"""
    # In a real implementation, this would trigger data refresh from various sources
    return {
        "success": True,
        "message": "Executive dashboard data refresh initiated",
        "refresh_id": f"refresh_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "estimated_completion": "2-3 minutes"
    }

@router.get("/alerts")
def get_executive_alerts() -> Dict[str, Any]:
    """Get executive alerts and notifications"""
    alerts = [
        {
            "id": "alert_001",
            "type": "warning",
            "title": "Conversion Rate Decline",
            "message": "Conversion rate has dropped 4.5% this week",
            "severity": "medium",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "id": "alert_002",
            "type": "success", 
            "title": "Social Engagement Surge",
            "message": "Social plays increased 30.9% - capitalize on momentum",
            "severity": "low",
            "created_at": datetime.datetime.now().isoformat()
        }
    ]
    
    return {
        "success": True,
        "alerts": alerts,
        "unread_count": len(alerts),
        "critical_count": len([a for a in alerts if a["severity"] == "high"])
    }
