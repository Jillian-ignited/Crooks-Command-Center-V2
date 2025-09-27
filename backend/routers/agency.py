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
            "agency_info": {"name": "High Voltage Digital", "contract_phase": "Phase 2", "monthly_budget": 7500},
            "current_metrics": {"completion_rate": 85.7, "on_time_rate": 92.3, "quality_score": 9.6, "active_projects": 4},
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/deliverables/{deliverable_id}/status")
async def update_deliverable(deliverable_id: int, update: DeliverableUpdate):
    try:
        return {"success": True, "deliverable_id": deliverable_id, "new_status": update.status, "quality_score": update.quality_score, "updated_at": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}/progress")
async def update_project(project_id: int, update: ProjectUpdate):
    try:
        return {"success": True, "project_id": project_id, "completion_percentage": update.completion_percentage, "status": update.status, "updated_at": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
