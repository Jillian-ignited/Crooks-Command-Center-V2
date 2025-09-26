from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import os
from typing import List, Optional

router = APIRouter(tags=["agency"])

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")

# Pydantic models for request/response
class DeliverableUpdate(BaseModel):
    status: str
    quality_score: Optional[int] = None

class ProjectUpdate(BaseModel):
    completion_percentage: int
    status: str

@router.get("/dashboard")
async def get_agency_dashboard():
    """Get comprehensive agency dashboard data"""
    try:
        dashboard_data = {
            "success": True,
            "agency_info": {
                "name": "High Voltage Digital",
                "contract_phase": "Phase 2",
                "monthly_budget": 7500,
                "contract_start": "2024-01-01",
                "phase_end": "2024-12-31"
            },
            "current_metrics": {
                "completion_rate": 85.7,
                "on_time_rate": 92.3,
                "quality_score": 9.6,
                "active_projects": 4,
                "completion_trend": 5.2,
                "on_time_trend": -2.1,
                "quality_trend": 0.3
            },
            "deliverables_summary": {
                "total": 14,
                "completed": 12,
                "in_progress": 2,
                "pending": 0,
                "overdue": 0
            },
            "budget_status": {
                "allocated": 7500,
                "spent": 5625,
                "remaining": 1875,
                "utilization_rate": 75.0
            },
            "recent_activity": [
                {
                    "type": "deliverable_completed",
                    "title": "Social Media Analytics Report",
                    "timestamp": "2024-09-21T14:30:00Z"
                },
                {
                    "type": "project_updated",
                    "title": "Website Content Updates",
                    "progress": 80,
                    "timestamp": "2024-09-20T16:45:00Z"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return dashboard_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load agency dashboard: {str(e)}"
        }

@router.get("/deliverables")
async def get_deliverables():
    """Get current deliverables with detailed status"""
    try:
        deliverables_data = {
            "success": True,
            "deliverables": [
                {
                    "id": 1,
                    "title": "Instagram Content Calendar",
                    "project": "Social Media Management",
                    "due_date": "2024-09-05",
                    "status": "Completed",
                    "quality_score": 98,
                    "completed_date": "2024-09-04"
                },
                {
                    "id": 2,
                    "title": "TikTok Video Series",
                    "project": "Content Creation",
                    "due_date": "2024-09-10",
                    "status": "Completed",
                    "quality_score": 95,
                    "completed_date": "2024-09-09"
                },
                {
                    "id": 3,
                    "title": "Brand Photography",
                    "project": "Visual Assets",
                    "due_date": "2024-09-15",
                    "status": "Completed",
                    "quality_score": 97,
                    "completed_date": "2024-09-14"
                },
                {
                    "id": 4,
                    "title": "Influencer Outreach Campaign",
                    "project": "Partnership Development",
                    "due_date": "2024-09-18",
                    "status": "Completed",
                    "quality_score": 94,
                    "completed_date": "2024-09-17"
                },
                {
                    "id": 5,
                    "title": "Email Marketing Templates",
                    "project": "Marketing Automation",
                    "due_date": "2024-09-20",
                    "status": "Completed",
                    "quality_score": 96,
                    "completed_date": "2024-09-19"
                },
                {
                    "id": 6,
                    "title": "Social Media Analytics Report",
                    "project": "Performance Analysis",
                    "due_date": "2024-09-22",
                    "status": "Completed",
                    "quality_score": 99,
                    "completed_date": "2024-09-21"
                },
                {
                    "id": 7,
                    "title": "Website Content Updates",
                    "project": "Web Development",
                    "due_date": "2024-09-28",
                    "status": "In Progress",
                    "progress": 80,
                    "estimated_completion": "2024-09-27"
                },
                {
                    "id": 8,
                    "title": "Q4 Strategy Presentation",
                    "project": "Strategic Planning",
                    "due_date": "2024-09-30",
                    "status": "Pending",
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
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return deliverables_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load deliverables: {str(e)}"
        }

@router.get("/projects")
async def get_projects():
    """Get active projects with progress tracking"""
    try:
        projects_data = {
            "success": True,
            "projects": [
                {
                    "id": 1,
                    "name": "Social Media Management",
                    "client": "Crooks & Castles",
                    "start_date": "2024-07-01",
                    "end_date": "2024-12-31",
                    "completion_percentage": 85,
                    "status": "Active",
                    "budget_allocated": 15000,
                    "budget_used": 12750
                },
                {
                    "id": 2,
                    "name": "Content Creation Pipeline",
                    "client": "Crooks & Castles",
                    "start_date": "2024-08-01",
                    "end_date": "2024-11-30",
                    "completion_percentage": 70,
                    "status": "Active",
                    "budget_allocated": 12000,
                    "budget_used": 8400
                },
                {
                    "id": 3,
                    "name": "Brand Photography Campaign",
                    "client": "Crooks & Castles",
                    "start_date": "2024-09-01",
                    "end_date": "2024-10-31",
                    "completion_percentage": 60,
                    "status": "Active",
                    "budget_allocated": 8000,
                    "budget_used": 4800
                },
                {
                    "id": 4,
                    "name": "Q4 Strategic Planning",
                    "client": "Crooks & Castles",
                    "start_date": "2024-09-15",
                    "end_date": "2024-12-15",
                    "completion_percentage": 25,
                    "status": "Active",
                    "budget_allocated": 10000,
                    "budget_used": 2500
                }
            ],
            "summary": {
                "total_projects": 4,
                "active_projects": 4,
                "completed_projects": 0,
                "total_budget": 45000,
                "budget_used": 28450,
                "average_completion": 60.0
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return projects_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load projects: {str(e)}"
        }

@router.get("/metrics")
async def get_agency_metrics():
    """Get comprehensive agency performance metrics"""
    try:
        metrics_data = {
            "success": True,
            "completion_rate": 85.7,
            "on_time_rate": 92.3,
            "quality_score": 9.6,
            "active_projects": 4,
            "completion_trend": 5.2,
            "on_time_trend": -2.1,
            "quality_trend": 0.3,
            "monthly_performance": [
                {
                    "month": "July 2024",
                    "deliverables": 8,
                    "completed": 8,
                    "on_time": 7,
                    "avg_quality": 9.5
                },
                {
                    "month": "August 2024",
                    "deliverables": 8,
                    "completed": 7,
                    "on_time": 7,
                    "avg_quality": 9.4
                },
                {
                    "month": "September 2024",
                    "deliverables": 8,
                    "completed": 6,
                    "on_time": 6,
                    "avg_quality": 9.7
                }
            ],
            "budget_metrics": {
                "total_allocated": 22500,
                "total_spent": 19575,
                "utilization_rate": 87.0,
                "efficiency_score": 9.2
            },
            "client_satisfaction": {
                "overall_rating": 9.4,
                "communication": 9.6,
                "quality": 9.5,
                "timeliness": 9.1,
                "value": 9.4
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return metrics_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load metrics: {str(e)}"
        }

@router.put("/deliverables/{deliverable_id}/status")
async def update_deliverable_status(deliverable_id: int, update: DeliverableUpdate):
    """Update the status of a specific deliverable"""
    try:
        # In a real implementation, this would update a database
        update_response = {
            "success": True,
            "message": f"Deliverable {deliverable_id} updated successfully",
            "deliverable_id": deliverable_id,
            "new_status": update.status,
            "quality_score": update.quality_score,
            "updated_at": datetime.now().isoformat()
        }
        
        return update_response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update deliverable: {str(e)}"
        }

@router.put("/projects/{project_id}/progress")
async def update_project_progress(project_id: int, update: ProjectUpdate):
    """Update project completion percentage and status"""
    try:
        # In a real implementation, this would update a database
        update_response = {
            "success": True,
            "message": f"Project {project_id} updated successfully",
            "project_id": project_id,
            "completion_percentage": update.completion_percentage,
            "status": update.status,
            "updated_at": datetime.now().isoformat()
        }
        
        return update_response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update project: {str(e)}"
        }

@router.get("/reports/weekly")
async def get_weekly_report():
    """Generate weekly agency performance report"""
    try:
        # Calculate week dates
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        report_data = {
            "success": True,
            "report_period": {
                "start_date": week_start.strftime("%Y-%m-%d"),
                "end_date": week_end.strftime("%Y-%m-%d"),
                "week_number": today.isocalendar()[1]
            },
            "deliverables": {
                "completed_this_week": 3,
                "due_this_week": 4,
                "completion_rate": 75.0,
                "quality_average": 9.6
            },
            "projects": {
                "active_projects": 4,
                "projects_on_track": 3,
                "projects_at_risk": 1,
                "overall_progress": 65.0
            },
            "budget": {
                "weekly_allocation": 1875,  # $7500/month ÷ 4 weeks
                "weekly_spend": 1406.25,
                "utilization": 75.0,
                "remaining": 468.75
            },
            "highlights": [
                "Social Media Analytics Report completed ahead of schedule",
                "Website Content Updates progressing well at 80% completion",
                "Q4 Strategy Presentation planning initiated"
            ],
            "concerns": [
                "Q4 Strategy Presentation timeline may need adjustment"
            ],
            "next_week_priorities": [
                "Complete Website Content Updates",
                "Finalize Q4 Strategy Presentation",
                "Begin October content calendar planning"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return report_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate weekly report: {str(e)}"
        }

@router.get("/compliance")
async def get_compliance_status():
    """Get brand compliance and quality metrics"""
    try:
        compliance_data = {
            "success": True,
            "overall_compliance": 96.2,
            "compliance_categories": {
                "brand_guidelines": 98.1,
                "cultural_authenticity": 95.7,
                "visual_standards": 97.3,
                "content_quality": 94.8,
                "delivery_standards": 96.9
            },
            "recent_audits": [
                {
                    "deliverable": "Instagram Content Calendar",
                    "audit_date": "2024-09-04",
                    "compliance_score": 98.1,
                    "notes": "Excellent adherence to brand guidelines"
                },
                {
                    "deliverable": "TikTok Video Series",
                    "audit_date": "2024-09-09",
                    "compliance_score": 95.2,
                    "notes": "Strong cultural authenticity, minor visual adjustments needed"
                },
                {
                    "deliverable": "Brand Photography",
                    "audit_date": "2024-09-14",
                    "compliance_score": 97.8,
                    "notes": "Outstanding visual quality and brand alignment"
                }
            ],
            "improvement_areas": [
                "Enhance cultural sensitivity review process",
                "Standardize visual contrast requirements"
            ],
            "compliance_trend": "improving",
            "last_audit": "2024-09-21",
            "next_audit": "2024-09-28"
        }
        
        return compliance_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load compliance data: {str(e)}"
        }
