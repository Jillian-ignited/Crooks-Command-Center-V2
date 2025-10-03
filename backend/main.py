# backend/main.py
from __future__ import annotations

import os
import logging
import importlib
import pkgutil
from types import ModuleType
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------------- Logging ----------------------------------------
log = logging.getLogger("app")
if not log.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    log.addHandler(h)
log.setLevel(logging.INFO)

# ----------------------------- Database ---------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# normalize postgres scheme for psycopg
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

Base.metadata.create_all(bind=engine)

# ------------------------------- App ------------------------------------------
app = FastAPI(title="Crooks Command Center V2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------- Auto-mount Routers ---------------------------------
def mount_all_routers(package: str = "backend.routers", prefix: str = "/api") -> None:
    """Discover every module under backend/routers and mount it if it defines `router`."""
    try:
        pkg = importlib.import_module(package)
    except Exception as e:
        log.error("Cannot import %s: %s", package, e)
        return

    for _finder, name, _ispkg in pkgutil.iter_modules(pkg.__path__):
        if name.startswith("_"):
            continue
        full_name = f"{package}.{name}"
        try:
            mod: ModuleType = importlib.import_module(full_name)
            router = getattr(mod, "router", None)
            if router is not None:
                app.include_router(router, prefix=prefix)
                log.info("Mounted %s at %s", full_name, prefix)
            else:
                log.debug("No `router` in %s; skipped", full_name)
        except Exception as e:
            log.warning("Skipped %s: %s", full_name, e)

mount_all_routers()

# --------------------------- Static Frontend ----------------------------------
STATIC_DIR = Path(__file__).resolve().parent / "static" / "site"
if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="site")
    log.info("Serving static site from %s", STATIC_DIR)
else:
    @app.get("/")
    def root_placeholder():
        return {
            "status": "ok",
            "hint": "Static site not found. Ensure build copies Next 'out/*' to backend/static/site."
        }

# ------------------------------ Health & Routes --------------------------------
@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/__routes")
def list_routes():
    return sorted(
        [
            {"path": r.path, "methods": sorted(m for m in getattr(r, "methods", set()) if m not in {"HEAD", "OPTIONS"})}
            for r in app.router.routes
        ],
        key=lambda x: x["path"],
    )
