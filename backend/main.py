from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from datetime import datetime

app = FastAPI(title="Crooks Command Center API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Critical API endpoints for dashboard functionality
@app.get("/api/executive/overview")
def get_executive_overview():
    return {
        "total_sales": 0,
        "total_orders": 0,
        "conversion_rate": 0.0,
        "engagement_rate": 0.0,
        "sales_trend": "flat",
        "orders_trend": "flat",
        "conversion_trend": "flat",
        "engagement_trend": "flat",
        "data_source": "no_uploads",
        "last_updated": datetime.now().isoformat(),
        "status": "awaiting_data",
        "recommendations": [
            "Upload Shopify sales data to see real performance metrics",
            "Connect social media data for engagement analytics",
            "Add content performance data for comprehensive insights"
        ]
    }

@app.get("/api/executive/summary")
def get_executive_summary():
    return {
        "period": "Current Period",
        "highlights": [
            {"title": "Sales Performance", "value": "$0", "change": "0%", "status": "awaiting_data"},
            {"title": "Order Volume", "value": "0", "change": "0%", "status": "awaiting_data"},
            {"title": "Engagement Rate", "value": "0%", "change": "0%", "status": "awaiting_data"}
        ],
        "key_metrics": {"revenue": 0, "orders": 0, "customers": 0, "engagement": 0},
        "insights": [
            "No data uploaded yet - upload Shopify reports to see real insights",
            "Connect social media data for engagement analysis",
            "Add competitive intelligence for market positioning"
        ],
        "status": "ready_for_data"
    }

@app.get("/api/executive/metrics")
def get_executive_metrics():
    return {
        "status": "connected",
        "data_sources": 0,
        "last_updated": datetime.now().isoformat(),
        "metrics": {"sales": 0, "orders": 0, "engagement": 0, "conversion": 0}
    }

@app.post("/api/executive/refresh")
def refresh_executive_data():
    return {
        "status": "refreshed",
        "timestamp": datetime.now().isoformat(),
        "message": "Executive data refreshed successfully"
    }

@app.get("/api/competitive/analysis")
def get_competitive_analysis():
    return {
        "market_position": "Awaiting data upload",
        "brand_identity": "Authentic Streetwear Pioneer",
        "differentiation": [
            "Upload competitive intelligence data to see differentiation analysis",
            "Connect social media monitoring for positioning insights",
            "Add brand mention tracking for market analysis"
        ],
        "competitive_threats": {"high": [], "medium": []},
        "opportunities": [
            "Upload competitor data to identify strategic opportunities",
            "Connect social listening tools for trend analysis",
            "Add market research data for positioning insights"
        ],
        "intelligence_score": 0,
        "coverage_level": "No data",
        "data_status": "awaiting_upload",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/competitive-analysis/comparison")
def get_competitive_comparison():
    return {
        "crooks_and_castles": {
            "brand_mentions": 0, "engagement_rate": 0.0, "follower_growth": 0,
            "sentiment": "No data", "data_status": "awaiting_upload"
        },
        "competitors": [],
        "group_average": {
            "brand_mentions": 0, "engagement_rate": 0.0, "follower_growth": 0, "sentiment": "No data"
        },
        "content_suggestions": [
            "Upload competitor data to receive AI-powered content suggestions",
            "Connect social media accounts for engagement analysis",
            "Add brand monitoring to identify content opportunities"
        ],
        "setup_status": "pending_data_connection",
        "last_updated": datetime.now().isoformat()
    }

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "frontend_serving": "active",
        "api_endpoints": "active"
    }

# Try to mount static files from multiple possible locations
static_mounted = False
static_dirs_to_try = [
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
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
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
        "endpoints": [
            "/api/executive/overview",
            "/api/executive/summary",
            "/api/competitive/analysis",
            "/api/competitive-analysis/comparison"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
