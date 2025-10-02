# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB bootstrap (creates tables if missing)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# --- Models (only the table we need for now) ---
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

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

# --- DB engine/session (reads your Render DATABASE_URL) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- App ---
app = FastAPI(title="Crooks Command Center V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create tables at boot (safe no-op after first run)
Base.metadata.create_all(bind=engine)

# --- Include your existing routers here (keep your imports as-is) ---
# from backend.routers import shopify, intelligence, ingest, summary, competitive, media
# app.include_router(ingest.router, prefix="/api")
# app.include_router(intelligence.router, prefix="/api")
# app.include_router(media.router, prefix="/api")
# app.include_router(shopify.router, prefix="/api")
# app.include_router(summary.router, prefix="/api")
# app.include_router(competitive.router, prefix="/api")

# Health
@app.get("/api/health")
def health():
    return {"ok": True}