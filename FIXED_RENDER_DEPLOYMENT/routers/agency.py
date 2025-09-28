from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(tags=["agency"])

class DeliverableUpdate(BaseModel):
    status: str
    quality_score: Optional[int] = None

class ProjectUpdate(BaseModel):
    completion_percentage: int
    status: str

@router.get("/dashboard")
async def dashboard() -> Dict[str, Any]:
    try:
        return {
            "success": True,
            "agency_info": {
                "name": "High Voltage Digital", 
                "contract_phase": "Phase 2", 
                "monthly_budget": 7500
            },
            "metrics": {
                "active_projects": 4,
                "completion_rate": 85.7,
                "overdue_deliverables": 2,
                "client_satisfaction": 4.8
            },
            "current_projects": [
                {
                    "name": "Q4 Heritage Campaign",
                    "client": "Crooks & Castles",
                    "status": "In Progress",
                    "end_date": "2025-12-15",
                    "completion": 65,
                    "budget_used": 4200
                },
                {
                    "name": "Social Media Content Pack",
                    "client": "Crooks & Castles", 
                    "status": "Review",
                    "end_date": "2025-10-30",
                    "completion": 90,
                    "budget_used": 2800
                },
                {
                    "name": "Brand Guidelines Update",
                    "client": "Crooks & Castles",
                    "status": "Planning",
                    "end_date": "2025-11-20",
                    "completion": 25,
                    "budget_used": 800
                },
                {
                    "name": "E-commerce Photography",
                    "client": "Crooks & Castles",
                    "status": "In Progress",
                    "end_date": "2025-11-05",
                    "completion": 45,
                    "budget_used": 1500
                }
            ],
            "upcoming_deadlines": [
                {
                    "title": "Campaign Creative Review",
                    "project_name": "Q4 Heritage Campaign",
                    "due_date": "2025-10-15",
                    "priority": "High",
                    "assignee": "Creative Team"
                },
                {
                    "title": "Final Asset Delivery",
                    "project_name": "Social Media Content Pack",
                    "due_date": "2025-10-30",
                    "priority": "Critical",
                    "assignee": "Production Team"
                },
                {
                    "title": "Brand Guidelines Draft",
                    "project_name": "Brand Guidelines Update",
                    "due_date": "2025-11-01",
                    "priority": "Medium",
                    "assignee": "Strategy Team"
                },
                {
                    "title": "Product Photography Session",
                    "project_name": "E-commerce Photography",
                    "due_date": "2025-10-25",
                    "priority": "High",
                    "assignee": "Photo Team"
                }
            ],
            "team_performance": {
                "total_team_members": 12,
                "active_assignments": 18,
                "avg_utilization": 78.5,
                "top_performer": "Sarah Chen - Creative Director"
            },
            "budget_tracking": {
                "total_budget": 7500,
                "spent_to_date": 5200,
                "remaining": 2300,
                "burn_rate": "On Track",
                "projected_overage": 0
            },
            "quality_metrics": {
                "avg_client_rating": 4.8,
                "revision_rate": 12.5,
                "on_time_delivery": 92.3,
                "client_satisfaction_trend": "+5.2%"
            },
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/deliverables/{deliverable_id}/status")
async def update_deliverable(deliverable_id: int, update: DeliverableUpdate):
    try:
        return {
            "success": True, 
            "deliverable_id": deliverable_id, 
            "new_status": update.status, 
            "quality_score": update.quality_score, 
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}/progress")
async def update_project(project_id: int, update: ProjectUpdate):
    try:
        return {
            "success": True, 
            "project_id": project_id, 
            "completion_percentage": update.completion_percentage, 
            "status": update.status, 
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
