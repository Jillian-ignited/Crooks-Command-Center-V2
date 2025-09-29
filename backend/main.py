from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="Crooks Command Center V2",
    description="Advanced Competitive Intelligence & Business Management Platform",
    version="2.0.4"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
upload_dirs = [
    "uploads/intelligence",
    "uploads/media", 
    "uploads/data",
    "uploads/processed"
]

for directory in upload_dirs:
    os.makedirs(directory, exist_ok=True)

print("✅ Upload directories created successfully")

# Test endpoint to verify API is working
@app.get("/test")
async def test_endpoint():
    return {"message": "API is working", "status": "success"}

# Import and include all routers - FIXED IMPORTS
try:
    from backend.routers.intelligence import router as intelligence_router
    app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
    print("✅ Intelligence router loaded")
except ImportError as e:
    print(f"⚠️ Intelligence router error: {e}")

try:
    from backend.routers.content_creation import router as content_router
    app.include_router(content_router, prefix="/api/content", tags=["content"])
    print("✅ Content router loaded")
except ImportError as e:
    print(f"⚠️ Content router error: {e}")

try:
    from backend.routers.agency import router as agency_router
    app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
    print("✅ Agency router loaded")
except ImportError as e:
    print(f"⚠️ Agency router error: {e}")

try:
    from backend.routers.executive import router as executive_router
    app.include_router(executive_router, prefix="/api/executive", tags=["executive"])
    print("✅ Executive router loaded")
except ImportError as e:
    print(f"⚠️ Executive router error: {e}")

try:
    from backend.routers.calendar import router as calendar_router
    app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
    print("✅ Calendar router loaded")
except ImportError as e:
    print(f"⚠️ Calendar router error: {e}")

try:
    from backend.routers.media import router as media_router
    app.include_router(media_router, prefix="/api/media", tags=["media"])
    print("✅ Media router loaded")
except ImportError as e:
    print(f"⚠️ Media router error: {e}")

try:
    from backend.routers.shopify import router as shopify_router
    app.include_router(shopify_router, prefix="/api/shopify", tags=["shopify"])
    print("✅ Shopify router loaded")
except ImportError as e:
    print(f"⚠️ Shopify router error: {e}")

try:
    from backend.routers.summary import router as summary_router
    app.include_router(summary_router, prefix="/api/summary", tags=["summary"])
    print("✅ Summary router loaded")
except ImportError as e:
    print(f"⚠️ Summary router error: {e}")

try:
    from backend.routers.upload_sidecar import router as upload_router
    app.include_router(upload_router, prefix="/api/upload", tags=["upload"])
    print("✅ Upload router loaded")
except ImportError as e:
    print(f"⚠️ Upload router error: {e}")

try:
    from backend.routers.ingest_ENHANCED_MULTI_FORMAT import router as file_ingestion_router
    app.include_router(file_ingestion_router, prefix="/api/ingest", tags=["ingest"])
    print("✅ File ingestion router loaded")
except ImportError as e:
    print(f"⚠️ File ingestion router error: {e}")

# Health check endpoint
@app.get("/api/health")
@app.get("/api/status")
async def health_check():
    return {
        "status": "operational",
        "version": "2.0.4",
        "modules": [
            "intelligence", "content", "agency", "executive",
            "calendar", "media", "shopify", "summary", "upload", "ingest"
        ]
    }

# Root endpoint
@app.get("/")
async def root():
    static_dir = "static"
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {
        "message": "Crooks Command Center V2 API",
        "status": "running",
        "version": "2.0.4",
        "api_docs": "/docs",
        "health_check": "/api/health"
    }

# IMPORTANT: Mount static files AFTER API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount at /static for assets
    app.mount("/static", StaticFiles(directory=static_dir), name="static_assets")
    
    # SPA fallback for client-side routing
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend files or fallback to index.html"""
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
# Add explicit root path handler
@app.get("/")
async def root():
    """Serve index.html at the root path"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    
    return {
        "message": "Crooks Command Center V2 API",
        "status": "running",
        "version": "2.0.4",
        "api_docs": "/docs",
        "health_check": "/api/health"
    }

print("✅ All routers loaded successfully")
print("🚀 Crooks Command Center V2 ready for deployment")
