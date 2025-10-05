from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from datetime import datetime

# Add the backend directory to Python path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

app = FastAPI(title="Crooks Command Center API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers with error handling
routers_loaded = {}

# Agency router
try:
    from routers.agency import router as agency_router
    app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
    routers_loaded["agency"] = True
    print("✅ Agency router loaded")
except Exception as e:
    print(f"❌ Agency router failed: {e}")
    routers_loaded["agency"] = False

# Calendar router
try:
    from routers.calendar import router as calendar_router
    app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
    routers_loaded["calendar"] = True
    print("✅ Calendar router loaded")
except Exception as e:
    print(f"❌ Calendar router failed: {e}")
    routers_loaded["calendar"] = False

# Competitive router
try:
    from routers.competitive import router as competitive_router
    app.include_router(competitive_router, prefix="/api/competitive", tags=["competitive"])
    routers_loaded["competitive"] = True
    print("✅ Competitive router loaded")
except Exception as e:
    print(f"❌ Competitive router failed: {e}")
    routers_loaded["competitive"] = False

# Competitive Analysis router
try:
    from routers.competitive_analysis import router as competitive_analysis_router
    app.include_router(competitive_analysis_router, prefix="/api/competitive-analysis", tags=["competitive-analysis"])
    routers_loaded["competitive_analysis"] = True
    print("✅ Competitive Analysis router loaded")
except Exception as e:
    print(f"❌ Competitive Analysis router failed: {e}")
    routers_loaded["competitive_analysis"] = False

# Content Creation router
try:
    from routers.content_creation import router as content_creation_router
    app.include_router(content_creation_router, prefix="/api/content", tags=["content"])
    routers_loaded["content_creation"] = True
    print("✅ Content Creation router loaded")
except Exception as e:
    print(f"❌ Content Creation router failed: {e}")
    routers_loaded["content_creation"] = False

# Executive router
try:
    from routers.executive import router as executive_router
    app.include_router(executive_router, prefix="/api/executive", tags=["executive"])
    routers_loaded["executive"] = True
    print("✅ Executive router loaded")
except Exception as e:
    print(f"❌ Executive router failed: {e}")
    routers_loaded["executive"] = False

# Ingest router
try:
    from routers.ingest import router as ingest_router
    app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"])
    routers_loaded["ingest"] = True
    print("✅ Ingest router loaded")
except Exception as e:
    print(f"❌ Ingest router failed: {e}")
    routers_loaded["ingest"] = False

# Intelligence router
try:
    from routers.intelligence import router as intelligence_router
    app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
    routers_loaded["intelligence"] = True
    print("✅ Intelligence router loaded")
except Exception as e:
    print(f"❌ Intelligence router failed: {e}")
    routers_loaded["intelligence"] = False

# Media router
try:
    from routers.media import router as media_router
    app.include_router(media_router, prefix="/api/media", tags=["media"])
    routers_loaded["media"] = True
    print("✅ Media router loaded")
except Exception as e:
    print(f"❌ Media router failed: {e}")
    routers_loaded["media"] = False

# Shopify router
try:
    from routers.shopify import router as shopify_router
    app.include_router(shopify_router, prefix="/api/shopify", tags=["shopify"])
    routers_loaded["shopify"] = True
    print("✅ Shopify router loaded")
except Exception as e:
    print(f"❌ Shopify router failed: {e}")
    routers_loaded["shopify"] = False

# Summary router
try:
    from routers.summary import router as summary_router
    app.include_router(summary_router, prefix="/api/summary", tags=["summary"])
    routers_loaded["summary"] = True
    print("✅ Summary router loaded")
except Exception as e:
    print(f"❌ Summary router failed: {e}")
    routers_loaded["summary"] = False

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "frontend_serving": "active",
        "api_endpoints": "active",
        "routers_loaded": routers_loaded,
        "python_path": sys.path[:3],  # Show first 3 entries for debugging
        "working_directory": os.getcwd(),
        "backend_directory": backend_dir
    }

# Try to mount static files from multiple possible locations
static_mounted = False
static_dirs_to_try = [
    "static/site",
    "backend/static/site",
    "frontend/out",
    "frontend/.next", 
    "frontend/build",
    "frontend/dist",
    "out",
    ".next",
    "build", 
    "dist",
    "public"
]

for static_dir in static_dirs_to_try:
    if os.path.exists(static_dir) and os.path.isdir(static_dir):
        try:
            # Mount the static files at root to serve Next.js assets correctly
            app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
            print(f"✅ Static files mounted from: {static_dir}")
            static_mounted = True
            break
        except Exception as e:
            print(f"❌ Failed to mount {static_dir}: {e}")
            continue

if not static_mounted:
    print("⚠️ No static directory found - frontend files may not be built")

# Serve frontend for all non-API routes
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Don't interfere with API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Try to find and serve index.html from various locations
    index_locations = [
        "static/site/index.html",
        "backend/static/site/index.html",
        "frontend/out/index.html",
        "frontend/.next/server/pages/index.html",
        "frontend/build/index.html", 
        "frontend/dist/index.html",
        "out/index.html",
        ".next/server/pages/index.html",
        "build/index.html",
        "dist/index.html",
        "public/index.html",
        "index.html"
    ]
    
    for index_path in index_locations:
        if os.path.exists(index_path):
            print(f"✅ Serving frontend from: {index_path}")
            return FileResponse(index_path)
    
    # If no frontend found, return helpful debug info
    return {
        "message": "Frontend not found - please build your React/Next.js app",
        "current_directory": os.getcwd(),
        "available_directories": [d for d in os.listdir(".") if os.path.isdir(d)],
        "checked_paths": index_locations,
        "api_status": "working",
        "suggestion": "Run 'npm run build' or 'npm run export' in your frontend directory"
    }

# Root endpoint that doesn't conflict with frontend
@app.get("/api/")
def api_root():
    available_endpoints = []
    
    if routers_loaded.get("agency"):
        available_endpoints.extend(["/api/agency/dashboard", "/api/agency/projects"])
    if routers_loaded.get("calendar"):
        available_endpoints.append("/api/calendar/events")
    if routers_loaded.get("competitive"):
        available_endpoints.append("/api/competitive/analysis")
    if routers_loaded.get("competitive_analysis"):
        available_endpoints.append("/api/competitive-analysis/comparison")
    if routers_loaded.get("content_creation"):
        available_endpoints.append("/api/content/briefs")
    if routers_loaded.get("executive"):
        available_endpoints.extend(["/api/executive/overview", "/api/executive/summary", "/api/executive/metrics"])
    if routers_loaded.get("ingest"):
        available_endpoints.append("/api/ingest/upload")
    if routers_loaded.get("intelligence"):
        available_endpoints.extend(["/api/intelligence/analysis", "/api/intelligence/upload", "/api/intelligence/summary"])
    if routers_loaded.get("media"):
        available_endpoints.append("/api/media/library")
    if routers_loaded.get("shopify"):
        available_endpoints.extend(["/api/shopify/dashboard", "/api/shopify/orders", "/api/shopify/analytics", "/api/shopify/upload"])
    if routers_loaded.get("summary"):
        available_endpoints.extend(["/api/summary/overview", "/api/summary/reports"])
    
    return {
        "message": "Crooks Command Center API",
        "version": "2.0.0",
        "status": "running",
        "frontend_serving": static_mounted,
        "routers_loaded": routers_loaded,
        "endpoints": available_endpoints,
        "debug_info": {
            "working_directory": os.getcwd(),
            "backend_directory": backend_dir,
            "python_path_entries": len(sys.path)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
