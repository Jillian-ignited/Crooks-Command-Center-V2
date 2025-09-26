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
    title="Crooks & Castles Command Center V2 - Enhanced",
    description="Complete competitive intelligence and revenue analytics platform with enhanced data ingestion, real agency tracking, and content creation tools",
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

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Import routers with enhanced error handling and fallback
def load_router_safely(module_path, router_name, prefix, tags):
    """Safely load router with detailed error logging"""
    try:
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info(f"✅ {prefix} router loaded successfully")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ {prefix} router module not found: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {prefix} router failed to load: {e}")
        return False

# Track loaded modules
loaded_modules = {}

# Core routers (with fallback endpoints)
loaded_modules['intelligence'] = load_router_safely("routers.intelligence", "router", "/intelligence", ["intelligence"])
loaded_modules['summary'] = load_router_safely("routers.summary", "router", "/summary", ["summary"])
loaded_modules['calendar'] = load_router_safely("routers.calendar", "router", "/calendar", ["calendar"])

# Enhanced routers
loaded_modules['agency'] = load_router_safely("routers.agency_REAL_TRACKING", "router", "/agency", ["agency"])
loaded_modules['ingest'] = load_router_safely("routers.ingest_ENHANCED_MULTI_FORMAT", "router", "/ingest", ["ingest"])
loaded_modules['shopify'] = load_router_safely("routers.shopify", "router", "/shopify", ["shopify"])
loaded_modules['content'] = load_router_safely("routers.content_creation", "router", "/content", ["content"])
loaded_modules['media'] = load_router_safely("routers.media", "router", "/media", ["media"])

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/uploads",
        "data/config", 
        "data/shopify",
        "data/calendar",
        "data/agency",
        "data/content",
        "media/images",
        "media/videos",
        "media/audio",
        "media/thumbnails",
        "static",
        "build"  # For Next.js build output
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directory ensured: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {e}")

# Create directories on startup
ensure_directories()

# Mount static files with error handling
try:
    # Try to mount Next.js build output first
    if Path("build").exists():
        app.mount("/static", StaticFiles(directory="build"), name="static")
        logger.info("✅ Mounted Next.js build directory")
    elif Path("static").exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Mounted static directory")
    else:
        logger.warning("⚠️ No static directory found")
except Exception as e:
    logger.error(f"❌ Failed to mount static files: {e}")

# Root endpoint with enhanced error handling
@app.get("/")
async def read_root():
    """Serve the main dashboard interface with fallback options"""
    try:
        # Try Next.js build output first
        build_file = Path("build/index.html")
        if build_file.exists():
            return FileResponse("build/index.html")
        
        # Try static fallback
        static_file = Path("static/index.html")
        if static_file.exists():
            return FileResponse("static/index.html")
        
        # Return a basic HTML page if no files found
        return JSONResponse(content={
            "message": "Crooks & Castles Command Center V2 - Enhanced",
            "status": "API Online",
            "frontend": "Not built - run 'npm run build' to build Next.js frontend",
            "available_endpoints": ["/health", "/api/status", "/api/overview"],
            "loaded_modules": loaded_modules
        })
        
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve dashboard: {str(e)}")

# Health check endpoint with detailed module status
@app.get("/health")
async def health_check():
    """Enhanced system health check with module status"""
    try:
        module_status = {}
        for module, loaded in loaded_modules.items():
            module_status[module] = "operational" if loaded else "failed to load"
        
        return {
            "status": "healthy",
            "service": "Crooks & Castles Command Center V2 - Enhanced",
            "version": "2.1.0",
            "timestamp": datetime.now().isoformat(),
            "modules": module_status,
            "directories_status": {
                "data": Path("data").exists(),
                "media": Path("media").exists(), 
                "static": Path("static").exists(),
                "build": Path("build").exists()
            },
            "new_features": [
                "Multi-format data upload (JSON, JSONL, CSV, Excel)",
                "Real agency project tracking with deliverables",
                "Content creation and planning tools",
                "Enhanced Shopify report upload support",
                "Unified intelligence analysis across all data sources",
                "Improved error handling and logging"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

# API status endpoint with fallback endpoint information
@app.get("/api/status")
async def api_status():
    """API status for frontend monitoring with fallback information"""
    try:
        available_endpoints = []
        
        # Add endpoints based on loaded modules
        if loaded_modules.get('intelligence'):
            available_endpoints.extend(["/intelligence/report", "/intelligence/upload"])
        else:
            available_endpoints.append("/intelligence/* - MODULE NOT LOADED")
            
        if loaded_modules.get('summary'):
            available_endpoints.append("/summary/overview")
        else:
            available_endpoints.append("/summary/* - MODULE NOT LOADED")
            
        if loaded_modules.get('calendar'):
            available_endpoints.append("/calendar/planning")
        else:
            available_endpoints.append("/calendar/* - MODULE NOT LOADED")
            
        if loaded_modules.get('agency'):
            available_endpoints.extend([
                "/agency/dashboard - ENHANCED",
                "/agency/projects - NEW", 
                "/agency/time-tracking - NEW"
            ])
        else:
            available_endpoints.append("/agency/* - MODULE NOT LOADED")
            
        if loaded_modules.get('ingest'):
            available_endpoints.extend([
                "/ingest/upload - ENHANCED",
                "/ingest/overview",
                "/ingest/status"
            ])
        else:
            available_endpoints.append("/ingest/* - MODULE NOT LOADED")
            
        if loaded_modules.get('content'):
            available_endpoints.extend([
                "/content/dashboard - NEW",
                "/content/create - NEW",
                "/content/ideas/generate - NEW",
                "/content/performance/analyze - NEW"
            ])
        else:
            available_endpoints.append("/content/* - MODULE NOT LOADED")
            
        if loaded_modules.get('shopify'):
            available_endpoints.append("/shopify/dashboard")
        else:
            available_endpoints.append("/shopify/* - MODULE NOT LOADED")
            
        if loaded_modules.get('media'):
            available_endpoints.extend(["/media/upload", "/media/list"])
        else:
            available_endpoints.append("/media/* - MODULE NOT LOADED")

        return {
            "api_status": "online",
            "endpoints_available": available_endpoints,
            "loaded_modules": loaded_modules,
            "fallback_endpoints": ["/health", "/api/status", "/api/overview"],
            "enhanced_features": {
                "data_ingestion": "Supports JSON, JSONL, CSV, Excel files" if loaded_modules.get('ingest') else "NOT AVAILABLE",
                "agency_tracking": "Real project management with deliverables and time tracking" if loaded_modules.get('agency') else "NOT AVAILABLE",
                "content_creation": "Content planning, idea generation, and performance analysis" if loaded_modules.get('content') else "NOT AVAILABLE",
                "unified_intelligence": "Analyzes social media + e-commerce data together" if loaded_modules.get('intelligence') else "NOT AVAILABLE"
            },
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"api_status": "error", "error": str(e)}
        )

# Enhanced data overview endpoint with error handling
@app.get("/api/overview")
async def enhanced_overview():
    """Enhanced overview combining all data sources with fallback data"""
    try:
        overview_data = {
            "data_sources": {
                "social_media": "Available via /ingest/overview" if loaded_modules.get('ingest') else "Module not loaded",
                "ecommerce": "Available via Shopify report uploads" if loaded_modules.get('shopify') else "Module not loaded",
                "agency_projects": "Available via /agency/dashboard" if loaded_modules.get('agency') else "Module not loaded",
                "content_pipeline": "Available via /content/dashboard" if loaded_modules.get('content') else "Module not loaded"
            },
            "capabilities": {
                "competitive_intelligence": "Advanced sentiment analysis and trend tracking" if loaded_modules.get('intelligence') else "NOT AVAILABLE",
                "revenue_analytics": "Shopify data integration with social media insights" if loaded_modules.get('shopify') else "NOT AVAILABLE",
                "project_management": "Real agency tracking with deliverables and timelines" if loaded_modules.get('agency') else "NOT AVAILABLE",
                "content_strategy": "Content creation tools with performance optimization" if loaded_modules.get('content') else "NOT AVAILABLE"
            },
            "workflow": [
                "1. Build frontend: npm run build",
                "2. Upload social media data (JSON/JSONL) via Data Ingest" + (" - AVAILABLE" if loaded_modules.get('ingest') else " - NOT AVAILABLE"),
                "3. Upload Shopify reports (CSV/Excel) via Data Ingest" + (" - AVAILABLE" if loaded_modules.get('shopify') else " - NOT AVAILABLE"), 
                "4. Create and track agency projects via Agency Dashboard" + (" - AVAILABLE" if loaded_modules.get('agency') else " - NOT AVAILABLE"),
                "5. Plan and create content via Content Creation tools" + (" - AVAILABLE" if loaded_modules.get('content') else " - NOT AVAILABLE"),
                "6. Get unified intelligence insights combining all data sources" + (" - AVAILABLE" if loaded_modules.get('intelligence') else " - NOT AVAILABLE")
            ],
            "missing_modules": [module for module, loaded in loaded_modules.items() if not loaded],
            "system_status": {
                "total_modules": len(loaded_modules),
                "loaded_modules": sum(loaded_modules.values()),
                "failed_modules": len(loaded_modules) - sum(loaded_modules.values())
            }
        }
        
        return JSONResponse(content={
            "success": True,
            "overview": overview_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Enhanced overview failed: {e}")
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get enhanced overview: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )

# Fallback endpoints for missing routers
@app.get("/intelligence/report")
async def intelligence_fallback():
    if not loaded_modules.get('intelligence'):
        raise HTTPException(status_code=503, detail="Intelligence module not loaded. Check router file exists.")
    
@app.get("/summary/overview") 
async def summary_fallback():
    if not loaded_modules.get('summary'):
        raise HTTPException(status_code=503, detail="Summary module not loaded. Check router file exists.")

@app.get("/calendar/planning")
async def calendar_fallback():
    if not loaded_modules.get('calendar'):
        raise HTTPException(status_code=503, detail="Calendar module not loaded. Check router file exists.")

@app.get("/agency/dashboard")
async def agency_fallback():
    if not loaded_modules.get('agency'):
        raise HTTPException(status_code=503, detail="Agency module not loaded. Check router file exists.")

@app.get("/ingest/upload")
async def ingest_fallback():
    if not loaded_modules.get('ingest'):
        raise HTTPException(status_code=503, detail="Ingest module not loaded. Check router file exists.")

@app.get("/content/dashboard")
async def content_fallback():
    if not loaded_modules.get('content'):
        raise HTTPException(status_code=503, detail="Content module not loaded. Check router file exists.")

@app.get("/shopify/dashboard") 
async def shopify_fallback():
    if not loaded_modules.get('shopify'):
        raise HTTPException(status_code=503, detail="Shopify module not loaded. Check router file exists.")

@app.get("/media/list")
async def media_fallback():
    if not loaded_modules.get('media'):
        raise HTTPException(status_code=503, detail="Media module not loaded. Check router file exists.")

if __name__ == "__main__":
    print("🚀 Starting Crooks & Castles Command Center V2 - Enhanced Edition...")
    print("📊 New Features:")
    print("   • Enhanced error handling and logging")
    print("   • Fallback endpoints for missing modules")
    print("   • Multi-format data upload (JSON, JSONL, CSV, Excel)")
    print("   • Real agency project tracking")
    print("   • Content creation and planning tools")
    print("   • Enhanced Shopify report integration")
    print("   • Unified intelligence across all data sources")
    print("\n⚠️  SETUP REQUIREMENTS:")
    print("   1. Create router files in /routers/ directory")
    print("   2. Run 'npm run build' to build Next.js frontend")
    print("   3. Ensure all data directories exist")
    uvicorn.run(app, host="0.0.0.0", port=8000)
