from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.shopify_integration_CONVERSION import (
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
    include_conversion: bool = True

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
                "shop_info": result["config"]["shop_info"],
                "features": result["config"]["features"]
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
                "features": config.get("features", {}),
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
    """Pull and sync sales data with conversion metrics from Shopify"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Pull sales data with conversion tracking
        sales_result = shopify.get_daily_sales_data(request.days_back)
        
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=sales_result["error"])
        
        return JSONResponse({
            "success": True,
            "message": f"Synced {request.days_back} days of sales data with conversion metrics",
            "data": sales_result,
            "conversion_summary": sales_result["summary"]["conversion_metrics"] if "conversion_metrics" in sales_result["summary"] else {}
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales sync failed: {str(e)}")

@router.post("/sync/traffic")
async def sync_traffic_data(request: AnalysisRequest):
    """Pull and sync traffic data with conversion funnel from Shopify"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Pull traffic data with conversion funnel
        traffic_result = shopify.get_traffic_data(request.days_back)
        
        if not traffic_result["success"]:
            raise HTTPException(status_code=500, detail=traffic_result["error"])
        
        return JSONResponse({
            "success": True,
            "message": f"Synced {request.days_back} days of traffic data with conversion funnel",
            "data": traffic_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Traffic sync failed: {str(e)}")

@router.post("/sync/products")
async def sync_product_performance():
    """Pull product performance data with conversion rates from Shopify"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Pull product data with conversion metrics
        product_result = shopify.get_product_performance(30)
        
        if not product_result["success"]:
            raise HTTPException(status_code=500, detail=product_result["error"])
        
        return JSONResponse({
            "success": True,
            "message": "Synced product performance data with conversion rates",
            "data": product_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product sync failed: {str(e)}")

@router.post("/analyze/correlation")
async def analyze_social_sales_correlation(request: AnalysisRequest):
    """Analyze correlation between social media activity, sales, and conversions"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get social media data
        social_df = load_all_uploaded_frames()
        if social_df.empty:
            raise HTTPException(status_code=400, detail="No social media data available. Upload competitor data first.")
        
        # Get sales data with conversion metrics
        sales_result = shopify.get_daily_sales_data(request.days_back)
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to get sales data: {sales_result['error']}")
        
        # Perform enhanced correlation analysis
        correlation_result = correlate_social_with_sales(social_df, sales_result["daily_data"])
        
        return JSONResponse({
            "success": True,
            "correlation_analysis": correlation_result,
            "sales_summary": sales_result["summary"],
            "conversion_insights": {
                "overall_conversion_rate": sales_result["summary"]["conversion_metrics"]["overall_conversion_rate"],
                "revenue_per_session": sales_result["summary"]["conversion_metrics"]["revenue_per_session"],
                "social_conversion_impact": correlation_result.get("conversion_correlations", {})
            },
            "social_data_points": len(social_df)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correlation analysis failed: {str(e)}")

@router.post("/analyze/hashtags")
async def analyze_hashtag_revenue_correlation():
    """Analyze which hashtags correlate with revenue and conversion spikes"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get social media data
        social_df = load_all_uploaded_frames()
        if social_df.empty:
            raise HTTPException(status_code=400, detail="No social media data available. Upload competitor data first.")
        
        # Get sales data with conversion metrics
        sales_result = shopify.get_daily_sales_data(30)
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to get sales data: {sales_result['error']}")
        
        # Analyze hashtag impact on revenue and conversions
        hashtag_result = analyze_hashtag_revenue_impact(social_df, sales_result["daily_data"])
        
        return JSONResponse({
            "success": True,
            "hashtag_analysis": hashtag_result,
            "conversion_insights": hashtag_result.get("conversion_insights", {}),
            "message": "Hashtag revenue and conversion correlation analysis complete"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashtag analysis failed: {str(e)}")

@router.get("/conversion/funnel")
async def get_conversion_funnel():
    """Get detailed conversion funnel analysis"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get traffic data with conversion funnel
        traffic_result = shopify.get_traffic_data(30)
        if not traffic_result["success"]:
            raise HTTPException(status_code=500, detail=traffic_result["error"])
        
        # Get sales data for additional context
        sales_result = shopify.get_daily_sales_data(30)
        
        funnel_data = {
            "conversion_funnel": traffic_result.get("conversion_funnel", {}),
            "traffic_summary": traffic_result.get("traffic_summary", {}),
            "optimization_opportunities": []
        }
        
        # Add optimization insights
        if traffic_result["success"] and sales_result["success"]:
            funnel = traffic_result["conversion_funnel"]
            conversion_rates = funnel.get("conversion_rates", {})
            
            # Identify optimization opportunities
            if conversion_rates.get("session_to_product_view", 0) < 50:
                funnel_data["optimization_opportunities"].append({
                    "stage": "Product Discovery",
                    "current_rate": conversion_rates.get("session_to_product_view", 0),
                    "opportunity": "Improve homepage and navigation to increase product page visits",
                    "priority": "High"
                })
            
            if conversion_rates.get("session_to_cart", 0) < 10:
                funnel_data["optimization_opportunities"].append({
                    "stage": "Add to Cart",
                    "current_rate": conversion_rates.get("session_to_cart", 0),
                    "opportunity": "Optimize product pages and add compelling CTAs",
                    "priority": "High"
                })
            
            if conversion_rates.get("cart_to_checkout", 0) < 40:
                funnel_data["optimization_opportunities"].append({
                    "stage": "Cart to Checkout",
                    "current_rate": conversion_rates.get("cart_to_checkout", 0),
                    "opportunity": "Reduce cart abandonment with better UX and incentives",
                    "priority": "Medium"
                })
            
            if conversion_rates.get("checkout_to_purchase", 0) < 25:
                funnel_data["optimization_opportunities"].append({
                    "stage": "Checkout Completion",
                    "current_rate": conversion_rates.get("checkout_to_purchase", 0),
                    "opportunity": "Streamline checkout process and reduce friction",
                    "priority": "High"
                })
        
        return JSONResponse({
            "success": True,
            "funnel_analysis": funnel_data
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion funnel analysis failed: {str(e)}")

@router.get("/conversion/sources")
async def get_traffic_source_conversions():
    """Get conversion rates by traffic source"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get sales data with traffic source breakdown
        sales_result = shopify.get_daily_sales_data(30)
        if not sales_result["success"]:
            raise HTTPException(status_code=500, detail=sales_result["error"])
        
        traffic_sources = sales_result["summary"].get("traffic_sources", {})
        total_orders = sales_result["summary"]["total_orders"]
        conversion_metrics = sales_result["summary"]["conversion_metrics"]
        
        # Calculate conversion rates by source
        source_conversions = []
        for source, orders in traffic_sources.items():
            estimated_sessions = orders * 10  # Rough estimate
            conversion_rate = (orders / estimated_sessions) * 100 if estimated_sessions > 0 else 0
            
            source_conversions.append({
                "source": source,
                "orders": orders,
                "estimated_sessions": estimated_sessions,
                "conversion_rate": round(conversion_rate, 2),
                "percentage_of_total_orders": round((orders / total_orders) * 100, 1) if total_orders > 0 else 0
            })
        
        # Sort by conversion rate
        source_conversions.sort(key=lambda x: x["conversion_rate"], reverse=True)
        
        return JSONResponse({
            "success": True,
            "traffic_source_conversions": source_conversions,
            "overall_metrics": conversion_metrics,
            "insights": {
                "best_converting_source": source_conversions[0]["source"] if source_conversions else None,
                "total_sources": len(source_conversions),
                "social_media_performance": [s for s in source_conversions if "social" in s["source"]]
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Traffic source conversion analysis failed: {str(e)}")

@router.get("/dashboard")
async def get_unified_dashboard():
    """Get unified performance dashboard with conversion metrics"""
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
        
        # Get sales data with conversion metrics
        sales_result = shopify.get_daily_sales_data(30)
        sales_available = sales_result["success"]
        
        # Get traffic data with conversion funnel
        traffic_result = shopify.get_traffic_data(30)
        traffic_available = traffic_result["success"]
        
        dashboard_data = {
            "shopify_connected": True,
            "social_data_available": social_available,
            "sales_data_available": sales_available,
            "traffic_data_available": traffic_available,
            "last_updated": datetime.now().isoformat()
        }
        
        if sales_available:
            dashboard_data["sales_metrics"] = sales_result["summary"]
            dashboard_data["conversion_metrics"] = sales_result["summary"]["conversion_metrics"]
        
        if traffic_available:
            dashboard_data["traffic_metrics"] = traffic_result["traffic_summary"]
            dashboard_data["conversion_funnel"] = traffic_result["conversion_funnel"]
        
        if social_available:
            dashboard_data["social_metrics"] = {
                "total_posts": len(social_df),
                "brands_tracked": social_df['brand'].nunique() if 'brand' in social_df.columns else 0,
                "date_range": f"{social_df['date'].min()} to {social_df['date'].max()}" if 'date' in social_df.columns else "Unknown"
            }
        
        # If both social and sales data are available, perform correlation analysis
        if social_available and sales_available:
            correlation_result = correlate_social_with_sales(social_df, sales_result["daily_data"])
            dashboard_data["correlation_insights"] = correlation_result
            
            # Hashtag analysis with conversion impact
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
    """Get comprehensive insights on what social media activities drive revenue and conversions"""
    try:
        shopify = get_shopify_instance()
        if not shopify:
            raise HTTPException(status_code=400, detail="Shopify not configured. Run /setup first.")
        
        # Get data
        social_df = load_all_uploaded_frames()
        sales_result = shopify.get_daily_sales_data(30)
        traffic_result = shopify.get_traffic_data(30)
        
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
        conversion_insights = []
        
        if correlation_result.get("correlation_found"):
            insights.extend(correlation_result.get("insights", []))
            
            # Add conversion-specific insights
            conv_corr = correlation_result.get("conversion_correlations", {})
            if conv_corr.get("posts_conversion", 0) > 0.3:
                conversion_insights.append(f"Social media activity positively impacts conversion rates (r={conv_corr['posts_conversion']:.2f})")
            if conv_corr.get("hashtags_conversion", 0) > 0.3:
                conversion_insights.append(f"Strategic hashtag use improves conversion performance (r={conv_corr['hashtags_conversion']:.2f})")
        
        if hashtag_result.get("success") and hashtag_result.get("top_revenue_hashtags"):
            top_hashtag = hashtag_result["top_revenue_hashtags"][0]
            insights.append(f"Top revenue-driving hashtag: {top_hashtag['hashtag']} (${top_hashtag['avg_revenue_per_post']:.2f} avg per post)")
            
            # Add conversion insights for hashtags
            conv_insights = hashtag_result.get("conversion_insights", {})
            if conv_insights.get("best_converting_hashtag"):
                conversion_insights.append(f"Best converting hashtag: {conv_insights['best_converting_hashtag']}")
        
        # Add strategic recommendations
        recommendations = [
            "Focus content creation around high-performing hashtags",
            "Increase posting frequency on days with strong sales correlation",
            "Monitor competitor activity during high-revenue periods",
            "Test content themes that show positive revenue correlation",
            "Optimize conversion funnel based on traffic source performance"
        ]
        
        # Add conversion-specific recommendations
        if traffic_result["success"]:
            funnel = traffic_result.get("conversion_funnel", {})
            conversion_rates = funnel.get("conversion_rates", {})
            
            if conversion_rates.get("session_to_cart", 0) < 15:
                recommendations.append("Improve product page conversion with better CTAs and social proof")
            if conversion_rates.get("cart_to_checkout", 0) < 50:
                recommendations.append("Reduce cart abandonment with exit-intent offers and simplified checkout")
        
        return JSONResponse({
            "success": True,
            "revenue_drivers": {
                "correlation_analysis": correlation_result,
                "hashtag_performance": hashtag_result,
                "key_insights": insights,
                "conversion_insights": conversion_insights,
                "strategic_recommendations": recommendations,
                "data_quality": {
                    "social_posts": len(social_df),
                    "sales_days": len(sales_result["daily_data"]),
                    "correlation_strength": "Strong" if correlation_result.get("strong_correlations") else "Moderate",
                    "conversion_data_available": traffic_result["success"] if traffic_result else False
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
    """Health check for Shopify integration with conversion tracking status"""
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
                    "features": config.get("features", {}),
                    "message": "Shopify integration with conversion tracking operational" if test_result["success"] else test_result.get("error")
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
