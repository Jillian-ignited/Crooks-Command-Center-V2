from datetime import date
from db import SessionLocal, Agency, AgencyProject
from sqlalchemy import select

def load_agency():
    with SessionLocal() as s:
        ags = s.scalars(select(Agency)).all()
        out = []
        for ag in ags:
            projs = s.scalars(select(AgencyProject).where(AgencyProject.agency_id==ag.id).order_by(AgencyProject.due_date.asc())).all()
            out.append({
                "name": ag.name,
                "phase": ag.phase,
                "current_deliverables": ag.current_deliverables,
                "monthly_budget": ag.monthly_budget,
                "budget_used": ag.budget_used,
                "on_time_delivery": ag.on_time_delivery,
                "quality_score": ag.quality_score,
                "next_phase_requirements": [],   # Optional: compute from phase
                "deliverables_breakdown": {
                    "completed": [p.name for p in projs if p.status=="completed"],
                    "in_progress": [p.name for p in projs if p.status=="in_progress"],
                    "pending": [p.name for p in projs if p.status=="pending"],
                },
                "current_projects": [
                    {"name": p.name, "status": p.status, "due_date": (p.due_date.isoformat() if p.due_date else None)}
                    for p in projs
                ],
                "performance_metrics": {
                    "response_time": ag.response_time,
                    "revision_rounds": ag.revision_rounds,
                    "client_satisfaction": ag.client_satisfaction
                }
            })
        return {"agencies": out}
