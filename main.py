# /backend/main.py - Fixed Import Paths for Deployment

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import json
import traceback
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crooks & Castles Command Center V2.1",
    description="Real data competitive intelligence and revenue analytics platform",
    version="2.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Safe router loading function
def load_router_safely(module_path, router_name, prefix, tags):
    """Safely load router with error handling"""
    try:
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info(f"✅ {prefix} router loaded")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ {prefix} router not found: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {prefix} router failed: {e}")
        return False

# Track loaded modules
loaded_modules = {}

# Load existing routers (these should work based on your file structure)
loaded_modules['intelligence'] = load_router_safely(
    "routers.intelligence", "router", "/intelligence", ["intelligence"]
)

loaded_modules['summary'] = load_router_safely(
    "routers.summary", "router", "/summary", ["summary"]
)

loaded_modules['calendar'] = load_router_safely(
    "routers.calendar", "router", "/calendar", ["calendar"]
)

loaded_modules['shopify'] = load_router_safely(
    "routers.shopify", "router", "/shopify", ["shopify"]
)

loaded_modules['media'] = load_router_safely(
    "routers.media", "router", "/media", ["media"]
)

# Load enhanced routers (these may or may not exist)
loaded_modules['agency'] = load_router_safely(
    "routers.agency_REAL_TRACKING", "router", "/agency", ["agency"]
)

loaded_modules['ingest'] = load_router_safely(
    "routers.ingest_ENHANCED_MULTI_FORMAT", "router", "/ingest", ["ingest"]
)

loaded_modules['content'] = load_router_safely(
    "routers.content_creation", "router", "/content", ["content"]
)

# Load the executive router (this is the new one we need)
loaded_modules['executive'] = load_router_safely(
    "routers.executive", "router", "/executive", ["executive"]
)

# Directory setup
def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        "data/uploads", "data/config", "data/shopify", "data/calendar",
        "data/agency", "data/content", "data/competitive",
        "media/images", "media/videos", "media/audio", "media/thumbnails",
        "static", "build"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create {directory}: {e}")

ensure_directories()

# Static file mounting
try:
    if Path("build").exists():
        app.mount("/static", StaticFiles(directory="build"), name="static")
        logger.info("✅ Mounted build directory")
    elif Path("static").exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Mounted static directory")
except Exception as e:
    logger.error(f"Failed to mount static files: {e}")

# Root endpoint
@app.get("/")
async def read_root():
    """Serve the main dashboard"""
    try:
        if Path("build/index.html").exists():
            return FileResponse("build/index.html")
        elif Path("static/index.html").exists():
            return FileResponse("static/index.html")
        else:
            return JSONResponse(content={
                "service": "Crooks & Castles Command Center V2.1",
                "status": "API Online",
                "message": "Frontend build not found",
                "loaded_modules": loaded_modules
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """System health check"""
    operational = sum(loaded_modules.values())
    total = len(loaded_modules)
    
    return {
        "status": "healthy" if operational > 0 else "degraded",
        "service": "Crooks & Castles Command Center V2.1",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "modules": loaded_modules,
        "health_score": f"{operational}/{total} modules loaded"
    }

# API status
@app.get("/api/status")
async def api_status():
    """API status information"""
    endpoints = []
    
    if loaded_modules.get('intelligence'):
        endpoints.append("/intelligence/report")
    if loaded_modules.get('executive'):
        endpoints.append("/executive/overview")
    if loaded_modules.get('summary'):
        endpoints.append("/summary/overview")
    if loaded_modules.get('calendar'):
        endpoints.append("/calendar/planning")
    if loaded_modules.get('agency'):
        endpoints.append("/agency/dashboard")
    if loaded_modules.get('ingest'):
        endpoints.append("/ingest/upload")
    if loaded_modules.get('shopify'):
        endpoints.append("/shopify/dashboard")
    if loaded_modules.get('media'):
        endpoints.append("/media/list")
    
    return {
        "api_status": "online",
        "endpoints_available": endpoints,
        "loaded_modules": loaded_modules,
        "last_updated": datetime.now().isoformat()
    }

# Fallback endpoints for missing modules
@app.get("/executive/overview")
async def executive_fallback():
    if not loaded_modules.get('executive'):
        return JSONResponse(
            status_code=503,
            content={
                "error": "Executive module not loaded",
                "message": "Create /routers/executive.py with the executive router code",
                "loaded_modules": loaded_modules
            }
        )

@app.get("/intelligence/report")
async def intelligence_fallback():
    if not loaded_modules.get('intelligence'):
        return JSONResponse(
            status_code=503,
            content={
                "error": "Intelligence module not loaded", 
                "message": "Create /routers/intelligence.py with the intelligence router code",
                "loaded_modules": loaded_modules
            }
        )

if __name__ == "__main__":
    print("🚀 Starting Crooks & Castles Command Center V2.1...")
    print(f"Loaded modules: {sum(loaded_modules.values())}/{len(loaded_modules)}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
