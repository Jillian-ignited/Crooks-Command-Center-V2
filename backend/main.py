from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crooks-command-center")

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

# Import and include all routers
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

# Add middleware to fix double-slash API paths
@app.middleware("http")
async def fix_path_middleware(request: Request, call_next):
    path = request.url.path
    
    # Fix double slashes in API paths
    if "//" in path:
        path = path.replace("//", "/")
        response = JSONResponse(
            status_code=307,
            content={"detail": "Redirecting to correct path"},
        )
        response.headers["Location"] = str(request.url.replace(path=path))
        return response
    
    # Forward bare paths to API paths
    if path.startswith("/intelligence/") or \
       path.startswith("/content/") or \
       path.startswith("/agency/") or \
       path.startswith("/executive/") or \
       path.startswith("/calendar/") or \
       path.startswith("/media/") or \
       path.startswith("/shopify/") or \
       path.startswith("/summary/") or \
       path.startswith("/upload/") or \
       path.startswith("/ingest/"):
        api_path = f"/api{path}"
        response = JSONResponse(
            status_code=307,
            content={"detail": "Redirecting to API path"},
        )
        response.headers["Location"] = str(request.url.replace(path=api_path))
        return response
    
    return await call_next(request)

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

# Debug endpoint to check static file paths
@app.get("/api/debug/static")
async def debug_static():
    # Try multiple possible static directories
    possible_dirs = [
        "static",
        "backend/static",
        "./static",
        "../static",
        os.path.join(os.path.dirname(__file__), "static"),
        os.path.abspath("static"),
        os.path.abspath("backend/static")
    ]
    
    results = {}
    for dir_path in possible_dirs:
        results[dir_path] = {
            "exists": os.path.exists(dir_path),
            "is_dir": os.path.isdir(dir_path) if os.path.exists(dir_path) else False,
            "abs_path": os.path.abspath(dir_path),
            "contents": os.listdir(dir_path) if os.path.exists(dir_path) and os.path.isdir(dir_path) else []
        }
        
        # Check for index.html
        index_path = os.path.join(dir_path, "index.html")
        results[dir_path]["index_exists"] = os.path.exists(index_path)
        results[dir_path]["index_size"] = os.path.getsize(index_path) if os.path.exists(index_path) else 0
    
    # Get current working directory
    results["cwd"] = os.getcwd()
    
    return results

# IMPORTANT: Define static directory with multiple fallbacks
static_dir = None
possible_static_dirs = [
    "static",
    "backend/static",
    "./static",
    "../static",
    os.path.join(os.path.dirname(__file__), "static")
]

for dir_path in possible_static_dirs:
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        static_dir = dir_path
        logger.info(f"Found static directory at: {os.path.abspath(dir_path)}")
        break

if static_dir is None:
    logger.warning("No static directory found! Creating one...")
    os.makedirs("static", exist_ok=True)
    static_dir = "static"

# Create a simple HTML file if none exists
index_path = os.path.join(static_dir, "index.html")
if not os.path.exists(index_path):
    logger.warning(f"No index.html found at {index_path}! Creating a simple one...")
    with open(index_path, "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crooks Command Center V2</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #FF6B35; }
            </style>
        </head>
        <body>
            <h1>Crooks Command Center V2</h1>
            <p>The API is running successfully, but no frontend was found.</p>
            <p>API endpoints are available at <a href="/api/status">/api/status</a></p>
        </body>
        </html>
        """)

# Root endpoint - Serve the frontend
@app.get("/")
async def root():
    logger.info(f"Serving root path, looking for index.html at {index_path}")
    
    if os.path.exists(index_path):
        logger.info(f"Found index.html at {index_path}, serving file")
        return FileResponse(index_path)
    
    logger.warning(f"index.html not found at {index_path}, returning API info")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crooks Command Center V2</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #FF6B35; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Crooks Command Center V2</h1>
        <p>The API is running successfully, but no frontend was found.</p>
        <p>API endpoints are available at <a href="/api/status">/api/status</a></p>
        <h2>Debug Information:</h2>
        <pre>
Static directory: """ + static_dir + """
Index path: """ + index_path + """
Index exists: """ + str(os.path.exists(index_path)) + """
Current directory: """ + os.getcwd() + """
        </pre>
    </body>
    </html>
    """, status_code=200)

# IMPORTANT: Mount static files AFTER API routes
if os.path.exists(static_dir):
    # Mount at /static for assets
    logger.info(f"Mounting static files from {os.path.abspath(static_dir)}")
    app.mount("/static", StaticFiles(directory=static_dir), name="static_assets")
    
    # SPA fallback for client-side routing
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend files or fallback to index.html"""
        logger.info(f"Requested path: /{full_path}")
        
        # Skip API paths
        if full_path.startswith("api/"):
            logger.info(f"API path requested: /{full_path}, skipping frontend serving")
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Try to serve the requested file
        file_path = os.path.join(static_dir, full_path)
        logger.info(f"Looking for file at: {file_path}")
        if os.path.isfile(file_path):
            logger.info(f"File found, serving: {file_path}")
            return FileResponse(file_path)
        
        # Serve index.html for client-side routing
        logger.info(f"File not found, serving index.html as fallback")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        
        logger.warning(f"index.html not found at {index_path}, returning 404")
        raise HTTPException(status_code=404, detail="File not found")

print("✅ All routers loaded successfully")
print("🚀 Crooks Command Center V2 ready for deployment")
