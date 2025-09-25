from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

class AgencyRequest(BaseModel):
    partnership_id: Optional[str] = "hvd_primary"
    include_deliverables: bool = True
    include_performance: bool = True

def get_hvd_partnership_data() -> Dict[str, Any]:
    """Get HVD partnership tracking data"""
    return {
        "partnership_id": "hvd_primary",
        "agency_name": "HVD Creative Agency",
        "partnership_status": "active",
        "start_date": "2025-08-01",
        "current_phase": "phase_2",
        "phases": {
            "phase_1": {
                "name": "Foundation & Strategy",
                "budget": 4000,
                "status": "completed",
                "completion_date": "2025-08-31",
                "deliverables_completed": 8,
                "deliverables_total": 8,
                "performance_score": 92
            },
            "phase_2": {
                "name": "Content Creation & Campaigns",
                "budget": 7500,
                "status": "in_progress",
                "start_date": "2025-09-01",
                "expected_completion": "2025-10-31",
                "deliverables_completed": 12,
                "deliverables_total": 18,
                "performance_score": 88
            },
            "phase_3": {
                "name": "Scale & Optimization",
                "budget": 10000,
                "status": "planned",
                "start_date": "2025-11-01",
                "expected_completion": "2025-12-31",
                "deliverables_completed": 0,
                "deliverables_total": 15,
                "performance_score": 0
            }
        },
        "total_budget": 21500,
        "budget_utilized": 11500,
        "budget_remaining": 10000,
        "overall_performance": 90,
        "partnership_health": "excellent"
    }

def get_deliverables_tracking() -> List[Dict[str, Any]]:
    """Get detailed deliverables tracking"""
    return [
        {
            "id": "del_001",
            "title": "Brand Strategy Document",
            "phase": "phase_1",
            "category": "strategy",
            "status": "completed",
            "due_date": "2025-08-15",
            "completion_date": "2025-08-14",
            "quality_score": 95,
            "client_approval": "approved",
            "description": "Comprehensive brand positioning and messaging strategy",
            "deliverable_type": "document",
            "priority": "high"
        },
        {
            "id": "del_002",
            "title": "Visual Identity Guidelines",
            "phase": "phase_1",
            "category": "design",
            "status": "completed",
            "due_date": "2025-08-20",
            "completion_date": "2025-08-19",
            "quality_score": 98,
            "client_approval": "approved",
            "description": "Complete visual identity system and brand guidelines",
            "deliverable_type": "design_system",
            "priority": "high"
        },
        {
            "id": "del_003",
            "title": "Content Calendar Q4 2025",
            "phase": "phase_1",
            "category": "planning",
            "status": "completed",
            "due_date": "2025-08-25",
            "completion_date": "2025-08-24",
            "quality_score": 90,
            "client_approval": "approved",
            "description": "Strategic content calendar with cultural moments integration",
            "deliverable_type": "calendar",
            "priority": "high"
        },
        {
            "id": "del_004",
            "title": "Hispanic Heritage Campaign",
            "phase": "phase_2",
            "category": "campaign",
            "status": "completed",
            "due_date": "2025-09-10",
            "completion_date": "2025-09-08",
            "quality_score": 93,
            "client_approval": "approved",
            "description": "Culturally authentic Hispanic Heritage Month campaign",
            "deliverable_type": "campaign",
            "priority": "high"
        },
        {
            "id": "del_005",
            "title": "Instagram Content Series (Week 1-2)",
            "phase": "phase_2",
            "category": "content",
            "status": "completed",
            "due_date": "2025-09-15",
            "completion_date": "2025-09-14",
            "quality_score": 87,
            "client_approval": "approved",
            "description": "14 Instagram posts with street culture focus",
            "deliverable_type": "content_package",
            "priority": "medium"
        },
        {
            "id": "del_006",
            "title": "TikTok Video Series (Hip-Hop Heritage)",
            "phase": "phase_2",
            "category": "content",
            "status": "in_progress",
            "due_date": "2025-09-30",
            "completion_date": null,
            "quality_score": null,
            "client_approval": "pending",
            "description": "8 TikTok videos celebrating hip-hop culture",
            "deliverable_type": "video_series",
            "priority": "high",
            "progress_percentage": 75
        },
        {
            "id": "del_007",
            "title": "BFCM Campaign Strategy",
            "phase": "phase_2",
            "category": "strategy",
            "status": "in_progress",
            "due_date": "2025-10-15",
            "completion_date": null,
            "quality_score": null,
            "client_approval": "pending",
            "description": "Black Friday Cyber Monday campaign strategy and assets",
            "deliverable_type": "campaign_strategy",
            "priority": "high",
            "progress_percentage": 60
        },
        {
            "id": "del_008",
            "title": "Influencer Partnership Framework",
            "phase": "phase_2",
            "category": "partnerships",
            "status": "in_review",
            "due_date": "2025-10-01",
            "completion_date": "2025-09-28",
            "quality_score": 91,
            "client_approval": "in_review",
            "description": "Framework for authentic influencer collaborations",
            "deliverable_type": "framework",
            "priority": "medium"
        },
        {
            "id": "del_009",
            "title": "Performance Analytics Dashboard",
            "phase": "phase_2",
            "category": "analytics",
            "status": "planned",
            "due_date": "2025-10-20",
            "completion_date": null,
            "quality_score": null,
            "client_approval": "pending",
            "description": "Custom analytics dashboard for campaign performance",
            "deliverable_type": "dashboard",
            "priority": "medium"
        },
        {
            "id": "del_010",
            "title": "Holiday Season Campaign",
            "phase": "phase_3",
            "category": "campaign",
            "status": "planned",
            "due_date": "2025-11-15",
            "completion_date": null,
            "quality_score": null,
            "client_approval": "pending",
            "description": "Comprehensive holiday season marketing campaign",
            "deliverable_type": "campaign",
            "priority": "high"
        }
    ]

def get_performance_metrics() -> Dict[str, Any]:
    """Get agency performance metrics"""
    return {
        "overall_performance": {
            "score": 90,
            "grade": "A",
            "status": "excellent",
            "trend": "improving"
        },
        "delivery_performance": {
            "on_time_delivery": 92,
            "quality_average": 91.5,
            "client_satisfaction": 94,
            "revision_rate": 8
        },
        "engagement_metrics": {
            "response_time_hours": 2.3,
            "communication_score": 96,
            "proactive_updates": 89,
            "meeting_attendance": 100
        },
        "creative_performance": {
            "creative_quality": 93,
            "brand_alignment": 95,
            "cultural_authenticity": 97,
            "innovation_score": 88
        },
        "business_impact": {
            "campaign_effectiveness": 87,
            "roi_improvement": 23,
            "brand_awareness_lift": 31,
            "engagement_growth": 45
        },
        "monthly_trends": [
            {"month": "August 2025", "score": 88, "deliverables": 8, "satisfaction": 92},
            {"month": "September 2025", "score": 92, "deliverables": 12, "satisfaction": 96},
            {"month": "October 2025", "score": 90, "deliverables": 6, "satisfaction": 94}
        ]
    }

def get_weekly_reports() -> List[Dict[str, Any]]:
    """Get weekly check-in reports"""
    return [
        {
            "week_ending": "2025-09-27",
            "status": "on_track",
            "deliverables_completed": 3,
            "deliverables_in_progress": 2,
            "issues_identified": 0,
            "client_feedback": "Excellent progress on TikTok series. Cultural authenticity is spot-on.",
            "next_week_priorities": [
                "Complete TikTok Hip-Hop Heritage series",
                "Begin BFCM campaign asset creation",
                "Review influencer partnership framework"
            ],
            "performance_highlights": [
                "TikTok series exceeding engagement expectations",
                "Cultural authenticity scoring 97%",
                "Client approval rate at 100% this week"
            ],
            "budget_status": {
                "weekly_spend": 1250,
                "budget_remaining": 8750,
                "on_budget": true
            }
        },
        {
            "week_ending": "2025-09-20",
            "status": "completed",
            "deliverables_completed": 4,
            "deliverables_in_progress": 1,
            "issues_identified": 1,
            "client_feedback": "Hispanic Heritage campaign resonated well with community. Minor timing adjustment needed.",
            "next_week_priorities": [
                "Launch TikTok video production",
                "Finalize influencer outreach strategy",
                "Begin BFCM planning phase"
            ],
            "performance_highlights": [
                "Hispanic Heritage campaign launched successfully",
                "Instagram content series completed ahead of schedule",
                "Strong community engagement on heritage content"
            ],
            "budget_status": {
                "weekly_spend": 1100,
                "budget_remaining": 10000,
                "on_budget": true
            }
        },
        {
            "week_ending": "2025-09-13",
            "status": "completed",
            "deliverables_completed": 2,
            "deliverables_in_progress": 3,
            "issues_identified": 0,
            "client_feedback": "Content quality is exceptional. Brand voice is perfectly captured.",
            "next_week_priorities": [
                "Complete Instagram content series",
                "Prepare Hispanic Heritage campaign launch",
                "Begin TikTok series pre-production"
            ],
            "performance_highlights": [
                "All deliverables approved on first review",
                "Brand voice consistency at 98%",
                "Cultural sensitivity review passed with flying colors"
            ],
            "budget_status": {
                "weekly_spend": 950,
                "budget_remaining": 11100,
                "on_budget": true
            }
        }
    ]

def get_strategic_goals() -> List[Dict[str, Any]]:
    """Get strategic partnership goals"""
    return [
        {
            "goal_id": "goal_001",
            "title": "Cultural Authenticity Leadership",
            "description": "Establish Crooks & Castles as the most culturally authentic streetwear brand",
            "category": "brand_positioning",
            "target_metric": "cultural_authenticity_score",
            "target_value": 95,
            "current_value": 92,
            "progress_percentage": 97,
            "status": "on_track",
            "timeline": "Q4 2025",
            "priority": "high"
        },
        {
            "goal_id": "goal_002",
            "title": "Community Engagement Growth",
            "description": "Increase meaningful community engagement by 50%",
            "category": "engagement",
            "target_metric": "community_engagement_rate",
            "target_value": 50,
            "current_value": 31,
            "progress_percentage": 62,
            "status": "on_track",
            "timeline": "Q1 2026",
            "priority": "high"
        },
        {
            "goal_id": "goal_003",
            "title": "Revenue Attribution",
            "description": "Achieve 25% revenue attribution from social campaigns",
            "category": "revenue",
            "target_metric": "social_revenue_attribution",
            "target_value": 25,
            "current_value": 18,
            "progress_percentage": 72,
            "status": "on_track",
            "timeline": "Q2 2026",
            "priority": "high"
        },
        {
            "goal_id": "goal_004",
            "title": "Brand Awareness Expansion",
            "description": "Increase brand awareness in target demographics by 40%",
            "category": "awareness",
            "target_metric": "brand_awareness_lift",
            "target_value": 40,
            "current_value": 31,
            "progress_percentage": 78,
            "status": "ahead_of_schedule",
            "timeline": "Q4 2025",
            "priority": "medium"
        }
    ]

@router.get("/partnership")
async def get_partnership_overview(partnership_id: str = "hvd_primary"):
    """Get comprehensive partnership overview"""
    try:
        partnership_data = get_hvd_partnership_data()
        deliverables = get_deliverables_tracking()
        performance = get_performance_metrics()
        strategic_goals = get_strategic_goals()
        
        # Calculate current phase progress
        current_phase = partnership_data["current_phase"]
        phase_data = partnership_data["phases"][current_phase]
        phase_progress = (phase_data["deliverables_completed"] / phase_data["deliverables_total"]) * 100
        
        # Calculate overall partnership progress
        total_deliverables_completed = sum(
            phase["deliverables_completed"] for phase in partnership_data["phases"].values()
        )
        total_deliverables = sum(
            phase["deliverables_total"] for phase in partnership_data["phases"].values()
        )
        overall_progress = (total_deliverables_completed / total_deliverables) * 100
        
        # Get recent deliverables
        recent_deliverables = [
            d for d in deliverables 
            if d["status"] in ["completed", "in_progress", "in_review"]
        ][-5:]
        
        # Get upcoming deliverables
        upcoming_deliverables = [
            d for d in deliverables 
            if d["status"] in ["planned", "in_progress"]
            and datetime.strptime(d["due_date"], "%Y-%m-%d") >= datetime.now()
        ][:5]
        
        return JSONResponse({
            "success": True,
            "partnership": partnership_data,
            "current_phase_progress": round(phase_progress, 1),
            "overall_progress": round(overall_progress, 1),
            "performance_metrics": performance,
            "strategic_goals": strategic_goals,
            "recent_deliverables": recent_deliverables,
            "upcoming_deliverables": upcoming_deliverables,
            "partnership_health": {
                "status": partnership_data["partnership_health"],
                "performance_score": performance["overall_performance"]["score"],
                "delivery_score": performance["delivery_performance"]["on_time_delivery"],
                "satisfaction_score": performance["delivery_performance"]["client_satisfaction"]
            },
            "key_metrics": {
                "total_budget": partnership_data["total_budget"],
                "budget_utilized": partnership_data["budget_utilized"],
                "budget_remaining": partnership_data["budget_remaining"],
                "deliverables_completed": total_deliverables_completed,
                "deliverables_total": total_deliverables,
                "performance_score": performance["overall_performance"]["score"]
            },
            "next_milestones": [
                {
                    "title": "Complete TikTok Hip-Hop Series",
                    "due_date": "2025-09-30",
                    "priority": "high"
                },
                {
                    "title": "BFCM Campaign Strategy",
                    "due_date": "2025-10-15",
                    "priority": "high"
                },
                {
                    "title": "Phase 3 Planning Session",
                    "due_date": "2025-10-25",
                    "priority": "medium"
                }
            ]
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Partnership overview retrieval failed: {str(e)}",
            "partnership": {},
            "performance_metrics": {},
            "strategic_goals": []
        })

@router.get("/deliverables")
async def get_deliverables_status(phase: Optional[str] = None, status: Optional[str] = None):
    """Get deliverables tracking with optional filtering"""
    try:
        deliverables = get_deliverables_tracking()
        
        # Apply filters
        if phase:
            deliverables = [d for d in deliverables if d["phase"] == phase]
        if status:
            deliverables = [d for d in deliverables if d["status"] == status]
        
        # Calculate statistics
        total_deliverables = len(deliverables)
        completed = len([d for d in deliverables if d["status"] == "completed"])
        in_progress = len([d for d in deliverables if d["status"] == "in_progress"])
        planned = len([d for d in deliverables if d["status"] == "planned"])
        in_review = len([d for d in deliverables if d["status"] == "in_review"])
        
        # Calculate average quality score for completed deliverables
        completed_deliverables = [d for d in deliverables if d["status"] == "completed" and d["quality_score"]]
        avg_quality = sum(d["quality_score"] for d in completed_deliverables) / len(completed_deliverables) if completed_deliverables else 0
        
        # Get overdue deliverables
        overdue = [
            d for d in deliverables 
            if d["status"] in ["in_progress", "planned"] 
            and datetime.strptime(d["due_date"], "%Y-%m-%d") < datetime.now()
        ]
        
        return JSONResponse({
            "success": True,
            "deliverables": deliverables,
            "statistics": {
                "total": total_deliverables,
                "completed": completed,
                "in_progress": in_progress,
                "planned": planned,
                "in_review": in_review,
                "overdue": len(overdue),
                "completion_rate": round((completed / total_deliverables) * 100, 1) if total_deliverables > 0 else 0,
                "average_quality_score": round(avg_quality, 1)
            },
            "overdue_deliverables": overdue,
            "upcoming_deadlines": [
                d for d in deliverables 
                if d["status"] in ["in_progress", "planned"]
                and datetime.strptime(d["due_date"], "%Y-%m-%d") >= datetime.now()
                and datetime.strptime(d["due_date"], "%Y-%m-%d") <= datetime.now() + timedelta(days=14)
            ]
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Deliverables retrieval failed: {str(e)}",
            "deliverables": [],
            "statistics": {}
        })

@router.get("/performance")
async def get_performance_dashboard():
    """Get agency performance dashboard"""
    try:
        performance = get_performance_metrics()
        weekly_reports = get_weekly_reports()
        
        # Calculate trends
        recent_scores = [report["performance_highlights"] for report in weekly_reports[-4:]]
        
        return JSONResponse({
            "success": True,
            "performance": performance,
            "weekly_reports": weekly_reports,
            "performance_trends": {
                "overall_trend": "improving",
                "delivery_trend": "stable",
                "quality_trend": "improving",
                "satisfaction_trend": "excellent"
            },
            "alerts": [
                {
                    "type": "success",
                    "message": "Performance exceeding expectations across all metrics",
                    "priority": "low"
                },
                {
                    "type": "info",
                    "message": "Cultural authenticity score at industry-leading 97%",
                    "priority": "medium"
                }
            ],
            "recommendations": [
                "Continue focus on cultural authenticity - it's a key differentiator",
                "Maintain current delivery pace to stay ahead of schedule",
                "Consider expanding TikTok content based on strong performance"
            ]
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Performance dashboard retrieval failed: {str(e)}",
            "performance": {},
            "weekly_reports": []
        })

@router.get("/reports")
async def get_weekly_reports_list(weeks: int = 4):
    """Get weekly check-in reports"""
    try:
        reports = get_weekly_reports()
        
        # Limit to requested number of weeks
        limited_reports = reports[:weeks]
        
        # Calculate summary statistics
        total_deliverables = sum(report["deliverables_completed"] for report in limited_reports)
        total_issues = sum(report["issues_identified"] for report in limited_reports)
        avg_weekly_spend = sum(report["budget_status"]["weekly_spend"] for report in limited_reports) / len(limited_reports)
        
        return JSONResponse({
            "success": True,
            "weekly_reports": limited_reports,
            "summary": {
                "weeks_reported": len(limited_reports),
                "total_deliverables_completed": total_deliverables,
                "total_issues_identified": total_issues,
                "average_weekly_spend": round(avg_weekly_spend, 2),
                "on_budget_weeks": len([r for r in limited_reports if r["budget_status"]["on_budget"]])
            },
            "trends": {
                "deliverable_trend": "increasing",
                "issue_trend": "decreasing",
                "budget_trend": "on_track",
                "satisfaction_trend": "high"
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Weekly reports retrieval failed: {str(e)}",
            "weekly_reports": [],
            "summary": {}
        })

@router.get("/goals")
async def get_strategic_goals_tracking():
    """Get strategic partnership goals tracking"""
    try:
        goals = get_strategic_goals()
        
        # Calculate overall progress
        total_progress = sum(goal["progress_percentage"] for goal in goals) / len(goals)
        
        # Categorize goals by status
        on_track = [g for g in goals if g["status"] == "on_track"]
        ahead_of_schedule = [g for g in goals if g["status"] == "ahead_of_schedule"]
        at_risk = [g for g in goals if g["status"] == "at_risk"]
        
        return JSONResponse({
            "success": True,
            "strategic_goals": goals,
            "overall_progress": round(total_progress, 1),
            "goal_status_summary": {
                "on_track": len(on_track),
                "ahead_of_schedule": len(ahead_of_schedule),
                "at_risk": len(at_risk),
                "total_goals": len(goals)
            },
            "priority_goals": [g for g in goals if g["priority"] == "high"],
            "next_milestones": [
                {
                    "goal": goal["title"],
                    "target": goal["target_value"],
                    "current": goal["current_value"],
                    "timeline": goal["timeline"]
                }
                for goal in goals if goal["progress_percentage"] < 90
            ]
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Strategic goals retrieval failed: {str(e)}",
            "strategic_goals": [],
            "overall_progress": 0
        })

@router.get("/health")
async def agency_health_check():
    """Health check for agency module"""
    try:
        partnership_data = get_hvd_partnership_data()
        performance = get_performance_metrics()
        
        return JSONResponse({
            "status": "healthy",
            "partnership_active": partnership_data["partnership_status"] == "active",
            "performance_score": performance["overall_performance"]["score"],
            "deliverables_on_track": True,
            "budget_status": "on_track",
            "last_check": datetime.now().isoformat(),
            "message": "Agency module operational with HVD partnership tracking"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "message": "Agency module health check failed"
        })
