from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import json, statistics
import pandas as pd
from collections import defaultdict

router = APIRouter(tags=["executive"])

SHOPIFY_DATA_DIR     = Path("data/shopify")
COMPETITIVE_DATA_DIR = Path("data/competitive")
UPLOADS_DIR          = Path("data/uploads")
for p in (SHOPIFY_DATA_DIR, COMPETITIVE_DATA_DIR, UPLOADS_DIR):
    p.mkdir(parents=True, exist_ok=True)

def _load_shopify(days: int) -> Dict[str, Any]:
    files = list(SHOPIFY_DATA_DIR.glob("*.csv")) + list(SHOPIFY_DATA_DIR.glob("*.json"))
    if not files:
        return {"total_sales": 0, "total_orders": 0, "conversion_rate": 0, "aov": 0, "traffic": 0, "status": "no_data"}
    orders: List[dict] = []
    for f in files:
        try:
            if f.suffix == ".csv":
                orders += pd.read_csv(f).to_dict("records")
            else:
                data = json.loads(f.read_text())
                orders += data if isinstance(data, list) else [data]
        except Exception:
            continue
    if not orders:
        return {"total_sales": 0, "total_orders": 0, "conversion_rate": 0, "aov": 0, "traffic": 0, "status": "no_recent_data"}

    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    for o in orders:
        try:
            dt = pd.to_datetime(o.get("created_at", o.get("date", datetime.now())))
            if dt >= cutoff: recent.append(o)
        except Exception:
            recent.append(o)
    if not recent:
        return {"total_sales": 0, "total_orders": 0, "conversion_rate": 0, "aov": 0, "traffic": 0, "status": "no_recent_data"}

    total_sales = sum(float(o.get("total_price", o.get("total", o.get("amount", 0)))) for o in recent)
    total_orders = len(recent)
    aov = total_sales / max(total_orders, 1)
    return {"total_sales": round(total_sales, 2), "total_orders": total_orders, "conversion_rate": 0, "aov": round(aov, 2), "traffic": 0, "status": "active"}

def _load_competitive() -> Dict[str, Any]:
    files = (
        list(COMPETITIVE_DATA_DIR.glob("*.json")) + list(COMPETITIVE_DATA_DIR.glob("*.csv")) +
        list(UPLOADS_DIR.glob("*.json")) + list(UPLOADS_DIR.glob("*.csv"))
    )
    if not files:
        return {"brands_analyzed": 0, "crooks_rank": None, "market_share": {}, "performance_comparison": {}, "status": "no_data"}

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
    if not rows:
        return {"brands_analyzed": 0, "crooks_rank": None, "market_share": {}, "performance_comparison": {}, "status": "no_data"}

    grouped = defaultdict(list)
    for r in rows:
        b = str(r.get("brand", "")).lower().strip()
        if b: grouped[b].append(r)
    if not grouped:
        return {"brands_analyzed": 0, "crooks_rank": None, "market_share": {}, "performance_comparison": {}, "status": "no_data"}

    metrics = {}
    for brand, posts in grouped.items():
        totals = []
        for p in posts:
            totals.append(int(p.get("likes", 0)) + int(p.get("comments", 0)) + int(p.get("shares", 0)))
        metrics[brand] = {"total_posts": len(posts), "avg_engagement": statistics.mean(totals) if totals else 0, "total_engagement": sum(totals)}
    ranked = sorted(metrics.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)
    crooks_rank = next((i for i,(b,_) in enumerate(ranked, 1) if "crooks" in b or "castles" in b), None)
    return {"brands_analyzed": len(metrics), "crooks_rank": crooks_rank, "market_share": {}, "performance_comparison": {}, "status": "active"}

def _recs(shopify: Dict[str, Any], comp: Dict[str, Any]) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []
    if shopify.get("status") == "no_data":
        recs.append({"title": "Upload Shopify Sales Data", "description": "No Shopify data found.", "priority": "critical", "expected_impact": "Enables revenue intelligence", "time_to_implement": "1 day"})
    if comp.get("status") == "no_data":
        recs.append({"title": "Upload Competitive Intelligence Data", "description": "No competitive data found.", "priority": "high", "expected_impact": "Enables market positioning", "time_to_implement": "1 day"})
    if shopify.get("aov", 0) < 75:
        recs.append({"title": "Increase AOV", "description": f"Current AOV: ${shopify.get('aov', 0):.2f}. Target $75–120.", "priority": "medium", "expected_impact": "15–25% revenue lift", "time_to_implement": "2–4 weeks"})
    cr = comp.get("crooks_rank")
    if cr and cr > 3:
        recs.append({"title": "Improve Competitive Position", "description": f"Currently ranked #{cr}. Focus engagement.", "priority": "high", "expected_impact": "Share/visibility up", "time_to_implement": "4–8 weeks"})
    return recs

@router.get("/overview")
async def get_executive_overview(days: int = Query(30, ge=1, le=365)):
    try:
        shopify = _load_shopify(days)
        comp = _load_competitive()
        alerts = []
        if shopify.get("status") == "no_data":
            alerts.append({"level": "critical", "message": "No Shopify sales data", "action": "Upload sales reports"})
        if comp.get("status") == "no_data":
            alerts.append({"level": "warning", "message": "No competitive data", "action": "Upload competitor data"})
        return {
            "success": True,
            "timeframe_days": days,
            "shopify_metrics": shopify,
            "competitive_analysis": comp,
            "recommendations": _recs(shopify, comp),
            "alerts": alerts,
            "data_sources": {"shopify": shopify.get("status") == "active", "competitive": comp.get("status") == "active", "social": False},
            "analysis_confidence": {"revenue": 95 if shopify.get("status") == "active" else 0, "competitive": 85 if comp.get("brands_analyzed", 0) > 0 else 0, "trending": 0},
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive overview failed: {e}")

@router.get("/data-sources")
async def get_data_sources_status():
    try:
        return {
            "shopify": {"files": len(list(SHOPIFY_DATA_DIR.glob('*'))), "status": "active" if any(SHOPIFY_DATA_DIR.glob('*')) else "missing"},
            "competitive": {"files": len(list(COMPETITIVE_DATA_DIR.glob('*'))), "status": "active" if any(COMPETITIVE_DATA_DIR.glob('*')) else "missing"},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
