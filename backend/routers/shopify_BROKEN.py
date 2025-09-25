"""
Fixed Shopify Router with Working Sync Endpoints
"""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.shopify_integration import (
    ShopifyIntegration, 
    setup_shopify_config,
    get_shopify_health
)
from typing import Dict, Any, Optional
import json
from pathlib import Path

router = APIRouter()

class AnalysisRequest(BaseModel):
    days_back: int = 30
    include_correlation: bool = True

def load_shopify_config() -> Optional[Dict[str, Any]]:
    """Load Shopify configuration if it exists"""
    try:
        # Use absolute path to ensure we're reading from the right location
        backend_dir = Path(__file__).parent.parent
        config_file = backend_dir / "data" / "config" / "shopify_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def get_shopify_instance() -> Optional[ShopifyIntegration]:
    """Get configured Shopify instance"""
    config = load_shopify_config()
    if config and config.get("status") == "connected":
        return ShopifyIntegration(config["shop_domain"], config["access_token"])
    return None

@router.post("/setup")
async def setup_shopify_integration(shop_domain: str = Form(...), access_token: str = Form(...)):
    """Setup Shopify integration with store credentials"""
    try:
        result = setup_shopify_config(shop_domain, access_token)
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": result["message"],
                "shop_info": result["config"]["shop_info"],
                "config": result["config"]
            })
        else:
            # Return the structured error response
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result["error"],
                    "normalized_domain": result.get("normalized_domain"),
                    "troubleshooting": result.get("troubleshooting")
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Unexpected error during setup: {str(e)}"
            }
        )

@router.get("/status")
async def get_shopify_status():
    """Get current Shopify integration status"""
    try:
        config = load_shopify_config()
        
        if not config:
            return JSONResponse({
                "connected": False,
                "message": "Shopify not configured"
            })
        
        if config.get("status") == "connected":
            return JSONResponse({
                "connected": True,
                "shop_info": config.get("shop_info", {}),
                "message": f"Connected to {config.get('shop_info', {}).get('shop_name', 'Shopify store')}"
            })
        else:
            return JSONResponse({
                "connected": False,
                "message": "Shopify configured but not connected",
                "error": config.get("error")
            })
            
    except Exception as e:
        return JSONResponse({
            "connected": False,
            "error": f"Status check failed: {str(e)}"
        })

@router.post("/sync/sales")
async def sync_sales_data(request: AnalysisRequest):
    """Pull and sync sales data from Shopify"""
    shopify = get_shopify_instance()
    if not shopify:
        return {
            "success": False,
            "error": "Shopify not configured. Please run setup first."
        }
    
    try:
        # Pull sales data
        sales_result = shopify.get_daily_sales_data(request.days_back)
        
        if not sales_result["success"]:
            return {
                "success": False,
                "error": sales_result["error"]
            }
        
        return {
            "success": True,
            "message": f"Synced {request.days_back} days of sales data successfully",
            "data": sales_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Sales sync failed: {str(e)}"
        }

@router.post("/sync/traffic")
async def sync_traffic_data(request: AnalysisRequest):
    """Pull and sync traffic data from Shopify"""
    shopify = get_shopify_instance()
    if not shopify:
        return {
            "success": False,
            "error": "Shopify not configured. Please run setup first."
        }
    
    try:
        # Pull traffic data
        traffic_result = shopify.get_traffic_data(request.days_back)
        
        if not traffic_result["success"]:
            return {
                "success": False,
                "error": traffic_result["error"]
            }
        
        return {
            "success": True,
            "message": f"Synced {request.days_back} days of traffic data successfully",
            "data": traffic_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Traffic sync failed: {str(e)}"
        }

@router.post("/sync/products")
async def sync_product_performance():
    """Pull product performance data from Shopify"""
    shopify = get_shopify_instance()
    if not shopify:
        return {
            "success": False,
            "error": "Shopify not configured. Please run setup first."
        }
    
    try:
        # Pull product data
        product_result = shopify.get_product_performance(30)
        
        if not product_result["success"]:
            return {
                "success": False,
                "error": product_result["error"]
            }
        
        return {
            "success": True,
            "message": "Product performance data synced successfully",
            "data": product_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Product sync failed: {str(e)}"
        }

@router.get("/dashboard")
async def get_shopify_dashboard():
    """Get Shopify dashboard data"""
    shopify = get_shopify_instance()
    if not shopify:
        return {
            "success": False,
            "error": "Shopify not configured. Please run setup first."
        }
    
    try:
        # Get sales data
        sales_result = shopify.get_daily_sales_data(30)
        
        if not sales_result["success"]:
            return {
                "success": False,
                "error": sales_result["error"]
            }
        
        # Mock correlation data for now
        correlation_insights = {
            "instagram": {"revenue_correlation": 0.65, "engagement_impact": "High"},
            "tiktok": {"revenue_correlation": 0.72, "engagement_impact": "Very High"},
            "twitter": {"revenue_correlation": 0.45, "engagement_impact": "Medium"}
        }
        
        return {
            "success": True,
            "dashboard": {
                "sales_metrics": sales_result.get("summary", {}),
                "correlation_insights": correlation_insights
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Dashboard data failed: {str(e)}"
        }

@router.get("/health")
async def get_shopify_health_status():
    """Get Shopify integration health status"""
    try:
        health_result = get_shopify_health()
        return health_result
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }
