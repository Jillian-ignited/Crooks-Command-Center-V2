# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse, JSONResponse
import importlib, os
from types import ModuleType
from typing import Optional, List, Tuple

APP_VERSION = "frontend-static-v4"
STATIC_ROOT = "backend/static/site"
NEXT_DIR    = os.path.join(STATIC_ROOT, "_next")
NEXT_STATIC = os.path.join(NEXT_DIR, "static")

app = FastAPI(title="Crooks Command Center", version=APP_VERSION)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Health ---
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

# Routers
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

# --- Explicit Next.js mounts (avoid 404s for hashed assets) ---
if os.path.isdir(NEXT_DIR):
    app.mount("/_next", StaticFiles(directory=NEXT_DIR, html=False), name="next")
    print(f"[main] Mounted '/_next' from {os.path.abspath(NEXT_DIR)}")
else:
    print(f"[main] WARN: Missing Next dir: {os.path.abspath(NEXT_DIR)}")

if os.path.isdir(NEXT_STATIC):
    app.mount("/_next/static", StaticFiles(directory=NEXT_STATIC, html=False), name="next-static")
    print(f"[main] Mounted '/_next/static' from {os.path.abspath(NEXT_STATIC)}")
else:
    print(f"[main] WARN: Missing Next static dir: {os.path.abspath(NEXT_STATIC)}")

# --- Serve SPA at root LAST (so it doesn’t shadow /api/*) ---
app.mount("/", StaticFiles(directory=STATIC_ROOT, html=True), name="site")

# --- Static diagnostics under /api so they cannot be shadowed ---
@app.get("/api/__static_ping", response_class=PlainTextResponse)
def __static_ping():
    parts = [
        f"ROOT exists={os.path.isdir(STATIC_ROOT)} path={os.path.abspath(STATIC_ROOT)}",
        f"_next exists={os.path.isdir(NEXT_DIR)} path={os.path.abspath(NEXT_DIR)}",
        f"_next/static exists={os.path.isdir(NEXT_STATIC)} path={os.path.abspath(NEXT_STATIC)}",
    ]
    return "\n".join(parts)

@app.get("/api/__static_debug")
def __static_debug():
    info = {
        "root":   {"path": os.path.abspath(STATIC_ROOT), "exists": os.path.isdir(STATIC_ROOT)},
        "next":   {"path": os.path.abspath(NEXT_DIR),    "exists": os.path.isdir(NEXT_DIR)},
        "static": {"path": os.path.abspath(NEXT_STATIC), "exists": os.path.isdir(NEXT_STATIC)},
        "samples": {"index_html": False, "css": [], "chunks": [], "has_health": False},
    }
    files = []
    if info["root"]["exists"]:
        for r, _, fs in os.walk(STATIC_ROOT):
            for f in fs:
                files.append(os.path.relpath(os.path.join(r, f), STATIC_ROOT))
    info["samples"]["index_html"] = any(p == "index.html" for p in files)
    info["samples"]["has_health"] = any(p == "health.txt" for p in files)
    info["samples"]["css"]    = [p for p in files if p.startswith("_next/static/css/")][:5]
    info["samples"]["chunks"] = [p for p in files if p.startswith("_next/static/chunks/")][:5]
    return JSONResponse(info)

# --- Startup: list routes ---
@app.on_event("startup")
async def _log_routes():
    print("=== ROUTES MOUNTED ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(r.methods))
            print(f"{methods:15} {r.path}")
    print("======================")
