# backend/main.py - PRODUCTION READY FOR RENDER
import os, importlib
from typing import Any, Dict, List
from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crooks Command Center", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health (both) ----------
@app.get("/health")
@app.get("/api/health")
def health() -> Dict[str, bool]:
    return {"ok": True}

# ---------- Routes list (both) ----------
@app.get("/routes")
@app.get("/api/routes")
def list_routes() -> Dict[str, Any]:
    out = []
    for r in app.routes:
        methods = sorted(list((getattr(r, "methods", set()) or set()) - {"HEAD","OPTIONS"}))
        out.append({"path": getattr(r, "path", ""), "name": getattr(r, "name", ""), "methods": methods})
    return {"routes": out}

# ---------- Auto-mount routers in backend/routers ----------
MODULE_PREFIXES = ["backend.routers", "routers"]
ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "routers")

# Map funky filenames to nicer prefixes
PREFIX_RULES: Dict[str, Dict[str, str]] = {
    "content_creation": {"bare": "/content", "api": "/api/content"},
    "ingest_ENHANCED_MULTI_FORMAT": {"bare": "/ingest", "api": "/api/ingest"},
    "upload_sidecar": {"bare": "/upload", "api": "/api/upload"},
}

def _infer_prefixes(module_name: str) -> Dict[str, str]:
    if module_name in PREFIX_RULES:
        return PREFIX_RULES[module_name]
    bare = "/" + module_name.replace("__", "/").replace("_", "-").lower()
    return {"bare": bare, "api": "/api" + bare}

def _import_router(module_name: str) -> APIRouter:
    last_err = None
    for base in MODULE_PREFIXES:
        try:
            mod = importlib.import_module(f"{base}.{module_name}")
            router = getattr(mod, "router")
            if not isinstance(router, APIRouter):
                raise TypeError(f"`router` in {base}.{module_name} is not fastapi.APIRouter")
            return router
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Unable to import router '{module_name}': {last_err}")

def _auto_mount_all() -> List[str]:
    mounted_prefixes: List[str] = []
    files = [f for f in os.listdir(ROUTERS_DIR) if f.endswith(".py") and f != "__init__.py" and not f.startswith("_")]
    for file in sorted(files):
        modname = file[:-3]
        try:
            router = _import_router(modname)
            prefixes = _infer_prefixes(modname)
            
            # Mount with trailing slash tolerance
            app.include_router(router, prefix=prefixes["bare"], tags=[modname])
            app.include_router(router, prefix=prefixes["api"], tags=[modname])
            
            mounted_prefixes.append(prefixes["bare"].lstrip("/"))
            print(f"[main] Mounted '{modname}' at {prefixes['bare']} and {prefixes['api']}")
        except Exception as e:
            print(f"[main] Skipped '{modname}': {e}")
    return mounted_prefixes

MOUNTED_NAMES = _auto_mount_all()

# ---------- SPA Fallback Middleware ----------
@app.middleware("http")
async def spa_fallback_and_api_redirect(request: Request, call_next):
    path = request.url.path
    method = request.method
    
    # Skip static assets and API paths
    if (path.startswith("/api/") or 
        path.startswith("/_next/") or 
        path.startswith("/static/") or 
        "." in path.split("/")[-1]):
        return await call_next(request)
    
    # Handle bare API paths - redirect to /api/*
    seg = path.split("/", 2)[1] if "/" in path else ""
    if seg in MOUNTED_NAMES:
        resp = await call_next(request)
        if resp.status_code in [404, 405]:
            # Try redirecting to /api version
            target = "/api" + path
            if method in ["GET", "HEAD"]:
                return RedirectResponse(url=target, status_code=307)
            else:
                # For POST/PUT/etc, preserve method and body
                return RedirectResponse(url=target, status_code=307)
        return resp
    
    # Try normal routing first
    response = await call_next(request)
    
    # SPA fallback for HTML requests that 404
    if (response.status_code == 404 and 
        "text/html" in request.headers.get("accept", "")):
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    return response

# ---------- API Status endpoint ----------
@app.get("/api/status")
def api_status():
    return {
        "status": "operational",
        "version": "2.0.0",
        "modules": MOUNTED_NAMES,
        "timestamp": "2024-09-28T00:00:00Z"
    }

# ---------- Static Next.js export at root ----------
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
