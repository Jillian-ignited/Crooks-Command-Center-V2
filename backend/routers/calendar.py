# backend/routers/calendar.py
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List, Optional

router = APIRouter()

VIEW_TO_DAYS = {"7":7, "30":30, "60":60, "quarter":90, "90":90}

def _window(days: int) -> Dict[str, str]:
    start = datetime.utcnow().date()
    end = start + timedelta(days=days)
    return {"start": str(start), "end": str(end)}

def _resolve(view: Optional[str], days: Optional[int]) -> int:
    if view:
        key = view.strip().lower()
        if key not in VIEW_TO_DAYS:
            raise HTTPException(status_code=400, detail=f"Unknown view '{view}'. Use one of {list(VIEW_TO_DAYS.keys())}.")
        return VIEW_TO_DAYS[key]
    return max(1, min(365, days or 7))

def _events(days: int) -> List[Dict]:
    today = datetime.utcnow()
    return [
        {"title": "Content Drop — Outerwear", "start": (today + timedelta(days=2)).isoformat(), "channel": "IG"},
        {"title": "Wholesale Line Review",     "start": (today + timedelta(days=7)).isoformat(), "channel": "Zoom"},
        {"title": "Influencer Capsule Brief",  "start": (today + timedelta(days=14)).isoformat(), "channel": "Email"},
    ]

def _streetwear_recos(days: int, region: str = "US") -> List[Dict[str, any]]:
    """Static-but-relevant suggestions keyed to seasonality & cadence."""
    recos: List[Dict[str, any]] = []
    now = datetime.utcnow()
    m = now.month

    # Always-on hooks
    recos.append({
        "theme": "Trend stitch + duet",
        "why": "Borrow distribution from creators and fan edits",
        "cta": "Post 2x weekly stitch/duet on TikTok",
        "channels": ["TikTok","Reels"],
        "sample_hooks": ["POV: real {brand} armor", "Street test: wear or pass?"],
    })
    recos.append({
        "theme": "Fit check + detail B-roll",
        "why": "Close-up fabric/print = saves and purchase intent",
        "cta": "Shoot macro details for current drop",
        "channels": ["Reels","Shorts"],
        "sample_hooks": ["Don’t buy streetwear without checking THIS", "What quality looks like:"],
    })

    # Seasonal pushes
    if days >= 30:
        recos.append({
            "theme": "Back-to-school carryover",
            "why": "Late BTS still converts into early fall",
            "cta": "Re-cut top 3 BTS reels w/ updated CTA",
            "channels": ["Reels","TikTok"],
        })
    if days >= 60:
        recos.append({
            "theme": "Denim x Graphic capsule",
            "why": "Bundle AOV lift into Q4",
            "cta": "2-for bundle offer + creator try-on",
            "channels": ["Reels","Email","Site HP"],
        })
    if days >= 90:
        recos.append({
            "theme": "Holiday micro-drops",
            "why": "Weekly drops beat single tentpole",
            "cta": "Plan 3x micro-drops w/ countdowns",
            "channels": ["IG","TikTok","Email"],
        })

    # Region nods (US streetwear retail cadence)
    if region.upper() == "US":
        recos.append({
            "theme": "Mall door heat-mapping",
            "why": "Prioritize doors with youth traffic spikes (PacSun/Zoomies adjacencies)",
            "cta": "Allocate window displays to high-traffic weekends",
            "channels": ["Wholesale","Retail Ops"],
        })

    # Month-based cultural notes (lightweight)
    if m in (9,10):  # Fall drop season
        recos.append({
            "theme": "Outerwear teaser loop",
            "why": "Outerwear peaks in Oct/Nov",
            "cta": "Tease lining/hidden graphics; collect notify-me emails",
            "channels": ["Reels","Email"],
        })
    if m in (11,12):  # Holiday
        recos.append({
            "theme": "Giftable under-$50",
            "why": "Accessories move fast at gift price points",
            "cta": "Create gift grid; bundle tee + accessory",
            "channels": ["Site","Email","Reels"],
        })

    return recos

@router.get("/status")
def status():
    return {
        "connected": False,             # flip when OAuth is wired
        "provider": "google",
        "note": "OAuth not configured",
        "checked_at": datetime.utcnow().isoformat()
    }

@router.get("/events")
def events(view: Optional[str] = Query(None), days: Optional[int] = Query(None),
           region: Optional[str] = Query("US"), include_culture: bool = Query(True)):
    d = _resolve(view, days)
    payload = {
        "window": _window(d),
        "events": _events(d),
        "culture_recommendations": _streetwear_recos(d, region) if include_culture else [],
        "region": region,
        "generated_at": datetime.utcnow().isoformat(),
    }
    return payload
