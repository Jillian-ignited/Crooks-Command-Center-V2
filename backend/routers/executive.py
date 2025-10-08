from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Intelligence

router = APIRouter()


@router.get("/overview")
def get_executive_overview(db: Session = Depends(get_db)):
    """Get executive dashboard overview with real data"""
    
    # Get intelligence stats
    total_files = db.query(func.count(IntelligenceFile.id)).scalar() or 0
    processed_files = db.query(func.count(IntelligenceFile.id)).filter(
        IntelligenceFile.status == "processed"
    ).scalar() or 0
    
    # Files this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    this_week = db.query(func.count(IntelligenceFile.id)).filter(
        IntelligenceFile.uploaded_at >= week_ago
    ).scalar() or 0
    
    # Get recent files
    recent_files = db.query(IntelligenceFile).order_by(
        desc(IntelligenceFile.uploaded_at)
    ).limit(5).all()
    
    return {
        "stats": {
            "total_files": total_files,
            "processed_files": processed_files,
            "this_week": this_week,
            "pending": total_files - processed_files
        },
        "recent_files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "source": f.source,
                "uploaded_at": f.uploaded_at.isoformat(),
                "has_analysis": bool(
                    f.analysis_results and 
                    isinstance(f.analysis_results, dict) and 
                    "analysis" in f.analysis_results and
                    "error" not in f.analysis_results
                )
            }
            for f in recent_files
        ],
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/priorities")
def get_weekly_priorities():
    """Get top 3 priorities for the week"""
    
    return {
        "week_of": datetime.utcnow().strftime("%Y-%m-%d"),
        "priorities": [
            {
                "id": 1,
                "title": "Review latest competitive intelligence",
                "description": "Analyze trends from recent Apify uploads",
                "action": "Go to Intelligence",
                "link": "/intelligence",
                "category": "intelligence"
            },
            {
                "id": 2,
                "title": "Plan upcoming campaigns",
                "description": "Create content strategy for next drop",
                "action": "Go to Campaigns",
                "link": "/campaigns",
                "category": "campaigns"
            },
            {
                "id": 3,
                "title": "Track agency deliverables",
                "description": "Check pending assets from High Voltage Digital",
                "action": "Go to Deliverables",
                "link": "/deliverables",
                "category": "deliverables"
            }
        ]
    }


@router.get("/quick-stats")
def get_quick_stats():
    """Get quick stats for dashboard cards"""
    
    # Mock Shopify data for now - will be real after Shopify module is fixed
    return {
        "revenue": {
            "current": 124567,
            "change": 12,
            "period": "vs last week"
        },
        "customers": {
            "current": 1234,
            "change": 8,
            "period": "vs last week"
        },
        "orders": {
            "current": 456,
            "change": 15,
            "period": "vs last week"
        },
        "avg_order_value": {
            "current": 273,
            "change": -2,
            "period": "vs last week"
        }
    }


@router.get("/summary")
def get_executive_summary(db: Session = Depends(get_db)):
    """Get executive summary"""
    
    overview = get_executive_overview(db)
    
    return {
        "period": "Current Week",
        "highlights": [
            {
                "title": "Intelligence Files",
                "value": str(overview["stats"]["total_files"]),
                "change": f"+{overview['stats']['this_week']} this week",
                "status": "active"
            },
            {
                "title": "AI Analysis",
                "value": str(overview["stats"]["processed_files"]),
                "change": f"{overview['stats']['pending']} pending",
                "status": "active"
            },
            {
                "title": "Revenue",
                "value": "$124,567",
                "change": "+12% vs last week",
                "status": "mock_data"
            }
        ],
        "insights": [
            f"{overview['stats']['total_files']} intelligence files uploaded",
            f"{overview['stats']['processed_files']} files analyzed with AI",
            f"{overview['stats']['this_week']} new uploads this week"
        ],
        "status": "active"
    }
