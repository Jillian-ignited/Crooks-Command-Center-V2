from fastapi import APIRouter, Query
from ..models.schemas import CalendarResponse
from ..services.calendar import list_events

router = APIRouter()

@router.get("", response_model=CalendarResponse)
async def get_calendar(range_days: int = Query(7, ge=1, le=120)):
    events = list_events(range_days)
    return {"range_days": range_days, "events": events}
