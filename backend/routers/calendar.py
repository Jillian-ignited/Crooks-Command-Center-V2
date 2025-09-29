# backend/routers/calendar.py
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import Dict

router = APIRouter()

VIEW_TO_DAYS = {"7":7, "30":30, "60":60, "quarter":90, "90":90}

def _window(days: int) -> Dict[str, str]:
    start = datetime.utcnow().date()
    end = start + timedelta(days=days)
    return {"start": str(start), "end": str(end)}

def _events(days: int):
    today = datetime.utcnow()
    base = [
        {"title": "Content Drop — Outerwear", "start": (today + timedelta(days=2)).isoformat(), "channel": "IG"},
        {"title": "Wholesale Line Review",     "start": (today + timedelta(days=7)).isoformat(), "channel": "Zoom"},
        {"title": "Influencer Capsule Brief",  "start": (today + timedelta(days=14)).isoformat(), "channel": "Email"},
    ]
    return base

def _recos(days: int):
    recos = []
    if days >= 30: recos.append({"theme":"Back-to-school carryover","why":"Late BTS content still converting","cta":"Re-cut top 3 reels"})
    if days >= 60: recos.append({"theme":"Denim + graphics bundle","why":"Bundle AOV lift in Q4","cta":"2-for promo"})
    if days >= 90: recos.append({"theme":"Holiday drop cadence","why":"Weekly micro-drops > single big drop","cta":"Plan 3x micro-drops"})
    return recos

def _resolve(view: str | None, days: int | None) -> int:
    if view:
        key = view.strip().lower()
        if key not in VIEW_TO_DAYS:
            raise HTTPException(status_code=400, detail=f"Unknown view '{view}'. Use one of {list(VIEW_TO_DAYS.keys())}.")
        return VIEW_TO_DAYS[key]
    return max(1, min(365, days or 7))

@router.get("/status")
def status():
    return {"connected": False, "provider": "google", "note": "OAuth not configured", "checked_at": datetime.utcnow().isoformat()}

@router.get("/events")
def events(view: str | None = Query(None), days: int | None = Query(None)):
    d = _resolve(view, days)
    return {"window": _window(d), "events": _events(d), "culture_recommendations": _recos(d)}
