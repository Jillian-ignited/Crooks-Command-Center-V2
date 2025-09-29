# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
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

# --- Health (@ /api/health and /health) ---
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True}

# --- Dynamic, tolerant router loader (so missing modules don't crash the app) ---
def try_import(path_candidates: List[str]) -> Tuple[Optional[ModuleType], Optional[str], Optional[Exception]]:
    last_error: Optional[Exception] = None
    for modpath in path_candidates:
        try:
            mod = importlib.import_module(modpath)
            return mod, modpath, None
        except Exception as e:
            last_error = e
    return None, None, last_error

def mount_router(name: str, prefix: str, candidates: List[str]):
    mod, used, err = try_import(candidates)
    if mod is None:
        print(f"[main] SKIP mounting '{name}' at /api{prefix} — module not found. Tried: {candidates}. Last error: {err}")
        return
    if not hasattr(mod, "router"):
        print(f"[main] SKIP mounting '{name}' at /api{prefix} — module '{used}' has no 'router'.")
        return
    app.include_router(mod.router, prefix=f"/api{prefix}", tags=[name])
    print(f"[main] Mounted '{name}' (from {used}) at /api{prefix}")

# === Mount routers (aliases included) ===
mount_router("agency",           "/agency",           ["backend.routers.agency"])
mount_router("calendar",         "/calendar",         ["backend.routers.calendar"])
mount_router("content",          "/content",          ["backend.routers.content_creation", "backend.routers.content"])
mount_router("executive",        "/executive",        ["backend.routers.executive"])
mount_router("ingest",           "/ingest",           ["backend.routers.ingest", "backend.routers.ingest_ENHANCED_MULTI_FORMAT"])
mount_router("intelligence",     "/intelligence",     ["backend.routers.intelligence"])
mount_router("media",            "/media",            ["backend.routers.media"])
mount_router("shopify",          "/shopify",          ["backend.routers.shopify"])
mount_router("summary",          "/summary",          ["backend.routers.summary"])
mount_router("upload_sidecar",   "/sidecar",          ["backend.routers.upload_sidecar", "backend.routers.sidecar"])

# --- Serve the built Next.js static site (exported to backend/static/site) ---
# NOTE: Run the frontend build+export+copy step in your Render build command.
# Mount *after* API so /api/* keeps priority. html=True enables SPA routing.
app.mount("/", StaticFiles(directory="backend/static/site", html=True), name="site")

# --- Startup route log ---
@app.on_event("startup")
async def _log_routes():
    print("=== ROUTES MOUNTED ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(r.methods))
            print(f"{methods:15} {r.path}")
    print("======================")
