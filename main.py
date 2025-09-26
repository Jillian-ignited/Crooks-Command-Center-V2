import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Crooks & Castles Command Center V2 - API",
    description="Backend API for executive dashboard and intelligence analysis",
    version="2.2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/uploads",
        "data/shopify", 
        "data/competitive",
        "data/config",
        "data/calendar",
        "data/agency",
        "data/content"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

ensure_directories()

# Import routers with error handling
routers_loaded = []

try:
    from routers.executive import router as executive_router
    app.include_router(executive_router, prefix="/executive", tags=["executive"])
    routers_loaded.append("executive")
except Exception as e:
    print(f"⚠️ Executive router failed: {e}")

try:
    from routers.intelligence import router as intelligence_router
    app.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
    routers_loaded.append("intelligence")
except Exception as e:
    print(f"⚠️ Intelligence router failed: {e}")

try:
    from routers.agency_REAL_TRACKING import router as agency_router
    app.include_router(agency_router, prefix="/agency", tags=["agency"])
    routers_loaded.append("agency")
except Exception as e:
    print(f"⚠️ Agency router failed: {e}")

try:
    from routers.ingest_ENHANCED_MULTI_FORMAT import router as ingest_router
    app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    routers_loaded.append("ingest")
except Exception as e:
    print(f"⚠️ Ingest router failed: {e}")

try:
    from routers.content_creation import router as content_router
    app.include_router(content_router, prefix="/content", tags=["content"])
    routers_loaded.append("content")
except Exception as e:
    print(f"⚠️ Content router failed: {e}")

try:
    from routers.calendar import router as calendar_router
    app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
    routers_loaded.append("calendar")
except Exception as e:
    print(f"⚠️ Calendar router failed: {e}")

try:
    from routers.summary import router as summary_router
    app.include_router(summary_router, prefix="/summary", tags=["summary"])
    routers_loaded.append("summary")
except Exception as e:
    print(f"⚠️ Summary router failed: {e}")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint for Render health check"""
    return {
        "status": "healthy",
        "service": "Crooks & Castles Command Center V2 - API",
        "version": "2.2.0",
        "routers_loaded": routers_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Crooks & Castles Command Center V2 - API",
        "version": "2.2.0",
        "routers_loaded": routers_loaded,
        "environment": "production" if os.getenv("RENDER") else "development",
        "timestamp": datetime.now().isoformat()
    }

# API status endpoint
@app.get("/api/status")
async def api_status():
    """API status for frontend monitoring"""
    return {
        "api_status": "online",
        "backend_version": "2.2.0",
        "routers_loaded": routers_loaded,
        "cors_enabled": True,
        "endpoints_available": [
            "/executive/overview - Executive dashboard",
            "/intelligence/report - Intelligence analysis", 
            "/ingest/upload - Data upload",
            "/agency/dashboard - Agency tracking",
            "/content/dashboard - Content creation",
            "/calendar/planning - Campaign calendar",
            "/summary/overview - Data overview"
        ],
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
