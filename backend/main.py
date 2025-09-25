from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Import all routers
from routers import (
    intelligence,
    summary, 
    calendar,
    agency,
    ingest_ENHANCED,
    shopify,
    media  # New media router
)

app = FastAPI(title="Crooks & Castles Command Center V2", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers with proper prefixes
app.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
app.include_router(summary.router, prefix="/summary", tags=["summary"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(agency.router, prefix="/agency", tags=["agency"])
app.include_router(ingest_ENHANCED.router, prefix="/ingest", tags=["ingest"])
app.include_router(shopify.router, prefix="/shopify", tags=["shopify"])
app.include_router(media.router, prefix="/media", tags=["media"])  # New media router

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/uploads",
        "data/config", 
        "data/shopify",
        "data/calendar",
        "data/agency",
        "data/media",
        "data/media/images",
        "data/media/videos",
        "data/media/audio",
        "data/media/documents",
        "static"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Create directories on startup
ensure_directories()

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main page
@app.get("/")
async def read_root():
    """Serve the main dashboard page"""
    static_file = "static/index.html"
    if os.path.exists(static_file):
        return FileResponse(static_file)
    else:
        return {"message": "Crooks & Castles Command Center V2 - API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Crooks & Castles Command Center V2",
        "version": "2.0.0"
    }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "title": "Crooks & Castles Command Center V2",
        "version": "2.0.0",
        "description": "Competitive Intelligence and Revenue Analytics Platform",
        "endpoints": {
            "intelligence": "/intelligence/*",
            "summary": "/summary/*",
            "calendar": "/calendar/*", 
            "agency": "/agency/*",
            "data_ingest": "/ingest/*",
            "shopify": "/shopify/*",
            "media": "/media/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
