# Line 1-5: Essential imports
import os
import importlib
from typing import Any, Dict, List
from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse

# Line 6-8: Static files and CORS imports
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Line 9: Create FastAPI app
app = FastAPI(title="Crooks Command Center", version="2.0.0")
@app. get ("/test")
def test_endpoint ():
return
{"message": "API is working", "status": "success"}
# Line 10-16: Add CORS middleware FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Line 17-25: Health endpoints
@app.get("/health")
@app.get("/api/health")
def health() -> Dict[str, bool]:
    return {"ok": True}

@app.get("/routes")
@app.get("/api/routes")
def list_routes() -> Dict[str, Any]:
    out = []
    for r in app.routes:
        methods = sorted(list((getattr(r, "methods", set()) or set()) - {"HEAD","OPTIONS"}))
        out.append({"path": getattr(r, "path", ""), "name": getattr(r, "name", ""), "methods": methods})
    return {"routes": out}

# Line 26-35: Router auto-mounting configuration
MODULE_PREFIXES = ["backend.routers", "routers"]
ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "routers")

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

# Line 36-50: Router import function
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

# Line 51-70: Auto-mount all routers BEFORE static files
def _auto_mount_all() -> List[str]:
    mounted_prefixes: List[str] = []
    if not os.path.exists(ROUTERS_DIR):
        print(f"[main] Warning: {ROUTERS_DIR} not found")
        return mounted_prefixes
    
    files = [f for f in os.listdir(ROUTERS_DIR) if f.endswith(".py") and f != "__init__.py" and not f.startswith("_")]
    for file in sorted(files):
        modname = file[:-3]
        try:
            router = _import_router(modname)
            prefixes = _infer_prefixes(modname)
            
            app.include_router(router, prefix=prefixes["bare"], tags=[modname])
            app.include_router(router, prefix=prefixes["api"], tags=[modname])
            
            mounted_prefixes.append(prefixes["bare"].lstrip("/"))
            print(f"[main] Mounted '{modname}' at {prefixes['bare']} and {prefixes['api']}")
        except Exception as e:
            print(f"[main] Skipped '{modname}': {e}")
    return mounted_prefixes

# Line 71: Mount all routers NOW
MOUNTED_NAMES = _auto_mount_all()

# Line 72-85: API status endpoint
@app.get("/api/status")
def api_status():
    return {
        "status": "operational",
        "version": "2.0.0",
        "modules": MOUNTED_NAMES,
        "timestamp": "2024-09-28T00:00:00Z"
    }

# Line 86-110: SPA fallback middleware (AFTER routers are mounted)
@app.middleware("http")
async def spa_fallback_and_api_redirect(request: Request, call_next):
    path = request.url.path
    method = request.method
    
    # Skip static assets and API paths - let them through
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
            target = "/api" + path
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

# Line 111-115: Static files mounted LAST (this was the problem!)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# CRITICAL: Mount static files at /static NOT at root to avoid catching API calls
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Line 116-120: Root endpoint that serves the main HTML
@app.get("/")
async def root():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Crooks Command Center V2", "status": "operational"}
