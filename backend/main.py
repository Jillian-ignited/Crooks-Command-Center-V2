from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Crooks Command Center API - Emergency Version")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Executive Overview Endpoints
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
            {
                "title": "Sales Performance",
                "value": "$0",
                "change": "0%",
                "status": "awaiting_data"
            },
            {
                "title": "Order Volume", 
                "value": "0",
                "change": "0%",
                "status": "awaiting_data"
            },
            {
                "title": "Engagement Rate",
                "value": "0%", 
                "change": "0%",
                "status": "awaiting_data"
            }
        ],
        "key_metrics": {
            "revenue": 0,
            "orders": 0,
            "customers": 0,
            "engagement": 0
        },
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
        "metrics": {
            "sales": 0,
            "orders": 0,
            "engagement": 0,
            "conversion": 0
        }
    }

@app.post("/api/executive/refresh")
def refresh_executive_data():
    return {
        "status": "refreshed",
        "timestamp": datetime.now().isoformat(),
        "message": "Executive data refreshed successfully"
    }

# Competitive Analysis Endpoints
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
        "competitive_threats": {
            "high": [],
            "medium": []
        },
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
            "brand_mentions": 0,
            "engagement_rate": 0.0,
            "follower_growth": 0,
            "sentiment": "No data",
            "data_status": "awaiting_upload"
        },
        "competitors": [],
        "group_average": {
            "brand_mentions": 0,
            "engagement_rate": 0.0,
            "follower_growth": 0,
            "sentiment": "No data"
        },
        "content_suggestions": [
            "Upload competitor data to receive AI-powered content suggestions",
            "Connect social media accounts for engagement analysis",
            "Add brand monitoring to identify content opportunities",
            "Set up competitor tracking for strategic insights"
        ],
        "setup_status": "pending_data_connection",
        "last_updated": datetime.now().isoformat()
    }

# Health Check Endpoints
@app.get("/")
def read_root():
    return {"message": "Crooks Command Center API - Emergency Version", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "emergency"}

@app.get("/api/__routes")
def list_routes():
    return {
        "routes": [
            "/api/executive/overview",
            "/api/executive/summary", 
            "/api/executive/metrics",
            "/api/executive/refresh",
            "/api/competitive/analysis",
            "/api/competitive-analysis/comparison"
        ],
        "status": "emergency_mode"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
