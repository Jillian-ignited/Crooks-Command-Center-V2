# backend/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any

app = FastAPI(title="Crooks Command Center", version="1.0.0")

def _include(module_name: str, prefix: str, tag: str):
    """
    Import backend.routers.<module_name>, grab `router`, and mount it.
    If anything is off (missing module/router), we log and keep booting.
    """
    try:
        mod = __import__(f"backend.routers.{module_name}", fromlist=["router"])
        router = getattr(mod, "router")
        app.include_router(router, prefix=prefix, tags=[tag])
        print(f"[main] Mounted router '{module_name}' at {prefix}")
    except Exception as e:
        print(f"[main] Skipped router '{module_name}': {e}")

# ---- YOUR ROUTERS (exact names you shared) ----
_include("agency",                       "/api/agency",        "agency")
_include("calendar",                     "/api/calendar",      "calendar")
_include("content_creation",             "/api/content",       "content")
_include("executive",                    "/api/executive",     "executive")
_include("ingest_ENHANCED_MULTI_FORMAT", "/api/ingest",        "ingest")
_include("intelligence",                 "/api/intelligence",  "intelligence")
_include("media",                        "/api/media",         "media")
_include("shopify",                      "/api/shopify",       "shopify")
_include("summary",                      "/api/summary",       "summary")
_include("upload_sidecar",               "/api/intelligence",  "intelligence")  # provides /upload

# Health
@app.get("/api/health")
def health():
    return {"ok": True}

# Introspection: see exactly what routes are mounted (helpful for quick validation)
@app.get("/api/_introspection")
def introspect() -> Dict[str, Any]:
    routes: List[Dict[str, str]] = []
    for r in app.routes:
        try:
            routes.append({
                "path": getattr(r, "path", ""),
                "methods": ",".join(sorted(getattr(r, "methods", []) - {"HEAD", "OPTIONS"})) or "",
                "name": getattr(r, "name", ""),
            })
        except Exception:
            pass
    return {"routes": routes}

# Serve static Next.js export at /
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
