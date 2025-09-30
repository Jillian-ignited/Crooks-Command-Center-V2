# backend/routers/executive.py
from __future__ import annotations
from fastapi import APIRouter
from backend.services import intelligence_store as store

router = APIRouter()

@router.get("/", name="executive_root")
def executive_root():
    return {"ok": True, "message": "Executive API ready"}

@router.get("/overview", name="executive_overview")
def executive_overview():
    data = store.executive_overview()
    # add a quick summary for cards
    total_brands = len({b["name"] for b in data["brands"]})
    total_comp   = len({c["name"] for c in data["competitors"]})
    total_bench  = len(data["benchmarks"])
    return {
        "ok": True,
        "cards": {
            "brands": total_brands,
            "competitors": total_comp,
            "benchmarks": total_bench
        },
        **data
    }

@router.get("/kpis", name="executive_kpis")
def executive_kpis():
    # stub KPIs; you can compute from benchmarks if desired
    return {"ok": True, "kpis":[
        {"name":"Benchmark Entries","value": len(store.list_benchmarks())},
        {"name":"Brands Tracked","value": len(store.list_brands())},
        {"name":"Competitors Tracked","value": len(store.list_competitors())}
    ]}

@router.get("/reports", name="executive_reports")
def executive_reports():
    # placeholder; could compile a PDF or HTML later
    return {"ok": True, "reports": []}
