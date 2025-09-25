from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.shopify_integration import (
    ShopifyIntegration, 
    correlate_social_with_sales, 
    analyze_hashtag_revenue_impact,
    setup_shopify_config
)
from services.scraper import load_all_uploaded_frames
from typing import Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime

router = APIRouter()

class ShopifyConfig(BaseModel):
    shop_domain: str
    access_token: str

class AnalysisRequest(BaseModel):
    days_back: int = 30
    include_correlation: bool = True

def load_shopify_config() -> Optional[Dict[str, Any]]:
    """Load Shopify configuration if it exists"""
    config_file = Path("data/config/shopify_config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def get_shopify_instance() -> Optional[ShopifyIntegration]:
    """Get configured Shopify instance"""
    config = load_shopify_config()
    if config and config.get("status") == "connected":
        return ShopifyIntegration(config["shop_domain"], config["access_token"])
    return None

@router.post("/setup")
async def setup_shopify_integration(config: ShopifyConfig):
    """Setup Shopify integration with store credentials"""
    try:
        result = setup_shopify_config(config.shop_domain, config.access_token)
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": result["message"],
                "shop_info": result["config"]["shop_info"]
            })
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

@router.get("/status")
async def get_shopify_status():
    """Get current Shopify integration status"""
    try:
        config = load_shopify_config()
        
        if not config:
            return JSONResponse({
                "connected": False,
                "message": "Shopify integration not configured"
            })
        
        shopify = get_shopify_instance()
        if shopify:
            test_result = shopify.test_connection()
            return JSONResponse({
                "connected": test_result["success"],
                "shop_info": config.get("shop_info", {}),
                "last_setup": config.get("setup_date"),
                "status": config.get("status"),
                "message": "Connected and operational" if test_result["success"] else test_result.get("error")
            })
        else:
            return JSONResponse({
                "connected": False,
                "message": "Configuration exists but connection failed"
            })
            
    except Exception as e:
        return JSONResponse({
            "connected": False,
            "error": f"Status check failed: {str(e)}"
        })

@router.post("/sync/sales")
async def sync_sales_data(request: AnalysisRequest):
    """Pull and sync sales data from Shopify"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Pull sales data
        sales_result = shopify.get_daily_sales_data(request.days_back)
        
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=sales_result["error"])
        
        return JSONResponse({
            "success": True,
            "message": f"Synced {request.days_back} days of sales data",
            "data": sales_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales sync failed: {str(e)}")

@router.post("/sync/traffic")
async def sync_traffic_data(request: AnalysisRequest):
    """Pull and sync traffic data from Shopify"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Pull traffic data
        traffic_result = shopify.get_traffic_data(request.days_back)
        
        if not traffic_result["success"]:
            raise HTTPException(status_code=500, detail=traffic_result["error"])
        
        return JSONResponse({
            "success": True,
            "message": f"Synced {request.days_back} days of traffic data",
            "data": traffic_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Traffic sync failed: {str(e)}")

@router.post("/sync/products")
async def sync_product_performance():
    """Pull product performance data from Shopify"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Pull product data
        product_result = shopify.get_product_performance(30)
        
        if not product_result["success"]:
            raise HTTPException(status_code=500, detail=product_result["error"])
        
        return JSONResponse({
            "success": True,
            "message": "Synced product performance data",
            "data": product_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product sync failed: {str(e)}")

@router.post("/analyze/correlation")
async def analyze_social_sales_correlation(request: AnalysisRequest):
    """Analyze correlation between social media activity and sales"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get social media data
        social_df = load_all_uploaded_frames()
        if social_df.empty:
            raise HTTPException(status_code=400, detail="No social media data available. Upload competitor data first.")
        
        # Get sales data
        sales_result = shopify.get_daily_sales_data(request.days_back)
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to get sales data: {sales_result['error']}")
        
        # Perform correlation analysis
        correlation_result = correlate_social_with_sales(social_df, sales_result["daily_data"])
        
        return JSONResponse({
            "success": True,
            "correlation_analysis": correlation_result,
            "sales_summary": sales_result["summary"],
            "social_data_points": len(social_df)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correlation analysis failed: {str(e)}")

@router.post("/analyze/hashtags")
async def analyze_hashtag_revenue_correlation():
    """Analyze which hashtags correlate with revenue spikes"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get social media data
        social_df = load_all_uploaded_frames()
        if social_df.empty:
            raise HTTPException(status_code=400, detail="No social media data available. Upload competitor data first.")
        
        # Get sales data
        sales_result = shopify.get_daily_sales_data(30)
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to get sales data: {sales_result['error']}")
        
        # Analyze hashtag impact
        hashtag_result = analyze_hashtag_revenue_impact(social_df, sales_result["daily_data"])
        
        return JSONResponse({
            "success": True,
            "hashtag_analysis": hashtag_result,
            "message": "Hashtag revenue correlation analysis complete"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashtag analysis failed: {str(e)}")

@router.get("/dashboard")
async def get_unified_dashboard():
    """Get unified performance dashboard combining social and sales data"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            return JSONResponse({
                "success": False,
                "message": "Shopify not configured",
                "dashboard": {
                    "shopify_connected": False,
                    "social_data_available": False,
                    "unified_metrics": {}
                }
            })
        
        # Get social media data
        social_df = load_all_uploaded_frames()
        social_available = not social_df.empty
        
        # Get sales data
        sales_result = shopify.get_daily_sales_data(30)
        sales_available = sales_result["success"]
        
        dashboard_data = {
            "shopify_connected": True,
            "social_data_available": social_available,
            "sales_data_available": sales_available,
            "last_updated": datetime.now().isoformat()
        }
        
        if sales_available:
            dashboard_data["sales_metrics"] = sales_result["summary"]
        
        if social_available:
            dashboard_data["social_metrics"] = {
                "total_posts": len(social_df),
                "brands_tracked": social_df['brand'].nunique() if 'brand' in social_df.columns else 0,
                "date_range": f"{social_df['date'].min()} to {social_df['date'].max()}" if 'date' in social_df.columns else "Unknown"
            }
        
        # If both are available, perform correlation analysis
        if social_available and sales_available:
            correlation_result = correlate_social_with_sales(social_df, sales_result["daily_data"])
            dashboard_data["correlation_insights"] = correlation_result
            
            # Hashtag analysis
            hashtag_result = analyze_hashtag_revenue_impact(social_df, sales_result["daily_data"])
            dashboard_data["hashtag_insights"] = hashtag_result
        
        return JSONResponse({
            "success": True,
            "dashboard": dashboard_data
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Dashboard generation failed: {str(e)}",
            "dashboard": {
                "shopify_connected": False,
                "social_data_available": False,
                "unified_metrics": {}
            }
        })

@router.get("/insights/revenue-drivers")
async def get_revenue_drivers():
    """Get insights on what social media activities drive revenue"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get data
        social_df = load_all_uploaded_frames()
        sales_result = shopify.get_daily_sales_data(30)
        
        if social_df.empty or not sales_result["success"]:
            return JSONResponse({
                "success": False,
                "message": "Insufficient data for revenue driver analysis"
            })
        
        # Perform comprehensive analysis
        correlation_result = correlate_social_with_sales(social_df, sales_result["daily_data"])
        hashtag_result = analyze_hashtag_revenue_impact(social_df, sales_result["daily_data"])
        
        # Generate strategic insights
        insights = []
        
        if correlation_result.get("correlation_found"):
            insights.extend(correlation_result.get("insights", []))
        
        if hashtag_result.get("success") and hashtag_result.get("top_revenue_hashtags"):
            top_hashtag = hashtag_result["top_revenue_hashtags"][0]
            insights.append(f"Top revenue-driving hashtag: {top_hashtag['hashtag']} (${top_hashtag['avg_revenue_per_post']:.2f} avg per post)")
        
        # Add strategic recommendations
        recommendations = [
            "Focus content creation around high-performing hashtags",
            "Increase posting frequency on days with strong sales correlation",
            "Monitor competitor activity during high-revenue periods",
            "Test content themes that show positive revenue correlation"
        ]
        
        return JSONResponse({
            "success": True,
            "revenue_drivers": {
                "correlation_analysis": correlation_result,
                "hashtag_performance": hashtag_result,
                "key_insights": insights,
                "strategic_recommendations": recommendations,
                "data_quality": {
                    "social_posts": len(social_df),
                    "sales_days": len(sales_result["daily_data"]),
                    "correlation_strength": "Strong" if correlation_result.get("strong_correlations") else "Moderate"
                }
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revenue driver analysis failed: {str(e)}")

@router.delete("/config")
async def remove_shopify_config():
    """Remove Shopify configuration"""
    try:
        config_file = Path("data/config/shopify_config.json")
        if config_file.exists():
            config_file.unlink()
            return JSONResponse({
                "success": True,
                "message": "Shopify configuration removed"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "No configuration found to remove"
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove config: {str(e)}")

@router.get("/health")
async def shopify_health_check():
    """Health check for Shopify integration"""
    try:
        config = load_shopify_config()
        if config:
            shopify = get_shopify_instance()
            if shopify:
                test_result = shopify.test_connection()
                return JSONResponse({
                    "status": "healthy" if test_result["success"] else "unhealthy",
                    "connected": test_result["success"],
                    "shop_name": test_result.get("shop_name", "Unknown"),
                    "message": "Shopify integration operational" if test_result["success"] else test_result.get("error")
                })
        
        return JSONResponse({
            "status": "not_configured",
            "connected": False,
            "message": "Shopify integration not set up"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "connected": False,
            "error": f"Health check failed: {str(e)}"
        })
