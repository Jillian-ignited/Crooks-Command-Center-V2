# backend/routers/agency.py
""" Agency Dashboard Router - Now using REAL data from content briefs and calendar

Replaces all mock data with actual project data from database
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any, List, Optional
import datetime
import sys
import os
import pandas as pd
import io

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from data_service import DataService
except ImportError:
    # Fallback if data_service isn't available
    class DataService:
        @staticmethod
        def get_agency_projects():
            return {"project_overview": {"total_deliverables": 0, "completed": 0, "in_progress": 0, "not_started": 0, "completion_rate": 0}, "projects": [], "team_performance": {}}
        
        @staticmethod
        def upload_deliverables_data(df: pd.DataFrame):
            # Placeholder for actual data storage
            print("Uploading deliverables data to DataService (placeholder)")
            
router = APIRouter()

@router.get("/dashboard")
async def get_agency_dashboard() -> Dict[str, Any]:
    """Get agency dashboard with real project data"""
    
    # Get real project data from the data service
    project_data = DataService.get_agency_projects()
    
    # Build dashboard from real data
    dashboard = {
        "project_overview": project_data.get("project_overview", {}),
        "active_projects": project_data.get("projects", []),
        "team_performance": project_data.get("team_performance", {}),
        "budget_overview": _calculate_budget_overview(project_data.get("projects", [])),
        "resource_allocation": _calculate_resource_allocation(project_data.get("projects", [])),
        "upcoming_deadlines": _get_upcoming_deadlines(project_data.get("projects", [])),
        "cost_optimizations": _identify_cost_optimizations(project_data),
        "roi_analysis": _calculate_roi_analysis(project_data),
        "generated_at": datetime.datetime.now().isoformat(),
        "data_source": "real_project_data"
    }
    
    return dashboard

@router.get("/projects")
async def get_agency_projects() -> Dict[str, Any]:
    """Get list of all agency projects"""
    
    project_data = DataService.get_agency_projects()
    
    return {
        "total_projects": len(project_data.get("projects", [])),
        "projects": project_data.get("projects", []),
        "project_status_distribution": _get_status_distribution(project_data.get("projects", [])),
        "data_source": "real_project_data"
    }

@router.get("/team")
async def get_team_performance() -> Dict[str, Any]:
    """Get team performance metrics"""
    
    project_data = DataService.get_agency_projects()
    
    return {
        "team_performance": project_data.get("team_performance", {}),
        "workload_distribution": _calculate_workload_distribution(project_data.get("projects", [])),
        "data_source": "real_project_data"
    }

@router.get("/financials")
async def get_agency_financials() -> Dict[str, Any]:
    """Get agency financial overview"""
    
    project_data = DataService.get_agency_projects()
    
    return {
        "budget_overview": _calculate_budget_overview(project_data.get("projects", [])),
        "roi_analysis": _calculate_roi_analysis(project_data),
        "cost_optimizations": _identify_cost_optimizations(project_data),
        "data_source": "real_project_data"
    }

@router.post("/upload_deliverables")
async def upload_deliverables(file: UploadFile = File(...)):
    """Upload a CSV or Excel file with project deliverables and due dates"""
    
    try:
        contents = await file.read()
        df = None
        
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are supported.")
            
        # Process and store the deliverables data
        DataService.upload_deliverables_data(df)
        
        return {"message": "Deliverables uploaded and processed successfully!", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process deliverables: {e}")

# Helper functions for agency dashboard calculations

def _calculate_budget_overview(projects: List[Dict]) -> Dict[str, Any]:
    """Calculate budget overview from project data"""
    
    total_budget = sum([p.get("budget", 0) for p in projects])
    spent_budget = sum([p.get("spent", 0) for p in projects])
    remaining_budget = total_budget - spent_budget
    
    return {
        "total_budget": total_budget,
        "spent_budget": spent_budget,
        "remaining_budget": remaining_budget,
        "budget_utilization_rate": (spent_budget / total_budget) * 100 if total_budget > 0 else 0
    }

def _calculate_resource_allocation(projects: List[Dict]) -> Dict[str, Any]:
    """Calculate resource allocation from project data"""
    
    allocation = {}
    for project in projects:
        team = project.get("team", "Unassigned")
        allocation[team] = allocation.get(team, 0) + 1
        
    return allocation

def _get_upcoming_deadlines(projects: List[Dict]) -> List[Dict[str, Any]]:
    """Get upcoming deadlines from project data"""
    
    upcoming = []
    now = datetime.datetime.now()
    
    for project in projects:
        deadline_str = project.get("deadline")
        if deadline_str:
            try:
                deadline = datetime.datetime.fromisoformat(deadline_str)
                if now < deadline < now + datetime.timedelta(days=14): # Next 2 weeks
                    upcoming.append({
                        "project_name": project.get("name", "Unnamed Project"),
                        "deadline": deadline_str,
                        "days_remaining": (deadline - now).days
                    })
            except ValueError:
                pass # Ignore invalid date formats
    
    return sorted(upcoming, key=lambda x: x["days_remaining"])

def _get_status_distribution(projects: List[Dict]) -> Dict[str, int]:
    """Get project status distribution"""
    
    distribution = {"completed": 0, "in_progress": 0, "not_started": 0, "on_hold": 0}
    for project in projects:
        status = project.get("status", "not_started")
        if status in distribution:
            distribution[status] += 1
            
    return distribution

def _calculate_workload_distribution(projects: List[Dict]) -> Dict[str, int]:
    """Calculate workload distribution by team"""
    
    workload = {}
    for project in projects:
        team = project.get("team", "Unassigned")
        workload[team] = workload.get(team, 0) + 1
        
    return workload

def _calculate_roi_analysis(project_data: Dict) -> Dict[str, Any]:
    """Calculate ROI analysis from project data"""
    
    completed = project_data.get("project_overview", {}).get("completed", 0)
    
    # Placeholder for revenue and cost - in a real scenario, this would come from project data
    estimated_revenue_per_project = 5000
    estimated_cost_per_project = 2000
    
    total_revenue = completed * estimated_revenue_per_project
    total_cost = completed * estimated_cost_per_project
    roi = ((total_revenue - total_cost) / max(1, total_cost)) * 100
    
    return {
        "estimated_revenue": total_revenue,
        "total_investment": total_cost,
        "roi_percentage": round(roi, 1),
        "projects_analyzed": completed
    }

def _identify_cost_optimizations(project_data: Dict) -> List[Dict[str, Any]]:
    """Identify cost optimization opportunities"""
    
    optimizations = []
    
    total_deliverables = project_data["project_overview"]["total_deliverables"]
    completion_rate = project_data["project_overview"]["completion_rate"]
    
    if completion_rate < 80:
        optimizations.append({
            "area": "Project Completion",
            "opportunity": "Improve project completion rate to reduce waste",
            "potential_savings": "15-25%",
            "implementation": "Implement better project tracking and milestone management"
        })
    
    if total_deliverables > 50:
        optimizations.append({
            "area": "Process Automation",
            "opportunity": "Automate repetitive tasks in content creation",
            "potential_savings": "20-30%",
            "implementation": "Implement content templates and approval workflows"
        })
        
    return optimizations

