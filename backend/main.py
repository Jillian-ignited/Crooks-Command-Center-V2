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

# Import routers with error handling
routers_loaded = []
router_errors = []

try:
    from routers import executive
    app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
    routers_loaded.append("executive")
    logger.info("✅ Executive router loaded")
except ImportError as e:
    router_errors.append(f"executive: {str(e)}")
    logger.error(f"❌ Failed to load executive router: {e}")

try:
    from routers import competitive
    app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])
    routers_loaded.append("competitive")
    logger.info("✅ Competitive router loaded")
except ImportError as e:
    router_errors.append(f"competitive: {str(e)}")
    logger.error(f"❌ Failed to load competitive router: {e}")

try:
    from routers import competitive_analysis
    app.include_router(competitive_analysis.router, prefix="/api/competitive-analysis", tags=["competitive_analysis"])
    routers_loaded.append("competitive_analysis")
    logger.info("✅ Competitive Analysis router loaded")
except ImportError as e:
    router_errors.append(f"competitive_analysis: {str(e)}")
    logger.error(f"❌ Failed to load competitive_analysis router: {e}")

try:
    from routers import shopify
    app.include_router(shopify.router, prefix="/api/shopify", tags=["shopify"])
    routers_loaded.append("shopify")
    logger.info("✅ Shopify router loaded")
except ImportError as e:
    router_errors.append(f"shopify: {str(e)}")
    logger.error(f"❌ Failed to load shopify router: {e}")

try:
    from routers import agency
    app.include_router(agency.router, prefix="/api/agency", tags=["agency"])
    routers_loaded.append("agency")
    logger.info("✅ Agency router loaded")
except ImportError as e:
    router_errors.append(f"agency: {str(e)}")
    logger.error(f"❌ Failed to load agency router: {e}")

try:
    from routers import calendar
    app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
    routers_loaded.append("calendar")
    logger.info("✅ Calendar router loaded")
except ImportError as e:
    router_errors.append(f"calendar: {str(e)}")
    logger.error(f"❌ Failed to load calendar router: {e}")

try:
    from routers import content_creation
    app.include_router(content_creation.router, prefix="/api/content", tags=["content"])
    routers_loaded.append("content_creation")
    logger.info("✅ Content Creation router loaded")
except ImportError as e:
    router_errors.append(f"content_creation: {str(e)}")
    logger.error(f"❌ Failed to load content_creation router: {e}")

try:
    from routers import intelligence
    app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
    routers_loaded.append("intelligence")
    logger.info("✅ Intelligence router loaded")
except ImportError as e:
    router_errors.append(f"intelligence: {str(e)}")
    logger.error(f"❌ Failed to load intelligence router: {e}")

try:
    from routers import media
    app.include_router(media.router, prefix="/api/media", tags=["media"])
    routers_loaded.append("media")
    logger.info("✅ Media router loaded")
except ImportError as e:
    router_errors.append(f"media: {str(e)}")
    logger.error(f"❌ Failed to load media router: {e}")

try:
    from routers import summary
    app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
    routers_loaded.append("summary")
    logger.info("✅ Summary router loaded")
except ImportError as e:
    router_errors.append(f"summary: {str(e)}")
    logger.error(f"❌ Failed to load summary router: {e}")

# Enhanced system endpoints
@app.get("/")
def read_root():
    return {
        "message": "Crooks Command Center API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Executive Dashboard",
            "Competitive Analysis", 
            "Content Planning",
            "Agency Management",
            "Cultural Calendar",
            "Intelligence Gathering",
            "Media Management",
            "Performance Analytics"
        ],
        "routers_loaded": routers_loaded,
        "router_errors": router_errors if router_errors else None
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "routers_active": len(routers_loaded),
        "routers_failed": len(router_errors),
        "uptime": "running"
    }

@app.get("/api/__whoami")
def whoami():
    return {
        "service": "Crooks Command Center",
        "purpose": "Authentic street culture marketing platform",
        "capabilities": [
            "Content planning and generation",
            "Competitive intelligence",
            "Agency contract fulfillment", 
            "Cultural calendar integration",
            "Performance optimization",
            "Brand compliance monitoring"
        ]
    }

@app.get("/api/__routes")
def list_routes():
    """List all available API routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and route.path.startswith('/api/'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else ["GET"]
            })
    
    return {
        "total_routes": len(routes),
        "routers_loaded": routers_loaded,
        "router_errors": router_errors,
        "routes": sorted(routes, key=lambda x: x['path'])
    }

@app.get("/api/__static_ping")
def static_ping():
    """Test static file serving capability"""
    static_dirs = [
        "frontend/out", "frontend/.next", "frontend/build", "frontend/dist",
        "out", ".next", "build", "dist"
    ]
    
    found_dirs = [d for d in static_dirs if os.path.exists(d)]
    
    return {
        "static_serving": "enabled" if found_dirs else "disabled",
        "available_directories": found_dirs,
        "checked_directories": static_dirs
    }

@app.get("/api/__static_debug")
def static_debug():
    """Debug static file configuration"""
    return {
        "current_directory": os.getcwd(),
        "directory_contents": os.listdir("."),
        "frontend_exists": os.path.exists("frontend"),
        "frontend_contents": os.listdir("frontend") if os.path.exists("frontend") else None
    }

@app.get("/api/__init_db")
def init_database():
    """Initialize database tables (placeholder)"""
    return {
        "status": "ready",
        "message": "Database initialization endpoint ready",
        "tables": [
            "agency_deliverables",
            "content_calendar", 
            "competitive_intelligence",
            "performance_metrics",
            "cultural_moments"
        ]
    }

# Enhanced static file serving
static_dirs = [
    "frontend/out",      # Next.js export
    "frontend/.next",    # Next.js build  
    "frontend/build",    # React build
    "frontend/dist",     # Vite build
    "out",              # Next.js export in root
    ".next",            # Next.js build in root
    "build",            # React build in root
    "dist"              # Vite build in root
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
else:
    logger.warning("⚠️ No static directory found for frontend files")

# Enhanced frontend serving with fallback
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Serve frontend files with intelligent fallback"""
    
    # Skip API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Try to find index.html in various locations
    index_paths = [
        "frontend/out/index.html",
        "frontend/.next/server/pages/index.html",
        "frontend/build/index.html", 
        "frontend/dist/index.html",
        "out/index.html",
        ".next/server/pages/index.html",
        "build/index.html",
        "dist/index.html",
        "frontend/index.html",
        "index.html"
    ]
    
    for index_path in index_paths:
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # Enhanced fallback with debugging info
    return {
        "error": "Frontend not configured",
        "message": "No frontend build found. Please build your Next.js/React app.",
        "checked_paths": index_paths,
        "current_directory": os.getcwd(),
        "available_files": [f for f in os.listdir(".") if not f.startswith(".")],
        "routers_loaded": routers_loaded,
        "suggestion": "Run 'npm run build' in your frontend directory"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Crooks Command Center API starting up...")
    logger.info(f"📊 Loaded {len(routers_loaded)} routers successfully")
    if router_errors:
        logger.warning(f"⚠️ {len(router_errors)} routers failed to load")
    logger.info("✅ Startup complete - Ready for authentic street culture marketing!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )
