# backend/routers/agency.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse

from backend.services import agency_store as store

router = APIRouter()

@router.get("/", name="agency_root")
def agency_root():
    store.init_schema()
    return {"ok": True, "message": "Agency API ready"}

@router.get("/deliverables", name="agency_deliverables")
def agency_deliverables(
    phase: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None)
):
    rows = store.list_deliverables(phase=phase, status=status, q=q)
    return {"items": rows, "phases": store.phases(), "stats": store.stats()}

@router.get("/deliverables/{item_id}", name="agency_deliverable_get")
def agency_deliverable_get(item_id: int):
    row = store.get_one(item_id)
    if not row:
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    return row

@router.put("/deliverables/{item_id}", name="agency_deliverable_update")
async def agency_deliverable_update(item_id: int, payload: Dict[str, Any]):
    row = store.update_one(item_id, payload or {})
    if not row:
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    return row

@router.get("/phases", name="agency_phases")
def agency_phases():
    return {"phases": store.phases()}

@router.get("/stats", name="agency_stats")
def agency_stats():
    return store.stats()

@router.post("/import", name="agency_import_csv")
async def agency_import_csv(file: UploadFile = File(...), truncate: bool = True):
    """
    Upload a CSV exported from your 'Agency Deliverables' plan.
    Headers should include: Phase, Task, Owner, Channel, Assets, Dependencies, Notes, Due Date, Priority
    """
    tmp = Path("/tmp/agency_upload.csv")
    data = await file.read()
    tmp.write_bytes(data)
    count = store.import_csv(tmp, truncate=truncate)
    return {"ok": True, "imported": count}

@router.get("/dashboard", name="agency_dashboard")
def agency_dashboard():
    # Minimal health/dashboard stub – extend later with KPIs
    return {"ok": True, "stats": store.stats()}

@router.get("/projects", name="agency_projects")
def agency_projects():
    # Optional group-by phase for a quick project view
    groups = {}
    for row in store.list_deliverables():
        groups.setdefault(row["phase"] or "Unassigned", []).append(row)
    return {"projects": [{"phase": k, "count": len(v)} for k, v in groups.items()]}

@router.get("/deliverables/assets-needed", name="agency_assets_needed")
def agency_assets_needed():
    # Items that mention assets but aren't 'Done' or 'Approved'
    rows = [r for r in store.list_deliverables() if (r["assets"] or "").strip() and r["status"] not in ("Approved","Done")]
    return {"items": rows}
