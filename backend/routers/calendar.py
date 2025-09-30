# backend/routers/calendar.py
from __future__ import annotations

import os
import datetime as dt
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Query

router = APIRouter()

# ----------------------------
# Seasonal / cultural moments
# ----------------------------
SEASONAL = [
    {"title": "Halloween Campaign",   "month": 10, "day": 31, "tags": ["seasonal", "retail"]},
    {"title": "Black Friday",         "month": 11, "day": 29, "tags": ["promo", "ecom"]},   # 2025 specific date
    {"title": "Cyber Monday",         "month": 12, "day": 1,  "tags": ["promo", "ecom"]},   # 2025 specific date
    {"title": "Holiday Gifting",      "month": 12, "day": 1,  "tags": ["seasonal"]},
    {"title": "New Year Kickoff",     "month": 1,  "day": 2,  "tags": ["brand"]},
    {"title": "Valentine’s Day",      "month": 2,  "day": 14, "tags": ["seasonal"]},
    {"title": "Back to School",       "month": 8,  "day": 1,  "tags": ["seasonal", "edu"]},
]

# ----------------------------
# Google status (flag only)
# ----------------------------
@router.get("/status", name="status")
def status():
    # You do NOT need Google connected to use the planning calendar.
    # This flag is just informative for your UI.
    return {"ok": True, "google_connected": False, "message": "Using local planning calendar."}

# ----------------------------
# Helpers
# ----------------------------
def _parse_date(s: str) -> Optional[dt.date]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime(s.strip(), fmt).date()
        except Exception:
            continue
    return None

def _in_window(d: Optional[dt.date], start: dt.date, end: dt.date) -> bool:
    return d is not None and start <= d <= end

def _next_occurrence(month: int, day: int, today: dt.date) -> dt.date:
    # normalize day to valid date for the month
    last_day = 28
    if month in (1,3,5,7,8,10,12):
        last_day = 31
    elif month in (4,6,9,11):
        last_day = 30
    # Feb safe cap
    if month == 2 and day > 29: day = 28
    day = min(day, last_day)

    occ = dt.date(today.year, month, day)
    return occ if occ >= today else dt.date(today.year + 1, month, day)

async def _fetch_agency_deliverables() -> List[Dict[str, Any]]:
    """
    Pulls deliverables from your own API: /api/agency/deliverables
    Tries to infer common field names for title/project/due/status.
    """
    base = os.environ.get("INTERNAL_BASE_URL")
    if not base:
        # Build a safe same-process base URL for Render / uvicorn
        port = os.environ.get("PORT", "8000")
        base = f"http://127.0.0.1:{port}"

    url = f"{base}/api/agency/deliverables"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return []
            data = r.json()
    except Exception:
        return []

    # Expect either a list, or a dict with an "items" array
    items = data if isinstance(data, list) else data.get("items", [])
    out = []
    for it in items:
        # Try multiple keys to be resilient
        title = it.get("title") or it.get("name") or it.get("deliverable") or "Deliverable"
        project = it.get("project") or it.get("brand") or it.get("client") or ""
        status = it.get("status") or it.get("state") or ""
        due = (
            it.get("due_date")
            or it.get("due")
            or it.get("deadline")
            or it.get("date")
            or it.get("target_date")
        )
        due_date = _parse_date(due) if isinstance(due, str) else None
        # Allow ISO dicts too e.g. {"$date": "..."}
        if not due_date and isinstance(due, dict):
            due_date = _parse_date(due.get("$date", ""))

        out.append({
            "title": title,
            "project": project,
            "status": status,
            "due_date": due_date.isoformat() if due_date else None,
            "raw": it,
        })
    return out

def _seasonal_events(today: dt.date, end: dt.date) -> List[Dict[str, Any]]:
    evs: List[Dict[str, Any]] = []
    for s in SEASONAL:
        occ = _next_occurrence(s["month"], s["day"], today)
        if _in_window(occ, today, end):
            evs.append({
                "title": s["title"],
                "start": occ.isoformat(),
                "end": occ.isoformat(),
                "kind": "opportunity",
                "tags": s["tags"],
                "suggested_actions": [
                    "Creative brief",
                    "Asset plan",
                    "Channel schedule",
                ],
            })
    return evs

# ----------------------------
# Main events endpoint
# ----------------------------
@router.get("/events", name="events")
async def events(range: int = Query(30, description="Days ahead window: 7, 30, 60, 90")):
    today = dt.date.today()
    end = today + dt.timedelta(days=range)
    items: List[Dict[str, Any]] = []

    # 1) Agency deliverables -> calendar events
    dels = await _fetch_agency_deliverables()
    for d in dels:
        due_date = _parse_date(d.get("due_date")) if isinstance(d.get("due_date"), str) else _parse_date(d.get("due_date", ""))
        if not due_date:
            # some sources provided iso already
            try:
                due_date = dt.date.fromisoformat(d.get("due_date")) if d.get("due_date") else None
            except Exception:
                due_date = None

        if _in_window(due_date, today, end):
            title_bits = [d.get("title", "Deliverable")]
            if d.get("project"):
                title_bits.append(f"({d['project']})")
            title = " ".join(title_bits)

            items.append({
                "title": title,
                "start": due_date.isoformat(),
                "end": due_date.isoformat(),
                "kind": "deliverable",
                "status": d.get("status", ""),
                "tags": ["deliverable"],
                "source": "agency",
            })

    # 2) Seasonal opportunities
    items.extend(_seasonal_events(today, end))

    # 3) Example recurring internal task inside window (optional)
    in3 = today + dt.timedelta(days=3)
    if _in_window(in3, today, end):
        items.append({
            "title": "Weekly Social Pulse",
            "start": in3.isoformat(),
            "end": in3.isoformat(),
            "kind": "task",
            "tags": ["social"],
            "source": "internal"
        })

    # Sort by start date
    items.sort(key=lambda x: x["start"])
    return {"ok": True, "range_days": range, "items": items}
