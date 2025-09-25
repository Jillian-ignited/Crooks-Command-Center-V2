"""
Completely Fixed Shopify Router - All Issues Resolved
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
            return {
                "success": True,
                "message": result["message"],
                "shop_domain": result["normalized_domain"],
                "status": "connected"
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "shop_domain": result["normalized_domain"],
                "status": "error",
                "troubleshooting": {
                    "domain_format": f"Tried to connect to: {result['normalized_domain']}.myshopify.com",
                    "suggestions": [
                        "Verify your shop domain (just the shop name, not the full URL)",
                        "Check your private app access token",
                        "Ensure your private app has the required permissions",
                        "Try entering just the shop name (e.g., 'crooksonline' instead of 'crooksonline.myshopify.com')"
                    ]
                }
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Setup failed: {str(e)}",
            "status": "error"
        }

@router.get("/status")
async def get_shopify_status():
    """Get current Shopify integration status"""
    try:
        config = load_shopify_config()
        
        if not config:
            return {
                "connected": False,
                "message": "Shopify not configured"
            }
        
        if config.get("status") == "connected":
            return {
                "connected": True,
                "message": f"Connected to {config.get('shop_domain', 'Unknown')}.myshopify.com",
                "shop_domain": config.get("shop_domain"),
                "setup_date": config.get("setup_date")
            }
        elif config.get("status") == "error":
            return {
                "connected": False,
                "message": "Shopify configured but not connected",
                "error": config.get("error", "Unknown error"),
                "shop_domain": config.get("shop_domain")
            }
        else:
            return {
                "connected": False,
                "message": "Shopify configuration incomplete"
            }
            
    except Exception as e:
        return {
            "connected": False,
            "message": f"Status check failed: {str(e)}"
        }

@router.post("/sync/sales")
async def sync_sales_data(request: AnalysisRequest):
    """Sync sales data from Shopify"""
    try:
        config = load_shopify_config()
        
        if not config:
            return {
                "success": False,
                "error": "Shopify not configured. Please run setup first.",
                "action_required": "Go to Shopify Setup tab and configure your store connection"
            }
        
        if config.get("status") != "connected":
            return {
                "success": False,
                "error": f"Shopify connection error: {config.get('error', 'Unknown error')}",
                "action_required": "Fix your Shopify configuration in the Setup tab"
            }
        
        shopify = ShopifyIntegration(config["shop_domain"], config["access_token"])
        result = shopify.get_sales_data(request.days_back)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully synced {request.days_back} days of sales data",
                "data": result,
                "summary": result.get("summary", {})
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "action_required": "Check your Shopify API permissions and access token"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Sales sync failed: {str(e)}",
            "action_required": "Check server logs and Shopify configuration"
        }

@router.post("/sync/traffic")
async def sync_traffic_data(request: AnalysisRequest):
    """Sync traffic data from Shopify"""
    try:
        config = load_shopify_config()
        
        if not config:
            return {
                "success": False,
                "error": "Shopify not configured. Please run setup first.",
                "action_required": "Go to Shopify Setup tab and configure your store connection"
            }
        
        if config.get("status") != "connected":
            return {
                "success": False,
                "error": f"Shopify connection error: {config.get('error', 'Unknown error')}",
                "action_required": "Fix your Shopify configuration in the Setup tab"
            }
        
        shopify = ShopifyIntegration(config["shop_domain"], config["access_token"])
        result = shopify.get_traffic_data(request.days_back)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully synced {request.days_back} days of traffic data",
                "data": result,
                "summary": result.get("summary", {})
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "action_required": "Check your Shopify Analytics API permissions"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Traffic sync failed: {str(e)}",
            "action_required": "Check server logs and Shopify configuration"
        }

@router.post("/sync/products")
async def sync_products_data():
    """Sync products data from Shopify"""
    try:
        config = load_shopify_config()
        
        if not config:
            return {
                "success": False,
                "error": "Shopify not configured. Please run setup first.",
                "action_required": "Go to Shopify Setup tab and configure your store connection"
            }
        
        if config.get("status") != "connected":
            return {
                "success": False,
                "error": f"Shopify connection error: {config.get('error', 'Unknown error')}",
                "action_required": "Fix your Shopify configuration in the Setup tab"
            }
        
        shopify = ShopifyIntegration(config["shop_domain"], config["access_token"])
        result = shopify.get_products_data()
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully synced products data",
                "data": result,
                "summary": result.get("summary", {})
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "action_required": "Check your Shopify Products API permissions"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Products sync failed: {str(e)}",
            "action_required": "Check server logs and Shopify configuration"
        }

@router.get("/dashboard")
async def get_shopify_dashboard():
    """Get Shopify dashboard data"""
    try:
        config = load_shopify_config()
        
        if not config:
            return {
                "success": False,
                "error": "Shopify not configured",
                "dashboard": {
                    "status": "not_configured",
                    "message": "Please configure Shopify integration first"
                }
            }
        
        if config.get("status") != "connected":
            return {
                "success": False,
                "error": "Shopify not connected",
                "dashboard": {
                    "status": "error",
                    "message": config.get("error", "Connection error"),
                    "shop_domain": config.get("shop_domain")
                }
            }
        
        # If connected, return basic dashboard info
        return {
            "success": True,
            "dashboard": {
                "status": "connected",
                "shop_domain": config.get("shop_domain"),
                "setup_date": config.get("setup_date"),
                "message": "Shopify integration active"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Dashboard failed: {str(e)}",
            "dashboard": {
                "status": "error",
                "message": "Failed to load dashboard"
            }
        }

@router.delete("/config")
async def delete_shopify_config():
    """Delete Shopify configuration"""
    try:
        backend_dir = Path(__file__).parent.parent
        config_file = backend_dir / "data" / "config" / "shopify_config.json"
        
        if config_file.exists():
            config_file.unlink()
            return {
                "success": True,
                "message": "Shopify configuration deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "No Shopify configuration found to delete"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete configuration: {str(e)}"
        }

@router.get("/test-connection")
async def test_shopify_connection():
    """Test current Shopify connection without saving config"""
    try:
        config = load_shopify_config()
        
        if not config:
            return {
                "success": False,
                "error": "No Shopify configuration found. Please run setup first."
            }
        
        shopify = ShopifyIntegration(config["shop_domain"], config["access_token"])
        result = shopify.test_connection()
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection test failed: {str(e)}"
        }
