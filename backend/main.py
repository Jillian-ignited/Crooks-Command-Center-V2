from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn

# Import all your routers
from routers.executive import router as executive_router
from routers.intelligence import router as intelligence_router
from routers.agency import router as agency_router
from routers.ingest import router as ingest_router
from routers.content_creation import router as content_router
from routers.calendar import router as calendar_router
from routers.summary import router as summary_router

# Create FastAPI app
app = FastAPI(
    title="Crooks & Castles Command Center V2 - Backend API",
    description="Enhanced backend API for Next.js frontend with real data intelligence",
    version="2.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with /api prefix
app.include_router(executive_router, prefix="/api/executive", tags=["executive"])
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(summary_router, prefix="/api/summary", tags=["summary"])

# Health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Crooks & Castles Command Center V2 is running"}

@app.get("/api/status")
async def api_status():
    return {
        "status": "operational",
        "version": "2.2.0",
        "endpoints": {
            "executive": "/api/executive/overview",
            "intelligence": "/api/intelligence/report",
            "agency": "/api/agency/dashboard",
            "calendar": "/api/calendar/overview",
            "ingest": "/api/ingest/overview"
        }
    }

# Serve Next.js frontend static files
frontend_path = "frontend/out"
if os.path.exists(frontend_path):
    # Mount static assets
    app.mount("/_next/static", StaticFiles(directory=f"{frontend_path}/_next/static"), name="static")
    app.mount("/_next", StaticFiles(directory=f"{frontend_path}/_next"), name="next")
    
    # Serve other static files
    if os.path.exists(f"{frontend_path}/favicon.ico"):
        @app.get("/favicon.ico")
        async def favicon():
            return FileResponse(f"{frontend_path}/favicon.ico")
    
    # Catch-all route for frontend (must be last)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't serve frontend for API routes or docs
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Try to serve the specific file
        file_path = f"{frontend_path}/{full_path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Try with .html extension
        html_path = f"{frontend_path}/{full_path}.html"
        if os.path.exists(html_path):
            return FileResponse(html_path)
        
        # Default to index.html for SPA routing
        index_path = f"{frontend_path}/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        # If no frontend files exist, show API info
        return {
            "message": "Crooks & Castles Command Center V2 API",
            "frontend_status": "not_built",
            "api_docs": "/docs",
            "health_check": "/health"
        }

else:
    # Frontend not built - serve API info at root
    @app.get("/")
    async def root():
        return {
            "message": "Crooks & Castles Command Center V2 API",
            "frontend_status": "not_built",
            "api_docs": "/docs",
            "health_check": "/health",
            "build_instructions": "Run 'cd frontend && npm run build' to build frontend"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
