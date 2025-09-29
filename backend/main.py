from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import glob
import importlib.util
import sys

# Create FastAPI app
app = FastAPI(title="Crooks Command Center V2", version="2.0.4")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from backend.routers.intelligence import router as intelligence_router
from backend.routers.content_creation import router as content_router
from backend.routers.agency import router as agency_router
from backend.routers.executive import router as executive_router
from backend.routers.calendar import router as calendar_router
from backend.routers.media import router as media_router
from backend.routers.shopify import router as shopify_router
from backend.routers.summary import router as summary_router
from backend.routers.ingest_ENHANCED_MULTI_FORMAT import router as ingest_router
from backend.routers.upload_sidecar import router as upload_router

# Mount routers
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
app.include_router(executive_router, prefix="/api/executive", tags=["executive"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(media_router, prefix="/api/media", tags=["media"])
app.include_router(shopify_router, prefix="/api/shopify", tags=["shopify"])
app.include_router(summary_router, prefix="/api/summary", tags=["summary"])
app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"])
app.include_router(upload_router, prefix="/api/upload", tags=["upload"])

# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get API status"""
    return {
        "message": "Crooks Command Center V2 API",
        "status": "running",
        "version": "2.0.4",
        "api_docs": "/docs",
        "health_check": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# API routes endpoint
@app.get("/api/routes")
async def api_routes():
    """Get available API routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and "api" in route.path:
            routes.append({
                "path": route.path,
                "methods": route.methods,
                "name": route.name
            })
    return {"routes": routes}

# Middleware for XHR requests to /path to be forwarded to /api/path
@app.middleware("http")
async def add_api_prefix(request: Request, call_next):
    path = request.url.path
    
    # Skip if already has /api prefix or accessing static files
    if path.startswith("/api/") or path.startswith("/static/") or path == "/":
        response = await call_next(request)
        return response
    
    # Check if this is an XHR request (not a page navigation)
    is_xhr = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    accepts_html = "text/html" in request.headers.get("Accept", "")
    
    # If it's an XHR request or doesn't accept HTML, try forwarding to /api/path
    if is_xhr or not accepts_html:
        # Forward to /api/path
        api_path = f"/api{path}"
        request.scope["path"] = api_path
        response = await call_next(request)
        
        # If not found, try the original path
        if response.status_code == 404:
            request.scope["path"] = path
            response = await call_next(request)
        
        return response
    
    # For HTML requests, continue normally (SPA will handle routing)
    response = await call_next(request)
    return response

# Mount static files AFTER API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static_assets")

# Serve index.html for SPA routing
@app.get("/")
@app.get("/{full_path:path}")
async def serve_spa(full_path: str = ""):
    """Serve SPA for client-side routing"""
    # Skip API paths
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Try to serve the requested file
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Serve index.html for client-side routing
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="File not found")

print("✅ All routers loaded successfully")
print("🚀 Crooks Command Center V2 ready for deployment")
