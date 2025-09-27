# backend/main.py
import os, importlib
from typing import Dict, Any, List
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# ---- Health + routes list (both prefixes) ----
@app.get("/health"); @app.get("/api/health")
def health(): return {"ok": True}

@app.get("/routes"); @app.get("/api/routes")
def routes():
    out = []
    for r in app.routes:
        methods = sorted(list((getattr(r, "methods", set()) or set()) - {"HEAD","OPTIONS"}))
        out.append({"path": getattr(r, "path", ""), "name": getattr(r, "name", ""), "methods": methods})
    return {"routes": out}

# ---- Auto-mount every router file in backend/routers ----
MODULE_PREFIXES = ["backend.routers", "routers"]  # works whether run as package or from repo root
ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "routers")

# Optional: per-file prefix overrides (left side = filename without .py)
PREFIX_RULES: Dict[str, Dict[str, str]] = {
    # filename: {"bare": "/<legacy>", "api": "/api/<new>"}
    "content_creation": {"bare": "/content",      "api": "/api/content"},
    "ingest_ENHANCED_MULTI_FORMAT": {"bare": "/ingest", "api": "/api/ingest"},
    # upload_sidecar contributes under intelligence
    "upload_sidecar": {"bare": "/intelligence",   "api": "/api/intelligence"},
    # add more special cases if needed
}

def _infer_prefixes(module_name: str) -> Dict[str, str]:
    if module_name in PREFIX_RULES:
        return PREFIX_RULES[module_name]
    # default: use file name as path, but normalize funky names a bit
    bare = "/" + module_name.replace("__", "/").replace("_", "-").lower()
    api  = "/api" + bare
    return {"bare": bare, "api": api}

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
            continue
    raise RuntimeError(f"Unable to import router '{module_name}': {last_err}")

def auto_mount_all() -> List[Dict[str, Any]]:
    results = []
    files = [f for f in os.listdir(ROUTERS_DIR) if f.endswith(".py") and f != "__init__.py" and not f.startswith("_")]
    for file in sorted(files):
        module_name = file[:-3]
        try:
            router = _import_router(module_name)
            prefixes = _infer_prefixes(module_name)
            app.include_router(router, prefix=prefixes["bare"], tags=[module_name])
            app.include_router(router, prefix=prefixes["api"],  tags=[module_name])
            results.append({"module": module_name, "mounted": True, "prefixes": [prefixes["bare"], prefixes["api"]], "routes": len(router.routes)})
            print(f"[main] Mounted '{module_name}' at {prefixes['bare']} AND {prefixes['api']} (routes: {len(router.routes)})")
        except Exception as e:
            results.append({"module": module_name, "mounted": False, "error": str(e)})
            print(f"[main] Skipped '{module_name}': {e}")
    return results

MOUNT_REPORT = auto_mount_all()

# Optional: expose the mount report for quick debugging
@app.get("/mount-report"); @app.get("/api/mount-report")
def mount_report(): return {"mounts": MOUNT_REPORT}

# ---- Serve static Next.js export at root ----
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
