# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

# === Import routers (files must exist in backend/routers/) ===
from backend.routers import (
    agency,
    calendar,
    content_creation,
    executive,
    ingest,
    intelligence,
    media,
    shopify,
    summary,
    upload_sidecar,
)

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# --- CORS (relaxed for now; tighten later) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health (both with and without /api for convenience) ---
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True}

# --- Helper to mount routers strictly under /api ---
def mount(rtr, name: str, prefix: str):
    app.include_router(rtr.router, prefix=f"/api{prefix}", tags=[name])

# === Mount every router exactly once under /api/* ===
mount(agency,           "agency",           "/agency")
mount(calendar,         "calendar",         "/calendar")
mount(content_creation, "content",          "/content")
mount(executive,        "executive",        "/executive")
mount(ingest,           "ingest",           "/ingest")
mount(intelligence,     "intelligence",     "/intelligence")
mount(media,            "media",            "/media")
mount(shopify,          "shopify",          "/shopify")
mount(summary,          "summary",          "/summary")
# DO NOT mount sidecar under /intelligence; give it its own prefix:
mount(upload_sidecar,   "upload_sidecar",   "/sidecar")

# --- Startup: log all active routes so you can sanity-check quickly ---
@app.on_event("startup")
async def _log_routes():
    print("=== ROUTES MOUNTED ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = ",".join(sorted(r.methods))
            print(f"{methods:15} {r.path}")
    print("======================")
