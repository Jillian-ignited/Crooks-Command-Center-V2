# backend/main.py
import os
import importlib
from typing import Any, Dict, List

from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# -------- Health + Introspection at BOTH prefixes --------
@app.get("/health")
@app.get("/api/health")
def health() -> Dict[str, bool]:
    return {"ok": True}

@app.get("/_introspection")
@app.get("/api/_introspection")
def introspect() -> Dict[str, Any]:
    out: List[Dict[str, str]] = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(set(r.methods or []) - {"HEAD", "OPTIONS"}))
            out.append({"path": r.path, "methods": methods, "name": r.name})
    return {"routes": out}

# -------- Router import + dual-mount helpers --------
# Works whether you run as "backend.main:app" or from repo root.
MODULE_PREFIXES = ["backend.routers", "routers"]

def _import_router(module_name: str) -> APIRouter:
    last_err: Exception | None = None
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

def _mount_both(module_name: str, bare_prefix: str, api_prefix: str, tag: str):
    router = _import_router(module_name)
    app.include_router(router, prefix=bare_prefix, tags=[tag])   # legacy (no /api)
    app.include_router(router, prefix=api_prefix, tags=[tag])    # new (/api)
    print(f"[main] Mounted '{module_name}' at {bare_prefix} AND {api_prefix} (routes: {len(router.routes)})")

# -------- Your routers (exact filenames under backend/routers) --------
_mount_both("agency",                       "/agency",        "/api/agency",        "agency")
_mount_both("calendar",                     "/calendar",      "/api/calendar",      "calendar")
_mount_both("content_creation",             "/content",       "/api/content",       "content")
_mount_both("executive",                    "/executive",     "/api/executive",     "executive")
_mount_both("ingest_ENHANCED_MULTI_FORMAT", "/ingest",        "/api/ingest",        "ingest")
_mount_both("intelligence",                 "/intelligence",  "/api/intelligence",  "intelligence")
_mount_both("media",                        "/media",         "/api/media",         "media")
_mount_both("shopify",                      "/shopify",       "/api/shopify",       "shopify")
_mount_both("summary",                      "/summary",       "/api/summary",       "summary")
# sidecar adds /upload under intelligence
_mount_both("upload_sidecar",               "/intelligence",  "/api/intelligence",  "intelligence")

# -------- (Optional) Router audit at BOTH prefixes --------
@app.get("/_router_audit")
@app.get("/api/_router_audit")
def router_audit() -> Dict[str, Any]:
    """Report which router modules exist and that they expose an APIRouter."""
    results: List[Dict[str, Any]] = []
    routers_dir = os.path.join(os.path.dirname(__file__), "routers")
    files = [f for f in os.listdir(routers_dir) if f.endswith(".py") and f != "__init__.py"]
    for file in sorted(files):
        modname = file[:-3]
        info: Dict[str, Any] = {"module": modname}
        try:
            r = _import_router(modname)
            info.update(
                importable=True,
                has_router_attr=True,
                router_is_APIRouter=True,
                route_count=len(r.routes),
            )
        except Exception as e:
            info.update(
                importable=False,
                has_router_attr=False,
                router_is_APIRouter=False,
                error=str(e),
            )
        results.append(info)
    return {"audit": results}

# -------- Static Next.js export at root --------
# Next export should copy into backend/static/ at build time.
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
