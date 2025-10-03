from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="Crooks Command Center API",
    description="Comprehensive content planning and performance optimization platform for authentic street culture marketing",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Import routers with correct paths for backend directory structure
routers_loaded = []
router_errors = []

# Try different import patterns based on your directory structure
import_patterns = [
    "backend.routers",  # If main.py is in root and routers in backend/routers/
    "routers",          # If main.py is in backend/ and routers in backend/routers/
    ".routers",         # Relative import if main.py is in backend/
]

def try_import_router(router_name, router_patterns):
    """Try to import a router using different patterns"""
    for pattern in router_patterns:
        try:
            if pattern == "backend.routers":
                module = __import__(f"{pattern}.{router_name}", fromlist=[router_name])
            elif pattern == "routers":
                module = __import__(f"{pattern}.{router_name}", fromlist=[router_name])
            elif pattern == ".routers":
                from . import routers
                module = getattr(routers, router_name)
            else:
                continue
            return module
        except (ImportError, AttributeError):
            continue
    return None

# Executive Router
executive = try_import_router("executive", import_patterns)
if executive:
    app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
    routers_loaded.append("executive")
    logger.info("✅ Executive router loaded")
else:
    router_errors.append("executive: Import failed with all patterns")
    logger.error("❌ Failed to load executive router")

# Competitive Router
competitive = try_import_router("competitive", import_patterns)
if competitive:
    app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])
    routers_loaded.append("competitive")
    logger.info("✅ Competitive router loaded")
else:
    router_errors.append("competitive: Import failed with all patterns")
    logger.error("❌ Failed to load competitive router")

# Competitive Analysis Router
competitive_analysis = try_import_router("competitive_analysis", import_patterns)
if competitive_analysis:
    app.include_router(competitive_analysis.router, prefix="/api/competitive-analysis", tags=["competitive_analysis"])
    routers_loaded.append("competitive_analysis")
    logger.info("✅ Competitive Analysis router loaded")
else:
    router_errors.append("competitive_analysis: Import failed with all patterns")
    logger.error("❌ Failed to load competitive_analysis router")

# Shopify Router
shopify = try_import_router("shopify", import_patterns)
if shopify:
    app.include_router(shopify.router, prefix="/api/shopify", tags=["shopify"])
    routers_loaded.append("shopify")
    logger.info("✅ Shopify router loaded")
else:
    router_errors.append("shopify: Import failed with all patterns")
    logger.error("❌ Failed to load shopify router")

# Agency Router
agency = try_import_router("agency", import_patterns)
if agency:
    app.include_router(agency.router, prefix="/api/agency", tags=["agency"])
    routers_loaded.append("agency")
    logger.info("✅ Agency router loaded")
else:
    router_errors.append("agency: Import failed with all patterns")
    logger.error("❌ Failed to load agency router")

# Calendar Router
calendar_router = try_import_router("calendar", import_patterns)
if calendar_router:
    app.include_router(calendar_router.router, prefix="/api/calendar", tags=["calendar"])
    routers_loaded.append("calendar")
    logger.info("✅ Calendar router loaded")
else:
    router_errors.append("calendar: Import failed with all patterns")
    logger.error("❌ Failed to load calendar router")

# Content Creation Router
content_creation = try_import_router("content_creation", import_patterns)
if content_creation:
    app.include_router(content_creation.router, prefix="/api/content", tags=["content"])
    routers_loaded.append("content_creation")
    logger.info("✅ Content Creation router loaded")
else:
    router_errors.append("content_creation: Import failed with all patterns")
    logger.error("❌ Failed to load content_creation router")

# Intelligence Router
intelligence = try_import_router("intelligence", import_patterns)
if intelligence:
    app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
    routers_loaded.append("intelligence")
    logger.info("✅ Intelligence router loaded")
else:
    router_errors.append("intelligence: Import failed with all patterns")
    logger.error("❌ Failed to load intelligence router")

# Media Router
media = try_import_router("media", import_patterns)
if media:
    app.include_router(media.router, prefix="/api/media", tags=["media"])
    routers_loaded.append("media")
    logger.info("✅ Media router loaded")
else:
    router_errors.append("media: Import failed with all patterns")
    logger.error("❌ Failed to load media router")

# Summary Router
summary = try_import_router("summary", import_patterns)
if summary:
    app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
    routers_loaded.append("summary")
    logger.info("✅ Summary router loaded")
else:
    router_errors.append("summary: Import failed with all patterns")
    logger.error("❌ Failed to load summary router")

# Fallback endpoints for critical functionality
if "executive" not in routers_loaded:
    @app.get("/api/executive/overview")
    def get_executive_overview_fallback():
        return {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": 0.0,
            "engagement_rate": 0.0,
            "status": "fallback_mode",
            "message": "Executive router not loaded - using fallback"
        }
    
    @app.get("/api/executive/summary")
    def get_executive_summary_fallback():
        return {
            "period": "Current Period",
            "highlights": [
                {"title": "Sales Performance", "value": "$0", "change": "0%"},
                {"title": "Order Volume", "value": "0", "change": "0%"},
                {"title": "Engagement Rate", "value": "0%", "change": "0%"}
            ],
            "status": "fallback_mode",
            "message": "Executive router not loaded - using fallback"
        }

if "competitive" not in routers_loaded:
    @app.get("/api/competitive/analysis")
    def get_competitive_analysis_fallback():
        return {
            "market_position": "Awaiting data upload",
            "brand_identity": "Authentic Streetwear Pioneer",
            "intelligence_score": 0,
            "status": "fallback_mode",
            "message": "Competitive router not loaded - using fallback"
        }

# Enhanced system endpoints
@app.get("/")
def read_root():
    return {
        "message": "Crooks Command Center API",
        "version": "2.0.0",
        "status": "running",
        "routers_loaded": routers_loaded,
        "router_errors": router_errors,
        "fallback_endpoints": len(router_errors) > 0,
        "directory_info": {
            "current_dir": os.getcwd(),
            "backend_exists": os.path.exists("backend"),
            "routers_exists": os.path.exists("routers"),
            "backend_routers_exists": os.path.exists("backend/routers")
        }
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "routers_active": len(routers_loaded),
        "routers_failed": len(router_errors),
        "fallback_mode": len(router_errors) > 0
    }

@app.get("/api/__debug")
def debug_info():
    """Debug endpoint to help diagnose import issues"""
    return {
        "current_directory": os.getcwd(),
        "directory_contents": os.listdir("."),
        "backend_exists": os.path.exists("backend"),
        "backend_contents": os.listdir("backend") if os.path.exists("backend") else None,
        "routers_exists": os.path.exists("routers"),
        "routers_contents": os.listdir("routers") if os.path.exists("routers") else None,
        "backend_routers_exists": os.path.exists("backend/routers"),
        "backend_routers_contents": os.listdir("backend/routers") if os.path.exists("backend/routers") else None,
        "python_path": os.environ.get("PYTHONPATH", "Not set"),
        "import_patterns_tried": import_patterns
    }

# Static file serving (unchanged)
static_dirs = [
    "frontend/out", "frontend/.next", "frontend/build", "frontend/dist",
    "out", ".next", "build", "dist"
]

static_dir = None
for dir_path in static_dirs:
    if os.path.exists(dir_path):
        static_dir = dir_path
        break

if static_dir:
    try:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"✅ Static files mounted from: {static_dir}")
    except Exception as e:
        logger.error(f"❌ Failed to mount static files: {e}")

# Frontend serving (unchanged)
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_paths = [
        "frontend/out/index.html", "frontend/.next/server/pages/index.html",
        "frontend/build/index.html", "frontend/dist/index.html",
        "out/index.html", ".next/server/pages/index.html",
        "build/index.html", "dist/index.html"
    ]
    
    for index_path in index_paths:
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    return {"error": "Frontend not found", "routers_loaded": routers_loaded}

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Crooks Command Center API starting up...")
    logger.info(f"📊 Loaded {len(routers_loaded)} routers successfully")
    if router_errors:
        logger.warning(f"⚠️ {len(router_errors)} routers failed to load - fallback endpoints active")
    logger.info("✅ Startup complete!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
