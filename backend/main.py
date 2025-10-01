# backend/main.py from __future__ import annotations

import importlib
import os
from pathlib import Path
from types import ModuleType
from typing import Optional, List, Tuple

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from backend.database import init_db

APP_VERSION = "frontend-static-v5"

STATIC_ROOT = Path("backend/static/site").resolve()
NEXT_DIR = STATIC_ROOT / "_next"
NEXT_STATIC = NEXT_DIR / "static"

STORAGE_ROOT = Path("backend/storage").resolve()
UPLOAD_ROOT = Path("backend/uploads").resolve()

for p in [STATIC_ROOT, STORAGE_ROOT, UPLOAD_ROOT]:
    try:
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        elif p.exists() and p.is_file():
            p.rename(p.with_suffix(p.suffix + ".bak"))
            p.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[main] WARN: could not ensure dir {p}: {e}")

app = FastAPI(title="Crooks Command Center", version=APP_VERSION)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("[main] Database initialized successfully")
    except Exception as e:
        print(f"[main] ERROR: Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True, "version": APP_VERSION}

@app.get("/api/__whoami", response_class=PlainTextResponse)
def whoami():
    return f"main.py={APP_VERSION}"

@app.get("/api/__init_db")
def force_init_db():
    """Manually initialize database tables"""
    try:
        init_db()
        return {"success": True, "message": "Database tables created"}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

def _try_import(paths: List[str]) -> Tuple[Optional[ModuleType], Optional[str], Optional[Exception]]:
    last_err: Optional[Exception] = None
    for p in paths:
        try:
            return importlib.import_module(p), p, None
        except Exception as e:
            last_err = e
    return None, None, last_err

def _mount(name: str, prefix: str, candidates: List[str]):
    mod, used, err = _try_import(candidates)
    if not mod:
        print(f"[main] SKIP '{name}' — not found. Tried {candidates}. Last error: {err}")
        return
    if not hasattr(mod, "router"):
        print(f"[main] SKIP '{name}' — module '{used}' has no 'router'.")
        return
    app.include_router(mod.router, prefix=f"/api{prefix}", tags=[name])
    print(f"[main] Mounted '{name}' (from {used}) at /api{prefix}")

_mount("agency", "/agency", ["backend.routers.agency"])
_mount("calendar", "/calendar", ["backend.routers.calendar"])
_mount("content", "/content", ["backend.routers.content_creation", "backend.routers.content"])
_mount("executive", "/executive", ["backend.routers.executive"])
_mount("ingest", "/ingest", ["backend.routers.ingest", "backend.routers.ingest_ENHANCED_MULTI_FORMAT"])
_mount("intelligence", "/intelligence", ["backend.routers.intelligence"])
_mount("media", "/media", ["backend.routers.media"])
_mount("shopify", "/shopify", ["backend.routers.shopify"])
_mount("summary", "/summary", ["backend.routers.summary"])
_mount("upload_sidecar", "/sidecar", ["backend.routers.upload_sidecar", "backend.routers.sidecar"])
_mount("competitive", "/competitive", ["backend.routers.competitive"])

@app.get("/api/__routes")
def list_routes():
    rows = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            rows.append({"path": r.path, "methods": sorted(list(r.methods)), "name": r.name})
    return rows

@app.get("/api/__static_ping", response_class=PlainTextResponse)
def static_ping():
    parts = [
        f"ROOT exists={STATIC_ROOT.is_dir()} path={STATIC_ROOT}",
        f"_next exists={NEXT_DIR.is_dir()} path={NEXT_DIR}",
        f"_next/static exists={NEXT_STATIC.is_dir()} path={NEXT_STATIC}",
    ]
    return "\n".join(parts)

@app.get("/api/__static_debug")
def static_debug():
    info = {
        "root": {"path": str(STATIC_ROOT), "exists": STATIC_ROOT.is_dir()},
        "next": {"path": str(NEXT_DIR), "exists": NEXT_DIR.is_dir()},
        "static": {"path": str(NEXT_STATIC), "exists": NEXT_STATIC.is_dir()},
        "samples": {"index_html": False, "css": [], "chunks": [], "has_health": False},
    }
    files = []
    if info["root"]["exists"]:
        for r, _, fs in os.walk(STATIC_ROOT):
            for f in fs:
                files.append(os.path.relpath(os.path.join(r, f), STATIC_ROOT))
    info["samples"]["index_html"] = any(p == "index.html" for p in files)
    info["samples"]["has_health"] = any(p == "health.txt" for p in files)
    info["samples"]["css"] = [p for p in files if p.startswith("_next/static/css/")][:5]
    info["samples"]["chunks"] = [p for p in files if p.startswith("_next/static/chunks/")][:5]
    return JSONResponse(info)

if NEXT_DIR.is_dir():
    app.mount("/_next", StaticFiles(directory=str(NEXT_DIR), html=False), name="next")
    print(f"[main] Mounted '/_next' from {NEXT_DIR}")
else:
    print(f"[main] WARN: Missing Next dir: {NEXT_DIR}")

if NEXT_STATIC.is_dir():
    app.mount("/_next/static", StaticFiles(directory=str(NEXT_STATIC), html=False), name="next-static")
    print(f"[main] Mounted '/_next/static' from {NEXT_STATIC}")
else:
    print(f"[main] WARN: Missing Next static dir: {NEXT_STATIC}")

app.mount("/", StaticFiles(directory=str(STATIC_ROOT), html=True), name="site")

@app.middleware("http")
async def api_not_found_to_json(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception:
        raise

@app.exception_handler(404)
async def api_404_handler(request: Request, exc):
    path = request.url.path
    if path.startswith("/api/"):
        return JSONResponse({"detail": "Not Found", "path": path}, status_code=404)
    return await app.router.default_app(scope=request.scope, receive=request.receive, send=request._send)

@app.on_event("startup")
async def _log_routes():
    print("=== ROUTES MOUNTED ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            print(f"{','.join(sorted(r.methods)):15} {r.path}")
    print("=== DEBUG PROBES READY===")