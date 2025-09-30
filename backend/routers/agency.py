from fastapi import APIRouter
from typing import Dict, Any, List
import datetime

router = APIRouter()

@router.get("/dashboard")
async def get_agency_dashboard() -> Dict[str, Any]:
    """Get agency dashboard overview"""
    return {
        "success": True,
        "week_of": datetime.datetime.now().strftime("%Y-%m-%d"),
        "deliverables": [
            {
                "id": "del_001",
                "title": "Q1 Brand Campaign Creative",
                "project": "Spring Collection Launch",
                "due_date": "2024-02-15",
                "status": "In Progress",
                "owner": "Creative Team",
                "priority": "high"
            },
            {
                "id": "del_002", 
                "title": "Social Media Content Calendar",
                "project": "Q1 Social Strategy",
                "due_date": "2024-01-30",
                "status": "Completed",
                "owner": "Social Team",
                "priority": "medium"
            }
        ],
        "metrics": {
            "completion_rate": 78,
            "on_time_rate": 85,
            "quality_score": 8.7,
            "active_projects": 3,
            "total_deliverables": 5,
            "completed_deliverables": 2,
            "overdue_deliverables": 1
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/deliverables")
async def get_deliverables() -> Dict[str, Any]:
    """Get agency deliverables"""
    return {
        "success": True,
        "deliverables": [
            {
                "id": "del_001",
                "title": "Q1 Brand Campaign Creative",
                "project": "Spring Collection Launch",
                "due_date": "2024-02-15",
                "status": "In Progress",
                "owner": "Creative Team",
                "priority": "high"
            },
            {
                "id": "del_002", 
                "title": "Social Media Content Calendar",
                "project": "Q1 Social Strategy",
                "due_date": "2024-01-30",
                "status": "Completed",
                "owner": "Social Team",
                "priority": "medium"
            }
        ],
        "total_count": 2
    }

@router.get("/projects")
async def get_projects() -> Dict[str, Any]:
    """Get agency projects"""
    return {
        "success": True,
        "projects": [
            {
                "id": "proj_001",
                "name": "Spring Collection Launch",
                "client": "Crooks & Castles",
                "completion_percentage": 65,
                "status": "active",
                "budget": 50000,
                "spent": 32500
            }
        ],
        "total_count": 1
    }

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get agency performance metrics"""
    return {
        "success": True,
        "completion_rate": 78,
        "on_time_rate": 85,
        "quality_score": 8.7,
        "active_projects": 3,
        "total_deliverables": 5,
        "timestamp": datetime.datetime.now().isoformat()
    }
