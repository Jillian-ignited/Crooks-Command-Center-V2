# backend/main.py
from __future__ import annotations

import os
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log = logging.getLogger("app")
if not log.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    log.addHandler(h)
    log.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Render sometimes provides postgres://; psycopg wants postgresql+psycopg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

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

# Create tables (no-op if already exist)
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------------------
# FastAPI app & CORS
# -----------------------------------------------------------------------------
app = FastAPI(title="Crooks Command Center V2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Routers (safe includes so missing files don’t crash the app)
# -----------------------------------------------------------------------------
def safe_include(module_path: str, prefix: str = "/api", router_attr: str = "router"):
    try:
        module = __import__(module_path, fromlist=[router_attr])
        router = getattr(module, router_attr)
        app.include_router(router, prefix=prefix)
        log.info("Mounted %s at %s", module_path, prefix)
    except Exception as e:
        log.warning("Skipped %s: %s", module_path, e)

# Add the ones you have; harmless if a file is missing
safe_include("backend.routers.shopify")
safe_include("backend.routers.intelligence")
safe_include("backend.routers.ingest_ENHANCED_MULTI_FORMAT")
safe_include("backend.routers.media")
safe_include("backend.routers.summary")
safe_include("backend.routers.competitive")
safe_include("backend.routers.calendar")
safe_include("backend.routers.agency")
safe_include("backend.routers.content_creation")
safe_include("backend.routers.executive")
safe_include("backend.routers.upload_sidecar")

# -----------------------------------------------------------------------------
# Static frontend (Next.js export copied to backend/static/site)
# -----------------------------------------------------------------------------
STATIC_DIR = Path(__file__).resolve().parent / "static" / "site"
if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
    # Mount AFTER API routes so /api/* isn’t shadowed
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="site")
    log.info("Serving static site from %s", STATIC_DIR)
else:
    @app.get("/")
    def root_placeholder():
        return {
            "status": "ok",
            "hint": "Static site not found. Ensure build copies Next 'out/*' to backend/static/site."
        }

# -----------------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"ok": True}