from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

router = APIRouter()

# Shopify configuration storage
SHOPIFY_CONFIG_FILE = "data/config/shopify_config.json"

class ShopifyConfig(BaseModel):
    store_url: str
    access_token: str

def load_shopify_config() -> Optional[Dict[str, str]]:
    """Load Shopify configuration from file"""
    try:
        if os.path.exists(SHOPIFY_CONFIG_FILE):
            with open(SHOPIFY_CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading Shopify config: {e}")
    return None

def save_shopify_config(store_url: str, access_token: str):
    """Save Shopify configuration to file"""
    try:
        os.makedirs(os.path.dirname(SHOPIFY_CONFIG_FILE), exist_ok=True)
        config = {
            "store_url": store_url,
            "access_token": access_token,
            "connected_at": datetime.now().isoformat()
        }
        with open(SHOPIFY_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving Shopify config: {e}")
        return False

def make_shopify_request(endpoint: str, config: Dict[str, str]) -> Optional[Dict]:
    """Make authenticated request to Shopify API"""
    try:
        store_url = config["store_url"]
        if not store_url.endswith('.myshopify.com'):
            store_url = f"{store_url}.myshopify.com"
        
        url = f"https://{store_url}/admin/api/2023-10/{endpoint}"
        headers = {
            "X-Shopify-Access-Token": config["access_token"],
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Shopify API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error making Shopify request: {e}")
        return None

@router.get("/setup")
async def get_shopify_setup():
    """Get current Shopify setup status"""
    try:
        config = load_shopify_config()
        if config:
            return {
                "connected": True,
                "store_url": config.get("store_url", ""),
                "connected_at": config.get("connected_at", ""),
                "status": "Connected"
            }
        else:
            return {
                "connected": False,
                "store_url": "",
                "connected_at": "",
                "status": "Not Connected"
            }
    except Exception as e:
        return {
            "connected": False,
            "store_url": "",
            "connected_at": "",
            "status": f"Error: {str(e)}"
        }

@router.post("/connect")
async def connect_shopify(store_url: str = Form(...), access_token: str = Form(...)):
    """Connect to Shopify store"""
    try:
        # Clean up store URL
        store_url = store_url.strip().lower()
        if store_url.startswith('http://') or store_url.startswith('https://'):
            store_url = store_url.split('://', 1)[1]
        if store_url.startswith('www.'):
            store_url = store_url[4:]
        if not store_url.endswith('.myshopify.com'):
            if '.' in store_url and not store_url.endswith('.myshopify.com'):
                # If it's a custom domain, we need the myshopify.com version
                return {
                    "success": False,
                    "message": "Please use your store's .myshopify.com URL (e.g., your-store.myshopify.com)"
                }
            else:
                store_url = f"{store_url}.myshopify.com"
        
        # Test connection
        config = {"store_url": store_url, "access_token": access_token}
        test_response = make_shopify_request("shop.json", config)
        
        if test_response and "shop" in test_response:
            # Save configuration
            if save_shopify_config(store_url, access_token):
                return {
                    "success": True,
                    "message": "Successfully connected to Shopify!",
                    "shop_name": test_response["shop"].get("name", "Unknown"),
                    "shop_domain": test_response["shop"].get("domain", store_url)
                }
            else:
                return {
                    "success": False,
                    "message": "Connected to Shopify but failed to save configuration"
                }
        else:
            return {
                "success": False,
                "message": "Connection failed: Unable to connect to your Shopify store. Please check your store URL and access token."
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}"
        }

@router.get("/status")
async def get_shopify_status():
    """Get Shopify connection status"""
    try:
        config = load_shopify_config()
        if not config:
            return {"connected": False, "message": "Not connected"}
        
        # Test current connection
        test_response = make_shopify_request("shop.json", config)
        if test_response and "shop" in test_response:
            return {
                "connected": True,
                "message": "Connected",
                "shop_name": test_response["shop"].get("name", "Unknown"),
                "store_url": config["store_url"]
            }
        else:
            return {
                "connected": False,
                "message": "Connection lost or invalid credentials"
            }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Error checking status: {str(e)}"
        }

@router.get("/sales")
async def get_sales_data(days: int = 30):
    """Get sales data from Shopify"""
    try:
        config = load_shopify_config()
        if not config:
            raise HTTPException(status_code=400, detail="Shopify not connected")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get orders
        endpoint = f"orders.json?status=any&created_at_min={start_date.isoformat()}&created_at_max={end_date.isoformat()}&limit=250"
        orders_response = make_shopify_request(endpoint, config)
        
        if not orders_response or "orders" not in orders_response:
            return {
                "success": False,
                "message": "Failed to fetch sales data",
                "data": {
                    "total_revenue": 0,
                    "total_orders": 0,
                    "average_order_value": 0,
                    "conversion_rate": 0,
                    "orders": []
                }
            }
        
        orders = orders_response["orders"]
        
        # Calculate metrics
        total_revenue = sum(float(order.get("total_price", 0)) for order in orders)
        total_orders = len(orders)
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Estimate conversion rate (basic calculation)
        estimated_sessions = total_orders * 25  # Rough estimate: 4% conversion rate
        conversion_rate = (total_orders / estimated_sessions * 100) if estimated_sessions > 0 else 0
        
        return {
            "success": True,
            "message": "Sales data retrieved successfully",
            "data": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "average_order_value": round(average_order_value, 2),
                "conversion_rate": round(conversion_rate, 2),
                "period_days": days,
                "orders": orders[:10]  # Return first 10 orders for analysis
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching sales data: {str(e)}",
            "data": {
                "total_revenue": 0,
                "total_orders": 0,
                "average_order_value": 0,
                "conversion_rate": 0,
                "orders": []
            }
        }

@router.get("/traffic")
async def get_traffic_data(days: int = 30):
    """Get traffic data (estimated from orders)"""
    try:
        config = load_shopify_config()
        if not config:
            raise HTTPException(status_code=400, detail="Shopify not connected")
        
        # Get sales data first
        sales_response = await get_sales_data(days)
        
        if not sales_response["success"]:
            return sales_response
        
        sales_data = sales_response["data"]
        total_orders = sales_data["total_orders"]
        
        # Estimate traffic metrics (industry averages)
        estimated_sessions = total_orders * 25  # 4% conversion rate
        estimated_page_views = estimated_sessions * 3  # 3 pages per session
        bounce_rate = 65  # Industry average
        
        return {
            "success": True,
            "message": "Traffic data estimated from sales",
            "data": {
                "sessions": estimated_sessions,
                "page_views": estimated_page_views,
                "bounce_rate": bounce_rate,
                "conversion_rate": sales_data["conversion_rate"],
                "orders": total_orders,
                "revenue": sales_data["total_revenue"],
                "note": "Traffic metrics are estimated based on industry averages and actual order data"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error estimating traffic data: {str(e)}",
            "data": {
                "sessions": 0,
                "page_views": 0,
                "bounce_rate": 0,
                "conversion_rate": 0,
                "orders": 0,
                "revenue": 0
            }
        }

@router.post("/sync")
async def sync_shopify_data():
    """Sync all Shopify data"""
    try:
        config = load_shopify_config()
        if not config:
            raise HTTPException(status_code=400, detail="Shopify not connected")
        
        # Get sales and traffic data
        sales_data = await get_sales_data(30)
        traffic_data = await get_traffic_data(30)
        
        return {
            "success": True,
            "message": "Shopify data synced successfully",
            "sales": sales_data,
            "traffic": traffic_data,
            "synced_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error syncing Shopify data: {str(e)}"
        }

@router.delete("/disconnect")
async def disconnect_shopify():
    """Disconnect from Shopify"""
    try:
        if os.path.exists(SHOPIFY_CONFIG_FILE):
            os.remove(SHOPIFY_CONFIG_FILE)
        
        return {
            "success": True,
            "message": "Disconnected from Shopify successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error disconnecting: {str(e)}"
        }
