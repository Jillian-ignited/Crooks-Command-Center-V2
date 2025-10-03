# backend/main.py
import os
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from starlette.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.main")

# ---------------- DB Models ----------------
Base = declarative_base()

class ShopifyUpload(Base):
    __tablename__ = "shopify_uploads"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    description = Column(String)
    processing_result = Column(JSON)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# ---------------- App ----------------
app = FastAPI(title="Crooks Command Center V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routers ----------------
ROUTERS = [
    ("agency", "Agency"),
    ("calendar", "Calendar"),
    ("competitive", "Competitive"),
    ("content_creation", "Content Creation"),
    ("database_setup", "Database Setup"),
    ("executive", "Executive"),
    ("ingest", "Ingest"),
    ("intelligence", "Intelligence"),
    ("media", "Media"),
    ("shopify", "Shopify"),
    ("summary", "Summary"),
]

for module, label in ROUTERS:
    try:
        mod = __import__(f"backend.routers.{module}", fromlist=["router"])
        app.include_router(mod.router, prefix="/api")
        logger.info(f"✅ {label} router loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load {label} router ({module}): {e}")

# ---------------- Static Files ----------------
static_dir = Path(__file__).resolve().parent / "static" / "site"
frontend_dir = Path(__file__).resolve().parent.parent / "frontend" / "out"

if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info(f"✅ Static files mounted from: {frontend_dir}")
elif static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    logger.info(f"✅ Static files mounted from: {static_dir}")
else:
    logger.warning("⚠️ No static frontend found to mount.")

# ---------------- Health & Utility ----------------
@app.get("/api/health")
def health():
    return {"ok": True}

@app.head("/")
def _render_head_ok():
    return Response(status_code=200)

@app.get("/api/__routes")
def list_routes(request: Request):
    """Debug: list all active routes"""
    routes = []
    for r in request.app.routes:
        if isinstance(r, APIRoute):
            methods = sorted(list(r.methods - {"HEAD", "OPTIONS"}))
            routes.append({"path": r.path, "methods": methods, "name": r.name})
    routes.sort(key=lambda x: (x["path"], ",".join(x["methods"])))
    return {"count": len(routes), "routes": routes}
