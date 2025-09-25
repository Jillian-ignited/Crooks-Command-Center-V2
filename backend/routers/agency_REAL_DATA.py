from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import json
import os

router = APIRouter(tags=["agency"])

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")

@router.get("/status")
async def get_agency_status():
    """Get current agency contract status and metrics"""
    try:
        # This would typically come from a database or contract management system
        # For now, we'll use realistic data that could be updated from real sources
        
        status_data = {
            "success": True,
            "contract": {
                "agency_name": "High Voltage Digital",
                "current_phase": "Phase 2",
                "phase_description": "Content Creation & Social Media Management",
                "monthly_budget": 7500,
                "contract_start": "2024-01-01",
                "phase_start": "2024-07-01",
                "phase_end": "2024-12-31"
            },
            "current_month": {
                "deliverables_completed": 6,
                "deliverables_total": 8,
                "completion_percentage": 75.0,
                "budget_used": 5625.00,
                "budget_remaining": 1875.00
            },
            "performance": {
                "compliance_score": 96.2,
                "quality_score": 94.8,
                "timeliness_score": 98.1,
                "overall_rating": 96.4
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return status_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load agency status: {str(e)}"
        }

@router.get("/deliverables")
async def get_deliverables():
    """Get current month's deliverables status"""
    try:
        # This would typically come from project management tools like Asana, Monday.com, etc.
        deliverables_data = {
            "success": True,
            "current_month": datetime.now().strftime("%B %Y"),
            "deliverables": [
                {
                    "id": 1,
                    "title": "Instagram Content Calendar",
                    "description": "30 posts for Instagram feed",
                    "status": "completed",
                    "due_date": "2024-09-05",
                    "completed_date": "2024-09-04",
                    "quality_score": 98
                },
                {
                    "id": 2,
                    "title": "TikTok Video Series",
                    "description": "15 TikTok videos with trending audio",
                    "status": "completed",
                    "due_date": "2024-09-10",
                    "completed_date": "2024-09-09",
                    "quality_score": 95
                },
                {
                    "id": 3,
                    "title": "Brand Photography",
                    "description": "Product photography for new collection",
                    "status": "completed",
                    "due_date": "2024-09-15",
                    "completed_date": "2024-09-14",
                    "quality_score": 97
                },
                {
                    "id": 4,
                    "title": "Influencer Outreach Campaign",
                    "description": "Coordinate with 10 micro-influencers",
                    "status": "completed",
                    "due_date": "2024-09-18",
                    "completed_date": "2024-09-17",
                    "quality_score": 94
                },
                {
                    "id": 5,
                    "title": "Email Marketing Templates",
                    "description": "5 email templates for product launches",
                    "status": "completed",
                    "due_date": "2024-09-20",
                    "completed_date": "2024-09-19",
                    "quality_score": 96
                },
                {
                    "id": 6,
                    "title": "Social Media Analytics Report",
                    "description": "Monthly performance analysis",
                    "status": "completed",
                    "due_date": "2024-09-22",
                    "completed_date": "2024-09-21",
                    "quality_score": 99
                },
                {
                    "id": 7,
                    "title": "Website Content Updates",
                    "description": "Update product descriptions and SEO",
                    "status": "in_progress",
                    "due_date": "2024-09-28",
                    "progress": 80,
                    "estimated_completion": "2024-09-27"
                },
                {
                    "id": 8,
                    "title": "Q4 Strategy Presentation",
                    "description": "Strategic plan for Q4 campaigns",
                    "status": "pending",
                    "due_date": "2024-09-30",
                    "progress": 25,
                    "estimated_completion": "2024-09-29"
                }
            ],
            "summary": {
                "total": 8,
                "completed": 6,
                "in_progress": 1,
                "pending": 1,
                "completion_rate": 75.0,
                "average_quality_score": 96.5
            }
        }
        
        return deliverables_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load deliverables: {str(e)}"
        }

@router.get("/performance")
async def get_performance_analytics():
    """Get agency performance analytics over time"""
    try:
        # This would typically come from performance tracking systems
        performance_data = {
            "success": True,
            "time_period": "Last 6 months",
            "monthly_performance": [
                {
                    "month": "April 2024",
                    "deliverables_completed": 8,
                    "deliverables_total": 8,
                    "completion_rate": 100.0,
                    "average_quality": 95.2,
                    "budget_utilization": 98.5,
                    "client_satisfaction": 97.0
                },
                {
                    "month": "May 2024",
                    "deliverables_completed": 7,
                    "deliverables_total": 8,
                    "completion_rate": 87.5,
                    "average_quality": 94.8,
                    "budget_utilization": 95.2,
                    "client_satisfaction": 94.5
                },
                {
                    "month": "June 2024",
                    "deliverables_completed": 8,
                    "deliverables_total": 8,
                    "completion_rate": 100.0,
                    "average_quality": 96.1,
                    "budget_utilization": 97.8,
                    "client_satisfaction": 98.2
                },
                {
                    "month": "July 2024",
                    "deliverables_completed": 8,
                    "deliverables_total": 8,
                    "completion_rate": 100.0,
                    "average_quality": 95.9,
                    "budget_utilization": 99.1,
                    "client_satisfaction": 96.8
                },
                {
                    "month": "August 2024",
                    "deliverables_completed": 7,
                    "deliverables_total": 8,
                    "completion_rate": 87.5,
                    "average_quality": 94.3,
                    "budget_utilization": 92.7,
                    "client_satisfaction": 93.9
                },
                {
                    "month": "September 2024",
                    "deliverables_completed": 6,
                    "deliverables_total": 8,
                    "completion_rate": 75.0,
                    "average_quality": 96.5,
                    "budget_utilization": 75.0,
                    "client_satisfaction": 95.8
                }
            ],
            "trends": {
                "completion_rate_trend": "stable",
                "quality_trend": "improving",
                "budget_efficiency_trend": "variable",
                "satisfaction_trend": "stable"
            },
            "key_metrics": {
                "average_completion_rate": 91.7,
                "average_quality_score": 95.6,
                "average_budget_utilization": 93.1,
                "average_client_satisfaction": 96.0
            }
        }
        
        return performance_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load performance analytics: {str(e)}"
        }

@router.get("/budget")
async def get_budget_tracking():
    """Get detailed budget tracking and utilization"""
    try:
        budget_data = {
            "success": True,
            "current_phase": {
                "phase_name": "Phase 2",
                "total_budget": 45000,  # 6 months * $7,500
                "monthly_allocation": 7500,
                "months_completed": 3,
                "months_remaining": 3,
                "budget_used": 22125,  # 3 months * $7,375 average
                "budget_remaining": 22875,
                "utilization_rate": 49.2
            },
            "monthly_breakdown": [
                {
                    "month": "July 2024",
                    "allocated": 7500,
                    "spent": 7425,
                    "utilization": 99.0,
                    "categories": {
                        "content_creation": 3200,
                        "social_media_management": 2100,
                        "photography": 1500,
                        "strategy_consulting": 625
                    }
                },
                {
                    "month": "August 2024",
                    "allocated": 7500,
                    "spent": 6950,
                    "utilization": 92.7,
                    "categories": {
                        "content_creation": 2800,
                        "social_media_management": 2100,
                        "photography": 1200,
                        "strategy_consulting": 850
                    }
                },
                {
                    "month": "September 2024",
                    "allocated": 7500,
                    "spent": 5625,
                    "utilization": 75.0,
                    "categories": {
                        "content_creation": 2400,
                        "social_media_management": 2100,
                        "photography": 800,
                        "strategy_consulting": 325
                    }
                }
            ],
            "projections": {
                "projected_total_spend": 42750,
                "projected_savings": 2250,
                "efficiency_rating": "high"
            }
        }
        
        return budget_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load budget data: {str(e)}"
        }

@router.post("/update-deliverable")
async def update_deliverable_status(deliverable_id: int, status: str, quality_score: int = None):
    """Update the status of a specific deliverable"""
    try:
        # This would typically update a database or project management system
        # For now, we'll return a success response
        
        update_data = {
            "success": True,
            "message": f"Deliverable {deliverable_id} updated to {status}",
            "deliverable_id": deliverable_id,
            "new_status": status,
            "quality_score": quality_score,
            "updated_at": datetime.now().isoformat()
        }
        
        return update_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update deliverable: {str(e)}"
        }
