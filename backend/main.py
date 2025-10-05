import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

app = FastAPI(title="Crooks Command Center API", version="2.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all routers
routers_loaded = {}

try:
    from routers.agency import router as agency_router
    app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
    routers_loaded["agency"] = True
    print("✅ Agency router loaded")
except Exception as e:
    routers_loaded["agency"] = False
    print(f"❌ Agency router failed: {e}")

try:
    from routers.calendar import router as calendar_router
    app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
    routers_loaded["calendar"] = True
    print("✅ Calendar router loaded")
except Exception as e:
    routers_loaded["calendar"] = False
    print(f"❌ Calendar router failed: {e}")

try:
    from routers.competitive import router as competitive_router
    app.include_router(competitive_router, prefix="/api/competitive", tags=["competitive"])
    routers_loaded["competitive"] = True
    print("✅ Competitive router loaded")
except Exception as e:
    routers_loaded["competitive"] = False
    print(f"❌ Competitive router failed: {e}")

try:
    from routers.competitive_analysis import router as competitive_analysis_router
    app.include_router(competitive_analysis_router, prefix="/api/competitive-analysis", tags=["competitive-analysis"])
    routers_loaded["competitive_analysis"] = True
    print("✅ Competitive Analysis router loaded")
except Exception as e:
    routers_loaded["competitive_analysis"] = False
    print(f"❌ Competitive Analysis router failed: {e}")

try:
    from routers.content_creation import router as content_creation_router
    app.include_router(content_creation_router, prefix="/api/content", tags=["content"])
    routers_loaded["content_creation"] = True
    print("✅ Content Creation router loaded")
except Exception as e:
    routers_loaded["content_creation"] = False
    print(f"❌ Content Creation router failed: {e}")

try:
    from routers.executive import router as executive_router
    app.include_router(executive_router, prefix="/api/executive", tags=["executive"])
    routers_loaded["executive"] = True
    print("✅ Executive router loaded")
except Exception as e:
    routers_loaded["executive"] = False
    print(f"❌ Executive router failed: {e}")

try:
    from routers.ingest import router as ingest_router
    app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"])
    routers_loaded["ingest"] = True
    print("✅ Ingest router loaded")
except Exception as e:
    routers_loaded["ingest"] = False
    print(f"❌ Ingest router failed: {e}")

try:
    from routers.intelligence import router as intelligence_router
    app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
    routers_loaded["intelligence"] = True
    print("✅ Intelligence router loaded")
except Exception as e:
    routers_loaded["intelligence"] = False
    print(f"❌ Intelligence router failed: {e}")

try:
    from routers.media import router as media_router
    app.include_router(media_router, prefix="/api/media", tags=["media"])
    routers_loaded["media"] = True
    print("✅ Media router loaded")
except Exception as e:
    routers_loaded["media"] = False
    print(f"❌ Media router failed: {e}")

try:
    from routers.shopify import router as shopify_router
    app.include_router(shopify_router, prefix="/api/shopify", tags=["shopify"])
    routers_loaded["shopify"] = True
    print("✅ Shopify router loaded")
except Exception as e:
    routers_loaded["shopify"] = False
    print(f"❌ Shopify router failed: {e}")

try:
    from routers.summary import router as summary_router
    app.include_router(summary_router, prefix="/api/summary", tags=["summary"])
    routers_loaded["summary"] = True
    print("✅ Summary router loaded")
except Exception as e:
    routers_loaded["summary"] = False
    print(f"❌ Summary router failed: {e}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "frontend_serving": "active",
        "api_endpoints": "active",
        "routers_loaded": routers_loaded,
        "database_migrations": "intelligence_files table updated"
    }

# API root endpoint
@app.get("/api/")
async def api_root():
    available_endpoints = []
    if routers_loaded.get("agency"): available_endpoints.extend(["/api/agency/dashboard", "/api/agency/projects"])
    if routers_loaded.get("calendar"): available_endpoints.extend(["/api/calendar/events"])
    if routers_loaded.get("competitive"): available_endpoints.extend(["/api/competitive/analysis"])
    if routers_loaded.get("competitive_analysis"): available_endpoints.extend(["/api/competitive-analysis/comparison"])
    if routers_loaded.get("content_creation"): available_endpoints.extend(["/api/content/briefs", "/api/content/create"])
    if routers_loaded.get("executive"): available_endpoints.extend(["/api/executive/overview", "/api/executive/summary", "/api/executive/metrics"])
    if routers_loaded.get("ingest"): available_endpoints.extend(["/api/ingest/upload", "/api/ingest/process", "/api/ingest/status"])
    if routers_loaded.get("intelligence"): available_endpoints.extend(["/api/intelligence/upload", "/api/intelligence/summary", "/api/intelligence/analysis", "/api/intelligence/reports"])
    if routers_loaded.get("media"): available_endpoints.extend(["/api/media/library", "/api/media/upload"])
    if routers_loaded.get("shopify"): available_endpoints.extend(["/api/shopify/dashboard", "/api/shopify/orders", "/api/shopify/analytics"])
    if routers_loaded.get("summary"): available_endpoints.extend(["/api/summary/overview", "/api/summary/reports"])
    
    return {
        "message": "Crooks Command Center API v2.1.0",
        "available_endpoints": available_endpoints,
        "health_check": "/api/health"
    }

# Find and mount static files
static_mounted = False
static_dirs_to_try = [
    "static/site",
    "backend/static/site", 
    "frontend/out"
]

for static_dir in static_dirs_to_try:
    if os.path.exists(static_dir) and os.path.isdir(static_dir):
        try:
            # Mount static files for assets like CSS, JS, images
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            app.mount("/_next", StaticFiles(directory=os.path.join(static_dir, "_next")), name="next_assets")
            print(f"✅ Static files mounted from: {static_dir}")
            static_mounted = True
            static_directory = static_dir
            break
        except Exception as e:
            print(f"❌ Failed to mount {static_dir}: {e}")
            continue

if not static_mounted:
    print("⚠️ No static directory found - frontend files may not be built")
    static_directory = None

# Serve specific HTML pages
@app.get("/shopify")
async def serve_shopify():
    if static_directory and os.path.exists(os.path.join(static_directory, "shopify.html")):
        return FileResponse(os.path.join(static_directory, "shopify.html"))
    raise HTTPException(status_code=404, detail="Shopify page not found")

@app.get("/content")
async def serve_content():
    if static_directory and os.path.exists(os.path.join(static_directory, "content.html")):
        return FileResponse(os.path.join(static_directory, "content.html"))
    raise HTTPException(status_code=404, detail="Content page not found")

@app.get("/media")
async def serve_media():
    if static_directory and os.path.exists(os.path.join(static_directory, "media.html")):
        return FileResponse(os.path.join(static_directory, "media.html"))
    raise HTTPException(status_code=404, detail="Media page not found")

@app.get("/ingest")
async def serve_ingest():
    if static_directory and os.path.exists(os.path.join(static_directory, "ingest.html")):
        return FileResponse(os.path.join(static_directory, "ingest.html"))
    raise HTTPException(status_code=404, detail="Ingest page not found")

@app.get("/competitive")
async def serve_competitive():
    if static_directory and os.path.exists(os.path.join(static_directory, "competitive.html")):
        return FileResponse(os.path.join(static_directory, "competitive.html"))
    raise HTTPException(status_code=404, detail="Competitive page not found")

@app.get("/agency")
async def serve_agency():
    if static_directory and os.path.exists(os.path.join(static_directory, "agency.html")):
        return FileResponse(os.path.join(static_directory, "agency.html"))
    raise HTTPException(status_code=404, detail="Agency page not found")

@app.get("/calendar")
async def serve_calendar():
    if static_directory and os.path.exists(os.path.join(static_directory, "calendar.html")):
        return FileResponse(os.path.join(static_directory, "calendar.html"))
    raise HTTPException(status_code=404, detail="Calendar page not found")

@app.get("/intelligence")
async def serve_intelligence():
    if static_directory and os.path.exists(os.path.join(static_directory, "intelligence.html")):
        return FileResponse(os.path.join(static_directory, "intelligence.html"))
    raise HTTPException(status_code=404, detail="Intelligence page not found")

@app.get("/summary")
async def serve_summary():
    if static_directory and os.path.exists(os.path.join(static_directory, "summary.html")):
        return FileResponse(os.path.join(static_directory, "summary.html"))
    raise HTTPException(status_code=404, detail="Summary page not found")

@app.get("/executive")
async def serve_executive():
    if static_directory and os.path.exists(os.path.join(static_directory, "executive.html")):
        return FileResponse(os.path.join(static_directory, "executive.html"))
    raise HTTPException(status_code=404, detail="Executive page not found")

@app.get("/upload")
async def serve_upload():
    if static_directory and os.path.exists(os.path.join(static_directory, "upload.html")):
        return FileResponse(os.path.join(static_directory, "upload.html"))
    raise HTTPException(status_code=404, detail="Upload page not found")

# Serve index.html for root and any other unmatched routes (SPA fallback)
@app.get("/")
async def serve_index():
    if static_directory and os.path.exists(os.path.join(static_directory, "index.html")):
        return FileResponse(os.path.join(static_directory, "index.html"))
    raise HTTPException(status_code=404, detail="Frontend not found")

# Catch-all for any other routes - serve index.html (SPA behavior)
@app.get("/{full_path:path}")
async def serve_spa_fallback(full_path: str):
    # Don't interfere with API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # For any other route, serve index.html (SPA behavior)
    if static_directory and os.path.exists(os.path.join(static_directory, "index.html")):
        return FileResponse(os.path.join(static_directory, "index.html"))
    
    raise HTTPException(status_code=404, detail="Page not found")
