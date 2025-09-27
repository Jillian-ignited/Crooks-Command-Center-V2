# backend/main.py
import os
import importlib
from typing import Any, Dict, List

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# ---- Health endpoints ----
@app.get("/health")
@app.get("/api/health")
def health() -> Dict[str, bool]:
    return {"ok": True}

# ---- Routes listing (simple introspection) ----
@app.get("/routes")
@app.get("/api/routes")
def list_routes() -> Dict[str, Any]:
    out = []
    for r in app.routes:
        methods = sorted(list((getattr(r, "methods", set()) or set()) - {"HEAD","OPTIONS"}))
        out.append({"path": getattr(r, "path", ""), "name": getattr(r, "name", ""), "methods": methods})
    return {"routes": out}

# ---- Auto-mount every router file in backend/routers ----
MODULE_PREFIXES = ["backend.routers", "routers"]
ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "routers")

# Optional overrides for special filenames
PREFIX_RULES: Dict[str, Dict[str, str]] = {
    "content_creation": {"bare": "/content", "api": "/api/content"},
    "ingest_ENHANCED_MULTI_FORMAT": {"bare": "/ingest", "api": "/api/ingest"},
    "upload_sidecar": {"bare": "/intelligence", "api": "/api/intelligence"},
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
                raise TypeError(f"`router` in {base}.{module_name} is not an APIRouter")
            return router
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Unable to import router '{module_name}': {last_err}")

def auto_mount_all():
    files = [f for f in os.listdir(ROUTERS_DIR) if f.endswith(".py") and f != "__init__.py"]
    for file in sorted(files):
        modname = file[:-3]
        try:
            router = _import_router(modname)
            prefixes = _infer_prefixes(modname)
            app.include_router(router, prefix=prefixes["bare"], tags=[modname])
            app.include_router(router, prefix=prefixes["api"], tags=[modname])
            print(f"[main] Mounted '{modname}' at {prefixes['bare']} and {prefixes['api']}")
        except Exception as e:
            print(f"[main] Skipped '{modname}': {e}")

auto_mount_all()

# ---- Serve static Next.js export ----
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
