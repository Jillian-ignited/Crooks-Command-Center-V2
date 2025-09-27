# backend/main.py
import os, importlib
from typing import Any, Dict, List
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

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
    "upload_sidecar": {"bare": "/intelligence", "api": "/api/intelligence"},  # gives /upload under intelligence
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
            app.include_router(router, prefix=prefixes["bare"], tags=[modname])  # legacy
            app.include_router(router, prefix=prefixes["api"],  tags=[modname])  # /api
            mounted_prefixes.append(prefixes["bare"].lstrip("/"))
            print(f"[main] Mounted '{modname}' at {prefixes['bare']} and {prefixes['api']}")
        except Exception as e:
            print(f"[main] Skipped '{modname}': {e}")
    return mounted_prefixes

MOUNTED_NAMES = _auto_mount_all()  # e.g. ['executive', 'calendar', 'intelligence', ...]

# ---------- Compat fallback: redirect unmatched legacy -> /api ----------
# If a request comes to /<name>/... and didn't match any route, 307 to /api/<name>/...
# NOTE: we only do this for names we mounted to avoid stealing arbitrary paths.
@app.middleware("http")
async def compat_redirect_mw(request: Request, call_next):
    path = request.url.path
    # If path already starts with /api/ or it's the root/static assets, just continue.
    if path.startswith("/api/") or path.startswith("/_next/") or path.startswith("/static/") or "." in path.split("/")[-1]:
        return await call_next(request)

    # If the first segment matches a mounted router name, try redirecting to /api/<path>
    seg = path.split("/", 2)[1] if "/" in path else ""
    if seg in MOUNTED_NAMES:
        # Let normal routing try first
        resp = await call_next(request)
        if resp.status_code == 404:
            # 307 preserves method & body for POST/PUT
            target = "/api" + path
            return RedirectResponse(url=target, status_code=307)
        return resp

    # default
    return await call_next(request)

# ---------- Static Next.js export at root ----------
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
