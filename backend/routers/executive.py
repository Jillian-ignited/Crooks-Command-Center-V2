from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..database import get_db
from ..models import Intelligence, Campaign, Deliverable, ShopifyMetric, CompetitorIntel

router = APIRouter()


@router.get("/overview")
def get_executive_overview(db: Session = Depends(get_db)):
    """Get executive dashboard overview"""
    
    today = datetime.now(timezone.utc)
    thirty_days_ago = today - timedelta(days=30)
    
    # Intelligence stats
    total_intelligence = db.query(Intelligence).count()
    recent_intelligence = db.query(Intelligence).filter(
        Intelligence.created_at >= thirty_days_ago
    ).count()
    
    # Campaign stats
    total_campaigns = db.query(Campaign).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()
    
    # Deliverables stats
    total_deliverables = db.query(Deliverable).count()
    completed_deliverables = db.query(Deliverable).filter(
        Deliverable.status == "completed"
    ).count()
    overdue_deliverables = db.query(Deliverable).filter(
        Deliverable.due_date < today,
        Deliverable.status != "completed"
    ).count()
    
    # Shopify stats (if available)
    try:
        shopify_metrics = db.query(ShopifyMetric).filter(
            ShopifyMetric.period_start >= thirty_days_ago
        ).all()
        
        total_revenue = sum(m.total_revenue for m in shopify_metrics)
        total_orders = sum(m.total_orders for m in shopify_metrics)
    except:
        total_revenue = 0
        total_orders = 0
    
    # Competitive intel stats
    total_competitive_intel = db.query(CompetitorIntel).count()
    threats = db.query(CompetitorIntel).filter(
        CompetitorIntel.sentiment == "threat"
    ).count()
    
    return {
        "intelligence": {
            "total": total_intelligence,
            "recent_30d": recent_intelligence
        },
        "campaigns": {
            "total": total_campaigns,
            "active": active_campaigns
        },
        "deliverables": {
            "total": total_deliverables,
            "completed": completed_deliverables,
            "overdue": overdue_deliverables,
            "completion_rate": round((completed_deliverables / total_deliverables * 100), 1) if total_deliverables > 0 else 0
        },
        "revenue": {
            "total_30d": round(total_revenue, 2),
            "orders_30d": total_orders,
            "avg_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0
        },
        "competitive": {
            "total_intel": total_competitive_intel,
            "threats": threats
        },
        "generated_at": today.isoformat()
    }


@router.get("/alerts")
def get_executive_alerts(db: Session = Depends(get_db)):
    """Get critical alerts for executive dashboard"""
    
    today = datetime.now(timezone.utc)
    alerts = []
    
    # Overdue deliverables
    overdue = db.query(Deliverable).filter(
        Deliverable.due_date < today,
        Deliverable.status != "completed"
    ).order_by(Deliverable.due_date).limit(5).all()
    
    for d in overdue:
        days_overdue = (today - d.due_date).days
        alerts.append({
            "type": "deliverable_overdue",
            "severity": "critical" if days_overdue > 7 else "warning",
            "title": f"Deliverable {days_overdue} days overdue",
            "message": d.title,
            "entity_id": d.id
        })
    
    # Upcoming high-priority deliverables
    upcoming = db.query(Deliverable).filter(
        Deliverable.due_date >= today,
        Deliverable.due_date <= today + timedelta(days=7),
        Deliverable.priority == "high",
        Deliverable.status != "completed"
    ).limit(3).all()
    
    for d in upcoming:
        days_until = (d.due_date - today).days
        alerts.append({
            "type": "deliverable_upcoming",
            "severity": "info",
            "title": f"High-priority deliverable due in {days_until} days",
            "message": d.title,
            "entity_id": d.id
        })
    
    # Recent competitive threats
    threats = db.query(CompetitorIntel).filter(
        CompetitorIntel.sentiment == "threat",
        CompetitorIntel.created_at >= today - timedelta(days=7)
    ).limit(3).all()
    
    for t in threats:
        alerts.append({
            "type": "competitive_threat",
            "severity": "warning",
            "title": f"Competitive threat: {t.competitor_name}",
            "message": t.content[:100] + "..." if len(t.content) > 100 else t.content,
            "entity_id": t.id
        })
    
    return {
        "alerts": alerts,
        "total": len(alerts)
    }
