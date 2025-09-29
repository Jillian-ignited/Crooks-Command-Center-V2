from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter(tags=["calendar"])

@router.get("")
@router.get("/")
def root():
    return {"ok": True, "router": "calendar"}

@router.get("/status")
def status():
    return {"connected": False, "provider": "google", "note": "OAuth not configured", "checked_at": datetime.utcnow().isoformat()}

@router.get("/events")
def events():
    today = datetime.utcnow().date()
    return {"window": {"start": str(today), "end": str(today + timedelta(days=7))}, "events": []}
