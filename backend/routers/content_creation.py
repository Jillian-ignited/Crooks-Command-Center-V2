# backend/routers/content_creation.py
from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List, Optional
from datetime import datetime

router = APIRouter()

def _as_list(x):
    if x is None: return []
    if isinstance(x, list): return x
    return [x]

@router.post("/brief")
def brief(payload: Dict[str, Any]):
    """
    Expected JSON:
    {
      "brand": "Crooks & Castles",
      "objective": "Drive sell-through on F/W drop",
      "audience": ["Gen Z", "streetwear"],
      "tone": ["armor", "grit"],
      "channels": ["IG Reels","TikTok","Email"],
      "campaign_window_days": 30,
      "constraints": ["keep logo primary", "UGC first"]
    }
    """
    brand = (payload.get("brand") or "").strip() or "Brand"
    objective = (payload.get("objective") or "Grow revenue").strip()
    audience = _as_list(payload.get("audience")) or ["streetwear consumer"]
    tone = _as_list(payload.get("tone")) or ["credible", "direct"]
    channels = _as_list(payload.get("channels")) or ["IG Reels", "TikTok"]
    window = int(payload.get("campaign_window_days") or 30)
    constraints = _as_list(payload.get("constraints")) or []

    pillars = [
        {"name": "Cred & Culture", "why": "Signals authenticity", "proofs": ["heritage drops", "artist co-signs"]},
        {"name": "Product Power", "why": "Moves units", "proofs": ["fabric callouts", "fit video", "close-up B-roll"]},
        {"name": "Community", "why": "Creates pull", "proofs": ["UGC stitch", "duet with fans", "store staff picks"]},
    ]
    kpis = {"revenue": "↑", "ROAS": "≥ 3.0", "ER": "≥ 6%", "AOV": "≥ $95"}
    deliverables = [
        {"type": "Reels", "count": 8, "notes": "hook-first; 6–9s"},
        {"type": "TikTok", "count": 8, "notes": "trend + stitch"},
        {"type": "Stills", "count": 12, "notes": "detail + fit"},
        {"type": "Email", "count": 4, "notes": "editorial + CTA"},
    ]

    return {
        "ok": True,
        "generated_at": datetime.utcnow().isoformat(),
        "brand": brand,
        "objective": objective,
        "audience": audience,
        "tone": tone,
        "channels": channels,
        "window_days": window,
        "constraints": constraints,
        "pillars": pillars,
        "kpis": kpis,
        "deliverables": deliverables,
        "run_of_show": [
            {"week": 1, "focus": "cred + announce"},
            {"week": 2, "focus": "product proof"},
            {"week": 3, "focus": "ugc + social proof"},
            {"week": 4, "focus": "offer + urgency"},
        ],
    }

@router.post("/ideas")
def ideas(payload: Dict[str, Any]):
    """
    Expected JSON:
    {
      "brand": "Crooks & Castles",
      "theme": "Armor + Cred",
      "count": 5,
      "channel": "IG Reels"
    }
    """
    brand = (payload.get("brand") or "Brand").strip()
    theme = (payload.get("theme") or "Cred").strip()
    count = max(1, min(20, int(payload.get("count") or 5)))
    channel = (payload.get("channel") or "IG Reels").strip()

    templates = [
        {
            "hook": "If you know, you know — {brand} {theme} drop.",
            "concept": "Quick cut: logo hit → detail close-up → fit.",
            "asset_types": ["Reel", "Still", "Story"],
            "caption_template": "Armor up. {brand} {theme}. Link in bio.",
            "kpi_target": {"ER": "≥ 6%"},
        },
        {
            "hook": "POV: you just upgraded to real {theme}.",
            "concept": "POV mirror fit + sound beat drop.",
            "asset_types": ["TikTok", "Reel"],
            "caption_template": "POV unlocked. #{brand} #{theme}",
            "kpi_target": {"View-Through": "≥ 35%"},
        },
        {
            "hook": "Don’t buy streetwear without checking THIS.",
            "concept": "Education: fabric, stitch, print method.",
            "asset_types": ["Reel", "Carousel"],
            "caption_template": "{brand} makes it right. {theme} standards.",
            "kpi_target": {"Saves": "↑"},
        },
        {
            "hook": "Street test: would you wear this?",
            "concept": "Man-on-street reactions to piece.",
            "asset_types": ["TikTok", "Reel"],
            "caption_template": "Say less. {brand} {theme}.",
            "kpi_target": {"Comments": "↑"},
        },
    ]

    out: List[Dict[str, Any]] = []
    for i in range(count):
        t = templates[i % len(templates)]
        out.append({
            "idx": i + 1,
            "channel": channel,
            "hook": t["hook"].format(brand=brand, theme=theme),
            "concept": t["concept"],
            "asset_types": t["asset_types"],
            "caption": t["caption_template"].format(brand=brand, theme=theme),
            "kpi_target": t["kpi_target"],
        })

    return {"ok": True, "brand": brand, "theme": theme, "count": count, "ideas": out}
