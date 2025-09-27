import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# --- API Routers under /api ---
try:
    from .routers import upload_sidecar
    app.include_router(upload_sidecar.router, prefix="/api/intelligence", tags=["intelligence"])
except Exception:
    pass

@app.get("/api/health")
def health():
    return {"ok": True}

# --- Serve static Next.js export at root ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
