from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime

# Import only the routers you're actually using
from .routers import intelligence
from .routers import executive
from .routers import competitive
from .routers import agency
from .routers import calendar
from .routers import shopify
from .routers import summary

# Import database initialization
from .database import init_db

app = FastAPI(
    title="Crooks Command Center API",
    version="2.0.0",
    description="Command center for competitive intelligence, brand performance, and campaign planning"
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    print("[Startup] ✅ Database initialized")

# Include routers
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])
app.include_router(agency.router, prefix="/api/agency", tags=["agency"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(shopify.router, prefix="/api/shopify", tags=["shopify"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])

# CORS configuration
ALLOWED_ORIGINS = [
    "https://crooks-command-center-v2.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
]

if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "active",
            "database": os.getenv("DATABASE_URL") is not None,
            "openai": os.getenv("OPENAI_API_KEY") is not None
        },
        "version": "2.0.0"
    }

# Simple static file serving
static_dir = "static/site"
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    print(f"[Startup] ✅ Static files served from {static_dir}")
else:
    print(f"[Startup] ⚠️ No static directory found at {static_dir}")

# API root
@app.get("/api/")
def api_root():
    return {
        "message": "Crooks Command Center API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "intelligence": "/api/intelligence/",
            "executive": "/api/executive/",
            "competitive": "/api/competitive/",
            "agency": "/api/agency/",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)