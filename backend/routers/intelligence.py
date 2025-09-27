from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import json, statistics, re
import pandas as pd
from collections import defaultdict

router = APIRouter(tags=["intelligence"])

COMPETITIVE_DATA_DIR = Path("data/competitive")
UPLOADS_DIR          = Path("data/uploads")
for p in (COMPETITIVE_DATA_DIR, UPLOADS_DIR):
    p.mkdir(parents=True, exist_ok=True)

# Use 11 brands (drop one to avoid UI mismatch)
ALL_BRANDS: List[str] = [
    "crooks & castles", "stussy", "supreme", "bape", "off-white",
    "fear of god", "essentials", "rhude", "palm angels", "amiri",
    "gallery dept"   # removed "chrome hearts" to keep 11
]

def _load_rows() -> List[dict]:
    files = list(COMPETITIVE_DATA_DIR.glob("*.csv")) + list(COMPETITIVE_DATA_DIR.glob("*.json")) + \
            list(UPLOADS_DIR.glob("*.csv")) + list(UPLOADS_DIR.glob("*.json"))
    rows: List[dict] = []
    for f in files:
        try:
            if f.suffix == ".csv":
                rows += pd.read_csv(f).to_dict("records")
            else:
                data = json.loads(f.read_text())
                rows += data if isinstance(data, list) else [data]
        except Exception:
            continue
    return rows

@router.get("/summary")
async def summary(brands: str | None = Query(None, description="comma list or 'all'"), days: int = Query(30, ge=1, le=365)):
    try:
        use_brands = ALL_BRANDS if (brands is None or brands.lower() == "all") else [b.strip().lower() for b in brands.split(",") if b.strip()]
        rows = _load_rows()
        cutoff = datetime.now() - timedelta(days=days)
        grouped = defaultdict(list)
        for r in rows:
            b = str(r.get("brand", "")).lower().strip()
            if b and (b in use_brands):
                try:
                    dt = pd.to_datetime(r.get("date") or r.get("created_at") or datetime.now())
                    if dt < cutoff: 
                        continue
                except Exception:
                    pass
                grouped[b].append(r)

        metrics: Dict[str, Dict[str, Any]] = {}
        for b in use_brands:
            posts = grouped.get(b, [])
            totals, likes_list = [], []
            for p in posts:
                likes  = int(p.get("likes", 0)); comments = int(p.get("comments", 0)); shares = int(p.get("shares", 0))
                totals.append(likes + comments + shares)
                likes_list.append(likes)
            metrics[b] = {
                "posts": len(posts),
                "avg_engagement": round(statistics.mean(totals), 2) if totals else 0,
                "total_engagement": sum(totals),
                "avg_likes": round(statistics.mean(likes_list), 2) if likes_list else 0,
            }
        return {"brands_used": use_brands, "metrics": metrics, "window_days": days, "last_updated": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"intelligence.summary failed: {e}")
