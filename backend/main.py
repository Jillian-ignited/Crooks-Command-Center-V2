# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from pathlib import Path

# --- DB bootstrap (same as your current) ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
import os

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

# --- App ---
app = FastAPI(title="Crooks Command Center V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (no-op if already exist)
Base.metadata.create_all(bind=engine)

# --- Include your routers here when ready ---
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

# --- Serve the built Next.js app ---
# Your build copies: frontend/out/* -> backend/static/site/
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static" / "site"

if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
    # IMPORTANT: mount AFTER API routes so /api/* still works
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="site")
else:
    # Helpful placeholder if static bundle missing
    @app.get("/")
    def root_placeholder():
        return {
            "status": "ok",
            "hint": "Static site not found. Ensure build copies Next 'out/*' to backend/static/site."
        }