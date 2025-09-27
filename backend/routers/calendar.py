from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

router = APIRouter(tags=["calendar"])

@router.get("/status")
async def status():
    return {"connected": False, "provider": "google", "note": "Wire OAuth to enable", "checked_at": datetime.now().isoformat()}

@router.get("/events")
async def events():
    try:
        today = datetime.now().date()
        return {
            "window": {"start": str(today), "end": str(today + timedelta(days=7))},
            "events": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
