# main.py - If your routers are in a package structure

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# If you have a backend package structure like backend/routers/
try:
    from backend.routers import executive, competitive, competitive_analysis
except ImportError:
    # Fallback for direct routers folder
    from routers import executive, competitive, competitive_analysis

app = FastAPI(title="Crooks Command Center API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])
app.include_router(competitive_analysis.router, prefix="/api/competitive-analysis", tags=["competitive_analysis"])

@app.get("/")
def read_root():
    return {"message": "Crooks Command Center API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
