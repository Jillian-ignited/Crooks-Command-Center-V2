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

# Import enhanced routers with error handling
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

# Enhanced routers
try:
    from routers.agency_REAL_TRACKING import router as agency_router
    app.include_router(agency_router, prefix="/agency", tags=["agency"])
    print("✅ Enhanced Agency router loaded")
except Exception as e:
    print(f"⚠️ Enhanced Agency router failed: {e}")

try:
    from routers.ingest_ENHANCED_MULTI_FORMAT import router as ingest_router
    app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    print("✅ Enhanced Ingest router loaded")
except Exception as e:
    print(f"⚠️ Enhanced Ingest router failed: {e}")

try:
    from routers.shopify import router as shopify_router
    app.include_router(shopify_router, prefix="/shopify", tags=["shopify"])
    print("✅ Shopify router loaded")
except Exception as e:
    print(f"⚠️ Shopify router failed: {e}")

try:
    from routers.content_creation import router as content_router
    app.include_router(content_router, prefix="/content", tags=["content"])
    print("✅ Content Creation router loaded")
except Exception as e:
    print(f"⚠️ Content Creation router failed: {e}")

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
        "data/content",
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
        "service": "Crooks & Castles Command Center V2 - Enhanced",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "intelligence": "operational",
            "summary": "operational", 
            "calendar": "operational",
            "agency": "enhanced - real tracking",
            "ingest": "enhanced - multi-format support",
            "shopify": "operational",
            "content": "new - content creation tools",
            "media": "operational"
        },
        "new_features": [
            "Multi-format data upload (JSON, JSONL, CSV, Excel)",
            "Real agency project tracking with deliverables",
            "Content creation and planning tools",
            "Enhanced Shopify report upload support",
            "Unified intelligence analysis across all data sources"
        ]
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
            "/agency/dashboard - ENHANCED",
            "/agency/projects - NEW",
            "/agency/time-tracking - NEW",
            "/ingest/upload - ENHANCED",
            "/ingest/overview",
            "/ingest/status",
            "/content/dashboard - NEW",
            "/content/create - NEW",
            "/content/ideas/generate - NEW",
            "/content/performance/analyze - NEW",
            "/shopify/dashboard",
            "/media/upload",
            "/media/list"
        ],
        "enhanced_features": {
            "data_ingestion": "Supports JSON, JSONL, CSV, Excel files",
            "agency_tracking": "Real project management with deliverables and time tracking",
            "content_creation": "Content planning, idea generation, and performance analysis",
            "unified_intelligence": "Analyzes social media + e-commerce data together"
        },
        "last_updated": datetime.now().isoformat()
    }

# Enhanced data overview endpoint
@app.get("/api/overview")
async def enhanced_overview():
    """Enhanced overview combining all data sources"""
    try:
        # Get data from all sources
        overview_data = {
            "data_sources": {
                "social_media": "Available via /ingest/overview",
                "ecommerce": "Available via Shopify report uploads",
                "agency_projects": "Available via /agency/dashboard",
                "content_pipeline": "Available via /content/dashboard"
            },
            "capabilities": {
                "competitive_intelligence": "Advanced sentiment analysis and trend tracking",
                "revenue_analytics": "Shopify data integration with social media insights",
                "project_management": "Real agency tracking with deliverables and timelines",
                "content_strategy": "Content creation tools with performance optimization"
            },
            "workflow": [
                "1. Upload social media data (JSON/JSONL) via Data Ingest",
                "2. Upload Shopify reports (CSV/Excel) via Data Ingest", 
                "3. Create and track agency projects via Agency Dashboard",
                "4. Plan and create content via Content Creation tools",
                "5. Get unified intelligence insights combining all data sources"
            ]
        }
        
        return JSONResponse(content={
            "success": True,
            "overview": overview_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get enhanced overview: {str(e)}"
            },
            status_code=500
        )

if __name__ == "__main__":
    print("🚀 Starting Crooks & Castles Command Center V2 - Enhanced Edition...")
    print("📊 New Features:")
    print("   • Multi-format data upload (JSON, JSONL, CSV, Excel)")
    print("   • Real agency project tracking")
    print("   • Content creation and planning tools")
    print("   • Enhanced Shopify report integration")
    print("   • Unified intelligence across all data sources")
    uvicorn.run(app, host="0.0.0.0", port=8000)
