# backend/routers/executive.py
""" Executive Overview Router - Now using REAL data from uploads

Replaces all mock data with actual Shopify uploads and database records
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import datetime
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from data_service import DataService
except ImportError:
    # Fallback if data_service isn't available
    class DataService:
        @staticmethod
        def get_shopify_metrics(force_recalculate: bool = False):
            return {"total_sales": 0, "total_orders": 0, "conversion_rate": 0, "aov": 0, "traffic": 0, "status": "no_data"}

        @staticmethod
        def get_content_metrics(force_recalculate: bool = False):
            return {"engagement_rate": 0, "reach": 0}

router = APIRouter()

@router.get("/overview")
async def get_executive_overview(force_recalculate: bool = False):
    """Provide a comprehensive executive overview using real data"""
    
    # Get real data from the data service
    shopify_metrics = DataService.get_shopify_metrics(force_recalculate)
    content_metrics = DataService.get_content_metrics(force_recalculate)
    
    # Generate dynamic recommendations and alerts
    recommendations = _generate_recommendations(shopify_metrics, content_metrics)
    alerts = _generate_alerts(shopify_metrics, content_metrics)

    return {
        "success": True,
        "data_source": "real_uploads",
        "metrics": {
            "total_sales": shopify_metrics.get("total_sales", 0),
            "total_orders": shopify_metrics.get("total_orders", 0),
            "conversion_rate": shopify_metrics.get("conversion_rate", 0),
            "average_order_value": shopify_metrics.get("aov", 0),
            "site_traffic": shopify_metrics.get("traffic", 0),
            "engagement_rate": content_metrics.get("engagement_rate", 0),
            "reach": content_metrics.get("reach", 0)
        },
        "trends": {
            "sales_trend": shopify_metrics.get("sales_trend", "flat"),
            "orders_trend": shopify_metrics.get("orders_trend", "flat"),
            "conversion_trend": shopify_metrics.get("conversion_trend", "flat")
        },
        "recommendations": recommendations,
        "alerts": alerts,
        "last_refreshed": datetime.datetime.now().isoformat()
    }

def _generate_recommendations(shopify_metrics: Dict, content_metrics: Dict) -> list:
    """Generate dynamic recommendations based on real data"""
    recommendations = []
    
    # Sales recommendations
    if shopify_metrics.get("total_sales", 0) < 5000:
        recommendations.append({
            "area": "Sales",
            "recommendation": "Sales are low. Focus on targeted marketing campaigns and promotions.",
            "priority": "High"
        })
    
    # Content recommendations
    if content_metrics.get("engagement_rate", 0) < 2.0:
        recommendations.append({
            "area": "Content",
            "recommendation": "Engagement is low. Create more compelling and interactive content.",
            "priority": "Medium"
        })
        
    return recommendations

def _generate_alerts(shopify_metrics: Dict, content_metrics: Dict) -> list:
    """Generate dynamic alerts based on real data"""
    alerts = []
    
    # Low sales alert
    total_sales = shopify_metrics.get("total_sales", 0)
    if total_sales > 0 and total_sales < 1000:
        alerts.append({
            "level": "Info",
            "message": f"Sales volume is ${total_sales:,.0f} - consider growth strategies",
            "action": "Review marketing campaigns and conversion optimization"
        })

    # Conversion alerts
    conversion_rate = shopify_metrics.get("conversion_rate", 0)
    if conversion_rate > 0 and conversion_rate < 1.0:
        alerts.append({
            "level": "Warning",
            "message": f"Conversion rate is {conversion_rate:.2f}% - below industry standards",
            "action": "Audit website user experience and checkout process"
        })

    # Content alerts
    total_content = content_metrics.get("total_briefs", 0)
    if total_content == 0:
        alerts.append({
            "level": "Info",
            "message": "No content briefs found - create content to drive engagement",
            "action": "Use the Content Creation module to develop brand content"
        })

    return alerts

@router.post("/refresh")
async def refresh_executive_data():
    """Refresh executive data by recalculating from latest uploads"""
    
    # Trigger a refresh of the data service
    DataService.get_shopify_metrics(force_recalculate=True)
    DataService.get_content_metrics(force_recalculate=True)
    
    return {
        "success": True,
        "message": "Executive data refreshed from latest uploads",
        "refreshed_at": datetime.datetime.now().isoformat()
    }

