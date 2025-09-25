from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

# Import all routers
from routers import (
    intelligence,
    summary, 
    calendar,
    agency_,
    ingest_ENHANCED,
    shopify
)

# Create FastAPI app
app = FastAPI(
    title="Crooks & Castles Command Center V2",
    description="Complete competitive intelligence and revenue analytics platform",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers with proper prefixes
app.include_router(intelligence_COMPLETE.router, prefix="/intelligence", tags=["intelligence"])
app.include_router(summary.router, prefix="/summary", tags=["summary"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(agency.router, prefix="/agency", tags=["agency"])
app.include_router(ingest_ENHANCED.router, prefix="/ingest", tags=["ingest"])
app.include_router(shopify.router, prefix="/shopify", tags=["shopify"])

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/uploads",
        "data/config", 
        "data/shopify",
        "data/calendar",
        "data/agency",
        "static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Create directories on startup
ensure_directories()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint - serve the main dashboard
@app.get("/")
async def read_root():
    """Serve the main dashboard interface"""
    static_file = Path("static/index.html")
    if static_file.exists():
        return FileResponse("static/index.html")
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Overall system health check"""
    return {
        "status": "healthy",
        "service": "Crooks & Castles Command Center V2",
        "version": "2.0.0",
        "modules": {
            "intelligence": "operational",
            "summary": "operational", 
            "calendar": "operational",
            "agency": "operational",
            "ingest": "operational",
            "shopify": "operational"
        }
    }

# API status endpoint
@app.get("/api/status")
async def api_status():
    """API status for frontend monitoring"""
    return {
        "api_status": "online",
        "endpoints_available": [
            "/intelligence/report",
            "/summary/overview",
            "/calendar/planning",
            "/agency/dashboard",
            "/ingest/upload",
            "/shopify/dashboard"
        ],
        "last_updated": "2025-09-25T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
