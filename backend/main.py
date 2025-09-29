# backend/main.py
from pathlib import Path
import importlib
from types import ModuleType
from typing import Optional, List, Tuple

from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

APP_VERSION = "frontend-static-v5"

# --- Paths ---
BASE_DIR     = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
STATIC_ROOT  = PROJECT_ROOT / "backend" / "static" / "site"      # Next export copied here
NEXT_DIR     = STATIC_ROOT / "_next"
MEDIA_ROOT   = PROJECT_ROOT / "backend" / "storage" / "media"    # <— moved here (avoid collisions)
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Crooks Command Center", version=APP_VERSION)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Health / identity ---
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True, "version": APP_VERSION}

@app.get("/api/__whoami", response_class=PlainTextResponse)
def whoami():
    return f"main.py={APP_VERSION}"

# --- Tolerant router loader ---
def _try_import(paths: List[str]) -> Tuple[Optional[ModuleType], Optional[str], Optional[Exception]]:
    last = None
    for p in paths:
        try:
            return importlib.import_module(p), p, None
        except Exception as e:
            last = e
    return None, None, last

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

# --- Routers ---
_mount("agency",           "/agency",           ["backend.routers.agency"])
_mount("calendar",         "/calendar",         ["backend.routers.calendar"])
_mount("content",          "/content",          ["backend.routers.content_creation","backend.routers.content"])
_mount("executive",        "/executive",        ["backend.routers.executive"])
_mount("ingest",           "/ingest",           ["backend.routers.ingest","backend.routers.ingest_ENHANCED_MULTI_FORMAT"])
_mount("intelligence",     "/intelligence",     ["backend.routers.intelligence"])
_mount("media",            "/media",            ["backend.routers.media"])
_mount("shopify",          "/shopify",          ["backend.routers.shopify"])
_mount("summary",          "/summary",          ["backend.routers.summary"])
_mount("upload_sidecar",   "/sidecar",          ["backend.routers.upload_sidecar","backend.routers.sidecar"])

# --- Debug probes ---
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
        f"media exists={MEDIA_ROOT.is_dir()} path={MEDIA_ROOT}",
    ]
    return "\n".join(parts)

@app.get("/api/__static_debug")
def static_debug():
    info = {
        "root":   {"path": str(STATIC_ROOT), "exists": STATIC_ROOT.is_dir()},
        "next":   {"path": str(NEXT_DIR),    "exists": NEXT_DIR.is_dir()},
        "static": {"path": str(NEXT_DIR / "static"), "exists": (NEXT_DIR / "static").is_dir()},
        "samples": {"index_html": False, "css": [], "chunks": [], "has_health": False},
    }
    files = []
    if STATIC_ROOT.is_dir():
        for p in STATIC_ROOT.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(STATIC_ROOT)).replace("\\", "/"))
    info["samples"]["index_html"] = any(p == "index.html" for p in files)
    info["samples"]["has_health"] = any(p == "health.txt" for p in files)
    info["samples"]["css"]    = [p for p in files if p.startswith("_next/static/css/")][:5]
    info["samples"]["chunks"] = [p for p in files if p.startswith("_next/static/chunks/")][:5]
    return JSONResponse(info)

# --- Static mounts ---
if NEXT_DIR.is_dir():
    app.mount("/_next", StaticFiles(directory=str(NEXT_DIR), html=False), name="next")
    print(f"[main] Mounted '/_next' from {NEXT_DIR}")
else:
    print(f"[main] WARN: Missing Next dir: {NEXT_DIR}")

app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT), html=False), name="media")

# --- API JSON-first errors ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"detail": exc.detail, "status": exc.status_code, "path": request.url.path}, status_code=exc.status_code)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

# --- API catch-all to avoid SPA swallowing ---
api_fallback = APIRouter()
@api_fallback.api_route("/api/{full_path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"], include_in_schema=False)
async def _api_404(full_path: str, request: Request):
    return JSONResponse({"detail": "Not Found", "path": f"/api/{full_path}"}, status_code=404)
app.include_router(api_fallback)

# --- Serve SPA last ---
app.mount("/", StaticFiles(directory=str(STATIC_ROOT), html=True), name="site")

# --- Startup log ---
@app.on_event("startup")
async def _log_routes():
    print("=== ROUTES MOUNTED ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            print(f"{','.join(sorted(r.methods)):15} {r.path}")
    print("=== DEBUG PROBES READY === /api/__whoami /api/__routes /api/__static_ping /api/__static_debug ===")
