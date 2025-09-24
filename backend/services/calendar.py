from typing import List, Dict, Any
from datetime import date, timedelta
from ..models.schemas import CalendarEvent

# Minimal curated cultural/streetwear calendar seed.
CULTURE_SEED = [
    {"date": "2025-10-31", "title": "Halloween (Costume Content Spike)", "category": "culture"},
    {"date": "2025-11-28", "title": "Black Friday (Streetwear Drops)", "category": "culture"},
    {"date": "2025-11-29", "title": "Small Business Saturday", "category": "culture"},
    {"date": "2025-12-02", "title": "Cyber Monday", "category": "culture"},
    {"date": "2026-02-07", "title": "New York Fashion Week (Feb)", "category": "culture"},
    {"date": "2026-02-16", "title": "NBA All-Star Weekend", "category": "culture"},
    {"date": "2026-03-17", "title": "St. Patrick's Day (Green Capsule)", "category": "culture"},
]

def list_events(range_days: int = 7) -> List[CalendarEvent]:
    today = date.today()
    end = today + timedelta(days=range_days)
    events = []
    for e in CULTURE_SEED:
        try:
            d = date.fromisoformat(e["date"])
        except:
            continue
        if today <= d <= end:
            events.append(CalendarEvent(**e))
    return events
