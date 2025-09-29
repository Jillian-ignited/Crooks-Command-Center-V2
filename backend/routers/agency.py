from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def agency_root():
    """Agency root endpoint"""
    return {
        "success": True,
        "message": "Agency API operational",
        "endpoints": ["/dashboard", "/projects", "/deliverables", "/metrics"]
    }

@router.get("/dashboard")
async def agency_dashboard():
    """Get agency dashboard data"""
    return {
        "success": True,
        "metrics": {
            "active_projects": 8,
            "completion_rate": 92,
            "overdue_deliverables": 3,
            "client_satisfaction": 4.8
        },
        "current_projects": [
            {
                "name": "Fall Collection Campaign",
                "client": "Crooks & Castles",
                "status": "In Progress",
                "progress": 65,
                "start_date": "2023-08-15",
                "end_date": "2023-10-15"
            },
            {
                "name": "Website Redesign",
                "client": "Crooks & Castles",
                "status": "In Progress",
                "progress": 40,
                "start_date": "2023-09-01",
                "end_date": "2023-11-15"
            },
            {
                "name": "Holiday Campaign Planning",
                "client": "Crooks & Castles",
                "status": "Planning",
                "progress": 15,
                "start_date": "2023-09-15",
                "end_date": "2023-12-01"
            },
            {
                "name": "Influencer Partnership Program",
                "client": "Crooks & Castles",
                "status": "In Progress",
                "progress": 50,
                "start_date": "2023-07-01",
                "end_date": "2023-10-31"
            }
        ],
        "upcoming_deadlines": [
            {
                "title": "Campaign Creative Approval",
                "project_name": "Fall Collection Campaign",
                "due_date": "2023-09-30"
            },
            {
                "title": "Website Wireframes",
                "project_name": "Website Redesign",
                "due_date": "2023-10-05"
            },
            {
                "title": "Influencer Shortlist",
                "project_name": "Influencer Partnership Program",
                "due_date": "2023-10-10"
            }
        ]
    }

@router.get("/projects")
async def agency_projects():
    """Get agency projects data"""
    return {
        "success": True,
        "projects": [
            {
                "id": "proj1",
                "name": "Fall Collection Campaign",
                "client": "Crooks & Castles",
                "status": "In Progress",
                "progress": 65,
                "start_date": "2023-08-15",
                "end_date": "2023-10-15",
                "team": ["Creative Director", "Photographer", "Copywriter", "Social Media Manager"],
                "deliverables": ["Campaign Strategy", "Photoshoot", "Social Media Assets", "Website Banner", "Email Campaign"]
            },
            {
                "id": "proj2",
                "name": "Website Redesign",
                "client": "Crooks & Castles",
                "status": "In Progress",
                "progress": 40,
                "start_date": "2023-09-01",
                "end_date": "2023-11-15",
                "team": ["UX Designer", "UI Designer", "Web Developer", "Content Strategist"],
                "deliverables": ["Wireframes", "UI Design", "Frontend Development", "CMS Integration", "Content Migration"]
            },
            {
                "id": "proj3",
                "name": "Holiday Campaign Planning",
                "client": "Crooks & Castles",
                "status": "Planning",
                "progress": 15,
                "start_date": "2023-09-15",
                "end_date": "2023-12-01",
                "team": ["Creative Director", "Strategist", "Copywriter", "Designer"],
                "deliverables": ["Campaign Concept", "Content Calendar", "Creative Brief", "Budget Allocation"]
            },
            {
                "id": "proj4",
                "name": "Influencer Partnership Program",
                "client": "Crooks & Castles",
                "status": "In Progress",
                "progress": 50,
                "start_date": "2023-07-01",
                "end_date": "2023-10-31",
                "team": ["Influencer Manager", "Social Media Manager", "Content Strategist", "Analytics Specialist"],
                "deliverables": ["Influencer Selection", "Partnership Terms", "Content Guidelines", "Performance Tracking"]
            }
        ],
        "total": 4,
        "active": 3,
        "planning": 1,
        "completed": 0
    }

@router.get("/deliverables")
async def agency_deliverables():
    """Get agency deliverables data"""
    return {
        "success": True,
        "deliverables": [
            {
                "id": "del1",
                "title": "Campaign Creative Approval",
                "project": "Fall Collection Campaign",
                "status": "Pending Approval",
                "due_date": "2023-09-30",
                "assigned_to": "Creative Director"
            },
            {
                "id": "del2",
                "title": "Website Wireframes",
                "project": "Website Redesign",
                "status": "In Progress",
                "due_date": "2023-10-05",
                "assigned_to": "UX Designer"
            },
            {
                "id": "del3",
                "title": "Influencer Shortlist",
                "project": "Influencer Partnership Program",
                "status": "In Progress",
                "due_date": "2023-10-10",
                "assigned_to": "Influencer Manager"
            },
            {
                "id": "del4",
                "title": "Holiday Campaign Concept",
                "project": "Holiday Campaign Planning",
                "status": "Not Started",
                "due_date": "2023-10-15",
                "assigned_to": "Creative Director"
            },
            {
                "id": "del5",
                "title": "Social Media Assets",
                "project": "Fall Collection Campaign",
                "status": "Completed",
                "due_date": "2023-09-15",
                "assigned_to": "Designer"
            }
        ],
        "total": 5,
        "completed": 1,
        "in_progress": 2,
        "pending_approval": 1,
        "not_started": 1
    }

@router.get("/metrics")
async def agency_metrics():
    """Get agency performance metrics"""
    return {
        "success": True,
        "metrics": {
            "project_metrics": {
                "on_time_completion": "92%",
                "average_project_duration": "45 days",
                "budget_adherence": "97%",
                "scope_changes": "2.3 per project"
            },
            "team_metrics": {
                "resource_utilization": "85%",
                "billable_hours": 1245,
                "non_billable_hours": 220,
                "overtime_hours": 45
            },
            "client_metrics": {
                "satisfaction_score": 4.8,
                "nps": 72,
                "retention_rate": "95%",
                "feedback_score": 4.6
            },
            "financial_metrics": {
                "revenue": "$245,000",
                "profit_margin": "32%",
                "average_project_value": "$61,250",
                "forecasted_q4_revenue": "$320,000"
            }
        }
    }
