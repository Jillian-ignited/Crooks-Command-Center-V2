from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import datetime

router = APIRouter()

# Mock agency data for development
MOCK_DELIVERABLES = [
    {
        "id": "del_001",
        "title": "Q1 Brand Campaign Creative",
        "project": "Spring Collection Launch",
        "due_date": "2024-02-15",
        "status": "In Progress",
        "owner": "Creative Team",
        "description": "Design assets for spring collection campaign",
        "priority": "high"
    },
    {
        "id": "del_002", 
        "title": "Social Media Content Calendar",
        "project": "Q1 Social Strategy",
        "due_date": "2024-01-30",
        "status": "Completed",
        "owner": "Social Team",
        "description": "Monthly content calendar for all social platforms",
        "priority": "medium"
    },
    {
        "id": "del_003",
        "title": "Influencer Partnership Deck",
        "project": "Influencer Outreach",
        "due_date": "2024-02-01",
        "status": "Pending",
        "owner": "Partnerships Team",
        "description": "Presentation deck for potential influencer collaborations",
        "priority": "medium"
    },
    {
        "id": "del_004",
        "title": "Website Homepage Redesign",
        "project": "Website Refresh",
        "due_date": "2024-02-28",
        "status": "In Progress", 
        "owner": "Design Team",
        "description": "Complete redesign of homepage layout and content",
        "priority": "high"
    },
    {
        "id": "del_005",
        "title": "Email Marketing Templates",
        "project": "Email Automation",
        "due_date": "2024-01-25",
        "status": "Overdue",
        "owner": "Marketing Team",
        "description": "Responsive email templates for automated campaigns",
        "priority": "high"
    }
]

MOCK_PROJECTS = [
    {
        "id": "proj_001",
        "name": "Spring Collection Launch",
        "client": "Crooks & Castles",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "completion_percentage": 65,
        "status": "active",
        "budget": 50000,
        "spent": 32500
    },
    {
        "id": "proj_002",
        "name": "Q1 Social Strategy", 
        "client": "Crooks & Castles",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "completion_percentage": 80,
        "status": "active",
        "budget": 25000,
        "spent": 20000
    },
    {
        "id": "proj_003",
        "name": "Website Refresh",
        "client": "Crooks & Castles",
        "start_date": "2024-01-15",
        "end_date": "2024-04-15",
        "completion_percentage": 35,
        "status": "active", 
        "budget": 75000,
        "spent": 26250
    }
]

MOCK_METRICS = {
    "completion_rate": 78,
    "completion_trend": 5,
    "on_time_rate": 85,
    "on_time_trend": -2,
    "quality_score": 8.7,
    "quality_trend": 0.3,
    "active_projects": 3,
    "total_deliverables": len(MOCK_DELIVERABLES),
    "completed_deliverables": len([d for d in MOCK_DELIVERABLES if d["status"] == "Completed"]),
    "overdue_deliverables": len([d for d in MOCK_DELIVERABLES if d["status"] == "Overdue"])
}

class StatusUpdate(BaseModel):
    status: str

@router.get("/dashboard")
def get_agency_dashboard() -> Dict[str, Any]:
    """Get agency dashboard overview"""
    return {
        "success": True,
        "week_of": datetime.datetime.now().strftime("%Y-%m-%d"),
        "deliverables": MOCK_DELIVERABLES[:5],  # Recent deliverables
        "metrics": MOCK_METRICS,
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/deliverables")
def get_deliverables(status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """Get agency deliverables with optional status filter"""
    deliverables = MOCK_DELIVERABLES
    
    if status:
        deliverables = [d for d in deliverables if d["status"].lower() == status.lower()]
    
    return {
        "success": True,
        "deliverables": deliverables[:limit],
        "total_count": len(deliverables),
        "filters": {
            "status": status
        }
    }

@router.get("/projects")
def get_projects(status: Optional[str] = None) -> Dict[str, Any]:
    """Get agency projects"""
    projects = MOCK_PROJECTS
    
    if status:
        projects = [p for p in projects if p["status"].lower() == status.lower()]
    
    return {
        "success": True,
        "projects": projects,
        "total_count": len(projects)
    }

@router.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    """Get agency performance metrics"""
    return {
        "success": True,
        **MOCK_METRICS,
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.put("/deliverables/{deliverable_id}/status")
def update_deliverable_status(deliverable_id: str, status_update: StatusUpdate) -> Dict[str, Any]:
    """Update the status of a deliverable"""
    # Find the deliverable
    deliverable = None
    for i, d in enumerate(MOCK_DELIVERABLES):
        if d["id"] == deliverable_id:
            deliverable = d
            MOCK_DELIVERABLES[i]["status"] = status_update.status
            break
    
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    return {
        "success": True,
        "message": f"Deliverable {deliverable_id} status updated to {status_update.status}",
        "deliverable": MOCK_DELIVERABLES[i]
    }

@router.get("/deliverables/{deliverable_id}")
def get_deliverable(deliverable_id: str) -> Dict[str, Any]:
    """Get a specific deliverable by ID"""
    deliverable = next((d for d in MOCK_DELIVERABLES if d["id"] == deliverable_id), None)
    
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    return {
        "success": True,
        "deliverable": deliverable
    }

@router.get("/projects/{project_id}")
def get_project(project_id: str) -> Dict[str, Any]:
    """Get a specific project by ID"""
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "success": True,
        "project": project
    }

@router.get("/team")
def get_team_info() -> Dict[str, Any]:
    """Get agency team information"""
    team_members = [
        {
            "id": "team_001",
            "name": "Sarah Johnson",
            "role": "Creative Director",
            "active_projects": 2,
            "workload": 85
        },
        {
            "id": "team_002",
            "name": "Mike Chen",
            "role": "Senior Designer", 
            "active_projects": 3,
            "workload": 92
        },
        {
            "id": "team_003",
            "name": "Emily Rodriguez",
            "role": "Social Media Manager",
            "active_projects": 2,
            "workload": 78
        },
        {
            "id": "team_004",
            "name": "David Kim",
            "role": "Project Manager",
            "active_projects": 3,
            "workload": 88
        }
    ]
    
    return {
        "success": True,
        "team_members": team_members,
        "total_members": len(team_members),
        "average_workload": sum(m["workload"] for m in team_members) / len(team_members)
    }

@router.get("/timeline")
def get_project_timeline() -> Dict[str, Any]:
    """Get project timeline and milestones"""
    timeline = [
        {
            "date": "2024-01-15",
            "event": "Spring Collection Launch - Kickoff",
            "type": "milestone",
            "project": "Spring Collection Launch"
        },
        {
            "date": "2024-01-30",
            "event": "Social Media Calendar Due",
            "type": "deliverable",
            "project": "Q1 Social Strategy"
        },
        {
            "date": "2024-02-01",
            "event": "Influencer Deck Presentation",
            "type": "deliverable", 
            "project": "Influencer Outreach"
        },
        {
            "date": "2024-02-15",
            "event": "Campaign Creative Review",
            "type": "milestone",
            "project": "Spring Collection Launch"
        },
        {
            "date": "2024-02-28",
            "event": "Website Redesign Launch",
            "type": "milestone",
            "project": "Website Refresh"
        }
    ]
    
    return {
        "success": True,
        "timeline": timeline,
        "upcoming_count": len([t for t in timeline if t["date"] >= datetime.datetime.now().strftime("%Y-%m-%d")])
    }
