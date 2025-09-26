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

# Enhanced router loading function with detailed logging
def load_router_safely(module_path, router_name, prefix, tags, description=""):
    """Safely load router with detailed error logging and fallback handling"""
    try:
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info(f"✅ {prefix} router loaded successfully - {description}")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ {prefix} router module not found: {module_path} - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {prefix} router failed to load: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

# Track loaded modules for health checks
loaded_modules = {}

# Core routers with enhanced error handling
logger.info("Loading core intelligence routers...")

loaded_modules['intelligence'] = load_router_safely(
    "routers.intelligence", "router", "/intelligence", ["intelligence"],
    "Real data competitive analysis - NO MOCK DATA"
)

loaded_modules['summary'] = load_router_safely(
    "routers.summary", "router", "/summary", ["summary"],
    "Executive summary generation"
)

loaded_modules['calendar'] = load_router_safely(
    "routers.calendar", "router", "/calendar", ["calendar"],
    "Cultural calendar and trend tracking"
)

# Enhanced routers with real data processing
logger.info("Loading enhanced routers...")

loaded_modules['agency'] = load_router_safely(
    "routers.agency_REAL_TRACKING", "router", "/agency", ["agency"],
    "Real agency project tracking with deliverables"
)

loaded_modules['ingest'] = load_router_safely(
    "routers.ingest_ENHANCED_MULTI_FORMAT", "router", "/ingest", ["ingest"],
    "Multi-format data upload (JSON, JSONL, CSV, Excel)"
)

loaded_modules['shopify'] = load_router_safely(
    "routers.shopify", "router", "/shopify", ["shopify"],
    "Shopify sales and revenue analytics"
)

loaded_modules['content'] = load_router_safely(
    "routers.content_creation", "router", "/content", ["content"],
    "Content creation and planning tools"
)

loaded_modules['media'] = load_router_safely(
    "routers.media", "router", "/media", ["media"],
    "Media file management and processing"
)

# PRIORITY #1: Executive Overview Integration - Real Data Intelligence
logger.info("Loading executive overview integration...")

loaded_modules['executive'] = load_router_safely(
    "routers.executive", "router", "/executive", ["executive"],
    "INTEGRATED INTELLIGENCE - Shopify + Competitive + Social Analysis"
)

# Enhanced directory management
def ensure_directories():
    """Ensure all required directories exist with proper permissions"""
    directories = [
        # Core data directories
        "data/uploads",
        "data/config", 
        "data/shopify",
        "data/calendar",
        "data/agency",
        "data/content",
        "data/competitive",  # For Apify scraping results
        
        # Media directories
        "media/images",
        "media/videos", 
        "media/audio",
        "media/thumbnails",
        
        # Static and build directories
        "static",
        "build"
    ]
    
    created_dirs = []
    failed_dirs = []
    
    for directory in directories:
        try:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(directory)
            logger.info(f"✅ Directory ensured: {directory}")
        except Exception as e:
            failed_dirs.append(directory)
            logger.error(f"❌ Failed to create directory {directory}: {e}")
    
    return {"created": created_dirs, "failed": failed_dirs}

# Create directories on startup
logger.info("Setting up directory structure...")
directory_status = ensure_directories()

# Enhanced static file serving with multiple fallback options
try:
    # Priority 1: Try Next.js build output
    if Path("build").exists() and any(Path("build").iterdir()):
        app.mount("/static", StaticFiles(directory="build"), name="static")
        logger.info("✅ Mounted Next.js build directory")
        static_source = "next_build"
    # Priority 2: Try static directory
    elif Path("static").exists() and any(Path("static").iterdir()):
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Mounted static directory")
        static_source = "static_dir"
    else:
        logger.warning("⚠️ No static directory found - frontend may not load")
        static_source = "none"
except Exception as e:
    logger.error(f"❌ Failed to mount static files: {e}")
    static_source = "failed"

# Enhanced root endpoint with intelligent fallback handling
@app.get("/")
async def read_root():
    """Serve the main dashboard interface with intelligent fallback options"""
    try:
        # Try Next.js build output first
        build_file = Path("build/index.html")
        if build_file.exists():
            logger.info("Serving from Next.js build output")
            return FileResponse("build/index.html")
        
        # Try static fallback
        static_file = Path("static/index.html")
        if static_file.exists():
            logger.info("Serving from static directory")
            return FileResponse("static/index.html")
        
        # Return API information if no frontend files found
        logger.warning("No frontend files found - serving API information")
        return JSONResponse(content={
            "service": "Crooks & Castles Command Center V2.1",
            "status": "API Online - Frontend Build Required",
            "message": "Run 'npm run build' in frontend directory to build the dashboard",
            "api_documentation": "/api/docs",
            "available_endpoints": {
                "health_check": "/health",
                "api_status": "/api/status", 
                "executive_overview": "/executive/overview",
                "intelligence_analysis": "/intelligence/report",
                "data_upload": "/ingest/upload"
            },
            "loaded_modules": loaded_modules,
            "setup_instructions": [
                "1. cd frontend && npm run build",
                "2. Copy build output to backend/static/",
                "3. Restart FastAPI server",
                "4. Upload data files via API endpoints"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve dashboard: {str(e)}")

# Enhanced health check with detailed system status
@app.get("/health")
async def health_check():
    """Comprehensive system health check with module and directory status"""
    try:
        # Module status analysis
        module_status = {}
        total_modules = len(loaded_modules)
        operational_modules = 0
        
        for module, loaded in loaded_modules.items():
            if loaded:
                module_status[module] = "operational"
                operational_modules += 1
            else:
                module_status[module] = "failed to load"
        
        # System health calculation
        health_percentage = (operational_modules / max(total_modules, 1)) * 100
        overall_status = "healthy" if health_percentage >= 70 else "degraded" if health_percentage >= 50 else "critical"
        
        # Directory status
        directory_health = {
            "data_directories": Path("data").exists(),
            "media_directories": Path("media").exists(), 
            "static_files": static_source != "none",
            "upload_directory": Path("data/uploads").exists()
        }
        
        return {
            "status": overall_status,
            "health_percentage": round(health_percentage, 1),
            "service": "Crooks & Castles Command Center V2.1 - Enhanced Intelligence Platform",
            "version": "2.1.0",
            "timestamp": datetime.now().isoformat(),
            "modules": module_status,
            "module_summary": {
                "total": total_modules,
                "operational": operational_modules,
                "failed": total_modules - operational_modules
            },
            "directories": directory_health,
            "static_source": static_source,
            "capabilities": {
                "real_data_analysis": loaded_modules.get('intelligence', False),
                "executive_overview": loaded_modules.get('executive', False),
                "shopify_integration": loaded_modules.get('shopify', False),
                "competitive_intelligence": loaded_modules.get('intelligence', False),
                "multi_format_upload": loaded_modules.get('ingest', False)
            },
            "new_features": [
                "Real competitive analysis across 12 brands (NO MOCK DATA)",
                "Integrated Shopify + Social + Competitive intelligence",
                "Multi-format data upload (JSON, JSONL, CSV, Excel)",
                "Real agency project tracking with deliverables",
                "Content creation and planning tools",
                "Enhanced trending topics from real social data"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
        )

# Enhanced API status endpoint with comprehensive module information
@app.get("/api/status")
async def api_status():
    """Detailed API status for frontend monitoring with module-specific information"""
    try:
        available_endpoints = []
        module_endpoints = {}
        
        # Intelligence endpoints
        if loaded_modules.get('intelligence'):
            intelligence_endpoints = [
                "/intelligence/report - Real competitive analysis",
                "/intelligence/upload - Data file upload",
                "/intelligence/uploads - List uploaded files",
                "/intelligence/status - Module status"
            ]
            available_endpoints.extend(intelligence_endpoints)
            module_endpoints['intelligence'] = intelligence_endpoints
        else:
            available_endpoints.append("/intelligence/* - MODULE NOT LOADED")
            
        # Executive overview endpoints  
        if loaded_modules.get('executive'):
            executive_endpoints = [
                "/executive/overview - Integrated intelligence dashboard",
                "/executive/data-sources - Data source status",
                "/executive/shopify/upload - Shopify data upload",
                "/executive/competitive/upload - Competitive data upload"
            ]
            available_endpoints.extend(executive_endpoints)
            module_endpoints['executive'] = executive_endpoints
        else:
            available_endpoints.append("/executive/* - MODULE NOT LOADED")
            
        # Other module endpoints
        module_mapping = {
            'summary': ["/summary/overview - Executive summary generation"],
            'calendar': ["/calendar/planning - Cultural calendar"],
            'agency': ["/agency/dashboard - ENHANCED", "/agency/projects - NEW", "/agency/time-tracking - NEW"],
            'ingest': ["/ingest/upload - ENHANCED", "/ingest/overview", "/ingest/status"],
            'content': ["/content/dashboard - NEW", "/content/create - NEW", "/content/ideas/generate - NEW"],
            'shopify': ["/shopify/dashboard - Revenue analytics"],
            'media': ["/media/upload", "/media/list"]
        }
        
        for module, endpoints in module_mapping.items():
            if loaded_modules.get(module):
                available_endpoints.extend(endpoints)
                module_endpoints[module] = endpoints
            else:
                available_endpoints.append(f"/{module}/* - MODULE NOT LOADED")

        return {
            "api_status": "online",
            "endpoints_available": available_endpoints,
            "module_endpoints": module_endpoints,
            "loaded_modules": loaded_modules,
            "core_endpoints": ["/health", "/api/status", "/api/overview"],
            "enhanced_features": {
                "real_data_processing": "All analysis uses actual uploaded data - NO MOCK DATA" if loaded_modules.get('intelligence') else "NOT AVAILABLE",
                "integrated_intelligence": "Shopify + Competitive + Social analysis combined" if loaded_modules.get('executive') else "NOT AVAILABLE",
                "multi_format_data_ingestion": "Supports JSON, JSONL, CSV, Excel files" if loaded_modules.get('ingest') else "NOT AVAILABLE",
                "competitive_analysis": "Real 12-brand competitive intelligence" if loaded_modules.get('intelligence') else "NOT AVAILABLE",
                "revenue_analytics": "Shopify sales data integration" if loaded_modules.get('shopify') else "NOT AVAILABLE"
            },
            "data_confidence": {
                "revenue_analysis": "High" if loaded_modules.get('shopify') else "Requires Shopify data",
                "competitive_intelligence": "High" if loaded_modules.get('intelligence') else "Requires uploaded data",
                "trending_analysis": "Medium" if loaded_modules.get('intelligence') else "Requires social media data"
            },
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"api_status": "error", "error": str(e)}
        )

# Enhanced data overview endpoint
@app.get("/api/overview")
async def enhanced_overview():
    """Enhanced overview combining all data sources with real-time status"""
    try:
        overview_data = {
            "platform_overview": {
                "name": "Crooks & Castles Command Center V2.1",
                "description": "Real data competitive intelligence and revenue analytics platform",
                "core_capabilities": [
                    "12-brand competitive analysis using real scraped data",
                    "Shopify revenue intelligence and trend analysis", 
                    "Social media performance correlation with sales data",
                    "Multi-format data ingestion and processing",
                    "Real-time trending topics and sentiment analysis"
                ]
            },
            "data_sources": {
                "social_media": f"Available via /ingest/overview - {loaded_modules.get('ingest', 'NOT LOADED')}",
                "ecommerce": f"Available via Shopify integration - {loaded_modules.get('shopify', 'NOT LOADED')}",
                "competitive_intelligence": f"12-brand analysis via /intelligence - {loaded_modules.get('intelligence', 'NOT LOADED')}",
                "agency_projects": f"Available via /agency/dashboard - {loaded_modules.get('agency', 'NOT LOADED')}",
                "content_pipeline": f"Available via /content/dashboard - {loaded_modules.get('content', 'NOT LOADED')}"
            },
            "key_differentiators": {
                "no_mock_data": "All analysis uses real uploaded data - no fake metrics or placeholders",
                "integrated_intelligence": "Combines Shopify sales + competitive analysis + social media performance",
                "real_competitive_analysis": "Actual market position vs 11 named competitors", 
                "actionable_insights": "Data-driven recommendations with specific implementation steps",
                "trend_analysis": "Real trending topics extracted from actual social media content"
            },
            "workflow": [
                "1. Upload competitive intelligence data (Apify scraping results for 12 brands)",
                "2. Upload Shopify sales reports (CSV/Excel format)", 
                "3. Upload social media performance data (JSON/JSONL/CSV)",
                "4. Access Executive Overview for integrated analysis and strategic recommendations",
                "5. Use Intelligence Analysis for detailed competitive insights",
                "6. Monitor trending topics and market position changes"
            ],
            "module_status": loaded_modules,
            "system_health": {
                "operational_modules": sum(loaded_modules.values()),
                "total_modules": len(loaded_modules),
                "health_percentage": round((sum(loaded_modules.values()) / len(loaded_modules)) * 100, 1)
            }
        }
        
        return JSONResponse(content={
            "success": True,
            "overview": overview_data,
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0"
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

# Fallback endpoints for missing routers with helpful error messages
@app.get("/intelligence/report")
async def intelligence_fallback():
    if not loaded_modules.get('intelligence'):
        raise HTTPException(
            status_code=503, 
            detail="Intelligence module not loaded. Create /routers/intelligence.py with real data processing router."
        )

@app.get("/executive/overview") 
async def executive_fallback():
    if not loaded_modules.get('executive'):
        raise HTTPException(
            status_code=503, 
            detail="Executive module not loaded. Create /routers/executive.py with integrated intelligence router."
        )

@app.get("/summary/overview")
async def summary_fallback():
    if not loaded_modules.get('summary'):
        raise HTTPException(
            status_code=503, 
            detail="Summary module not loaded. Check router file exists."
        )

@app.get("/calendar/planning")
async def calendar_fallback():
    if not loaded_modules.get('calendar'):
        raise HTTPException(
            status_code=503, 
            detail="Calendar module not loaded. Check router file exists."
        )

@app.get("/agency/dashboard")
async def agency_fallback():
    if not loaded_modules.get('agency'):
        raise HTTPException(
            status_code=503, 
            detail="Agency module not loaded. Check router file exists."
        )

@app.get("/ingest/upload")
async def ingest_fallback():
    if not loaded_modules.get('ingest'):
        raise HTTPException(
            status_code=503, 
            detail="Ingest module not loaded. Check router file exists."
        )

@app.get("/content/dashboard")
async def content_fallback():
    if not loaded_modules.get('content'):
        raise HTTPException(
            status_code=503, 
            detail="Content module not loaded. Check router file exists."
        )

@app.get("/shopify/dashboard") 
async def shopify_fallback():
    if not loaded_modules.get('shopify'):
        raise HTTPException(
            status_code=503, 
            detail="Shopify module not loaded. Check router file exists."
        )

@app.get("/media/list")
async def media_fallback():
    if not loaded_modules.get('media'):
        raise HTTPException(
            status_code=503, 
            detail="Media module not loaded. Check router file exists."
        )

# Startup event for system initialization
@app.on_event("startup")
async def startup_event():
    logger.info("=== CROOKS & CASTLES COMMAND CENTER V2.1 STARTUP ===")
    logger.info(f"Loaded modules: {sum(loaded_modules.values())}/{len(loaded_modules)}")
    logger.info(f"Directory status: {len(directory_status['created'])} created, {len(directory_status['failed'])} failed")
    logger.info(f"Static files: {static_source}")
    logger.info("=== STARTUP COMPLETE ===")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Starting Crooks & Castles Command Center V2.1 - Enhanced Edition")
    print("="*80)
    print("\n📊 Enhanced Features:")
    print("   • Real competitive analysis across 12 brands (NO MOCK DATA)")
    print("   • Integrated Shopify + Social + Competitive intelligence")
    print("   • Multi-format data upload (JSON, JSONL, CSV, Excel)")
    print("   • Real agency project tracking with deliverables")
    print("   • Content creation and planning tools")
    print("   • Enhanced trending topics from actual social media data")
    print("   • Executive overview dashboard with actionable insights")
    
    print("\n⚙️  System Requirements:")
    print("   1. Upload competitive intelligence data (12 brands)")
    print("   2. Upload Shopify sales reports for revenue analysis")
    print("   3. Upload social media data for trend analysis")
    print("   4. Build frontend: cd frontend && npm run build")
    
    print("\n🔗 Access Points:")
    print("   • Dashboard: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/api/docs") 
    print("   • Executive Overview: http://localhost:8000/executive/overview")
    print("   • Health Check: http://localhost:8000/health")
    
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=False  # Set to True for development
    )
