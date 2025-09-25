from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Crooks & Castles Command Center V2",
    description="Complete competitive intelligence and revenue analytics platform with media management",
    version="2.0.2"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers with error handling
try:
    from routers.intelligence import router as intelligence_router
    app.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
    print("✅ Intelligence router loaded")
except Exception as e:
    print(f"⚠️ Intelligence router failed: {e}")

try:
    from routers.summary import router as summary_router
    app.include_router(summary_router, prefix="/summary", tags=["summary"])
    print("✅ Summary router loaded")
except Exception as e:
    print(f"⚠️ Summary router failed: {e}")

try:
    from routers.calendar import router as calendar_router
    app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
    print("✅ Calendar router loaded")
except Exception as e:
    print(f"⚠️ Calendar router failed: {e}")

try:
    from routers.agency import router as agency_router
    app.include_router(agency_router, prefix="/agency", tags=["agency"])
    print("✅ Agency router loaded")
except Exception as e:
    print(f"⚠️ Agency router failed: {e}")

try:
    from routers.ingest import router as ingest_router
    app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    print("✅ Ingest router loaded")
except Exception as e:
    print(f"⚠️ Ingest router failed: {e}")

try:
    from routers.shopify import router as shopify_router
    app.include_router(shopify_router, prefix="/shopify", tags=["shopify"])
    print("✅ Shopify router loaded")
except Exception as e:
    print(f"⚠️ Shopify router failed: {e}")

try:
    from routers.media import router as media_router
    app.include_router(media_router, prefix="/media", tags=["media"])
    print("✅ Media router loaded")
except Exception as e:
    print(f"⚠️ Media router failed: {e}")

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/uploads",
        "data/config", 
        "data/shopify",
        "data/calendar",
        "data/agency",
        "media/images",
        "media/videos",
        "media/audio",
        "media/thumbnails",
        "static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ensured: {directory}")

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
        "version": "2.0.2",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "intelligence": "operational",
            "summary": "operational", 
            "calendar": "operational",
            "agency": "operational",
            "ingest": "operational",
            "shopify": "operational",
            "media": "operational"
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
            "/ingest/overview",
            "/ingest/status",
            "/shopify/dashboard",
            "/media/upload",
            "/media/list"
        ],
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Crooks & Castles Command Center V2...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
