# backend/main.py
import os
import logging
from pathlib import Path
from typing import List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles

# --- Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("backend.main")

# --- App ---
app = FastAPI(title="Crooks Command Center V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers ----------

def mount_frontend(app: FastAPI) -> None:
    """
    Serve the prerendered Next.js site.
    Prefers backend/static/site (what your build copies to),
    falls back to frontend/out if present.
    """
    candidates: List[Tuple[str, Path]] = [
        ("backend/static/site", Path(__file__).resolve().parent / "static" / "site"),
        ("frontend/out", Path(__file__).resolve().parents[1] / "frontend" / "out"),
    ]
    for label, p in candidates:
        if p.exists() and p.is_dir():
            app.mount("/", StaticFiles(directory=str(p), html=True), name="site")
            log.info("✅ Static files mounted from: %s", label)
            break
    else:
        log.warning("⚠️ No static site found. Expected one of: %s", ", ".join(x[0] for x in candidates))

def list_routes(app: FastAPI) -> List[dict]:
    """
    Return a concise catalog of all registered API routes.
    """
    out = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            out.append({
                "path": route.path,
                "methods": sorted(list(route.methods or [])),
                "name": route.name,
            })
    # Only return API endpoints to keep it clean
    return [r for r in out if r["path"].startswith("/api") or r["path"] == "/"]

def safe_include(module_path: str, prefix: str = "/api") -> bool:
    """
    Try to import a router module and include its `router`.
    Returns True if included, False on failure.
    """
    try:
        mod = __import__(module_path, fromlist=["router"])
        router = getattr(mod, "router", None)
        if router is None:
            log.error("❌ %s has no 'router' attribute", module_path)
            return False
        app.include_router(router, prefix=prefix)
        log.info("✅ %s router loaded", module_path)
        return True
    except Exception:
        log.exception("❌ Failed to load router: %s", module_path)
        return False

# ---------- Core API: health + route index ----------

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/__routes")
def routes_index():
    """Returns the live API routes (so you can see what’s actually registered)."""
    return JSONResponse(list_routes(app))

# Root handler to avoid HEAD/GET 405s and serve index.html if mounted
@app.get("/")
def root_index():
    # If static is mounted, StaticFiles will serve index.html automatically.
    # Returning a tiny OK fallback keeps things friendly if no static is present.
    return PlainTextResponse("Crooks Command Center API is running. See /api/health", status_code=200)

# ---------- Optional: simple 404 hint for /api ----------

@app.get("/api")
def api_root_hint():
    return {"hint": "This is the API root. See /api/__routes for endpoints."}

# ---------- Include your routers ----------

# Use fully-qualified paths so imports work in Render
router_modules = [
    "backend.routers.executive",
    "backend.routers.competitive",
    "backend.routers.competitive_analysis",  # if missing, we log and keep going
    "backend.routers.shopify",
    "backend.routers.agency",
    "backend.routers.calendar",
    "backend.routers.content_creation",
    "backend.routers.intelligence",
    "backend.routers.media",
    "backend.routers.summary",
    "backend.routers.ingest",  # use the actual filename present in your repo
    # "backend.routers.ingest_ENHANCED_MULTI_FORMAT",  # add back if this file exists
    # "backend.routers.upload_sidecar",                 # add back if this file exists
]

_loaded = 0
_failed = 0
for mod in router_modules:
    if safe_include(mod):
        _loaded += 1
    else:
        _failed += 1

# ---------- Frontend static mount ----------
mount_frontend(app)

log.info("🚀 Crooks Command Center API starting up...")
log.info("📊 Loaded %d routers successfully", _loaded)
if _failed:
    log.warning("⚠️ %d routers failed to load - fallback endpoints active", _failed)
log.info("✅ Startup complete!")
