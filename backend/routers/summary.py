# backend/routers/summary.py
from __future__ import annotations

import os
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.services import intelligence_store as store

DEFAULT_BRAND = os.getenv("DEFAULT_BRAND", "Crooks & Castles")

router = APIRouter()

@router.get("/overview", summary="Executive-style summary with real insights")
def overview(brand: str = Query(DEFAULT_BRAND)):
    data = store.executive_overview(brand=brand)

    r7  = data["recaps"]["7d"]
    r30 = data["recaps"]["30d"]
    s7  = data["recaps"]["social"]["7d"]
    s30 = data["recaps"]["social"]["30d"]

    # Primary KPIs (30d window as headline)
    kpis = {
        "revenue": float(r30.get("net_sales", 0.0)),
        "orders": float(r30.get("orders", 0.0)),
        "aov": float(r30.get("aov", 0.0)),
        "sessions": float(r30.get("sessions", 0.0)),
        "conversion_pct": float(r30.get("conversion_pct", 0.0)),
        "wow": {
            "revenue": r7["wow"]["net_sales"],     # 7d vs prior 7d
            "orders": r7["wow"]["orders"],
            "aov": r7["wow"]["aov"],
            "conversion_pct": r7["wow"]["conversion_pct"],
            "sessions": r7["wow"]["sessions"],
            "plays": s7["wow"]["plays"],
            "likes": s7["wow"]["likes"],
            "comments": s7["wow"]["comments"],
        },
    }

    notes = []
    # Insight rules (simple, clear)
    if r7["wow"]["net_sales"]["pct"] < -10:
        notes.append("Revenue down >10% WoW — review traffic mix and top-of-funnel efficiency.")
    if r7["wow"]["orders"]["pct"] < -10 and r7["wow"]["conversion_pct"]["pct"] >= 0:
        notes.append("Orders down but conversion steady — traffic volume likely dropped.")
    if r30["aov"] < 100:
        notes.append("AOV < $100 — consider bundles or tiered thresholds ('Spend $150 get a gift').")
    if r30["conversion_pct"] < 1.2:
        notes.append("Conversion < 1.2% — tighten targeting and add PDP/cart urgency cues.")
    if (s30["plays"] or 0) > 0 and (s30["comments"] + s30["saves"]) / max(1, s30["plays"]) < 0.02:
        notes.append("Social engagement per view < 2% — iterate first-3s hooks & creator-led edits.")
    if not notes:
        notes.append("KPIs healthy — scale top creatives and refresh offer angles.")

    hashtags = s7.get("top_hashtags", {"combined": [], "tiktok": [], "instagram": []})

    resp = {
        "ok": True,
        "brand": brand,
        "kpis": kpis,
        "windows": {
            "7d": {"commerce": r7, "social": s7},
            "30d": {"commerce": r30, "social": s30},
        },
        "hashtags": hashtags,
        "notes": notes,
        "snapshot": data.get("snapshot", {}),
    }
    return JSONResponse(resp)
