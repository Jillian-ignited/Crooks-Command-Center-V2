# backend/routers/calendar.py
from __future__ import annotations
import datetime as dt
from fastapi import APIRouter, Query

router = APIRouter()

SEASONAL = [
    {"title":"Halloween Campaign", "month":10, "day":31, "tags":["seasonal","retail"]},
    {"title":"Black Friday", "month":11, "day":1, "tags":["promo","ecom"]},    # using Nov 1 as a month anchor to suggest prep
    {"title":"Cyber Monday", "month":11, "day":25, "tags":["promo","ecom"]},   # approximate
    {"title":"Holiday Gifting", "month":12, "day":1, "tags":["seasonal"]},
    {"title":"New Year Kickoff", "month":1, "day":2, "tags":["brand"]},
    {"title":"Back to School", "month":8, "day":1, "tags":["seasonal","edu"]},
]

@router.get("/status", name="status")
def status():
    # Not connected to Google by default. You DON'T need external calendar for basic planning.
    return {"ok": True, "google_connected": False, "message":"Using local planning calendar."}

@router.get("/events", name="events")
def events(range: int = Query(30, description="Days ahead: 7,30,60,90")):
    today = dt.date.today()
    end = today + dt.timedelta(days=range)
    items = []

    # Seasonal suggestions within window
    for s in SEASONAL:
        # guess the next occurrence this year or next
        year = today.year
        occ = dt.date(year, s["month"], min(s["day"], 28 if s["month"]==2 else 30 if s["month"] in (4,6,9,11) else 31))
        if occ < today:
            occ = dt.date(year+1, s["month"], min(s["day"], 28 if s["month"]==2 else 30 if s["month"] in (4,6,9,11) else 31))
        if today <= occ <= end:
            items.append({
                "title": s["title"],
                "start": occ.isoformat(),
                "end": occ.isoformat(),
                "kind": "opportunity",
                "tags": s["tags"],
                "suggested_actions": [
                    "Creative brief",
                    "Asset plan",
                    "Channel schedule"
                ]
            })

    # Simple placeholders for planned tasks (you can pipe from deliverables)
    items.append({
        "title":"Weekly Social Pulse",
        "start": (today + dt.timedelta(days=3)).isoformat(),
        "end":   (today + dt.timedelta(days=3)).isoformat(),
        "kind":"task",
        "tags":["social"]
    })

    return {"ok": True, "range_days": range, "items": items}
