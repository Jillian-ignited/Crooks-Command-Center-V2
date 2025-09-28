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

@router.get("/upcoming")
@router.get("/upcoming/")
async def upcoming_events():
    """Get upcoming calendar events"""
    try:
        today = datetime.now()
        return {
            "success": True,
            "upcoming_events": [
                {
                    "id": "evt_001",
                    "title": "Content Review Meeting",
                    "date": (today + timedelta(days=1)).isoformat(),
                    "type": "meeting",
                    "priority": "high",
                    "attendees": ["Creative Team", "Brand Manager"]
                },
                {
                    "id": "evt_002", 
                    "title": "BFCM Campaign Launch",
                    "date": (today + timedelta(days=3)).isoformat(),
                    "type": "campaign",
                    "priority": "critical",
                    "attendees": ["Marketing Team", "Agency Partners"]
                },
                {
                    "id": "evt_003",
                    "title": "Heritage Month Content Deadline",
                    "date": (today + timedelta(days=5)).isoformat(),
                    "type": "deadline",
                    "priority": "medium",
                    "attendees": ["Content Team"]
                },
                {
                    "id": "evt_004",
                    "title": "Quarterly Business Review",
                    "date": (today + timedelta(days=7)).isoformat(),
                    "type": "review",
                    "priority": "high",
                    "attendees": ["Executive Team", "Agency Partners"]
                }
            ],
            "calendar_summary": {
                "total_events": 4,
                "high_priority": 2,
                "meetings_this_week": 2,
                "deadlines_this_week": 1
            },
            "next_7_days": str(today.date()) + " to " + str((today + timedelta(days=7)).date()),
            "last_updated": today.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
