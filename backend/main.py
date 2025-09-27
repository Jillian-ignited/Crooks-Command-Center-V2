# backend/main.py
import os, importlib
from typing import Any, Dict, List
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
from fastapi import APIRouter

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# figure out the right module prefix automatically
# we prefer "backend.routers.<mod>", but also try "routers.<mod>" as a fallback
MODULE_PREFIX_CANDIDATES = ["backend.routers", "routers"]

INCLUDED: Dict[str, Dict[str, Any]] = {}

def _import_router(module_name: str) -> APIRouter:
    last_err = None
    for base in MODULE_PREFIX_CANDIDATES:
        try:
            mod = importlib.import_module(f"{base}.{module_name}")
            router = getattr(mod, "router")
            if not isinstance(router, APIRouter):
                raise TypeError(f"`router` in {base}.{module_name} is not a fastapi.APIRouter")
            return router
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Unable to import router '{module_name}': {last_err}")

def _include_both(module_name: str, bare_prefix: str, api_prefix: str, tag: str):
    try:
        router = _import_router(module_name)
        app.include_router(router, prefix=bare_prefix, tags=[tag])
        app.include_router(router, prefix=api_prefix, tags=[tag])
        route_count = len(getattr(router, "routes", []))
        INCLUDED[module_name] = {"prefixes": [bare_prefix, api_prefix], "count": route_count}
        print(f"[main] Mounted '{module_name}' at {bare_prefix} and {api_prefix} (routes: {route_count})")
    except Exception as e:
        INCLUDED[module_name] = {"error": str(e)}
        print(f"[main] Skipped '{module_name}': {e}")

# === YOUR ROUTERS (exact filenames you listed in backend/routers) ===
_include_both("agency",                       "/agency",        "/api/agency",        "agency")
_include_both("calendar",                     "/calendar",      "/api/calendar",      "calendar")
_include_both("content_creation",             "/content",       "/api/content",       "content")
_include_both("executive",                    "/executive",     "/api/executive",     "executive")
_include_both("ingest_ENHANCED_MULTI_FORMAT", "/ingest",        "/api/ingest",        "ingest")
_include_both("intelligence",                 "/intelligence",  "/api/intelligence",  "intelligence")
_include_both("media",                        "/media",         "/api/media",         "media")
_include_both("shopify",                      "/shopify",       "/api/shopify",       "shopify")
_include_both("summary",                      "/summary",       "/api/summary",       "summary")
_include_both("upload_sidecar",               "/intelligence",  "/api/intelligence",  "intelligence")  # adds /upload

# health + introspection
@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/_introspection")
def introspect():
    out: List[Dict[str, str]] = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(set(r.methods or []) - {"HEAD","OPTIONS"}))
            out.append({"path": r.path, "methods": methods, "name": r.name})
    return {"routes": out}

@app.get("/api/_router_audit")
def router_audit():
    results: List[Dict[str, Any]] = []
    # look in backend/routers
    routers_dir = os.path.join(os.path.dirname(__file__), "routers")
    files = [f for f in os.listdir(routers_dir) if f.endswith(".py") and f != "__init__.py"]
    for file in sorted(files):
        module_name = file[:-3]
        info: Dict[str, Any] = {"module": module_name}
        try:
            router = _import_router(module_name)
            info["importable"] = True
            info["has_router_attr"] = True
            info["router_is_APIRouter"] = True
        except Exception as e:
            info["importable"] = False
            info["has_router_attr"] = False
            info["router_is_APIRouter"] = False
            info["error"] = str(e)
        inc = INCLUDED.get(module_name)
        if inc and "prefixes" in inc:
            info["mounted"] = True
            info["mounted_prefixes"] = inc["prefixes"]
            info["router_route_count"] = inc["count"]
        else:
            info["mounted"] = False
            if inc and "error" in inc:
                info["mount_error"] = inc["error"]
        results.append(info)
    return {"audit": results}

# serve static Next.js export at /
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
