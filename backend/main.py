from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from datetime import datetime

# Import ALL routers
from routers.agency import router as agency_router
from routers.calendar import router as calendar_router
from routers.competitive import router as competitive_router
from routers.competitive_analysis import router as competitive_analysis_router
from routers.content_creation import router as content_creation_router
from routers.executive import router as executive_router
from routers.ingest import router as ingest_router
from routers.intelligence import router as intelligence_router
from routers.media import router as media_router
from routers.shopify import router as shopify_router
from routers.summary import router as summary_router

app = FastAPI(title="Crooks Command Center API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ALL routers
app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(competitive_router, prefix="/api/competitive", tags=["competitive"])
app.include_router(competitive_analysis_router, prefix="/api/competitive-analysis", tags=["competitive-analysis"])
app.include_router(content_creation_router, prefix="/api/content", tags=["content"])
app.include_router(executive_router, prefix="/api/executive", tags=["executive"])
app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"])
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(media_router, prefix="/api/media", tags=["media"])
app.include_router(shopify_router, prefix="/api/shopify", tags=["shopify"])
app.include_router(summary_router, prefix="/api/summary", tags=["summary"])

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "frontend_serving": "active",
        "api_endpoints": "active",
        "routers_loaded": [
            "agency", "calendar", "competitive", "competitive_analysis", 
            "content_creation", "executive", "ingest", "intelligence", 
            "media", "shopify", "summary"
        ]
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
    return {
        "message": "Crooks Command Center API",
        "version": "2.0.0",
        "status": "running",
        "frontend_serving": static_mounted,
        "routers_loaded": [
            "agency", "calendar", "competitive", "competitive_analysis", 
            "content_creation", "executive", "ingest", "intelligence", 
            "media", "shopify", "summary"
        ],
        "endpoints": [
            # Agency endpoints
            "/api/agency/dashboard",
            "/api/agency/projects",
            
            # Calendar endpoints  
            "/api/calendar/events",
            
            # Competitive endpoints
            "/api/competitive/analysis",
            
            # Competitive Analysis endpoints
            "/api/competitive-analysis/comparison",
            
            # Content Creation endpoints
            "/api/content/briefs",
            "/api/content/create",
            
            # Executive endpoints
            "/api/executive/overview",
            "/api/executive/summary", 
            "/api/executive/metrics",
            
            # Ingest endpoints
            "/api/ingest/upload",
            
            # Intelligence endpoints
            "/api/intelligence/analysis",
            "/api/intelligence/reports",
            "/api/intelligence/upload",
            
            # Media endpoints
            "/api/media/library",
            "/api/media/upload",
            
            # Shopify endpoints
            "/api/shopify/dashboard",
            "/api/shopify/orders",
            "/api/shopify/analytics",
            "/api/shopify/upload",
            
            # Summary endpoints
            "/api/summary/overview",
            "/api/summary/reports"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
