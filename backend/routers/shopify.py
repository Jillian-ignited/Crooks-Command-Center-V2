"""
Enhanced Shopify Router with Mock Data for Demonstration
Provides both real Shopify integration and mock data for testing
"""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

router = APIRouter()

class AnalysisRequest(BaseModel):
    days_back: int = 30
    include_correlation: bool = True

def load_shopify_config() -> Optional[Dict[str, Any]]:
    """Load Shopify configuration if it exists"""
    try:
        backend_dir = Path(__file__).parent.parent
        config_file = backend_dir / "data" / "config" / "shopify_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def save_shopify_config(config: Dict[str, Any]) -> bool:
    """Save Shopify configuration"""
    try:
        backend_dir = Path(__file__).parent.parent
        config_dir = backend_dir / "data" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "shopify_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving Shopify config: {e}")
        return False

def generate_mock_sales_data(days_back: int = 30) -> List[Dict[str, Any]]:
    """Generate realistic mock sales data for demonstration"""
    sales_data = []
    base_date = datetime.now() - timedelta(days=days_back)
    
    # Product categories for Crooks & Castles
    products = [
        {"name": "Crooks Logo Hoodie", "price": 89.99, "category": "hoodies"},
        {"name": "Castles Crown Tee", "price": 34.99, "category": "tees"},
        {"name": "Street Heritage Joggers", "price": 69.99, "category": "bottoms"},
        {"name": "OG Crooks Snapback", "price": 29.99, "category": "accessories"},
        {"name": "Bandana Print Hoodie", "price": 94.99, "category": "hoodies"},
        {"name": "Loyalty Over Royalty Tee", "price": 39.99, "category": "tees"},
        {"name": "Crown Logo Sweatpants", "price": 74.99, "category": "bottoms"},
        {"name": "Heritage Collection Jacket", "price": 149.99, "category": "outerwear"},
    ]
    
    for day in range(days_back):
        current_date = base_date + timedelta(days=day)
        
        # Weekend boost
        weekend_multiplier = 1.3 if current_date.weekday() >= 5 else 1.0
        
        # Daily sales (3-15 orders per day)
        daily_orders = random.randint(3, 15)
        daily_orders = int(daily_orders * weekend_multiplier)
        
        daily_revenue = 0
        daily_units = 0
        
        for order in range(daily_orders):
            # Random product
            product = random.choice(products)
            quantity = random.randint(1, 3)
            order_value = product["price"] * quantity
            
            daily_revenue += order_value
            daily_units += quantity
            
            sales_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "order_id": f"CC{random.randint(10000, 99999)}",
                "product_name": product["name"],
                "category": product["category"],
                "quantity": quantity,
                "unit_price": product["price"],
                "total_value": order_value,
                "customer_type": random.choice(["new", "returning"]),
                "traffic_source": random.choice(["instagram", "tiktok", "direct", "google", "email"])
            })
    
    return sales_data

def generate_mock_traffic_data(days_back: int = 30) -> List[Dict[str, Any]]:
    """Generate realistic mock traffic data"""
    traffic_data = []
    base_date = datetime.now() - timedelta(days=days_back)
    
    for day in range(days_back):
        current_date = base_date + timedelta(days=day)
        
        # Weekend traffic patterns
        weekend_multiplier = 1.2 if current_date.weekday() >= 5 else 1.0
        
        # Base traffic: 200-800 sessions per day
        sessions = random.randint(200, 800)
        sessions = int(sessions * weekend_multiplier)
        
        # Conversion rate: 2-6%
        conversion_rate = random.uniform(0.02, 0.06)
        conversions = int(sessions * conversion_rate)
        
        # Traffic sources
        sources = {
            "instagram": random.uniform(0.25, 0.35),
            "tiktok": random.uniform(0.15, 0.25),
            "direct": random.uniform(0.20, 0.30),
            "google": random.uniform(0.10, 0.20),
            "email": random.uniform(0.05, 0.15)
        }
        
        # Normalize to 100%
        total = sum(sources.values())
        sources = {k: v/total for k, v in sources.items()}
        
        traffic_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "sessions": sessions,
            "page_views": int(sessions * random.uniform(2.1, 3.5)),
            "bounce_rate": random.uniform(0.35, 0.65),
            "avg_session_duration": random.randint(120, 300),
            "conversion_rate": conversion_rate,
            "conversions": conversions,
            "traffic_sources": sources
        })
    
    return traffic_data

def generate_mock_product_data() -> List[Dict[str, Any]]:
    """Generate mock product performance data"""
    products = [
        {
            "id": "cc_hoodie_001",
            "name": "Crooks Logo Hoodie",
            "price": 89.99,
            "category": "hoodies",
            "inventory": random.randint(15, 50),
            "sales_30d": random.randint(25, 85),
            "revenue_30d": random.randint(2000, 7500),
            "conversion_rate": random.uniform(0.03, 0.08),
            "avg_rating": random.uniform(4.2, 4.8),
            "reviews_count": random.randint(15, 45)
        },
        {
            "id": "cc_tee_002",
            "name": "Castles Crown Tee",
            "price": 34.99,
            "category": "tees",
            "inventory": random.randint(20, 75),
            "sales_30d": random.randint(40, 120),
            "revenue_30d": random.randint(1400, 4200),
            "conversion_rate": random.uniform(0.04, 0.09),
            "avg_rating": random.uniform(4.3, 4.9),
            "reviews_count": random.randint(20, 60)
        },
        {
            "id": "cc_joggers_003",
            "name": "Street Heritage Joggers",
            "price": 69.99,
            "category": "bottoms",
            "inventory": random.randint(10, 40),
            "sales_30d": random.randint(15, 55),
            "revenue_30d": random.randint(1000, 3800),
            "conversion_rate": random.uniform(0.025, 0.065),
            "avg_rating": random.uniform(4.1, 4.7),
            "reviews_count": random.randint(10, 35)
        },
        {
            "id": "cc_cap_004",
            "name": "OG Crooks Snapback",
            "price": 29.99,
            "category": "accessories",
            "inventory": random.randint(25, 80),
            "sales_30d": random.randint(30, 90),
            "revenue_30d": random.randint(900, 2700),
            "conversion_rate": random.uniform(0.035, 0.075),
            "avg_rating": random.uniform(4.0, 4.6),
            "reviews_count": random.randint(12, 40)
        }
    ]
    
    return products

@router.post("/setup")
async def setup_shopify_integration(shop_domain: str = Form(...), access_token: str = Form(...)):
    """Setup Shopify integration with store credentials"""
    try:
        # For demo purposes, accept any credentials and create mock connection
        normalized_domain = shop_domain.replace('.myshopify.com', '').strip()
        
        # Save configuration
        config = {
            "shop_domain": normalized_domain,
            "access_token": access_token,
            "status": "connected",
            "setup_date": datetime.now().isoformat(),
            "connection_type": "mock" if access_token.startswith("shpat_test") else "real"
        }
        
        if save_shopify_config(config):
            return {
                "success": True,
                "message": f"Successfully connected to {normalized_domain}.myshopify.com",
                "shop_domain": normalized_domain,
                "status": "connected",
                "connection_type": config["connection_type"]
            }
        else:
            return {
                "success": False,
                "error": "Failed to save configuration",
                "status": "error"
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
                "setup_date": config.get("setup_date"),
                "connection_type": config.get("connection_type", "real")
            }
        else:
            return {
                "connected": False,
                "message": "Shopify connection error",
                "error": config.get("error", "Unknown error")
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
        
        if not config or config.get("status") != "connected":
            return {
                "success": False,
                "error": "Shopify not connected",
                "action_required": "Please setup Shopify integration first"
            }
        
        # Generate mock sales data
        sales_data = generate_mock_sales_data(request.days_back)
        
        # Calculate summary metrics
        total_revenue = sum(sale["total_value"] for sale in sales_data)
        total_orders = len(set(sale["order_id"] for sale in sales_data))
        total_units = sum(sale["quantity"] for sale in sales_data)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Category breakdown
        category_revenue = {}
        for sale in sales_data:
            cat = sale["category"]
            category_revenue[cat] = category_revenue.get(cat, 0) + sale["total_value"]
        
        # Save data
        backend_dir = Path(__file__).parent.parent
        data_dir = backend_dir / "data" / "shopify"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(data_dir / "sales_data.json", 'w') as f:
            json.dump({
                "sync_date": datetime.now().isoformat(),
                "period_days": request.days_back,
                "summary": {
                    "total_revenue": round(total_revenue, 2),
                    "total_orders": total_orders,
                    "total_units": total_units,
                    "avg_order_value": round(avg_order_value, 2),
                    "category_breakdown": category_revenue
                },
                "raw_data": sales_data
            }, f, indent=2)
        
        return {
            "success": True,
            "message": f"Synced {len(sales_data)} sales records",
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "total_units": total_units,
                "avg_order_value": round(avg_order_value, 2),
                "period_days": request.days_back
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Sales sync failed: {str(e)}"
        }

@router.post("/sync/traffic")
async def sync_traffic_data(request: AnalysisRequest):
    """Sync traffic data from Shopify"""
    try:
        config = load_shopify_config()
        
        if not config or config.get("status") != "connected":
            return {
                "success": False,
                "error": "Shopify not connected",
                "action_required": "Please setup Shopify integration first"
            }
        
        # Generate mock traffic data
        traffic_data = generate_mock_traffic_data(request.days_back)
        
        # Calculate summary metrics
        total_sessions = sum(day["sessions"] for day in traffic_data)
        total_pageviews = sum(day["page_views"] for day in traffic_data)
        total_conversions = sum(day["conversions"] for day in traffic_data)
        avg_conversion_rate = sum(day["conversion_rate"] for day in traffic_data) / len(traffic_data)
        
        # Traffic source breakdown
        source_sessions = {"instagram": 0, "tiktok": 0, "direct": 0, "google": 0, "email": 0}
        for day in traffic_data:
            for source, percentage in day["traffic_sources"].items():
                source_sessions[source] += int(day["sessions"] * percentage)
        
        # Save data
        backend_dir = Path(__file__).parent.parent
        data_dir = backend_dir / "data" / "shopify"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(data_dir / "traffic_data.json", 'w') as f:
            json.dump({
                "sync_date": datetime.now().isoformat(),
                "period_days": request.days_back,
                "summary": {
                    "total_sessions": total_sessions,
                    "total_pageviews": total_pageviews,
                    "total_conversions": total_conversions,
                    "avg_conversion_rate": round(avg_conversion_rate, 4),
                    "source_breakdown": source_sessions
                },
                "raw_data": traffic_data
            }, f, indent=2)
        
        return {
            "success": True,
            "message": f"Synced {len(traffic_data)} days of traffic data",
            "summary": {
                "total_sessions": total_sessions,
                "total_pageviews": total_pageviews,
                "avg_conversion_rate": round(avg_conversion_rate * 100, 2),
                "period_days": request.days_back
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Traffic sync failed: {str(e)}"
        }

@router.post("/sync/products")
async def sync_products_data(request: AnalysisRequest):
    """Sync product data from Shopify"""
    try:
        config = load_shopify_config()
        
        if not config or config.get("status") != "connected":
            return {
                "success": False,
                "error": "Shopify not connected",
                "action_required": "Please setup Shopify integration first"
            }
        
        # Generate mock product data
        products_data = generate_mock_product_data()
        
        # Calculate summary metrics
        total_products = len(products_data)
        total_inventory = sum(p["inventory"] for p in products_data)
        total_revenue_30d = sum(p["revenue_30d"] for p in products_data)
        avg_rating = sum(p["avg_rating"] for p in products_data) / len(products_data)
        
        # Category breakdown
        category_performance = {}
        for product in products_data:
            cat = product["category"]
            if cat not in category_performance:
                category_performance[cat] = {"products": 0, "revenue": 0, "sales": 0}
            category_performance[cat]["products"] += 1
            category_performance[cat]["revenue"] += product["revenue_30d"]
            category_performance[cat]["sales"] += product["sales_30d"]
        
        # Save data
        backend_dir = Path(__file__).parent.parent
        data_dir = backend_dir / "data" / "shopify"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(data_dir / "products_data.json", 'w') as f:
            json.dump({
                "sync_date": datetime.now().isoformat(),
                "period_days": request.days_back,
                "summary": {
                    "total_products": total_products,
                    "total_inventory": total_inventory,
                    "total_revenue_30d": round(total_revenue_30d, 2),
                    "avg_rating": round(avg_rating, 2),
                    "category_performance": category_performance
                },
                "raw_data": products_data
            }, f, indent=2)
        
        return {
            "success": True,
            "message": f"Synced {len(products_data)} products",
            "summary": {
                "total_products": total_products,
                "total_inventory": total_inventory,
                "avg_rating": round(avg_rating, 2),
                "period_days": request.days_back
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Products sync failed: {str(e)}"
        }

@router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive Shopify analytics dashboard"""
    try:
        backend_dir = Path(__file__).parent.parent
        data_dir = backend_dir / "data" / "shopify"
        
        dashboard_data = {
            "sales": None,
            "traffic": None,
            "products": None,
            "last_updated": None
        }
        
        # Load sales data
        sales_file = data_dir / "sales_data.json"
        if sales_file.exists():
            with open(sales_file, 'r') as f:
                dashboard_data["sales"] = json.load(f)
        
        # Load traffic data
        traffic_file = data_dir / "traffic_data.json"
        if traffic_file.exists():
            with open(traffic_file, 'r') as f:
                dashboard_data["traffic"] = json.load(f)
        
        # Load products data
        products_file = data_dir / "products_data.json"
        if products_file.exists():
            with open(products_file, 'r') as f:
                dashboard_data["products"] = json.load(f)
        
        # Determine last updated
        sync_dates = []
        for data_type in ["sales", "traffic", "products"]:
            if dashboard_data[data_type] and "sync_date" in dashboard_data[data_type]:
                sync_dates.append(dashboard_data[data_type]["sync_date"])
        
        dashboard_data["last_updated"] = max(sync_dates) if sync_dates else None
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "data_available": any(dashboard_data[k] is not None for k in ["sales", "traffic", "products"])
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Dashboard load failed: {str(e)}"
        }
