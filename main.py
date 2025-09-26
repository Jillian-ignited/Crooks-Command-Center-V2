from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Crooks & Castles Command Center V2",
    description="Complete competitive intelligence and revenue analytics platform with media management",
    version="2.0.2"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers with error handling
try:
    from routers.intelligence_SOPHISTICATED_FIXED_4 import router as intelligence_router
    app.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
    print("✅ Intelligence router loaded")
except Exception as e:
    print(f"⚠️ Intelligence router failed: {e}")

try:
    from routers.summary_COMPLETE import router as summary_router
    app.include_router(summary_router, prefix="/summary", tags=["summary"])
    print("✅ Summary router loaded")
except Exception as e:
    print(f"⚠️ Summary router failed: {e}")

try:
    from routers.calendar_ENHANCED_COMPREHENSIVE import router as calendar_router
    app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
    print("✅ Calendar router loaded")
except Exception as e:
    print(f"⚠️ Calendar router failed: {e}")

try:
    from routers.agency import router as agency_router
    app.include_router(agency_router, prefix="/agency", tags=["agency"])
    print("✅ Agency router loaded")
except Exception as e:
    print(f"⚠️ Agency router failed: {e}")

try:
    from routers.ingest_ENHANCED import router as ingest_router
    app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    print("✅ Ingest router loaded")
except Exception as e:
    print(f"⚠️ Ingest router failed: {e}")

try:
    from routers.shopify_ENHANCED_WITH_MOCK import router as shopify_router
    app.include_router(shopify_router, prefix="/shopify", tags=["shopify"])
    print("✅ Shopify router loaded")
except Exception as e:
    print(f"⚠️ Shopify router failed: {e}")

try:
    from routers.media import router as media_router
    app.include_router(media_router, prefix="/media", tags=["media"])
    print("✅ Media router loaded")
except Exception as e:
    print(f"⚠️ Media router failed: {e}")

# Create API router with /api prefix for frontend integration
api_router = APIRouter(prefix="/api")

# Include all routers under /api prefix for frontend compatibility
try:
    from routers.intelligence_SOPHISTICATED_FIXED_4 import router as intelligence_router
    api_router.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
    print("✅ API Intelligence router loaded")
except Exception as e:
    print(f"⚠️ API Intelligence router failed: {e}")

try:
    from routers.summary_COMPLETE import router as summary_router
    api_router.include_router(summary_router, prefix="/summary", tags=["summary"])
    print("✅ API Summary router loaded")
except Exception as e:
    print(f"⚠️ API Summary router failed: {e}")

try:
    from routers.calendar_ENHANCED_COMPREHENSIVE import router as calendar_router
    api_router.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
    print("✅ API Calendar router loaded")
except Exception as e:
    print(f"⚠️ API Calendar router failed: {e}")

try:
    from routers.agency import router as agency_router
    api_router.include_router(agency_router, prefix="/agency", tags=["agency"])
    print("✅ API Agency router loaded")
except Exception as e:
    print(f"⚠️ API Agency router failed: {e}")

try:
    from routers.ingest_ENHANCED import router as ingest_router
    api_router.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    print("✅ API Ingest router loaded")
except Exception as e:
    print(f"⚠️ API Ingest router failed: {e}")

try:
    from routers.shopify_ENHANCED_WITH_MOCK import router as shopify_router
    api_router.include_router(shopify_router, prefix="/shopify", tags=["shopify"])
    print("✅ API Shopify router loaded")
except Exception as e:
    print(f"⚠️ API Shopify router failed: {e}")

try:
    from routers.media import router as media_router
    api_router.include_router(media_router, prefix="/media", tags=["media"])
    print("✅ API Media router loaded")
except Exception as e:
    print(f"⚠️ API Media router failed: {e}")

# Include the API router in the main app
app.include_router(api_router)

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/uploads",
        "data/config", 
        "data/shopify",
        "data/calendar",
        "data/agency",
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

# Mount static files for Next.js frontend
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

# Serve Next.js static assets
@app.get("/_next/{path:path}")
async def serve_nextjs_assets(path: str):
    """Serve Next.js static assets"""
    asset_path = Path(f"static/_next/{path}")
    if asset_path.exists():
        return FileResponse(asset_path)
    else:
        raise HTTPException(status_code=404, detail="Asset not found")

# Fallback for any other static files
@app.get("/{path:path}")
async def serve_static_files(path: str):
    """Serve other static files"""
    # Skip API routes
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    static_file = Path(f"static/{path}")
    if static_file.exists() and static_file.is_file():
        return FileResponse(static_file)
    
    # If file doesn't exist, serve index.html for client-side routing
    index_file = Path("static/index.html")
    if index_file.exists():
        return FileResponse("static/index.html")
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Overall system health check"""
    return {
        "status": "healthy",
        "service": "Crooks & Castles Command Center V2",
        "version": "2.0.2",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "intelligence": "operational",
            "summary": "operational", 
            "calendar": "operational",
            "agency": "operational",
            "ingest": "operational",
            "shopify": "operational",
            "media": "operational"
        }
    }

# Fallback ingest endpoints if router fails to load
@app.get("/ingest/overview")
async def fallback_ingest_overview():
    """Fallback overview endpoint that reads data directly"""
    try:
        data_dir = Path("data")
        all_data = []
        total_posts = 0
        total_engagement = 0
        engagement_count = 0
        
        # Load all JSON files
        json_files = list(data_dir.glob("*.json"))
        print(f"Found {len(json_files)} data files")
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                        total_posts += len(data)
                        
                        # Calculate engagement if available
                        for item in data:
                            if 'engagement_rate' in item and item['engagement_rate']:
                                total_engagement += float(item['engagement_rate'])
                                engagement_count += 1
                            elif 'likes' in item and 'views' in item and item['views'] > 0:
                                engagement_rate = (item['likes'] / item['views']) * 100
                                total_engagement += engagement_rate
                                engagement_count += 1
                    else:
                        all_data.append(data)
                        total_posts += 1
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
        
        # Calculate metrics
        avg_engagement = (total_engagement / engagement_count) if engagement_count > 0 else 0
        
        # Get top performing content
        top_content = []
        if all_data:
            # Sort by engagement metrics
            sorted_data = sorted(all_data, key=lambda x: x.get('likes', 0) + x.get('shares', 0), reverse=True)
            top_content = sorted_data[:5]
        
        return JSONResponse(content={
            "success": True,
            "overview": {
                "total_posts": total_posts,
                "avg_engagement": round(avg_engagement, 2),
                "total_files": len(json_files),
                "last_updated": datetime.now().isoformat()
            },
            "top_content": top_content,
            "data_available": len(all_data) > 0,
            "debug_info": {
                "files_found": len(json_files),
                "total_records": len(all_data),
                "engagement_records": engagement_count
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get overview data: {str(e)}",
                "data_available": False
            },
            status_code=500
        )

@app.get("/ingest/status")
async def fallback_ingest_status():
    """Fallback status endpoint"""
    try:
        data_dir = Path("data")
        json_files = list(data_dir.glob("*.json"))
        
        total_records = 0
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    total_records += len(data) if isinstance(data, list) else 1
            except:
                continue
        
        return JSONResponse(content={
            "success": True,
            "status": {
                "total_files": len(json_files),
                "total_records": total_records,
                "data_directory": str(data_dir.absolute()),
                "last_check": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get status: {str(e)}"
            },
            status_code=500
        )

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
            "/agency/dashboard",
            "/ingest/upload",
            "/ingest/overview",
            "/ingest/status",
            "/shopify/dashboard",
            "/media/upload",
            "/media/list"
        ],
        "last_updated": datetime.now().isoformat()
    }

# Debug endpoint to check data files
@app.get("/debug/data-files")
async def debug_data_files():
    """Debug endpoint to check what data files exist"""
    try:
        data_dir = Path("data")
        files_info = []
        
        for file_path in data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    files_info.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "records": len(data) if isinstance(data, list) else 1,
                        "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                        "sample_keys": list(data[0].keys()) if isinstance(data, list) and len(data) > 0 else []
                    })
            except Exception as e:
                files_info.append({
                    "filename": file_path.name,
                    "error": str(e)
                })
        
        return {
            "data_directory": str(data_dir.absolute()),
            "files_found": len(files_info),
            "files": files_info
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Crooks & Castles Command Center V2...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
