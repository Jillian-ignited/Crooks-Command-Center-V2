# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
import importlib
from types import ModuleType
from typing import Optional, List, Tuple

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# --- CORS (relaxed while stabilizing) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health at both paths for convenience ---
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True}

# --- Helper: attempt to import a router module from several candidate names ---
def try_import(path_candidates: List[str]) -> Tuple[Optional[ModuleType], Optional[str], Optional[Exception]]:
    for modpath in path_candidates:
        try:
            mod = importlib.import_module(modpath)
            return mod, modpath, None
        except Exception as e:
            last_error = e
            continue
    return None, None, last_error  # type: ignore

# --- Helper to include a router if found ---
def mount_router(name: str, prefix: str, candidates: List[str]):
    mod, used, err = try_import(candidates)
    if mod is None:
        print(f"[main] SKIP mounting '{name}' at /api{prefix} — module not found. Tried: {candidates}. Last error: {err}")
        return
    if not hasattr(mod, "router"):
        print(f"[main] SKIP mounting '{name}' at /api{prefix} — module '{used}' has no 'router' attribute.")
        return
    app.include_router(mod.router, prefix=f"/api{prefix}", tags=[name])
    print(f"[main] Mounted '{name}' (from {used}) at /api{prefix}")

# === Mount routers (with aliases so missing files don't crash the app) ===
mount_router("agency",           "/agency",           ["backend.routers.agency"])
mount_router("calendar",         "/calendar",         ["backend.routers.calendar"])
mount_router("content",          "/content",          ["backend.routers.content_creation", "backend.routers.content"])
mount_router("executive",        "/executive",        ["backend.routers.executive"])
mount_router("ingest",           "/ingest",           ["backend.routers.ingest", "backend.routers.ingest_ENHANCED_MULTI_FORMAT"])
mount_router("intelligence",     "/intelligence",     ["backend.routers.intelligence"])
mount_router("media",            "/media",            ["backend.routers.media"])
mount_router("shopify",          "/shopify",          ["backend.routers.shopify"])
mount_router("summary",          "/summary",          ["backend.routers.summary"])
# Give sidecar its own prefix; do NOT overlap intelligence
mount_router("upload_sidecar",   "/sidecar",          ["backend.routers.upload_sidecar", "backend.routers.sidecar"])

# --- Startup: log all active routes so you can sanity-check quickly ---
@app.on_event("startup")
async def _log_routes():
    print("=== ROUTES MOUNTED ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(r.methods))
            print(f"{methods:15} {r.path}")
    print("======================")
