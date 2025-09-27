import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# ---------- API: include all routers under /api/<name> ----------
# Each router module must expose a FastAPI APIRouter as `router`.

def _include(module_name: str, prefix: str, tag: str):
    """
    Safe include helper. Logs import failures without killing the app.
    """
    try:
        module = __import__(f"backend.routers.{module_name}", fromlist=["router"])
        router = getattr(module, "router")
        app.include_router(router, prefix=prefix, tags=[tag])
        print(f"[main] Mounted router '{module_name}' at {prefix}")
    except Exception as e:
        print(f"[main] Skipped router '{module_name}' ({e})")

# Map your modules to URL prefixes
_include("agency",                "/api/agency",                "agency")
_include("calendar",              "/api/calendar",              "calendar")
_include("content_creation",      "/api/content",               "content")
_include("executive",             "/api/executive",             "executive")
_include("ingest_ENHANCED_MULTI_FORMAT", "/api/ingest",         "ingest")
_include("intelligence",          "/api/intelligence",          "intelligence")
_include("media",                 "/api/media",                 "media")
_include("shopify",               "/api/shopify",               "shopify")
_include("summary",               "/api/summary",               "summary")
_include("upload_sidecar",        "/api/intelligence",          "intelligence")  # adds /upload

# Health
@app.get("/api/health")
def health():
    return {"ok": True}

# ---------- Static frontend (Next.js export) at root ----------
# Next export should write into backend/static/ (see package.json scripts).
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
