# backend/main.py
from __future__ import annotations

import os
import logging
import importlib
from types import ModuleType
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Logging ---
log = logging.getLogger("app")
if not log.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    log.addHandler(h)
    log.setLevel(logging.INFO)

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Allow Render's postgres:// value
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# Minimal model so the table exists for uploads (safe no-op if already defined elsewhere)
class ShopifyUpload(Base):
    __tablename__ = "shopify_uploads"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    description = Column(String)
    processing_result = Column(JSON)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# Create tables (idempotent)
Base.metadata.create_all(bind=engine)

# --- App ---
app = FastAPI(title="Crooks Command Center V2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
from backend.routers import agency, calendar, competitive, content_creation, database_setup, executive, ingest, intelligence, media, shopify, summary

app.include_router(agency.router, prefix="/api/agency", tags=["agency"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])
app.include_router(content_creation.router, prefix="/api/content", tags=["content"])
app.include_router(database_setup.router, prefix="/api/db", tags=["database"])
app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(shopify.router, prefix="/api/shopify", tags=["shopify"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])


# --- Static Files ---
static_files_path = Path(__file__).parent / "static" / "site"
if static_files_path.exists():
    app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")
    log.info(f"Serving static site from {static_files_path}")
else:
    log.warning(f"Static site directory not found at {static_files_path}")


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
