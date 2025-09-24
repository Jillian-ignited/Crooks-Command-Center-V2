from datetime import date
from fastapi import APIRouter
from ..models.schemas import AgencyResponse, Deliverable

router = APIRouter()

@router.get("", response_model=AgencyResponse)
async def get_agency():
    # Starter structure - editable from frontend later
    week = date.today().isoformat()
    deliverables = [
        Deliverable(title="IG/TikTok: Archive Teaser", status="planned", owner="Social", due=week),
        Deliverable(title="Creator Collab Outreach (3)", status="in-progress", owner="Growth", due=week),
        Deliverable(title="Drop Page QA", status="planned", owner="Ecom", due=week),
    ]
    return {"week_of": week, "deliverables": deliverables}
