from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .routers import intelligence, campaigns, deliverables, executive, shopify, competitive
from .database import engine, get_db
from .models import Base

load_dotenv()

app = FastAPI(
    title="Crooks Command Center API",
    description="Intelligence-driven brand management system",
    version="2.0.0"
)

# CORS Configuration
ALLOWED_ORIGINS = [
    "https://crooks-command-center-v2-1d5b.vercel.app",
    "http://crooks-command-center-v2-1d5b.vercel.app",
    "https://crooks-command-center-v2.onrender.com",
    "https://crookscommandcenter.netlify.app",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(deliverables.router, prefix="/api/deliverables", tags=["deliverables"])
app.include_router(executive.router, prefix="/api/executive", tags=["executive"])
app.include_router(shopify.router, prefix="/api/shopify", tags=["shopify"])
app.include_router(competitive.router, prefix="/api/competitive", tags=["competitive"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("[Database] Initializing connection...")
    try:
        # Test database connection
        db = next(get_db())
        print("[Database] ✅ Connection established")
    except Exception as e:
        print(f"[Database] ❌ Connection failed: {e}")
        raise

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Crooks Command Center API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }

@app.get("/api")
def api_root():
    """API root with available endpoints"""
    return {
        "message": "Crooks Command Center API",
        "endpoints": {
            "intelligence": "/api/intelligence",
            "campaigns": "/api/campaigns",
            "deliverables": "/api/deliverables",
            "executive": "/api/executive",
            "shopify": "/api/shopify",
            "competitive": "/api/competitive",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
