# backend/main.py
import os
import importlib
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
from fastapi import APIRouter

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# ---------- include helper + registry ----------
INCLUDED: Dict[str, Dict[str, Any]] = {}  # module_name -> {"prefix": str, "count": int} OR {"error": str}

def _include(module_name: str, prefix: str, tag: str):
    """
    Import backend.routers.<module_name>, get `router`, assert it's an APIRouter,
    include it at <prefix>, and record status in INCLUDED.
    """
    try:
        mod = importlib.import_module(f"backend.routers.{module_name}")
        router = getattr(mod, "router")
        if not isinstance(router, APIRouter):
            raise TypeError(f"`router` in {module_name}.py is not a fastapi.APIRouter")
        app.include_router(router, prefix=prefix, tags=[tag])
        # record how many routes the router contributed (pre-prefix)
        route_count = len(getattr(router, "routes", []))
        INCLUDED[module_name] = {"prefix": prefix, "count": route_count}
        print(f"[main] Mounted '{module_name}' at {prefix} (routes: {route_count})")
    except Exception as e:
        INCLUDED[module_name] = {"error": str(e)}
        print(f"[main] Skipped '{module_name}': {e}")

# ---------- YOUR ROUTERS (exact filenames you shared) ----------
_include("agency",                       "/api/agency",        "agency")
_include("calendar",                     "/api/calendar",      "calendar")
_include("content_creation",             "/api/content",       "content")
_include("executive",                    "/api/executive",     "executive")
_include("ingest_ENHANCED_MULTI_FORMAT", "/api/ingest",        "ingest")
_include("intelligence",                 "/api/intelligence",  "intelligence")
_include("media",                        "/api/media",         "media")
_include("shopify",                      "/api/shopify",       "shopify")
_include("summary",                      "/api/summary",       "summary")
_include("upload_sidecar",               "/api/intelligence",  "intelligence")  # adds /upload under intelligence

# ---------- health + introspection ----------
@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/_introspection")
def introspect() -> Dict[str, Any]:
    """List every route currently mounted (path, methods, name)."""
    out: List[Dict[str, str]] = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(set(r.methods or []) - {"HEAD", "OPTIONS"}))
            out.append({"path": r.path, "methods": methods, "name": r.name})
    return {"routes": out}

@app.get("/api/_router_audit")
def router_audit() -> Dict[str, Any]:
    """
    Scan backend/routers/*.py and report:
      - importable
      - has `router`
      - is APIRouter
      - mounted (based on INCLUDED)
      - contributed route count (from INCLUDED)
    """
    routers_dir = os.path.join(os.path.dirname(__file__), "routers")
    files = [f for f in os.listdir(routers_dir) if f.endswith(".py") and f != "__init__.py"]
    results: List[Dict[str, Any]] = []

    for file in sorted(files):
        module_name = file[:-3]  # drop .py
        info: Dict[str, Any] = {"module": module_name}
        try:
            mod = importlib.import_module(f"backend.routers.{module_name}")
            info["importable"] = True
            has_router = hasattr(mod, "router")
            info["has_router_attr"] = has_router
            if has_router:
                info["router_is_APIRouter"] = isinstance(getattr(mod, "router"), APIRouter)
            else:
                info["router_is_APIRouter"] = False
        except Exception as e:
            info["importable"] = False
            info["error"] = str(e)

        # inclusion status
        mounted = module_name in INCLUDED and "prefix" in INCLUDED[module_name]
        info["mounted"] = mounted
        if mounted:
            info["mounted_prefix"] = INCLUDED[module_name]["prefix"]
            info["router_route_count"] = INCLUDED[module_name]["count"]
        else:
            err = INCLUDED.get(module_name, {}).get("error")
            if err:
                info["mount_error"] = err

        results.append(info)

    return {"audit": results}

# ---------- static frontend (Next.js export) ----------
# Next export should write to backend/static/ (e.g., via: next export -o ../backend/static)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
