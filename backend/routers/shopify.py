from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, text
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..database import get_db
from ..models import ShopifyMetric

router = APIRouter()


@router.get("/dashboard")
def get_shopify_dashboard(
    period: str = "30d",
    db: Session = Depends(get_db)
):
    """Get Shopify analytics dashboard"""
    
    # Parse period
    days = int(period.replace('d', ''))
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    try:
        # Get metrics for period
        metrics = db.query(ShopifyMetric).filter(
            and_(
                ShopifyMetric.period_type == "daily",
                ShopifyMetric.period_start >= start_date,
                ShopifyMetric.period_start <= end_date
            )
        ).order_by(ShopifyMetric.period_start).all()
        
        # Calculate totals
        total_revenue = sum(m.total_revenue for m in metrics)
        total_orders = sum(m.total_orders for m in metrics)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "avg_order_value": round(avg_order_value, 2),
                "conversion_rate": round(sum(m.conversion_rate for m in metrics) / len(metrics), 2) if metrics else 0
            },
            "daily_metrics": [
                {
                    "date": m.period_start.isoformat(),
                    "revenue": m.total_revenue,
                    "orders": m.total_orders,
                    "aov": m.avg_order_value,
                    "sessions": m.total_sessions,
                    "conversion_rate": m.conversion_rate
                }
                for m in metrics
            ]
        }
    except Exception as e:
        print(f"[Shopify] Dashboard error: {e}")
        # Return empty data if no metrics exist yet
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_revenue": 0,
                "total_orders": 0,
                "avg_order_value": 0,
                "conversion_rate": 0
            },
            "daily_metrics": []
        }


@router.post("/metrics")
def create_shopify_metric(
    period_type: str,
    period_start: str,
    period_end: str,
    total_orders: int = 0,
    total_revenue: float = 0.0,
    avg_order_value: float = 0.0,
    total_sessions: int = 0,
    conversion_rate: float = 0.0,
    db: Session = Depends(get_db)
):
    """Create a new Shopify metric entry"""
    
    metric = ShopifyMetric(
        period_type=period_type,
        period_start=datetime.fromisoformat(period_start.replace('Z', '+00:00')),
        period_end=datetime.fromisoformat(period_end.replace('Z', '+00:00')),
        total_orders=total_orders,
        total_revenue=total_revenue,
        avg_order_value=avg_order_value,
        total_sessions=total_sessions,
        conversion_rate=conversion_rate
    )
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    return {
        "success": True,
        "metric_id": metric.id,
        "created_at": metric.created_at.isoformat()
    }


@router.post("/migrate-table")
def migrate_shopify_table(db: Session = Depends(get_db)):
    """DANGER: Recreate shopify_metrics table - will delete all data!"""
    
    try:
        # Drop old table
        db.execute(text("DROP TABLE IF EXISTS shopify_metrics CASCADE"))
        db.commit()
        
        # Create new table with ALL required columns
        db.execute(text("""
            CREATE TABLE shopify_metrics (
                id SERIAL PRIMARY KEY,
                period_type VARCHAR NOT NULL,
                period_start TIMESTAMP WITH TIME ZONE NOT NULL,
                period_end TIMESTAMP WITH TIME ZONE NOT NULL,
                total_orders INTEGER DEFAULT 0,
                total_revenue FLOAT DEFAULT 0,
                avg_order_value FLOAT DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                conversion_rate FLOAT DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.commit()
        
        # Create indexes
        db.execute(text("CREATE INDEX ix_shopify_metrics_id ON shopify_metrics(id)"))
        db.execute(text("CREATE INDEX ix_shopify_metrics_period_type ON shopify_metrics(period_type)"))
        db.execute(text("CREATE INDEX ix_shopify_metrics_period_start ON shopify_metrics(period_start)"))
        db.commit()
        
        return {
            "success": True,
            "message": "✅ Shopify metrics table recreated successfully!"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Migration failed: {str(e)}")


@router.get("/metrics")
def get_shopify_metrics(
    period_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get Shopify metrics"""
    
    query = db.query(ShopifyMetric)
    
    if period_type:
        query = query.filter(ShopifyMetric.period_type == period_type)
    
    metrics = query.order_by(desc(ShopifyMetric.period_start)).limit(limit).all()
    
    return {
        "metrics": [
            {
                "id": m.id,
                "period_type": m.period_type,
                "period_start": m.period_start.isoformat(),
                "period_end": m.period_end.isoformat(),
                "total_orders": m.total_orders,
                "total_revenue": m.total_revenue,
                "avg_order_value": m.avg_order_value,
                "total_sessions": m.total_sessions,
                "conversion_rate": m.conversion_rate,
                "created_at": m.created_at.isoformat()
            }
            for m in metrics
        ],
        "total": len(metrics)
    }
