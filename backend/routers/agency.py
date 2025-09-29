from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(tags=["agency"])

class DeliverableUpdate(BaseModel):
    status: str
    quality_score: Optional[int] = None

class ProjectUpdate(BaseModel):
    completion_percentage: int
    status: str

@router.get("")
@router.get("/")
def root():
    return {"ok": True, "router": "agency"}

@router.get("/dashboard")
def dashboard() -> Dict[str, Any]:
    return {
        "success": True,
        "agency_info": {"name": "Agency", "phase": "Phase 1"},
        "current_metrics": {"completion_rate": 0, "on_time_rate": 0, "quality_score": 0, "active_projects": 0},
        "last_updated": datetime.utcnow().isoformat(),
    }

@router.put("/deliverables/{deliverable_id}/status")
def update_deliverable(deliverable_id: int, update: DeliverableUpdate):
    return {"success": True, "deliverable_id": deliverable_id, "new_status": update.status, "quality_score": update.quality_score, "updated_at": datetime.utcnow().isoformat()}

@router.put("/projects/{project_id}/progress")
def update_project(project_id: int, update: ProjectUpdate):
    return {"success": True, "project_id": project_id, "completion_percentage": update.completion_percentage, "status": update.status, "updated_at": datetime.utcnow().isoformat()}
