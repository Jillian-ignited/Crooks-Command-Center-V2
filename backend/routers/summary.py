# backend/routers/summary.py
""" Summary Overview Router - Now using REAL data from content and media uploads

Replaces all mock data with actual database records
"""

from fastapi import APIRouter
from typing import Dict, Any, List
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
        def get_content_metrics():
            return {"total_briefs": 0, "completed_briefs": 0, "total_media": 0, "engagement_rate": 0, "reach": 0}
        
        @staticmethod
        def get_shopify_metrics():
            return {"total_sales": 0, "total_orders": 0}

router = APIRouter()

@router.get("/overview")
async def get_summary_overview(period: str = "30d") -> Dict[str, Any]:
    """Get summary overview from real content and media data"""
    
    # Get real content metrics
    content_metrics = DataService.get_content_metrics()
    
    # Get Shopify metrics for conversion data
    shopify_metrics = DataService.get_shopify_metrics()
    
    # Calculate period in days
    period_days = _parse_period(period)
    
    # Generate real highlights based on actual data
    highlights = _generate_highlights(content_metrics, shopify_metrics, period_days)
    
    # Build metrics from real data
    metrics = {
        "engagement_rate": content_metrics.get("engagement_rate", 0),
        "reach": content_metrics.get("reach", 0),
        "conversions": shopify_metrics.get("total_orders", 0),
        "content_pieces": content_metrics.get("total_briefs", 0),
        "completed_content": content_metrics.get("completed_briefs", 0),
        "media_assets": content_metrics.get("total_media", 0)
    }
    
    # Calculate performance indicators
    performance = _calculate_performance(content_metrics, shopify_metrics, period_days)
    
    return {
        "period": period,
        "highlights": highlights,
        "metrics": metrics,
        "performance": performance,
        "content_breakdown": _get_content_breakdown(content_metrics),
        "top_performing_content": _get_top_performing_content(),
        "recommendations": _generate_summary_recommendations(content_metrics, shopify_metrics),
        "data_freshness": {
            "content_last_update": content_metrics.get("last_created"),
            "shopify_last_sync": shopify_metrics.get("last_updated")
        },
        "generated_at": datetime.datetime.now().isoformat(),
        "data_source": "real_data"
    }

@router.get("/executive")
async def get_executive_summary() -> Dict[str, Any]:
    """Get executive summary with key metrics and insights"""
    
    content_metrics = DataService.get_content_metrics()
    shopify_metrics = DataService.get_shopify_metrics()
    
    # Calculate key performance indicators
    total_content = content_metrics.get("total_briefs", 0)
    completed_content = content_metrics.get("completed_briefs", 0)
    completion_rate = (completed_content / total_content * 100) if total_content > 0 else 0
    
    # Revenue per content piece (if we have both content and sales data)
    revenue_per_content = 0
    if total_content > 0 and shopify_metrics.get("total_sales", 0) > 0:
        revenue_per_content = shopify_metrics["total_sales"] / total_content
    
    return {
        "executive_summary": {
            "total_content_pieces": total_content,
            "content_completion_rate": round(completion_rate, 1),
            "total_media_assets": content_metrics.get("total_media", 0),
            "estimated_reach": content_metrics.get("reach", 0),
            "revenue_attribution": shopify_metrics.get("total_sales", 0),
            "revenue_per_content": round(revenue_per_content, 2)
        },
        "key_insights": _generate_executive_insights(content_metrics, shopify_metrics),
        "action_items": _generate_action_items(content_metrics, shopify_metrics),
        "period_analyzed": "last_30_days",
        "generated_at": datetime.datetime.now().isoformat()
    }

@router.post("/generate")
async def generate_summary(content_type: str = "overview", period: str = "30d") -> Dict[str, Any]:
    """Generate a new summary report"""
    
    if content_type == "executive":
        return await get_executive_summary()
    else:
        return await get_summary_overview(period)

def _parse_period(period: str) -> int:
    """Parse period string to days"""
    if period.endswith('d'):
        return int(period[:-1])
    elif period.endswith('w'):
        return int(period[:-1]) * 7
    elif period.endswith('m'):
        return int(period[:-1]) * 30
    else:
        return 30  # default

def _generate_highlights(content_metrics: Dict, shopify_metrics: Dict, period_days: int) -> List[str]:
    """Generate highlights based on real data"""
    
    highlights = []
    
    # Content highlights
    total_content = content_metrics.get("total_briefs", 0)
    completed_content = content_metrics.get("completed_briefs", 0)
    
    if total_content > 0:
        highlights.append(f"{total_content} content pieces created")
        
        if completed_content > 0:
            completion_rate = (completed_content / total_content * 100)
            highlights.append(f"{completion_rate:.1f}% content completion rate")
    else:
        highlights.append("No content created yet - opportunity for growth")
    
    # Media highlights
    total_media = content_metrics.get("total_media", 0)
    if total_media > 0:
        highlights.append(f"{total_media} media assets created")
    
    # Sales highlights
    total_sales = shopify_metrics.get("total_sales", 0)
    total_orders = shopify_metrics.get("total_orders", 0)
    
    if total_sales > 0:
        highlights.append(f"${total_sales:,.0f} in total sales")
    
    if total_orders > 0:
        highlights.append(f"{total_orders} orders processed")
    
    # Engagement highlights
    engagement_rate = content_metrics.get("engagement_rate", 0)
    if engagement_rate > 0:
        highlights.append(f"{engagement_rate:.1f}% engagement rate")
    
    # Default highlight if no data
    if not highlights:
        highlights.append("Upload data to see performance highlights")
    
    return highlights

def _calculate_performance(content_metrics: Dict, shopify_metrics: Dict, period_days: int) -> Dict[str, Any]:
    """Calculate performance indicators"""
    
    # Content performance
    total_content = content_metrics.get("total_briefs", 0)
    completed_content = content_metrics.get("completed_briefs", 0)
    
    content_velocity = total_content / period_days if period_days > 0 else 0
    completion_rate = (completed_content / total_content * 100) if total_content > 0 else 0
    
    # Sales performance
    total_sales = shopify_metrics.get("total_sales", 0)
    total_orders = shopify_metrics.get("total_orders", 0)
    
    daily_sales = total_sales / period_days if period_days > 0 else 0
    daily_orders = total_orders / period_days if period_days > 0 else 0
    
    return {
        "content_velocity": round(content_velocity, 2),
        "completion_rate": round(completion_rate, 1),
        "daily_sales": round(daily_sales, 2),
        "daily_orders": round(daily_orders, 1),
        "revenue_per_order": round(total_sales / total_orders, 2) if total_orders > 0 else 0
    }

def _get_content_breakdown(content_metrics: Dict) -> Dict[str, Any]:
    """Get breakdown of content types"""
    
    return {
        "social_media": content_metrics.get("social_media", 0),
        "email_campaigns": content_metrics.get("email_campaigns", 0),
        "total_briefs": content_metrics.get("total_briefs", 0),
        "completed_briefs": content_metrics.get("completed_briefs", 0),
        "media_assets": content_metrics.get("total_media", 0)
    }

def _get_top_performing_content() -> List[Dict[str, Any]]:
    """Get top performing content (placeholder for now)"""
    
    # This would query actual performance data from database
    # For now, return empty list since we need engagement/performance tracking
    return []

def _generate_summary_recommendations(content_metrics: Dict, shopify_metrics: Dict) -> List[Dict[str, Any]]:
    """Generate recommendations based on summary data"""
    
    recommendations = []
    
    # Content recommendations
    total_content = content_metrics.get("total_briefs", 0)
    completed_content = content_metrics.get("completed_briefs", 0)
    
    if total_content == 0:
        recommendations.append({
            "type": "content",
            "priority": "high",
            "title": "Start Content Creation",
            "description": "No content found. Begin creating content briefs to establish your brand presence.",
            "action": "Create your first content brief in the Content Creation module"
        })
    elif completed_content < total_content:
        incomplete = total_content - completed_content
        recommendations.append({
            "type": "content",
            "priority": "medium", 
            "title": "Complete Pending Content",
            "description": f"{incomplete} content pieces are incomplete. Finish them to maximize your content impact.",
            "action": "Review and complete pending content briefs"
        })
    
    # Sales recommendations
    total_sales = shopify_metrics.get("total_sales", 0)
    if total_sales == 0:
        recommendations.append({
            "type": "data",
            "priority": "high",
            "title": "Upload Sales Data",
            "description": "No sales data found. Upload Shopify reports to track revenue performance.",
            "action": "Upload Shopify CSV files through the Intelligence module"
        })
    
    # Media recommendations
    total_media = content_metrics.get("total_media", 0)
    if total_media == 0 and total_content > 0:
        recommendations.append({
            "type": "media",
            "priority": "medium",
            "title": "Add Media Assets",
            "description": "Content exists but no media assets found. Add visuals to enhance content performance.",
            "action": "Upload images and videos through the Media module"
        })
    
    return recommendations

def _generate_executive_insights(content_metrics: Dict, shopify_metrics: Dict) -> List[str]:
    """Generate executive insights from data"""
    
    insights = []
    
    # Content insights
    total_content = content_metrics.get("total_briefs", 0)
    completed_content = content_metrics.get("completed_briefs", 0)
    
    if total_content > 0:
        completion_rate = (completed_content / total_content * 100)
        if completion_rate >= 80:
            insights.append(f"Strong content execution with {completion_rate:.1f}% completion rate")
        elif completion_rate >= 50:
            insights.append(f"Moderate content completion at {completion_rate:.1f}% - room for improvement")
        else:
            insights.append(f"Low content completion at {completion_rate:.1f}% - needs attention")
    
    # Sales insights
    total_sales = shopify_metrics.get("total_sales", 0)
    total_orders = shopify_metrics.get("total_orders", 0)
    
    if total_sales > 0 and total_orders > 0:
        aov = total_sales / total_orders
        insights.append(f"Average order value is ${aov:.2f}")
        
        if aov > 100:
            insights.append("High-value customer base with strong AOV")
        elif aov > 50:
            insights.append("Moderate AOV with potential for upselling")
        else:
            insights.append("Low AOV suggests need for product bundling or premium offerings")
    
    # Cross-channel insights
    if total_content > 0 and total_sales > 0:
        revenue_per_content = total_sales / total_content
        insights.append(f"Each content piece generates approximately ${revenue_per_content:.2f} in revenue")
    
    # Default insight if no data
    if not insights:
        insights.append("Upload data to generate actionable insights")
    
    return insights

def _generate_action_items(content_metrics: Dict, shopify_metrics: Dict) -> List[Dict[str, Any]]:
    """Generate action items for executives"""
    
    action_items = []
    
    # Content action items
    total_content = content_metrics.get("total_briefs", 0)
    completed_content = content_metrics.get("completed_briefs", 0)
    
    if total_content == 0:
        action_items.append({
            "priority": "high",
            "item": "Develop content strategy and create first content briefs",
            "owner": "Marketing Team",
            "timeline": "1 week"
        })
    elif completed_content < total_content:
        action_items.append({
            "priority": "medium",
            "item": f"Complete {total_content - completed_content} pending content pieces",
            "owner": "Content Team", 
            "timeline": "2 weeks"
        })
    
    # Data action items
    if shopify_metrics.get("total_sales", 0) == 0:
        action_items.append({
            "priority": "high",
            "item": "Upload Shopify sales data for performance tracking",
            "owner": "Operations Team",
            "timeline": "3 days"
        })
    
    # Media action items
    if content_metrics.get("total_media", 0) == 0 and total_content > 0:
        action_items.append({
            "priority": "medium",
            "item": "Create visual assets to support content marketing",
            "owner": "Creative Team",
            "timeline": "1 week"
        })
    
    return action_items

