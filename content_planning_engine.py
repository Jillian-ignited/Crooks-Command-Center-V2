"""
Content Planning for Crooks & Castles
- Campaigns are modeled as groups of CalendarEvent rows.
- We namespace titles as: "[{campaign}] {milestone}"
- No new tables. Fully compatible with existing db.py models.
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_
from db import SessionLocal, CalendarEvent

def _title(campaign: str, milestone: str) -> str:
    return f"[{campaign}] {milestone}".strip()

def _is_campaign_title(title: str, campaign: str) -> bool:
    tag = f"[{campaign}] "
    return title.startswith(tag)

def plan_campaign(
    campaign: str,
    window_start: str,
    window_end: str,
    deliverables: List[str],
    assets_mapped: Optional[List[str]] = None,
    budget_allocation: float = 0.0,
    cultural_context: str = "",
    target_kpis: Optional[Dict[str, Any]] = None,
    status: str = "planned",
) -> Dict[str, Any]:
    """
    Create a campaign window and auto-schedule milestones evenly across the window.
    """
    d0 = date.fromisoformat(window_start)
    d1 = date.fromisoformat(window_end)
    days = max((d1 - d0).days, 0)
    n = max(len(deliverables), 1)
    step = max(days // max(n - 1, 1), 0)

    created_ids = []
    with SessionLocal() as s:
        for i, d in enumerate(deliverables):
            when = d0 + timedelta(days=i * step)
            ev = CalendarEvent(
                date=when,
                title=_title(campaign, d),
                description=f"{campaign} · {d}",
                budget_allocation=float(budget_allocation) / n if n else 0.0,
                deliverables=[d],
                assets_mapped=assets_mapped or [],
                cultural_context=cultural_context,
                target_kpis=target_kpis or {},
                status=status,
            )
            s.add(ev); s.commit(); s.refresh(ev)
            created_ids.append(ev.id)
    return {"ok": True, "campaign": campaign, "created_event_ids": created_ids}

def list_campaigns(prefix: str = "") -> List[Dict[str, Any]]:
    """
    Return campaign aggregates by campaign tag.
    """
    with SessionLocal() as s:
        rows = s.scalars(select(CalendarEvent).order_by(CalendarEvent.date.asc())).all()

    # collect by campaign tag
    by_campaign: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        title = r.title or ""
        if not title.startswith("[") or "]" not in title:
            continue
        tag = title[1:title.index("]")]
        if prefix and not tag.lower().startswith(prefix.lower()):
            continue

        bucket = by_campaign.setdefault(tag, {
            "campaign": tag,
            "events": [],
            "window_start": None,
            "window_end": None,
            "budget_total": 0.0,
        })
        di = {
            "id": r.id,
            "date": r.date.isoformat() if r.date else None,
            "milestone": title[title.index("]") + 1:].strip(),
            "status": r.status,
            "deliverables": r.deliverables or [],
            "assets_mapped": r.assets_mapped or [],
            "kpis": r.target_kpis or {},
            "budget_allocation": r.budget_allocation or 0.0,
            "cultural_context": r.cultural_context or "",
            "description": r.description or "",
        }
        bucket["events"].append(di)
        if r.date:
            d = r.date
            bucket["window_start"] = min(bucket["window_start"] or d, d)
            bucket["window_end"]   = max(bucket["window_end"] or d, d)
        bucket["budget_total"] += (r.budget_allocation or 0.0)

    # sort events
    for v in by_campaign.values():
        v["events"].sort(key=lambda x: (x["date"] or ""))
        if v["window_start"]: v["window_start"] = v["window_start"].isoformat()
        if v["window_end"]:   v["window_end"]   = v["window_end"].isoformat()
    return sorted(by_campaign.values(), key=lambda x: x["campaign"].lower())

def campaign_overview(campaign: str) -> Dict[str, Any]:
    """
    Single-campaign rollup with status counts and asset gaps.
    """
    data = [c for c in list_campaigns(prefix=campaign) if c["campaign"].lower() == campaign.lower()]
    if not data:
        return {"campaign": campaign, "events": [], "status_counts": {}, "asset_gaps": []}

    c = data[0]
    status_counts = {}
    all_assets = set()
    gaps = []
    for e in c["events"]:
        status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1
        if e["assets_mapped"]:
            all_assets.update(e["assets_mapped"])
        else:
            gaps.append({"id": e["id"], "milestone": e["milestone"], "date": e["date"]})

    return {
        "campaign": c["campaign"],
        "window_start": c["window_start"],
        "window_end": c["window_end"],
        "budget_total": round(c["budget_total"], 2),
        "events": c["events"],
        "status_counts": status_counts,
        "asset_count": len(all_assets),
        "asset_gaps": gaps,
    }

def update_milestone_status(event_id: int, status: str) -> Dict[str, Any]:
    with SessionLocal() as s:
        ev = s.get(CalendarEvent, event_id)
        if not ev:
            return {"ok": False, "error": "not_found"}
        ev.status = status
        s.commit()
        return {"ok": True}

def retitle_milestone(event_id: int, new_milestone: str) -> Dict[str, Any]:
    with SessionLocal() as s:
        ev = s.get(CalendarEvent, event_id)
        if not ev:
            return {"ok": False, "error": "not_found"}
        # preserve campaign tag if present
        old = ev.title or ""
        if old.startswith("[") and "]" in old:
            tag = old[:old.index("]")+1]
            ev.title = f"{tag} {new_milestone}".strip()
        else:
            ev.title = new_milestone
        s.commit()
        return {"ok": True}

def delete_campaign(campaign: str) -> Dict[str, Any]:
    with SessionLocal() as s:
        rows = s.scalars(select(CalendarEvent)).all()
        to_delete = [r for r in rows if _is_campaign_title(r.title or "", campaign)]
        for r in to_delete:
            s.delete(r)
        s.commit()
        return {"ok": True, "deleted": len(to_delete)}
