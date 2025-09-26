from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from pathlib import Path

# Import your routers
from routers import executive, intelligence, agency, calendar, summary

# Create the FastAPI app
app = FastAPI(title="Crooks Command Center V2")

# Mount API routes with /api prefix
app.mount("/api/executive", executive.router, name="executive")
app.mount("/api/intelligence", intelligence.router, name="intelligence")
app.mount("/api/agency", agency.router, name="agency")
app.mount("/api/calendar", calendar.router, name="calendar")
app.mount("/api/summary", summary.router, name="summary")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve static files from root
@app.get("/{path:path}")
async def serve_static(path: str, request: Request):
    # API documentation path
    if path == "docs" or path == "redoc" or path == "openapi.json":
        return await request.call_next(request)
    
    # Check if the file exists in the static directory
    static_path = Path("static") / path
    if static_path.exists() and static_path.is_file():
        return FileResponse(static_path)
    
    # Default to index.html for SPA routing
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    
    # Fallback to 404
    return JSONResponse({"detail": "Not Found"}, status_code=404)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Root endpoint redirects to index.html
@app.get("/")
async def root():
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Welcome to Crooks Command Center V2 API"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
