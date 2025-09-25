"""
Test script to verify sync endpoints work correctly
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class AnalysisRequest(BaseModel):
    days_back: int = 30
    include_correlation: bool = True

@app.post("/test/sync/sales")
async def test_sync_sales_data(request: AnalysisRequest):
    """Test sales sync endpoint"""
    return {
        "success": False,
        "error": "Shopify not configured. Please run setup first.",
        "test": "This is a test response"
    }

@app.post("/test/sync/traffic")
async def test_sync_traffic_data(request: AnalysisRequest):
    """Test traffic sync endpoint"""
    return {
        "success": True,
        "message": f"Synced {request.days_back} days of traffic data successfully",
        "data": {"test": "mock data"}
    }

@app.post("/test/sync/products")
async def test_sync_product_performance():
    """Test products sync endpoint"""
    return {
        "success": True,
        "message": "Product performance data synced successfully",
        "data": {"test": "mock product data"}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
