# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers (make sure these files exist in backend/routers/)
from backend.routers import intelligence, summary, calendar
from backend.routers import agency, content_creation, executive, ingest, media, shopify, upload_sidecar

app = FastAPI(title="Crooks Command Center")

# CORS (relax now, tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Health (both with and without /api for convenience)
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True}

def mount(rtr, name: str, prefix: str):
    # frontend/lib/api.js prefixes with /api, so we mount only under /api/*
    app.include_router(rtr.router, prefix=f"/api{prefix}", tags=[name])

# Mount routers (add others here as needed; these three fix your current 404s)
mount(intelligence, "intelligence", "/intelligence")
mount(summary,       "summary",       "/summary")
mount(calendar,      "calendar",      "/calendar")

# Optional: mount the rest if you’re using them now
mount(agency,           "agency",           "/agency")
mount(content_creation, "content",          "/content")
mount(executive,        "executive",        "/executive")
mount(ingest,           "ingest",           "/ingest")
mount(media,            "media",            "/media")
mount(shopify,          "shopify",          "/shopify")
# Give sidecar its own prefix (do NOT mount under /intelligence)
mount(upload_sidecar,   "upload_sidecar",   "/sidecar")
