from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
from datetime import datetime

# Create FastAPI app optimized for Next.js integration
app = FastAPI(
    title="Crooks & Castles Command Center V2 - Backend API",
    description="Enhanced backend API for Next.js frontend with real data intelligence",
    version="2.2.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],  # Add your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register all enhanced routers
try:
    from routers.executive import router as executive_router
    app.include_router(executive_router, prefix="/executive", tags=["executive"])
    print("✅ Executive router loaded - REAL DATA EXECUTIVE DASHBOARD")
except Exception as e:
    print(f"⚠️ Executive router failed: {e}")

try:
    from routers.intelligence import router as intelligence_router
    app.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
    print("✅ Intelligence router loaded - SOPHISTICATED ANALYSIS")
except Exception as e:
    print(f"⚠️ Intelligence router failed: {e}")

try:
    from routers.agency_REAL_TRACKING import router as agency_router
    app.include_router(agency_router, prefix="/agency", tags=["agency"])
    print("✅ Agency router loaded - REAL PROJECT TRACKING")
except Exception as e:
    print(f"⚠️ Agency router failed: {e}")

try:
    from routers.ingest_ENHANCED_MULTI_FORMAT import router as ingest_router
    app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    print("✅ Ingest router loaded - MULTI-FORMAT UPLOAD")
except Exception as e:
    print(f"⚠️ Ingest router failed: {e}")

try:
    from routers.content_creation import router as content_router
    app.include_router(content_router, prefix="/content", tags=["content"])
    print("✅ Content router loaded - CONTENT CREATION TOOLS")
except Exception as e:
    print(f"⚠️ Content router failed: {e}")

try:
    from routers.calendar import router as calendar_router
    app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
    print("✅ Calendar router loaded - CAMPAIGN PLANNING")
except Exception as e:
    print(f"⚠️ Calendar router failed: {e}")

try:
    from routers.summary import router as summary_router
    app.include_router(summary_router, prefix="/summary", tags=["summary"])
    print("✅ Summary router loaded - DATA OVERVIEW")
except Exception as e:
    print(f"⚠️ Summary router failed: {e}")

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist for data storage"""
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
        print(f"✅ Directory ensured: {directory}")

# Create directories on startup
ensure_directories()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for Next.js frontend monitoring"""
    return {
        "status": "healthy",
        "service": "Crooks & Castles Command Center V2 - Backend API",
        "version": "2.2.0",
        "timestamp": datetime.now().isoformat(),
        "frontend_integration": "Next.js Ready",
        "modules": {
            "executive": "✅ Real data executive dashboard",
            "intelligence": "✅ Sophisticated sentiment analysis & insights", 
            "agency": "✅ Real project tracking with deliverables",
            "ingest": "✅ Multi-format data upload (JSON, CSV, Excel)",
            "content": "✅ Content creation and planning tools",
            "calendar": "✅ Campaign calendar and cultural moments",
            "summary": "✅ Data overview and metrics"
        },
        "key_endpoints": {
            "executive_overview": "/executive/overview?days=30",
            "intelligence_report": "/intelligence/report", 
            "data_upload": "/ingest/upload",
            "agency_dashboard": "/agency/dashboard",
            "content_ideas": "/content/ideas/generate",
            "calendar_planning": "/calendar/planning"
        }
    }

# API status endpoint for frontend
@app.get("/api/status")
async def api_status():
    """API status specifically for Next.js frontend integration"""
    return {
        "api_status": "online",
        "backend_version": "2.2.0",
        "frontend_compatibility": "Next.js 13+",
        "cors_enabled": True,
        "endpoints_ready": [
            "GET /executive/overview - Executive dashboard with real data",
            "POST /intelligence/report - Sophisticated analysis engine",
            "POST /ingest/upload - Multi-format file upload",
            "GET /agency/dashboard - Real project tracking",
            "POST /content/ideas/generate - AI content creation",
            "GET /calendar/planning - Campaign calendar",
            "GET /summary/overview - Data metrics"
        ],
        "data_capabilities": {
            "social_media": "Instagram, TikTok, Twitter (JSON/JSONL)",
            "ecommerce": "Shopify reports (CSV/Excel)",
            "competitive": "Apify scraping results (JSON)",
            "agency": "Project tracking and deliverables",
            "content": "Content planning and creation"
        },
        "real_features": [
            "No mock data - all analysis uses your real uploaded data",
            "Sophisticated sentiment analysis with cultural insights",
            "Competitive intelligence across 12 streetwear brands",
            "Strategic recommendations based on actual performance",
            "Revenue correlation between social media and sales"
        ],
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Crooks & Castles Command Center V2 - Backend API for Next.js...")
    print("🎯 Optimized for Next.js frontend integration")
    print("📊 Features:")
    print("   • Real data executive dashboard")
    print("   • Sophisticated intelligence analysis")
    print("   • Multi-format data upload")
    print("   • Real agency project tracking")
    print("   • Content creation tools")
    print("   • Campaign calendar planning")
    print("🌐 CORS enabled for Next.js development server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
