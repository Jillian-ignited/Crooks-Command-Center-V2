from datetime import date, timedelta
from db import SessionLocal, CalendarEvent
from sqlalchemy import select

def _range(days):
    start = date.today()
    end = start + timedelta(days=days)
    return start, end

def load_calendar():
    out = {'7_day_view': [], '30_day_view': [], '60_day_view': [], '90_day_view': []}
    with SessionLocal() as s:
        for key, horizon in [('7_day_view',7), ('30_day_view',30), ('60_day_view',60), ('90_day_view',90)]:
            start, end = _range(horizon)
            rows = s.scalars(select(CalendarEvent).where(CalendarEvent.date>=start, CalendarEvent.date<=end).order_by(CalendarEvent.date.asc())).all()
            out[key] = [
                {
                    "date": r.date.isoformat(), "title": r.title, "description": r.description,
                    "budget_allocation": r.budget_allocation,
                    "deliverables": r.deliverables or [],
                    "assets_mapped": r.assets_mapped or [],
                    "cultural_context": r.cultural_context,
                    "target_kpis": r.target_kpis or {},
                    "status": r.status
                } for r in rows
            ]
    return out
