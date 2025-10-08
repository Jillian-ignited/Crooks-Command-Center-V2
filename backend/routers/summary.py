from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from backend.database import get_db
from backend.models import (
    Intelligence, 
    CompetitorIntel, 
    ShopifyMetric,
    ShopifyOrder,
    Deliverable,
    Campaign
)
import json

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get executive dashboard summary with real data from all modules"""
    
    # Intelligence Stats
    total_intelligence = db.query(func.count(Intelligence.id)).scalar() or 0
    
    intelligence_by_category = db.query(
        Intelligence.category,
        func.count(Intelligence.id).label('count')
    ).group_by(Intelligence.category).all()
    
    recent_intelligence = db.query(Intelligence).order_by(
        desc(Intelligence.created_at)
    ).limit(5).all()
    
    # Competitive Intel Stats
    total_competitors = db.query(
        func.count(func.distinct(CompetitorIntel.competitor_name))
    ).scalar() or 0
    
    total_competitive_intel = db.query(func.count(CompetitorIntel.id)).scalar() or 0
    
    competitive_by_category = db.query(
        CompetitorIntel.category,
        func.count(CompetitorIntel.id).label('count')
    ).group_by(CompetitorIntel.category).all()
    
    recent_competitive = db.query(CompetitorIntel).order_by(
        desc(CompetitorIntel.created_at)
    ).limit(5).all()
    
    # Shopify Performance (Last 30 days) - Using ShopifyMetric
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    shopify_metrics = db.query(ShopifyMetric).filter(
        ShopifyMetric.period_start >= thirty_days_ago
    ).all()
    
    total_orders = sum(m.total_orders for m in shopify_metrics if m.total_orders)
    total_revenue = sum(m.total_revenue for m in shopify_metrics if m.total_revenue)
    total_sessions = sum(m.total_sessions for m in shopify_metrics if m.total_sessions)
    
    avg_conversion = (sum(m.conversion_rate for m in shopify_metrics if m.conversion_rate) / len(shopify_metrics)) if shopify_metrics else 0
    avg_aov = total_revenue / total_orders if total_orders > 0 else 0
    
    # Get trend (compare to previous 30 days)
    sixty_days_ago = datetime.now(timezone.utc) - timedelta(days=60)
    previous_metrics = db.query(ShopifyMetric).filter(
        ShopifyMetric.period_start >= sixty_days_ago,
        ShopifyMetric.period_start < thirty_days_ago
    ).all()
    
    prev_revenue = sum(m.total_revenue for m in previous_metrics if m.total_revenue)
    revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    prev_orders = sum(m.total_orders for m in previous_metrics if m.total_orders)
    orders_change = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
    
    # Deliverables Status
    total_deliverables = db.query(func.count(Deliverable.id)).scalar() or 0
    
    deliverables_by_status = db.query(
        Deliverable.status,
        func.count(Deliverable.id).label('count')
    ).group_by(Deliverable.status).all()
    
    overdue_deliverables = db.query(Deliverable).filter(
        Deliverable.status != 'completed',
        Deliverable.due_date < datetime.now(timezone.utc)
    ).count()
    
    upcoming_deliverables = db.query(Deliverable).filter(
        Deliverable.status.in_(['in_progress', 'not_started']),
        Deliverable.due_date >= datetime.now(timezone.utc),
        Deliverable.due_date <= datetime.now(timezone.utc) + timedelta(days=7)
    ).all()
    
    # Campaign Stats
    total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0
    active_campaigns = db.query(Campaign).filter(Campaign.status == 'active').count()
    
    # Generate AI Insights from actual data
    insights = []
    
    if revenue_change > 10:
        insights.append({
            "type": "positive",
            "title": "Strong Revenue Growth",
            "description": f"Revenue increased {revenue_change:.1f}% vs. previous period"
        })
    elif revenue_change < -10:
        insights.append({
            "type": "alert",
            "title": "Revenue Decline",
            "description": f"Revenue decreased {abs(revenue_change):.1f}% vs. previous period"
        })
    
    if overdue_deliverables > 0:
        insights.append({
            "type": "alert",
            "title": "Overdue Deliverables",
            "description": f"{overdue_deliverables} deliverable(s) are past due"
        })
    
    if total_competitive_intel > 0:
        insights.append({
            "type": "info",
            "title": "Competitive Intelligence Active",
            "description": f"Tracking {total_competitors} competitors with {total_competitive_intel} intel entries"
        })
    
    if avg_conversion > 0 and avg_conversion < 1.5:
        insights.append({
            "type": "opportunity",
            "title": "Conversion Rate Below Industry Average",
            "description": f"Current CR {avg_conversion:.2f}% vs. streetwear industry avg ~2-3%"
        })
    
    if active_campaigns == 0 and total_campaigns > 0:
        insights.append({
            "type": "opportunity",
            "title": "No Active Campaigns",
            "description": "Consider activating one of your planned campaigns"
        })
    
    return {
        "intelligence": {
            "total_entries": total_intelligence,
            "by_category": {cat: count for cat, count in intelligence_by_category},
            "recent": [
                {
                    "id": e.id,
                    "title": e.title,
                    "category": e.category,
                    "created_at": e.created_at.isoformat()
                }
                for e in recent_intelligence
            ]
        },
        "competitive": {
            "total_competitors": total_competitors,
            "total_intel_entries": total_competitive_intel,
            "by_category": {cat: count for cat, count in competitive_by_category},
            "recent": [
                {
                    "id": c.id,
                    "competitor_name": c.competitor_name,
                    "category": c.category,
                    "created_at": c.created_at.isoformat()
                }
                for c in recent_competitive
            ]
        },
        "shopify": {
            "period": "Last 30 Days",
            "total_orders": int(total_orders),
            "total_revenue": round(total_revenue, 2),
            "total_sessions": int(total_sessions),
            "avg_conversion_rate": round(avg_conversion, 2),
            "avg_order_value": round(avg_aov, 2),
            "revenue_change_percent": round(revenue_change, 1),
            "orders_change_percent": round(orders_change, 1)
        },
        "agency": {
            "total_deliverables": total_deliverables,
            "by_status": {status: count for status, count in deliverables_by_status},
            "overdue": overdue_deliverables,
            "upcoming_due": [
                {
                    "id": d.id,
                    "title": d.title,
                    "due_date": d.due_date.isoformat(),
                    "status": d.status
                }
                for d in upcoming_deliverables
            ]
        },
        "campaigns": {
            "total": total_campaigns,
            "active": active_campaigns
        },
        "insights": insights,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@router.get("/performance-trends")
def get_performance_trends(days: int = 90, db: Session = Depends(get_db)):
    """Get performance trends over time"""
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    metrics = db.query(ShopifyMetric).filter(
        ShopifyMetric.period_start >= start_date
    ).order_by(ShopifyMetric.period_start).all()
    
    trends = []
    for metric in metrics:
        trends.append({
            "date": metric.period_start.isoformat(),
            "orders": metric.total_orders or 0,
            "revenue": round(metric.total_revenue, 2) if metric.total_revenue else 0,
            "sessions": metric.total_sessions or 0,
            "conversion_rate": round(metric.conversion_rate, 2) if metric.conversion_rate else 0,
            "aov": round(metric.avg_order_value, 2) if metric.avg_order_value else 0
        })
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.now(timezone.utc).isoformat(),
        "data_points": len(trends),
        "trends": trends
    }

@router.get("/competitive-landscape")
def get_competitive_landscape(db: Session = Depends(get_db)):
    """Get competitive landscape analysis"""
    
    competitors = db.query(
        CompetitorIntel.competitor_name,
        func.count(CompetitorIntel.id).label('intel_count'),
        func.max(CompetitorIntel.created_at).label('last_update')
    ).group_by(CompetitorIntel.competitor_name).all()
    
    landscape = []
    for comp in competitors:
        # Get latest intel for this competitor
        latest = db.query(CompetitorIntel).filter(
            CompetitorIntel.competitor_name == comp.competitor_name
        ).order_by(desc(CompetitorIntel.created_at)).first()
        
        # Get intel by category
        by_category = db.query(
            CompetitorIntel.category,
            func.count(CompetitorIntel.id).label('count')
        ).filter(
            CompetitorIntel.competitor_name == comp.competitor_name
        ).group_by(CompetitorIntel.category).all()
        
        landscape.append({
            "competitor": comp.competitor_name,
            "intel_entries": comp.intel_count,
            "last_updated": comp.last_update.isoformat(),
            "latest_summary": latest.ai_analysis if latest else None,
            "coverage": {cat: count for cat, count in by_category}
        })
    
    return {
        "total_competitors": len(competitors),
        "landscape": landscape
    }

@router.get("/content-readiness")
def get_content_readiness(db: Session = Depends(get_db)):
    """Assess content and deliverable readiness for campaigns"""
    
    # Get upcoming campaigns
    thirty_days = datetime.now(timezone.utc) + timedelta(days=30)
    upcoming_campaigns = db.query(Campaign).filter(
        Campaign.start_date >= datetime.now(timezone.utc),
        Campaign.start_date <= thirty_days,
        Campaign.status.in_(['planning', 'active'])
    ).all()
    
    readiness = []
    for campaign in upcoming_campaigns:
        # Check if deliverables exist for this campaign
        related_deliverables = db.query(Deliverable).filter(
            Deliverable.campaign_id == campaign.id
        ).all()
        
        completed = sum(1 for d in related_deliverables if d.status == 'completed')
        total_tasks = len(related_deliverables)
        
        readiness.append({
            "campaign": campaign.name,
            "date": campaign.start_date.isoformat() if campaign.start_date else None,
            "days_until": (campaign.start_date - datetime.now(timezone.utc)).days if campaign.start_date else None,
            "tasks_completed": completed,
            "tasks_total": total_tasks,
            "readiness_score": (completed / total_tasks * 100) if total_tasks > 0 else 0,
            "status": "ready" if completed == total_tasks else "in_progress" if completed > 0 else "not_started"
        })
    
    return {
        "upcoming_campaigns": len(upcoming_campaigns),
        "readiness": readiness
    }
