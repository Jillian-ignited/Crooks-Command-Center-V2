# backend/routers/executive.py
from __future__ import annotations
from fastapi import APIRouter, Query
from backend.services import intelligence_store as store

router = APIRouter()

@router.get("/", name="executive_root")
def executive_root():
    return {"ok": True, "message": "Executive API"}

@router.get("/overview", name="executive_overview")
def executive_overview(brand: str | None = Query(None, description="Brand filter (defaults to Crooks & Castles)")):
    data = store.executive_overview(brand=brand or store.DEFAULT_BRAND)
    return {"ok": True, **data}

@router.get("/kpis", name="executive_kpis")
def executive_kpis(brand: str | None = Query(None)):
    ov = store.executive_overview(brand=brand or store.DEFAULT_BRAND)
    rec = ov["recaps"]["7d"]  # default KPIs from 7d (frontend can also request 30d)
    return {
        "ok": True,
        "brand": brand or store.DEFAULT_BRAND,
        "kpis": [
            {"name": "Orders (7d)", "value": rec["orders"]},
            {"name": "Net Sales (7d)", "value": rec["net_sales"]},
            {"name": "AOV (7d)", "value": rec["aov"]},
            {"name": "Conversion % (7d)", "value": rec["conversion_pct"]},
            {"name": "Sessions (7d)", "value": rec["sessions"]},
        ],
        "refreshed_at": rec["refreshed_at"],
        "current": rec["current"],
    }
