from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, text
from datetime import datetime, timezone, timedelta
from typing import Optional
import csv
from io import StringIO

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


@router.get("/customer-stats")
def get_customer_stats(days: int = 30, db: Session = Depends(get_db)):
    """Get customer statistics - returns zeros until real data available"""
    
    # TODO: Integrate with Shopify API for real customer data
    return {
        "total_customers": 0,
        "new_customers": 0,
        "returning_customers": 0,
        "customer_retention_rate": 0
    }


@router.get("/top-products")
def get_top_products(days: int = 30, limit: int = 10, db: Session = Depends(get_db)):
    """Get top selling products - returns empty until real data imported"""
    return {"products": []}


@router.get("/orders")
def get_recent_orders(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent orders - returns empty until Shopify API integrated"""
    return {"orders": []}


@router.post("/import-csv")
async def import_shopify_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify data from CSV - handles Shopify export format"""
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # Handle BOM
        
        print(f"[Shopify Import] File received: {file.filename}")
        
        csv_file = StringIO(decoded)
        reader = csv.DictReader(csv_file)
        
        # Log the headers
        headers = reader.fieldnames
        print(f"[Shopify Import] CSV Headers: {headers}")
        
        # Detect which type of Shopify export this is
        is_sales_export = 'Net sales' in headers or 'Total sales' in headers
        is_conversion_export = 'Conversion rate' in headers and 'Sessions' in headers
        is_orders_export = 'Average order value' in headers and 'Orders' in headers
        
        print(f"[Shopify Import] Detected - Sales: {is_sales_export}, Conversion: {is_conversion_export}, Orders: {is_orders_export}")
        
        created = 0
        updated = 0
        errors = []
        
        for idx, row in enumerate(reader, start=2):
            try:
                # Get date
                date_str = row.get('Day') or row.get('Date')
                
                if not date_str or not date_str.strip() or 'previous_period' in date_str.lower():
                    continue  # Skip previous period rows
                
                # Parse date
                period_start = None
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y']
                
                for fmt in date_formats:
                    try:
                        period_start = datetime.strptime(date_str.strip(), fmt)
                        break
                    except:
                        continue
                
                if not period_start:
                    errors.append(f"Row {idx}: Could not parse date '{date_str}'")
                    continue
                
                period_end = period_start + timedelta(days=1)
                
                # Check if metric already exists for this date
                existing = db.query(ShopifyMetric).filter(
                    ShopifyMetric.period_start == period_start
                ).first()
                
                if existing:
                    metric = existing
                else:
                    metric = ShopifyMetric(
                        period_type="daily",
                        period_start=period_start,
                        period_end=period_end
                    )
                
                # Extract data based on export type
                if is_sales_export:
                    # Sales over time export
                    orders_str = row.get('Orders', '0')
                    net_sales_str = row.get('Net sales', '0')
                    total_sales_str = row.get('Total sales', '0')
                    
                    orders = int(float(orders_str.replace(',', '').strip()) if orders_str else 0)
                    revenue = float(net_sales_str.replace('$', '').replace(',', '').strip() if net_sales_str else 0)
                    
                    metric.total_orders = orders
                    metric.total_revenue = revenue
                    metric.avg_order_value = revenue / orders if orders > 0 else 0
                    
                    print(f"[Shopify] Row {idx}: Orders={orders}, Revenue=${revenue}")
                
                if is_conversion_export:
                    # Conversion rate export
                    sessions_str = row.get('Sessions', '0')
                    conversion_str = row.get('Conversion rate', '0')
                    completed_str = row.get('Sessions that completed checkout', '0')
                    
                    sessions = int(float(sessions_str.replace(',', '').strip()) if sessions_str else 0)
                    conversion = float(conversion_str.replace('%', '').strip() if conversion_str else 0)
                    
                    metric.total_sessions = sessions
                    metric.conversion_rate = conversion
                    
                    # If we have orders from completed checkouts, use that
                    if completed_str:
                        completed = int(float(completed_str.replace(',', '').strip()))
                        if metric.total_orders == 0:
                            metric.total_orders = completed
                    
                    print(f"[Shopify] Row {idx}: Sessions={sessions}, Conversion={conversion}%")
                
                if is_orders_export:
                    # Orders export
                    orders_str = row.get('Orders', '0')
                    aov_str = row.get('Average order value', '0')
                    
                    orders = int(float(orders_str.replace(',', '').strip()) if orders_str else 0)
                    aov = float(aov_str.replace('$', '').replace(',', '').strip() if aov_str else 0)
                    
                    metric.total_orders = orders
                    metric.avg_order_value = aov
                    
                    # Calculate revenue from orders * aov if we don't have it
                    if metric.total_revenue == 0:
                        metric.total_revenue = orders * aov
                    
                    print(f"[Shopify] Row {idx}: Orders={orders}, AOV=${aov}")
                
                # Recalculate derived metrics
                if metric.total_orders > 0 and metric.total_revenue > 0:
                    metric.avg_order_value = metric.total_revenue / metric.total_orders
                
                if metric.total_orders > 0 and metric.total_sessions > 0:
                    metric.conversion_rate = (metric.total_orders / metric.total_sessions) * 100
                
                if existing:
                    updated += 1
                else:
                    db.add(metric)
                    created += 1
                
            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                errors.append(error_msg)
                print(f"[Shopify Import] ❌ {error_msg}")
        
        db.commit()
        print(f"[Shopify Import] ✅ Success - Created: {created}, Updated: {updated}")
        
        return {
            "success": True,
            "message": f"✅ Imported Shopify data - Created {created} new records, Updated {updated} existing records",
            "created": created,
            "updated": updated,
            "errors": errors[:5] if errors else [],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        db.rollback()
        error_msg = f"Import failed: {str(e)}"
        print(f"[Shopify Import] ❌ {error_msg}")
        raise HTTPException(500, error_msg)


@router.post("/generate-sample-data")
def generate_sample_shopify_data(days: int = 30, db: Session = Depends(get_db)):
    """Generate sample Shopify data for testing"""
    
    try:
        import random
        
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        created = 0
        
        for i in range(days):
            date = today - timedelta(days=days - i - 1)
            
            # Generate realistic-looking data
            base_orders = random.randint(15, 45)
            base_revenue = base_orders * random.uniform(60, 120)
            base_sessions = base_orders * random.randint(25, 50)
            
            metric = ShopifyMetric(
                period_type="daily",
                period_start=date,
                period_end=date + timedelta(days=1),
                total_orders=base_orders,
                total_revenue=round(base_revenue, 2),
                avg_order_value=round(base_revenue / base_orders, 2),
                total_sessions=base_sessions,
                conversion_rate=round((base_orders / base_sessions * 100), 2)
            )
            
            db.add(metric)
            created += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Generated {created} days of sample data",
            "created": created
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Generation failed: {str(e)}")


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
