# /backend/main.py - Complete Enhanced FastAPI Application
# Crooks & Castles Command Center V2.1 - Real Data Intelligence Platform

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
import os

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="Crooks & Castles Command Center V2.1 - Enhanced Intelligence Platform",
    description="Complete competitive intelligence and revenue analytics platform with real data processing, integrated Shopify analytics, and 12-brand competitive analysis",
    version="2.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler for better error reporting
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# Enhanced router loading function with detailed error reporting
def load_router_safely(router_path: str, prefix: str, tags: list, description: str):
    """Safely load a router with detailed error reporting"""
    try:
        module = __import__(f"routers.{router_path}", fromlist=[router_path])
        router = getattr(module, 'router')
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info(f"✅ {description}")
        return True
    except ImportError as e:
        logger.error(f"❌ {description} - Import Error: {e}")
        return False
    except AttributeError as e:
        logger.error(f"❌ {description} - Router not found: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - Unexpected error: {e}")
        return False

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "message": "Crooks & Castles Command Center V2.1 - Enhanced Intelligence Platform",
        "features": [
            "Real Data Competitive Analysis",
            "Integrated Shopify Analytics", 
            "Executive Intelligence Dashboard",
            "12-Brand Competitive Tracking",
            "Trending Topics Analysis",
            "Platform Performance Analytics"
        ]
    }

# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get detailed API status and module information"""
    
    # Check data directories
    data_dirs = {
        "shopify": Path("data/shopify"),
        "competitive": Path("data/competitive"),
        "uploads": Path("data/uploads")
    }
    
    dir_status = {}
    for name, path in data_dirs.items():
        dir_status[name] = {
            "exists": path.exists(),
            "files": len(list(path.glob("*"))) if path.exists() else 0,
            "path": str(path)
        }
    
    return {
        "api_version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "data_directories": dir_status,
        "available_endpoints": {
            "executive": "/executive/overview",
            "competitive": "/intelligence/competitive-analysis", 
            "trending": "/intelligence/trending-topics",
            "platform": "/intelligence/platform-performance",
            "health": "/health",
            "docs": "/api/docs"
        },
        "system_status": "operational"
    }

# PRIORITY #1: Executive Overview Integration - REAL DATA
logger.info("🚀 Loading Executive Overview Integration...")
executive_loaded = load_router_safely(
    "executive", 
    "/executive", 
    ["executive"], 
    "Executive Overview router loaded - INTEGRATED INTELLIGENCE - Shopify + Competitive + Social Analysis"
)

if not executive_loaded:
    logger.warning("⚠️ Executive router not loaded. Create /routers/executive.py with integrated intelligence router.")
    
    @app.get("/executive/overview")
    async def executive_fallback():
        return {
            "error": "Executive module not loaded",
            "message": "Create /routers/executive.py with integrated intelligence router.",
            "required_file": "/routers/executive.py",
            "status": "module_missing"
        }

# PRIORITY #2: Intelligence Analysis - REAL DATA COMPETITIVE ANALYSIS
logger.info("🧠 Loading Intelligence Analysis...")
intelligence_loaded = load_router_safely(
    "intelligence", 
    "/intelligence", 
    ["intelligence"], 
    "Intelligence router loaded successfully - Real data competitive analysis - NO MOCK DATA"
)

if not intelligence_loaded:
    logger.warning("⚠️ Intelligence router not loaded. Create /routers/intelligence.py with competitive analysis.")
    
    @app.get("/intelligence/competitive-analysis")
    async def intelligence_fallback():
        return {
            "error": "Intelligence module not loaded",
            "message": "Create /routers/intelligence.py with competitive analysis router.",
            "required_file": "/routers/intelligence.py",
            "status": "module_missing"
        }

# Enhanced content creation router
logger.info("📝 Loading Enhanced Content Creation...")
content_loaded = load_router_safely(
    "content_creation", 
    "/content", 
    ["content"], 
    "Enhanced Content Creation router loaded - AI-powered content generation with competitor insights"
)

# Enhanced Shopify integration
logger.info("🛒 Loading Enhanced Shopify Integration...")
shopify_loaded = load_router_safely(
    "shopify", 
    "/shopify", 
    ["shopify"], 
    "Enhanced Shopify router loaded - Real revenue data integration"
)

# Agency tracking with real data
logger.info("📊 Loading Enhanced Agency Tracking...")
agency_loaded = load_router_safely(
    "agency_REAL_TRACKING", 
    "/agency", 
    ["agency"], 
    "Enhanced Agency router loaded - Real performance tracking"
)

# Enhanced data ingestion
logger.info("📥 Loading Enhanced Data Ingestion...")
ingest_loaded = load_router_safely(
    "ingest_ENHANCED_MULTI_FORMAT", 
    "/ingest", 
    ["ingest"], 
    "Enhanced Multi-Format Ingest router loaded - CSV, JSON, Excel support"
)

# Summary and reporting
logger.info("📋 Loading Summary & Reporting...")
summary_loaded = load_router_safely(
    "summary", 
    "/summary", 
    ["summary"], 
    "Summary router loaded - Automated reporting and insights"
)

# Calendar integration
logger.info("📅 Loading Calendar Integration...")
calendar_loaded = load_router_safely(
    "calendar", 
    "/calendar", 
    ["calendar"], 
    "Calendar router loaded - Content scheduling and planning"
)

# Media management
logger.info("🎬 Loading Media Management...")
media_loaded = load_router_safely(
    "media", 
    "/media", 
    ["media"], 
    "Media router loaded - Asset management and processing"
)

# Serve Next.js frontend
logger.info("🌐 Setting up frontend integration...")

# Check if Next.js build exists
FRONTEND_BUILD_DIR = Path("../frontend/.next")
FRONTEND_OUT_DIR = Path("../frontend/out")

if FRONTEND_OUT_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_OUT_DIR)), name="static")
    logger.info("✅ Next.js static files mounted from /out directory")
elif FRONTEND_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR)), name="static")
    logger.info("✅ Next.js build files mounted from /.next directory")
else:
    logger.warning("⚠️ Next.js build not found. Run 'npm run build' in frontend directory.")

# Catch-all route for Next.js routing
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve Next.js frontend for all unmatched routes"""
    
    # API routes should not be served by frontend
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Try to serve from Next.js build
    if FRONTEND_OUT_DIR.exists():
        index_file = FRONTEND_OUT_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    elif FRONTEND_BUILD_DIR.exists():
        index_file = FRONTEND_BUILD_DIR / "index.html"  
        if index_file.exists():
            return FileResponse(str(index_file))
    
    # Fallback message
    return JSONResponse({
        "message": "Crooks & Castles Command Center V2.1",
        "frontend_status": "Build Next.js frontend with 'npm run build'",
        "api_docs": "/api/docs",
        "health_check": "/health",
        "executive_dashboard": "/executive/overview",
        "competitive_analysis": "/intelligence/competitive-analysis"
    })

# Startup message
@app.on_event("startup")
async def startup_event():
    """Enhanced startup message with module status"""
    
    logger.info("=" * 70)
    logger.info("🚀 CROOKS & CASTLES COMMAND CENTER V2.1 - ENHANCED INTELLIGENCE PLATFORM")
    logger.info("=" * 70)
    
    # Module status report
    modules = {
        "Executive Overview": executive_loaded,
        "Intelligence Analysis": intelligence_loaded,
        "Content Creation": content_loaded,
        "Shopify Integration": shopify_loaded,
        "Agency Tracking": agency_loaded,
        "Data Ingestion": ingest_loaded,
        "Summary & Reporting": summary_loaded,
        "Calendar Integration": calendar_loaded,
        "Media Management": media_loaded
    }
    
    loaded_count = sum(modules.values())
    total_count = len(modules)
    
    logger.info(f"📊 MODULE STATUS: {loaded_count}/{total_count} modules loaded successfully")
    logger.info("")
    
    for module, status in modules.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {module}")
    
    logger.info("")
    logger.info("🔗 KEY ENDPOINTS:")
    logger.info("   • Executive Dashboard: http://localhost:8000/executive/overview")
    logger.info("   • Competitive Analysis: http://localhost:8000/intelligence/competitive-analysis")
    logger.info("   • API Documentation: http://localhost:8000/api/docs")
    logger.info("   • Health Check: http://localhost:8000/health")
    logger.info("   • System Status: http://localhost:8000/api/status")
    logger.info("")
    
    if loaded_count < total_count:
        logger.warning("⚠️  Some modules failed to load. Check file paths and dependencies.")
        logger.info("💡 Missing routers? Create them in /routers/ directory.")
    
    logger.info("🎯 DATA SOURCES:")
    logger.info("   • Shopify Data: /data/shopify/ (CSV, JSON)")
    logger.info("   • Competitive Data: /data/competitive/ (CSV, JSON)")  
    logger.info("   • Upload Directory: /data/uploads/ (Any format)")
    logger.info("")
    logger.info("🎉 READY FOR COMPETITIVE INTELLIGENCE & REVENUE ANALYTICS!")
    logger.info("=" * 70)

if __name__ == "__main__":
    # Ensure data directories exist
    data_dirs = ["data/shopify", "data/competitive", "data/uploads"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
