from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter(tags=["calendar"])

VIEW_TO_DAYS = {
    "7": 7,
    "30": 30,
    "60": 60,
    "90": 90,          # quarterly
    "quarter": 90,
    "q": 90,
}

def _window(days: int) -> Dict[str, str]:
    start = datetime.utcnow().date()
    end = start + timedelta(days=days)
    return {"start": str(start), "end": str(end)}

def _stub_events(days: int):
    # lightweight mock events so UI isn’t empty
    today = datetime.utcnow()
    return [
        {"title": "Content Drop — Outerwear", "start": (today + timedelta(days=2)).isoformat(), "channel": "IG"},
        {"title": "Wholesale Line Review",     "start": (today + timedelta(days=7)).isoformat(), "channel": "Zoom"},
        {"title": "Influencer Capsule Brief",  "start": (today + timedelta(days=14)).isoformat(), "channel": "Email"},
    ][: 3 if days <= 7 else 3]

def _culture_recos(days: int):
    # deterministic “smart” recos tied to horizon
    recos = []
    if days >= 30:
        recos.append({"theme": "Back-to-school carryover", "why": "Late BTS content still converting", "cta": "Re-cut top 3 reels"})
    if days >= 60:
        recos.append({"theme": "Denim + graphics bundle", "why": "Bundle AOV lift in Q4", "cta": "2-for promo"})
    if days >= 90:
        recos.append({"theme": "Holiday drop cadence", "why": "Weekly micro-drops > single big drop", "cta": "Plan 3x micro-drops"})
    return recos

def _resolve_days(view: str | None, days: int | None) -> int:
    if view:
        key = view.strip().lower()
        if key not in VIEW_TO_DAYS:
            raise HTTPException(status_code=400, detail=f"Unknown view '{view}'. Use one of {list(VIEW_TO_DAYS.keys())}.")
        return VIEW_TO_DAYS[key]
    return max(1, min(365, days or 7))

@router.get("")
@router.get("/")
def root(view: str | None = Query(None), days: int | None = Query(None)):
    d = _resolve_days(view, days)
    return {"ok": True, "window": _window(d), "events": _stub_events(d), "culture_recommendations": _culture_recos(d)}

@router.get("/status")
def status():
    # If you later wire OAuth, flip connected=True and add provider data.
    return {"connected": False, "provider": "google", "note": "OAuth not configured", "checked_at": datetime.utcnow().isoformat()}

@router.get("/events")
def events(view: str | None = Query(None), days: int | None = Query(None)):
    d = _resolve_days(view, days)
    return {"window": _window(d), "events": _stub_events(d), "culture_recommendations": _culture_recos(d)}
