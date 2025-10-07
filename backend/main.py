from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Import routers
from .routers import intelligence
from .routers import executive
from .routers import competitive
from .routers import agency
from .routers import campaigns  # NEW: Replaces calendar
from .routers import shopify
from .routers import summary
from .routers import deliverables
from .database import init_db

app = FastAPI(
    title="Crooks Command Center API",
    version="2.5.0",  # Updated version
    description="Command center for competitive intelligence, brand performance, and campaign planning"
)

@app.on_event("startup")
def on_startup():
    init_db()
    print("[Startup] ✅ Database initialized")

# CORS - FIXED FOR VERCEL
ALLOWED_ORIGINS = [
    "https://crooks-command-center-v2-1d5b.vercel.app",
    "http://crooks-command-center-v2-1d5b.vercel.app",
    "https://crooks-command-center-v2.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
]

if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_ORIGINS = ["*"]

# CRITICAL: Add CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Include routers AFTER CORS
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])
app.include_router(agency.router, prefix="/api/agency", tags=["agency"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])  # NEW
app.include_router(shopify.router, prefix="/api/shopify", tags=["shopify"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
app.include_router(deliverables.router, prefix="/api/deliverables", tags=["deliverables"])
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
        "version": "2.5.0",
        "cors_origins": ALLOWED_ORIGINS
    }

@app.get("/api/")
def api_root():
    return {
        "message": "Crooks Command Center API",
        "version": "2.5.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "intelligence": "/api/intelligence/",
            "executive": "/api/executive/",
            "competitive": "/api/competitive/",
            "agency": "/api/agency/",
            "campaigns": "/api/campaigns/",  # NEW
            "shopify": "/api/shopify/",
            "summary": "/api/summary/",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
