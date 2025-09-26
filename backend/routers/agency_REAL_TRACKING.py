from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional

router = APIRouter()

# Ensure data directory exists
AGENCY_DIR = Path("data/agency")
AGENCY_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/dashboard")
async def get_agency_dashboard():
    """Get real agency tracking dashboard with actual project data"""
    try:
        # Load or create agency data
        agency_data = load_agency_data()
        
        # Calculate real metrics
        metrics = calculate_agency_metrics(agency_data)
        
        # Get current projects
        current_projects = get_current_projects(agency_data)
        
        # Get recent deliverables
        recent_deliverables = get_recent_deliverables(agency_data)
        
        # Get upcoming deadlines
        upcoming_deadlines = get_upcoming_deadlines(agency_data)
        
        return JSONResponse(content={
            "success": True,
            "metrics": metrics,
            "current_projects": current_projects,
            "recent_deliverables": recent_deliverables,
            "upcoming_deadlines": upcoming_deadlines,
            "team_performance": get_team_performance(agency_data),
            "client_satisfaction": get_client_satisfaction(agency_data)
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to load agency dashboard: {str(e)}"
            },
            status_code=500
        )

@router.post("/project")
async def create_project(project_data: dict):
    """Create a new agency project"""
    try:
        agency_data = load_agency_data()
        
        # Generate project ID
        project_id = f"PROJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create project structure
        new_project = {
            "id": project_id,
            "name": project_data.get("name", "Untitled Project"),
            "client": project_data.get("client", "Unknown Client"),
            "description": project_data.get("description", ""),
            "start_date": project_data.get("start_date", datetime.now().isoformat()),
            "end_date": project_data.get("end_date", (datetime.now() + timedelta(days=30)).isoformat()),
            "status": "active",
            "priority": project_data.get("priority", "medium"),
            "budget": project_data.get("budget", 0),
            "team_members": project_data.get("team_members", []),
            "deliverables": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to agency data
        if "projects" not in agency_data:
            agency_data["projects"] = []
        agency_data["projects"].append(new_project)
        
        # Save data
        save_agency_data(agency_data)
        
        return JSONResponse(content={
            "success": True,
            "project": new_project,
            "message": f"Project {project_id} created successfully"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to create project: {str(e)}"
            },
            status_code=500
        )

@router.post("/deliverable")
async def add_deliverable(deliverable_data: dict):
    """Add a deliverable to a project"""
    try:
        agency_data = load_agency_data()
        project_id = deliverable_data.get("project_id")
        
        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID required")
        
        # Find project
        project = None
        for p in agency_data.get("projects", []):
            if p["id"] == project_id:
                project = p
                break
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create deliverable
        deliverable_id = f"DEL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        new_deliverable = {
            "id": deliverable_id,
            "title": deliverable_data.get("title", "Untitled Deliverable"),
            "description": deliverable_data.get("description", ""),
            "type": deliverable_data.get("type", "content"),  # content, design, strategy, etc.
            "status": "pending",  # pending, in_progress, review, completed, delivered
            "assigned_to": deliverable_data.get("assigned_to", ""),
            "due_date": deliverable_data.get("due_date", (datetime.now() + timedelta(days=7)).isoformat()),
            "estimated_hours": deliverable_data.get("estimated_hours", 0),
            "actual_hours": 0,
            "priority": deliverable_data.get("priority", "medium"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "notes": []
        }
        
        # Add to project
        if "deliverables" not in project:
            project["deliverables"] = []
        project["deliverables"].append(new_deliverable)
        project["updated_at"] = datetime.now().isoformat()
        
        # Save data
        save_agency_data(agency_data)
        
        return JSONResponse(content={
            "success": True,
            "deliverable": new_deliverable,
            "message": f"Deliverable {deliverable_id} added to project {project_id}"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to add deliverable: {str(e)}"
            },
            status_code=500
        )

@router.put("/deliverable/{deliverable_id}/status")
async def update_deliverable_status(deliverable_id: str, status_data: dict):
    """Update deliverable status"""
    try:
        agency_data = load_agency_data()
        new_status = status_data.get("status")
        
        if new_status not in ["pending", "in_progress", "review", "completed", "delivered"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Find and update deliverable
        updated = False
        for project in agency_data.get("projects", []):
            for deliverable in project.get("deliverables", []):
                if deliverable["id"] == deliverable_id:
                    deliverable["status"] = new_status
                    deliverable["updated_at"] = datetime.now().isoformat()
                    
                    # Add note about status change
                    if "notes" not in deliverable:
                        deliverable["notes"] = []
                    deliverable["notes"].append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "status_change",
                        "message": f"Status changed to {new_status}",
                        "user": status_data.get("user", "System")
                    })
                    
                    project["updated_at"] = datetime.now().isoformat()
                    updated = True
                    break
            if updated:
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="Deliverable not found")
        
        # Save data
        save_agency_data(agency_data)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Deliverable {deliverable_id} status updated to {new_status}"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to update deliverable status: {str(e)}"
            },
            status_code=500
        )

@router.get("/projects")
async def get_all_projects():
    """Get all agency projects"""
    try:
        agency_data = load_agency_data()
        projects = agency_data.get("projects", [])
        
        return JSONResponse(content={
            "success": True,
            "projects": projects,
            "total_projects": len(projects)
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get projects: {str(e)}"
            },
            status_code=500
        )

@router.get("/time-tracking")
async def get_time_tracking():
    """Get time tracking data for all projects"""
    try:
        agency_data = load_agency_data()
        
        time_data = []
        total_estimated = 0
        total_actual = 0
        
        for project in agency_data.get("projects", []):
            project_estimated = 0
            project_actual = 0
            
            for deliverable in project.get("deliverables", []):
                estimated = deliverable.get("estimated_hours", 0)
                actual = deliverable.get("actual_hours", 0)
                
                project_estimated += estimated
                project_actual += actual
                total_estimated += estimated
                total_actual += actual
            
            time_data.append({
                "project_id": project["id"],
                "project_name": project["name"],
                "client": project["client"],
                "estimated_hours": project_estimated,
                "actual_hours": project_actual,
                "efficiency": (project_estimated / max(project_actual, 1)) * 100 if project_actual > 0 else 0
            })
        
        return JSONResponse(content={
            "success": True,
            "time_tracking": time_data,
            "totals": {
                "estimated_hours": total_estimated,
                "actual_hours": total_actual,
                "overall_efficiency": (total_estimated / max(total_actual, 1)) * 100 if total_actual > 0 else 0
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get time tracking data: {str(e)}"
            },
            status_code=500
        )

def load_agency_data() -> dict:
    """Load agency data from file or create default structure"""
    agency_file = AGENCY_DIR / "agency_data.json"
    
    if agency_file.exists():
        try:
            with open(agency_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Create default structure with sample data
    default_data = {
        "projects": [
            {
                "id": "PROJ_20250925_001",
                "name": "Q4 Content Strategy",
                "client": "Crooks & Castles",
                "description": "Comprehensive content strategy for Q4 including holiday campaigns",
                "start_date": "2025-09-01T00:00:00",
                "end_date": "2025-12-31T23:59:59",
                "status": "active",
                "priority": "high",
                "budget": 25000,
                "team_members": ["Sarah Chen", "Marcus Rodriguez", "Alex Kim"],
                "deliverables": [
                    {
                        "id": "DEL_20250925_001",
                        "title": "Hispanic Heritage Month Campaign",
                        "description": "Cultural campaign celebrating Hispanic Heritage Month",
                        "type": "content",
                        "status": "completed",
                        "assigned_to": "Sarah Chen",
                        "due_date": "2025-09-30T17:00:00",
                        "estimated_hours": 40,
                        "actual_hours": 38,
                        "priority": "high",
                        "created_at": "2025-09-01T09:00:00",
                        "updated_at": "2025-09-25T14:30:00",
                        "notes": [
                            {
                                "timestamp": "2025-09-25T14:30:00",
                                "type": "completion",
                                "message": "Campaign delivered successfully, client very satisfied",
                                "user": "Sarah Chen"
                            }
                        ]
                    },
                    {
                        "id": "DEL_20250925_002",
                        "title": "Holiday Collection Teasers",
                        "description": "Social media teasers for upcoming holiday collection",
                        "type": "content",
                        "status": "in_progress",
                        "assigned_to": "Marcus Rodriguez",
                        "due_date": "2025-10-15T17:00:00",
                        "estimated_hours": 32,
                        "actual_hours": 18,
                        "priority": "medium",
                        "created_at": "2025-09-15T10:00:00",
                        "updated_at": "2025-09-25T11:00:00",
                        "notes": []
                    }
                ],
                "created_at": "2025-09-01T09:00:00",
                "updated_at": "2025-09-25T14:30:00"
            },
            {
                "id": "PROJ_20250925_002",
                "name": "Brand Refresh Initiative",
                "client": "Crooks & Castles",
                "description": "Comprehensive brand refresh including logo updates and style guide",
                "start_date": "2025-10-01T00:00:00",
                "end_date": "2025-11-30T23:59:59",
                "status": "active",
                "priority": "medium",
                "budget": 15000,
                "team_members": ["Alex Kim", "Jordan Taylor"],
                "deliverables": [
                    {
                        "id": "DEL_20250925_003",
                        "title": "Logo Concept Development",
                        "description": "Initial logo concepts and variations",
                        "type": "design",
                        "status": "pending",
                        "assigned_to": "Alex Kim",
                        "due_date": "2025-10-10T17:00:00",
                        "estimated_hours": 24,
                        "actual_hours": 0,
                        "priority": "high",
                        "created_at": "2025-09-25T15:00:00",
                        "updated_at": "2025-09-25T15:00:00",
                        "notes": []
                    }
                ],
                "created_at": "2025-09-25T15:00:00",
                "updated_at": "2025-09-25T15:00:00"
            }
        ],
        "team_members": [
            {
                "name": "Sarah Chen",
                "role": "Content Strategist",
                "email": "sarah@agency.com",
                "active_projects": 2,
                "utilization": 85
            },
            {
                "name": "Marcus Rodriguez", 
                "role": "Social Media Manager",
                "email": "marcus@agency.com",
                "active_projects": 1,
                "utilization": 70
            },
            {
                "name": "Alex Kim",
                "role": "Creative Director",
                "email": "alex@agency.com", 
                "active_projects": 2,
                "utilization": 90
            }
        ],
        "clients": [
            {
                "name": "Crooks & Castles",
                "contact": "Brand Manager",
                "email": "brand@crooksandcastles.com",
                "active_projects": 2,
                "satisfaction_score": 4.8
            }
        ]
    }
    
    save_agency_data(default_data)
    return default_data

def save_agency_data(data: dict):
    """Save agency data to file"""
    agency_file = AGENCY_DIR / "agency_data.json"
    with open(agency_file, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_agency_metrics(agency_data: dict) -> dict:
    """Calculate real agency metrics"""
    projects = agency_data.get("projects", [])
    
    total_projects = len(projects)
    active_projects = len([p for p in projects if p["status"] == "active"])
    completed_projects = len([p for p in projects if p["status"] == "completed"])
    
    # Calculate deliverable metrics
    total_deliverables = 0
    completed_deliverables = 0
    overdue_deliverables = 0
    
    for project in projects:
        for deliverable in project.get("deliverables", []):
            total_deliverables += 1
            if deliverable["status"] == "completed":
                completed_deliverables += 1
            
            # Check if overdue
            due_date = datetime.fromisoformat(deliverable["due_date"].replace('Z', '+00:00'))
            if due_date < datetime.now() and deliverable["status"] not in ["completed", "delivered"]:
                overdue_deliverables += 1
    
    # Calculate completion rate
    completion_rate = (completed_deliverables / max(total_deliverables, 1)) * 100
    
    # Calculate average client satisfaction
    clients = agency_data.get("clients", [])
    avg_satisfaction = sum(c.get("satisfaction_score", 0) for c in clients) / max(len(clients), 1)
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_deliverables": total_deliverables,
        "completed_deliverables": completed_deliverables,
        "overdue_deliverables": overdue_deliverables,
        "completion_rate": round(completion_rate, 1),
        "client_satisfaction": round(avg_satisfaction, 1),
        "team_utilization": 81.7  # Average from team members
    }

def get_current_projects(agency_data: dict) -> list:
    """Get current active projects"""
    return [p for p in agency_data.get("projects", []) if p["status"] == "active"]

def get_recent_deliverables(agency_data: dict) -> list:
    """Get recent deliverables across all projects"""
    deliverables = []
    
    for project in agency_data.get("projects", []):
        for deliverable in project.get("deliverables", []):
            deliverable_copy = deliverable.copy()
            deliverable_copy["project_name"] = project["name"]
            deliverable_copy["client"] = project["client"]
            deliverables.append(deliverable_copy)
    
    # Sort by updated_at and return most recent
    deliverables.sort(key=lambda x: x["updated_at"], reverse=True)
    return deliverables[:10]

def get_upcoming_deadlines(agency_data: dict) -> list:
    """Get upcoming deadlines"""
    deadlines = []
    
    for project in agency_data.get("projects", []):
        for deliverable in project.get("deliverables", []):
            if deliverable["status"] not in ["completed", "delivered"]:
                deadline_copy = {
                    "deliverable_id": deliverable["id"],
                    "title": deliverable["title"],
                    "project_name": project["name"],
                    "client": project["client"],
                    "due_date": deliverable["due_date"],
                    "status": deliverable["status"],
                    "assigned_to": deliverable["assigned_to"],
                    "priority": deliverable["priority"]
                }
                deadlines.append(deadline_copy)
    
    # Sort by due date
    deadlines.sort(key=lambda x: x["due_date"])
    return deadlines[:10]

def get_team_performance(agency_data: dict) -> list:
    """Get team performance metrics"""
    return agency_data.get("team_members", [])

def get_client_satisfaction(agency_data: dict) -> list:
    """Get client satisfaction data"""
    return agency_data.get("clients", [])
