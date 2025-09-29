# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

# --- Import router submodules explicitly (avoids __init__ export pitfalls) ---
import backend.routers.agency as agency
import backend.routers.calendar as calendar
import backend.routers.content_creation as content_creation
import backend.routers.executive as executive
import backend.routers.ingest as ingest
import backend.routers.intelligence as intelligence
import backend.routers.media as media
import backend.routers.shopify as shopify
import backend.routers.summary as summary
import backend.routers.upload_sidecar as upload_sidecar

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# --- CORS (relaxed while stabilizing; tighten later) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health at both paths for convenience ---
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True}

# --- Helper to mount routers strictly under /api/* ---
def mount(rtr, name: str, prefix: str):
    app.include_router(rtr.router, prefix=f"/api{prefix}", tags=[name])

# --- Mount every router exactly once, under /api/* ---
mount(agency,           "agency",           "/agency")
mount(calendar,         "calendar",         "/calendar")
mount(content_creation, "content",          "/content")
mount(executive,        "executive",        "/executive")
mount(ingest,           "ingest",           "/ingest")
mount(intelligence,     "intelligence",     "/intelligence")
mount(media,            "media",            "/media")
mount(shopify,          "shopify",          "/shopify")
mount(summary,          "summary",          "/summary")
# Sidecar gets its own prefix (do NOT overlap intelligence)
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
