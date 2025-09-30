# backend/routers/agency.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import csv
import io
import uuid

router = APIRouter()

# Store uploaded deliverables data (in production, use database)
UPLOADED_DELIVERABLES = []

# Default agency deliverables data
DEFAULT_DELIVERABLES = [
    {
        "id": "del_001",
        "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
        "category": "Ad Creative",
        "task": "Develop 3–4 ad creatives/month (static + light video/motion)",
        "due_date": "2025-10-21",
        "asset_requirements": "Static graphics (1080x1080, 1200x628), vertical video (9:16), UGC/motion as needed",
        "status": "Not Started",
        "owner": "",
        "priority": "High",
        "estimated_hours": 40,
        "budget_allocated": 5000
    },
    {
        "id": "del_002", 
        "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
        "category": "Ad Management",
        "task": "Set up low-spend campaigns on Meta & Google (brand awareness + retargeting)",
        "due_date": "2025-10-07",
        "asset_requirements": "Meta/Google campaign setup, targeting, pixel tracking, budget pacing",
        "status": "In Progress",
        "owner": "Digital Team",
        "priority": "High",
        "estimated_hours": 20,
        "budget_allocated": 3000
    },
    {
        "id": "del_003",
        "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)", 
        "category": "Social Media Content",
        "task": "Create & publish 8–12 posts/month across social channels",
        "due_date": "2025-10-20",
        "asset_requirements": "Square (1080x1080) + vertical (1080x1920), captions, hashtags",
        "status": "Not Started",
        "owner": "Content Team",
        "priority": "Medium",
        "estimated_hours": 60,
        "budget_allocated": 4000
    }
]

@router.get("/dashboard")
async def get_agency_dashboard():
    """Get comprehensive agency dashboard with project overview"""
    
    try:
        # Use uploaded data if available, otherwise use defaults
        deliverables = UPLOADED_DELIVERABLES if UPLOADED_DELIVERABLES else DEFAULT_DELIVERABLES
        
        # Calculate dashboard metrics
        total_deliverables = len(deliverables)
        completed = len([d for d in deliverables if d.get("status") == "Completed"])
        in_progress = len([d for d in deliverables if d.get("status") == "In Progress"])
        not_started = len([d for d in deliverables if d.get("status") == "Not Started"])
        overdue = len([d for d in deliverables if is_overdue(d.get("due_date", ""))])
        
        # Calculate budget metrics
        total_budget = sum(d.get("budget_allocated", 0) for d in deliverables)
        spent_budget = sum(d.get("budget_allocated", 0) for d in deliverables if d.get("status") == "Completed")
        
        # Get upcoming deadlines
        upcoming_deadlines = get_upcoming_deadlines(deliverables)
        
        # Phase breakdown
        phases = {}
        for deliverable in deliverables:
            phase = deliverable.get("phase", "Unknown Phase")
            if phase not in phases:
                phases[phase] = {"total": 0, "completed": 0, "in_progress": 0}
            phases[phase]["total"] += 1
            if deliverable.get("status") == "Completed":
                phases[phase]["completed"] += 1
            elif deliverable.get("status") == "In Progress":
                phases[phase]["in_progress"] += 1
        
        dashboard_data = {
            "project_overview": {
                "total_deliverables": total_deliverables,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started,
                "overdue": overdue,
                "completion_rate": round((completed / total_deliverables * 100), 1) if total_deliverables > 0 else 0
            },
            "budget_overview": {
                "total_allocated": total_budget,
                "spent": spent_budget,
                "remaining": total_budget - spent_budget,
                "utilization_rate": round((spent_budget / total_budget * 100), 1) if total_budget > 0 else 0
            },
            "phase_breakdown": phases,
            "upcoming_deadlines": upcoming_deadlines,
            "team_workload": {
                "Digital Team": len([d for d in deliverables if d.get("owner") == "Digital Team"]),
                "Content Team": len([d for d in deliverables if d.get("owner") == "Content Team"]),
                "Creative Team": len([d for d in deliverables if d.get("owner") == "Creative Team"]),
                "Unassigned": len([d for d in deliverables if not d.get("owner")])
            },
            "priority_distribution": {
                "High": len([d for d in deliverables if d.get("priority") == "High"]),
                "Medium": len([d for d in deliverables if d.get("priority") == "Medium"]),
                "Low": len([d for d in deliverables if d.get("priority") == "Low"])
            },
            "recent_activity": [
                {
                    "date": "2025-09-30T10:00:00Z",
                    "action": "Deliverable updated",
                    "description": "Ad Management campaign setup marked as In Progress",
                    "user": "Digital Team"
                },
                {
                    "date": "2025-09-29T15:30:00Z", 
                    "action": "New deliverable added",
                    "description": "Social Media Content creation task assigned",
                    "user": "Project Manager"
                },
                {
                    "date": "2025-09-28T09:15:00Z",
                    "action": "Budget updated",
                    "description": "Ad Creative budget allocation increased to $5,000",
                    "user": "Account Manager"
                }
            ],
            "alerts": [
                {
                    "type": "deadline",
                    "message": f"{overdue} deliverable(s) are overdue",
                    "severity": "high" if overdue > 0 else "low"
                },
                {
                    "type": "budget",
                    "message": f"Budget utilization at {round((spent_budget / total_budget * 100), 1)}%",
                    "severity": "medium" if spent_budget / total_budget > 0.8 else "low"
                }
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load agency dashboard: {str(e)}")

@router.get("/deliverables")
async def get_agency_deliverables(
    phase: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None
):
    """Get agency deliverables with optional filtering"""
    
    try:
        # Use uploaded data if available, otherwise use defaults
        deliverables = UPLOADED_DELIVERABLES if UPLOADED_DELIVERABLES else DEFAULT_DELIVERABLES
        
        # Apply filters
        filtered_deliverables = deliverables.copy()
        
        if phase:
            filtered_deliverables = [d for d in filtered_deliverables if phase.lower() in d.get("phase", "").lower()]
        
        if status:
            filtered_deliverables = [d for d in filtered_deliverables if d.get("status", "").lower() == status.lower()]
        
        if category:
            filtered_deliverables = [d for d in filtered_deliverables if d.get("category", "").lower() == category.lower()]
        
        # Add calculated fields
        for deliverable in filtered_deliverables:
            deliverable["is_overdue"] = is_overdue(deliverable.get("due_date", ""))
            deliverable["days_until_due"] = days_until_due(deliverable.get("due_date", ""))
        
        # Get summary statistics
        summary = {
            "total_deliverables": len(filtered_deliverables),
            "by_status": {},
            "by_category": {},
            "by_phase": {}
        }
        
        for deliverable in filtered_deliverables:
            # Status breakdown
            status_key = deliverable.get("status", "Unknown")
            summary["by_status"][status_key] = summary["by_status"].get(status_key, 0) + 1
            
            # Category breakdown
            category_key = deliverable.get("category", "Unknown")
            summary["by_category"][category_key] = summary["by_category"].get(category_key, 0) + 1
            
            # Phase breakdown
            phase_key = deliverable.get("phase", "Unknown")
            summary["by_phase"][phase_key] = summary["by_phase"].get(phase_key, 0) + 1
        
        return {
            "deliverables": filtered_deliverables,
            "summary": summary,
            "filters_applied": {
                "phase": phase,
                "status": status,
                "category": category
            },
            "data_source": "uploaded_csv" if UPLOADED_DELIVERABLES else "default_data"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agency deliverables: {str(e)}")

@router.post("/deliverables/upload")
async def upload_deliverables_csv(
    file: UploadFile = File(...),
    replace_existing: bool = Form(False)
):
    """Upload and process agency deliverables CSV file"""
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read and parse CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(csv_reader)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty or invalid")
        
        # Process and validate CSV data
        processed_deliverables = []
        
        for i, row in enumerate(rows):
            try:
                # Map CSV columns to deliverable fields (flexible column mapping)
                deliverable = {
                    "id": f"del_{uuid.uuid4().hex[:8]}",
                    "phase": row.get("Phase") or row.get("phase") or f"Phase {i+1}",
                    "category": row.get("Category") or row.get("category") or "General",
                    "task": row.get("Task") or row.get("task") or row.get("description") or "Task description",
                    "due_date": row.get("Due Date") or row.get("due_date") or row.get("deadline") or "",
                    "asset_requirements": row.get("Asset Requirements") or row.get("asset_requirements") or row.get("assets") or "",
                    "status": row.get("Status") or row.get("status") or "Not Started",
                    "owner": row.get("Owner") or row.get("owner") or row.get("assignee") or "",
                    "priority": row.get("Priority") or row.get("priority") or "Medium",
                    "estimated_hours": parse_number(row.get("Estimated Hours") or row.get("hours") or "0"),
                    "budget_allocated": parse_number(row.get("Budget") or row.get("budget_allocated") or "0"),
                    "notes": row.get("Notes") or row.get("notes") or "",
                    "uploaded_at": datetime.now().isoformat()
                }
                
                processed_deliverables.append(deliverable)
                
            except Exception as e:
                # Log error but continue processing other rows
                print(f"Error processing row {i+1}: {str(e)}")
                continue
        
        if not processed_deliverables:
            raise HTTPException(status_code=400, detail="No valid deliverables found in CSV")
        
        # Update global deliverables data
        global UPLOADED_DELIVERABLES
        if replace_existing:
            UPLOADED_DELIVERABLES = processed_deliverables
        else:
            UPLOADED_DELIVERABLES.extend(processed_deliverables)
        
        # Generate upload summary
        upload_summary = {
            "upload_id": f"upload_{uuid.uuid4().hex[:8]}",
            "filename": file.filename,
            "uploaded_at": datetime.now().isoformat(),
            "total_rows": len(rows),
            "processed_deliverables": len(processed_deliverables),
            "skipped_rows": len(rows) - len(processed_deliverables),
            "replace_existing": replace_existing,
            "total_deliverables_now": len(UPLOADED_DELIVERABLES)
        }
        
        return {
            "success": True,
            "message": f"Successfully uploaded {len(processed_deliverables)} deliverables from {file.filename}",
            "upload_summary": upload_summary,
            "sample_deliverables": processed_deliverables[:3]  # Show first 3 as preview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload deliverables CSV: {str(e)}")

@router.get("/projects")
async def get_agency_projects():
    """Get agency projects overview"""
    
    try:
        # Use uploaded data if available, otherwise use defaults
        deliverables = UPLOADED_DELIVERABLES if UPLOADED_DELIVERABLES else DEFAULT_DELIVERABLES
        
        # Group deliverables by phase to create projects
        projects = {}
        
        for deliverable in deliverables:
            phase = deliverable.get("phase", "Unknown Phase")
            if phase not in projects:
                projects[phase] = {
                    "name": phase,
                    "deliverables": [],
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "total_budget": 0,
                    "start_date": None,
                    "end_date": None,
                    "status": "active"
                }
            
            projects[phase]["deliverables"].append(deliverable)
            projects[phase]["total_tasks"] += 1
            projects[phase]["total_budget"] += deliverable.get("budget_allocated", 0)
            
            if deliverable.get("status") == "Completed":
                projects[phase]["completed_tasks"] += 1
            
            # Update project dates
            due_date = deliverable.get("due_date")
            if due_date:
                if not projects[phase]["start_date"] or due_date < projects[phase]["start_date"]:
                    projects[phase]["start_date"] = due_date
                if not projects[phase]["end_date"] or due_date > projects[phase]["end_date"]:
                    projects[phase]["end_date"] = due_date
        
        # Calculate project completion rates
        for project in projects.values():
            project["completion_rate"] = round(
                (project["completed_tasks"] / project["total_tasks"] * 100), 1
            ) if project["total_tasks"] > 0 else 0
            
            # Determine project status
            if project["completion_rate"] == 100:
                project["status"] = "completed"
            elif project["completion_rate"] > 0:
                project["status"] = "in_progress"
            else:
                project["status"] = "not_started"
        
        projects_list = list(projects.values())
        
        return {
            "projects": projects_list,
            "summary": {
                "total_projects": len(projects_list),
                "active_projects": len([p for p in projects_list if p["status"] in ["active", "in_progress"]]),
                "completed_projects": len([p for p in projects_list if p["status"] == "completed"]),
                "total_budget": sum(p["total_budget"] for p in projects_list),
                "avg_completion_rate": round(
                    sum(p["completion_rate"] for p in projects_list) / len(projects_list), 1
                ) if projects_list else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agency projects: {str(e)}")

@router.get("/metrics")
async def get_agency_metrics():
    """Get agency performance metrics and KPIs"""
    
    try:
        # Use uploaded data if available, otherwise use defaults
        deliverables = UPLOADED_DELIVERABLES if UPLOADED_DELIVERABLES else DEFAULT_DELIVERABLES
        
        # Calculate various metrics
        total_deliverables = len(deliverables)
        completed = len([d for d in deliverables if d.get("status") == "Completed"])
        in_progress = len([d for d in deliverables if d.get("status") == "In Progress"])
        overdue = len([d for d in deliverables if is_overdue(d.get("due_date", ""))])
        
        # Budget metrics
        total_budget = sum(d.get("budget_allocated", 0) for d in deliverables)
        spent_budget = sum(d.get("budget_allocated", 0) for d in deliverables if d.get("status") == "Completed")
        
        # Time metrics
        total_hours = sum(d.get("estimated_hours", 0) for d in deliverables)
        completed_hours = sum(d.get("estimated_hours", 0) for d in deliverables if d.get("status") == "Completed")
        
        # Team productivity
        team_assignments = {}
        for deliverable in deliverables:
            owner = deliverable.get("owner", "Unassigned")
            if owner not in team_assignments:
                team_assignments[owner] = {"total": 0, "completed": 0}
            team_assignments[owner]["total"] += 1
            if deliverable.get("status") == "Completed":
                team_assignments[owner]["completed"] += 1
        
        # Calculate team productivity rates
        for team, stats in team_assignments.items():
            stats["productivity_rate"] = round(
                (stats["completed"] / stats["total"] * 100), 1
            ) if stats["total"] > 0 else 0
        
        metrics_data = {
            "overall_performance": {
                "completion_rate": round((completed / total_deliverables * 100), 1) if total_deliverables > 0 else 0,
                "on_time_delivery_rate": round(((total_deliverables - overdue) / total_deliverables * 100), 1) if total_deliverables > 0 else 0,
                "budget_utilization": round((spent_budget / total_budget * 100), 1) if total_budget > 0 else 0,
                "resource_utilization": round((completed_hours / total_hours * 100), 1) if total_hours > 0 else 0
            },
            "project_health": {
                "total_deliverables": total_deliverables,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": total_deliverables - completed - in_progress,
                "overdue": overdue,
                "at_risk": len([d for d in deliverables if days_until_due(d.get("due_date", "")) <= 3 and d.get("status") != "Completed"])
            },
            "financial_metrics": {
                "total_budget": total_budget,
                "spent_budget": spent_budget,
                "remaining_budget": total_budget - spent_budget,
                "budget_variance": 0,  # Would calculate from actual vs planned
                "cost_per_deliverable": round(total_budget / total_deliverables, 2) if total_deliverables > 0 else 0
            },
            "team_performance": team_assignments,
            "category_breakdown": get_category_metrics(deliverables),
            "timeline_analysis": {
                "avg_days_to_complete": 14,  # Mock data - would calculate from actual completion times
                "fastest_completion": 3,
                "slowest_completion": 28,
                "upcoming_deadlines_7d": len([d for d in deliverables if 0 <= days_until_due(d.get("due_date", "")) <= 7])
            },
            "quality_metrics": {
                "deliverables_requiring_revision": 2,  # Mock data
                "client_satisfaction_score": 4.7,
                "internal_quality_score": 4.5,
                "rework_rate": 8.5
            }
        }
        
        return metrics_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agency metrics: {str(e)}")

def is_overdue(due_date_str: str) -> bool:
    """Check if a deliverable is overdue"""
    if not due_date_str:
        return False
    
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return due_date.date() < datetime.now().date()
    except:
        return False

def days_until_due(due_date_str: str) -> int:
    """Calculate days until due date"""
    if not due_date_str:
        return 999  # Far future for items without due dates
    
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        delta = due_date.date() - datetime.now().date()
        return delta.days
    except:
        return 999

def get_upcoming_deadlines(deliverables: List[Dict], days_ahead: int = 7) -> List[Dict]:
    """Get deliverables with upcoming deadlines"""
    upcoming = []
    
    for deliverable in deliverables:
        days_until = days_until_due(deliverable.get("due_date", ""))
        if 0 <= days_until <= days_ahead and deliverable.get("status") != "Completed":
            upcoming.append({
                "task": deliverable.get("task", ""),
                "due_date": deliverable.get("due_date", ""),
                "days_until_due": days_until,
                "priority": deliverable.get("priority", "Medium"),
                "owner": deliverable.get("owner", "Unassigned"),
                "category": deliverable.get("category", "")
            })
    
    # Sort by days until due
    upcoming.sort(key=lambda x: x["days_until_due"])
    return upcoming[:10]  # Return top 10

def get_category_metrics(deliverables: List[Dict]) -> Dict[str, Any]:
    """Get metrics broken down by category"""
    categories = {}
    
    for deliverable in deliverables:
        category = deliverable.get("category", "Unknown")
        if category not in categories:
            categories[category] = {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "not_started": 0,
                "total_budget": 0,
                "total_hours": 0
            }
        
        categories[category]["total"] += 1
        categories[category]["total_budget"] += deliverable.get("budget_allocated", 0)
        categories[category]["total_hours"] += deliverable.get("estimated_hours", 0)
        
        status = deliverable.get("status", "Not Started")
        if status == "Completed":
            categories[category]["completed"] += 1
        elif status == "In Progress":
            categories[category]["in_progress"] += 1
        else:
            categories[category]["not_started"] += 1
    
    # Calculate completion rates
    for category_data in categories.values():
        category_data["completion_rate"] = round(
            (category_data["completed"] / category_data["total"] * 100), 1
        ) if category_data["total"] > 0 else 0
    
    return categories

def parse_number(value: str) -> float:
    """Parse string to number, handling various formats"""
    if not value:
        return 0.0
    
    try:
        # Remove common non-numeric characters
        cleaned = str(value).replace('$', '').replace(',', '').replace('%', '').strip()
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0
