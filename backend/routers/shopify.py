from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta, timezone
from typing import Optional
import csv
import io

from ..database import get_db
from ..models import ShopifyOrder, ShopifyMetrics

router = APIRouter()


@router.get("/dashboard")
def get_shopify_dashboard(
    period: str = "30d",  # 7d, 30d, 90d, 1y
    db: Session = Depends(get_db)
):
    """Get Shopify dashboard metrics for executive view"""
    
    now = datetime.now(timezone.utc)
    
    # Calculate period
    if period == "7d":
        start_date = now - timedelta(days=7)
        prev_start = now - timedelta(days=14)
        prev_end = start_date
    elif period == "90d":
        start_date = now - timedelta(days=90)
        prev_start = now - timedelta(days=180)
        prev_end = start_date
    elif period == "1y":
        start_date = now - timedelta(days=365)
        prev_start = now - timedelta(days=730)
        prev_end = start_date
    else:  # 30d default
        start_date = now - timedelta(days=30)
        prev_start = now - timedelta(days=60)
        prev_end = start_date
    
    # Try to get data from ShopifyMetric (analytics imports) FIRST
    current_metrics = db.query(ShopifyMetric).filter(
        and_(
            ShopifyMetric.period_type == "daily",
            ShopifyMetric.period_start >= start_date,
            ShopifyMetric.period_start <= now
        )
    ).all()
    
    prev_metrics = db.query(ShopifyMetric).filter(
        and_(
            ShopifyMetric.period_type == "daily",
            ShopifyMetric.period_start >= prev_start,
            ShopifyMetric.period_start < prev_end
        )
    ).all()
    
    # Calculate from metrics if available
    if current_metrics:
        # Current period
        current_revenue = sum(m.total_revenue or 0 for m in current_metrics)
        current_order_count = sum(m.total_orders or 0 for m in current_metrics)
        current_sessions = sum(m.total_sessions or 0 for m in current_metrics)
        
        # Calculate average order value
        current_aov = current_revenue / current_order_count if current_order_count > 0 else 0
        
        # Calculate conversion rate
        current_conversion = 0
        if current_sessions > 0:
            # Use weighted average conversion rate
            total_conversion = sum(m.conversion_rate * m.total_sessions for m in current_metrics if m.conversion_rate and m.total_sessions)
            current_conversion = total_conversion / current_sessions if current_sessions > 0 else 0
        
        # Previous period
        prev_revenue = sum(m.total_revenue or 0 for m in prev_metrics)
        prev_order_count = sum(m.total_orders or 0 for m in prev_metrics)
        prev_sessions = sum(m.total_sessions or 0 for m in prev_metrics)
        prev_aov = prev_revenue / prev_order_count if prev_order_count > 0 else 0
        prev_conversion = 0
        if prev_sessions > 0:
            total_conversion = sum(m.conversion_rate * m.total_sessions for m in prev_metrics if m.conversion_rate and m.total_sessions)
            prev_conversion = total_conversion / prev_sessions if prev_sessions > 0 else 0
        
        # Get unique customers from orders if available
        current_orders = db.query(ShopifyOrder).filter(
            and_(
                ShopifyOrder.created_at >= start_date,
                ShopifyOrder.created_at <= now
            )
        ).all()
        prev_orders = db.query(ShopifyOrder).filter(
            and_(
                ShopifyOrder.created_at >= prev_start,
                ShopifyOrder.created_at < prev_end
            )
        ).all()
        
        current_customers = len(set(o.customer_email for o in current_orders if o.customer_email)) if current_orders else 0
        prev_customers = len(set(o.customer_email for o in prev_orders if o.customer_email)) if prev_orders else 0
        
    else:
        # Fall back to ShopifyOrder table (individual orders)
        current_orders = db.query(ShopifyOrder).filter(
            and_(
                ShopifyOrder.created_at >= start_date,
                ShopifyOrder.created_at <= now
            )
        ).all()
        
        prev_orders = db.query(ShopifyOrder).filter(
            and_(
                ShopifyOrder.created_at >= prev_start,
                ShopifyOrder.created_at < prev_end
            )
        ).all()
        
        current_revenue = sum(o.total_price or 0 for o in current_orders)
        current_order_count = len(current_orders)
        current_aov = current_revenue / current_order_count if current_order_count > 0 else 0
        current_customers = len(set(o.customer_email for o in current_orders if o.customer_email))
        current_sessions = 0
        current_conversion = 0
        
        prev_revenue = sum(o.total_price or 0 for o in prev_orders)
        prev_order_count = len(prev_orders)
        prev_aov = prev_revenue / prev_order_count if prev_order_count > 0 else 0
        prev_customers = len(set(o.customer_email for o in prev_orders if o.customer_email))
        prev_sessions = 0
        prev_conversion = 0
    
    # Calculate growth
    def calc_growth(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    
    return {
        "period": period,
        "revenue": {
            "current": round(current_revenue, 2),
            "previous": round(prev_revenue, 2),
            "growth": round(calc_growth(current_revenue, prev_revenue), 1)
        },
        "orders": {
            "current": current_order_count,
            "previous": prev_order_count,
            "growth": round(calc_growth(current_order_count, prev_order_count), 1)
        },
        "avg_order_value": {
            "current": round(current_aov, 2),
            "previous": round(prev_aov, 2),
            "growth": round(calc_growth(current_aov, prev_aov), 1)
        },
        "customers": {
            "current": current_customers,
            "previous": prev_customers,
            "growth": round(calc_growth(current_customers, prev_customers), 1)
        },
        "conversion_rate": {
            "current": round(current_conversion, 2),
            "previous": round(prev_conversion, 2),
            "growth": round(calc_growth(current_conversion, prev_conversion), 1)
        },
        "sessions": {
            "current": int(current_sessions),
            "previous": int(prev_sessions),
            "growth": round(calc_growth(current_sessions, prev_sessions), 1)
        }
    }
@router.post("/migrate-table")
def migrate_shopify_table(db: Session = Depends(get_db)):
    """DANGER: Recreate shopify_metrics table - will delete all data!"""
    
    from sqlalchemy import text
    
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

@router.get("/orders")
def get_orders(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get recent Shopify orders"""
    
    orders = db.query(ShopifyOrder).order_by(
        desc(ShopifyOrder.created_at)
    ).limit(limit).offset(offset).all()
    
    total = db.query(func.count(ShopifyOrder.id)).scalar()
    
    return {
        "orders": [
            {
                "id": o.id,
                "order_number": o.order_number,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "total_price": o.total_price,
                "customer_email": o.customer_email,
                "financial_status": o.financial_status,
                "fulfillment_status": o.fulfillment_status,
                "items_count": len(o.line_items) if o.line_items else 0
            }
            for o in orders
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/orders/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    """Get detailed order information"""
    
    order = db.query(ShopifyOrder).filter(ShopifyOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(404, "Order not found")
    
    return {
        "id": order.id,
        "order_id": order.order_id,
        "order_number": order.order_number,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "total_price": order.total_price,
        "subtotal_price": order.subtotal_price,
        "total_tax": order.total_tax,
        "total_discounts": order.total_discounts,
        "customer_email": order.customer_email,
        "financial_status": order.financial_status,
        "fulfillment_status": order.fulfillment_status,
        "line_items": order.line_items,
        "referring_site": order.referring_site,
        "source_name": order.source_name,
        "shipping_city": order.shipping_city,
        "shipping_province": order.shipping_province,
        "shipping_country": order.shipping_country,
        "tags": order.tags,
        "note": order.note
    }


@router.post("/import-csv")
async def import_shopify_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify orders from CSV export"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    try:
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported = 0
        updated = 0
        errors = []
        
        for row in csv_reader:
            try:
                # Parse dates
                created_at = None
                if row.get('Created at'):
                    try:
                        created_at = datetime.fromisoformat(row['Created at'].replace('Z', '+00:00'))
                    except:
                        created_at = datetime.strptime(row['Created at'], '%Y-%m-%d %H:%M:%S')
                        created_at = created_at.replace(tzinfo=timezone.utc)
                
                # Check if order exists
                order_id = row.get('Name') or row.get('Order') or row.get('Order Number')
                if not order_id:
                    continue
                
                existing = db.query(ShopifyOrder).filter(
                    ShopifyOrder.order_id == order_id
                ).first()
                
                # Parse line items (if present)
                line_items = []
                if row.get('Lineitem name'):
                    line_items.append({
                        "name": row.get('Lineitem name'),
                        "quantity": int(row.get('Lineitem quantity', 1)),
                        "price": float(row.get('Lineitem price', 0))
                    })
                
                order_data = {
                    "order_id": order_id,
                    "order_number": row.get('Order Number') or order_id,
                    "created_at": created_at,
                    "total_price": float(row.get('Total', 0) or 0),
                    "subtotal_price": float(row.get('Subtotal', 0) or 0),
                    "total_tax": float(row.get('Taxes', 0) or 0),
                    "total_discounts": float(row.get('Discount Amount', 0) or 0),
                    "customer_email": row.get('Email') or row.get('Billing Email'),
                    "customer_id": row.get('Customer ID'),
                    "financial_status": row.get('Financial Status'),
                    "fulfillment_status": row.get('Fulfillment Status'),
                    "line_items": line_items if line_items else None,
                    "referring_site": row.get('Referring Site'),
                    "landing_site": row.get('Landing Site'),
                    "source_name": row.get('Source'),
                    "shipping_city": row.get('Shipping City'),
                    "shipping_province": row.get('Shipping Province'),
                    "shipping_country": row.get('Shipping Country'),
                    "tags": row.get('Tags'),
                    "note": row.get('Note')
                }
                
                if existing:
                    # Update existing order
                    for key, value in order_data.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    # Create new order
                    order = ShopifyOrder(**order_data)
                    db.add(order)
                    imported += 1
                
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "imported": imported,
            "updated": updated,
            "errors": errors[:10] if errors else [],
            "message": f"Imported {imported} new orders, updated {updated} existing orders"
        }
        
    except Exception as e:
        raise HTTPException(400, f"Error importing CSV: {str(e)}")


@router.post("/import-analytics-conversion")
async def import_conversion_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify conversion rate analytics CSV"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    try:
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_current = 0
        imported_previous = 0
        updated_current = 0
        updated_previous = 0
        
        for row in csv_reader:
            try:
                # CURRENT PERIOD
                day = row.get('Day')
                if day:
                    # Parse date
                    try:
                        date = datetime.strptime(day, '%m/%d/%Y')
                        date = date.replace(tzinfo=timezone.utc)
                    except:
                        try:
                            date = datetime.strptime(day, '%Y-%m-%d')
                            date = date.replace(tzinfo=timezone.utc)
                        except:
                            continue
                    
                    sessions = int(float(row.get('Sessions', 0)))
                    conversion_rate = float(row.get('Conversion rate', 0))
                    
                    existing = db.query(ShopifyMetrics).filter(
                        and_(
                            ShopifyMetrics.period_type == "daily",
                            ShopifyMetrics.period_start == date
                        )
                    ).first()
                    
                    if existing:
                        existing.total_sessions = sessions
                        existing.conversion_rate = conversion_rate
                        updated_current += 1
                    else:
                        metric = ShopifyMetrics(
                            period_type="daily",
                            period_start=date,
                            period_end=date + timedelta(days=1),
                            total_sessions=sessions,
                            conversion_rate=conversion_rate
                        )
                        db.add(metric)
                        imported_current += 1
                
                # PREVIOUS PERIOD
                day_prev = row.get('Day (previous_period)')
                if day_prev:
                    try:
                        date_prev = datetime.strptime(day_prev, '%m/%d/%Y')
                        date_prev = date_prev.replace(tzinfo=timezone.utc)
                    except:
                        try:
                            date_prev = datetime.strptime(day_prev, '%Y-%m-%d')
                            date_prev = date_prev.replace(tzinfo=timezone.utc)
                        except:
                            continue
                    
                    sessions_prev = int(float(row.get('Sessions (previous_period)', 0)))
                    conversion_prev = float(row.get('Conversion rate (previous_period)', 0))
                    
                    existing_prev = db.query(ShopifyMetrics).filter(
                        and_(
                            ShopifyMetrics.period_type == "daily",
                            ShopifyMetrics.period_start == date_prev
                        )
                    ).first()
                    
                    if existing_prev:
                        existing_prev.total_sessions = sessions_prev
                        existing_prev.conversion_rate = conversion_prev
                        updated_previous += 1
                    else:
                        metric_prev = ShopifyMetrics(
                            period_type="daily",
                            period_start=date_prev,
                            period_end=date_prev + timedelta(days=1),
                            total_sessions=sessions_prev,
                            conversion_rate=conversion_prev
                        )
                        db.add(metric_prev)
                        imported_previous += 1
                
            except Exception as e:
                continue
        
        db.commit()
        
        return {
            "success": True,
            "imported_current": imported_current,
            "imported_previous": imported_previous,
            "updated_current": updated_current,
            "updated_previous": updated_previous,
            "message": f"Current: {imported_current} new, {updated_current} updated | Previous: {imported_previous} new, {updated_previous} updated"
        }
        
    except Exception as e:
        raise HTTPException(400, f"Error importing CSV: {str(e)}")


@router.post("/import-analytics-orders")
async def import_orders_analytics_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify orders over time analytics CSV"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    try:
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_current = 0
        imported_previous = 0
        updated_current = 0
        updated_previous = 0
        
        for row in csv_reader:
            try:
                # CURRENT PERIOD
                day = row.get('Day')
                if day:
                    try:
                        date = datetime.strptime(day, '%m/%d/%Y')
                        date = date.replace(tzinfo=timezone.utc)
                    except:
                        try:
                            date = datetime.strptime(day, '%Y-%m-%d')
                            date = date.replace(tzinfo=timezone.utc)
                        except:
                            continue
                    
                    orders = int(float(row.get('Orders', 0)))
                    avg_order_value = float(row.get('Average order value', 0))
                    
                    existing = db.query(ShopifyMetrics).filter(
                        and_(
                            ShopifyMetrics.period_type == "daily",
                            ShopifyMetrics.period_start == date
                        )
                    ).first()
                    
                    if existing:
                        existing.total_orders = orders
                        existing.avg_order_value = avg_order_value
                        updated_current += 1
                    else:
                        metric = ShopifyMetrics(
                            period_type="daily",
                            period_start=date,
                            period_end=date + timedelta(days=1),
                            total_orders=orders,
                            avg_order_value=avg_order_value
                        )
                        db.add(metric)
                        imported_current += 1
                
                # PREVIOUS PERIOD
                day_prev = row.get('Day (previous_period)')
                if day_prev:
                    try:
                        date_prev = datetime.strptime(day_prev, '%m/%d/%Y')
                        date_prev = date_prev.replace(tzinfo=timezone.utc)
                    except:
                        try:
                            date_prev = datetime.strptime(day_prev, '%Y-%m-%d')
                            date_prev = date_prev.replace(tzinfo=timezone.utc)
                        except:
                            continue
                    
                    orders_prev = int(float(row.get('Orders (previous_period)', 0)))
                    avg_order_value_prev = float(row.get('Average order value (previous_period)', 0))
                    
                    existing_prev = db.query(ShopifyMetrics).filter(
                        and_(
                            ShopifyMetrics.period_type == "daily",
                            ShopifyMetrics.period_start == date_prev
                        )
                    ).first()
                    
                    if existing_prev:
                        existing_prev.total_orders = orders_prev
                        existing_prev.avg_order_value = avg_order_value_prev
                        updated_previous += 1
                    else:
                        metric_prev = ShopifyMetrics(
                            period_type="daily",
                            period_start=date_prev,
                            period_end=date_prev + timedelta(days=1),
                            total_orders=orders_prev,
                            avg_order_value=avg_order_value_prev
                        )
                        db.add(metric_prev)
                        imported_previous += 1
                
            except Exception as e:
                continue
        
        db.commit()
        
        return {
            "success": True,
            "imported_current": imported_current,
            "imported_previous": imported_previous,
            "updated_current": updated_current,
            "updated_previous": updated_previous,
            "message": f"Current: {imported_current} new, {updated_current} updated | Previous: {imported_previous} new, {updated_previous} updated"
        }
        
    except Exception as e:
        raise HTTPException(400, f"Error importing CSV: {str(e)}")


@router.post("/import-analytics-sales")
async def import_sales_analytics_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify total sales over time analytics CSV"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    try:
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_current = 0
        imported_previous = 0
        updated_current = 0
        updated_previous = 0
        
        for row in csv_reader:
            try:
                # CURRENT PERIOD
                day = row.get('Day')
                if day:
                    try:
                        date = datetime.strptime(day, '%m/%d/%Y')
                        date = date.replace(tzinfo=timezone.utc)
                    except:
                        try:
                            date = datetime.strptime(day, '%Y-%m-%d')
                            date = date.replace(tzinfo=timezone.utc)
                        except:
                            continue
                    
                    orders = int(float(row.get('Orders', 0)))
                    net_sales = float(row.get('Net sales', 0))
                    total_sales = float(row.get('Total sales', 0))
                    
                    existing = db.query(ShopifyMetrics).filter(
                        and_(
                            ShopifyMetrics.period_type == "daily",
                            ShopifyMetrics.period_start == date
                        )
                    ).first()
                    
                    if existing:
                        existing.total_orders = orders
                        existing.total_revenue = total_sales
                        if orders > 0:
                            existing.avg_order_value = total_sales / orders
                        updated_current += 1
                    else:
                        metric = ShopifyMetrics(
                            period_type="daily",
                            period_start=date,
                            period_end=date + timedelta(days=1),
                            total_orders=orders,
                            total_revenue=total_sales,
                            avg_order_value=total_sales / orders if orders > 0 else 0
                        )
                        db.add(metric)
                        imported_current += 1
                
                # PREVIOUS PERIOD
                day_prev = row.get('Day (previous_period)')
                if day_prev:
                    try:
                        date_prev = datetime.strptime(day_prev, '%m/%d/%Y')
                        date_prev = date_prev.replace(tzinfo=timezone.utc)
                    except:
                        try:
                            date_prev = datetime.strptime(day_prev, '%Y-%m-%d')
                            date_prev = date_prev.replace(tzinfo=timezone.utc)
                        except:
                            continue
                    
                    orders_prev = int(float(row.get('Orders (previous_period)', 0)))
                    net_sales_prev = float(row.get('Net sales (previous_period)', 0))
                    total_sales_prev = float(row.get('Total sales (previous_period)', 0))
                    
                    existing_prev = db.query(ShopifyMetrics).filter(
                        and_(
                            ShopifyMetrics.period_type == "daily",
                            ShopifyMetrics.period_start == date_prev
                        )
                    ).first()
                    
                    if existing_prev:
                        existing_prev.total_orders = orders_prev
                        existing_prev.total_revenue = total_sales_prev
                        if orders_prev > 0:
                            existing_prev.avg_order_value = total_sales_prev / orders_prev
                        updated_previous += 1
                    else:
                        metric_prev = ShopifyMetrics(
                            period_type="daily",
                            period_start=date_prev,
                            period_end=date_prev + timedelta(days=1),
                            total_orders=orders_prev,
                            total_revenue=total_sales_prev,
                            avg_order_value=total_sales_prev / orders_prev if orders_prev > 0 else 0
                        )
                        db.add(metric_prev)
                        imported_previous += 1
                
            except Exception as e:
                continue
        
        db.commit()
        
        return {
            "success": True,
            "imported_current": imported_current,
            "imported_previous": imported_previous,
            "updated_current": updated_current,
            "updated_previous": updated_previous,
            "message": f"Current: {imported_current} new, {updated_current} updated | Previous: {imported_previous} new, {updated_previous} updated"
        }
        
    except Exception as e:
        raise HTTPException(400, f"Error importing CSV: {str(e)}")


@router.get("/top-products")
def get_top_products(
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top selling products"""
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    orders = db.query(ShopifyOrder).filter(
        ShopifyOrder.created_at >= start_date
    ).all()
    
    # Aggregate product sales
    product_sales = {}
    for order in orders:
        if order.line_items:
            for item in order.line_items:
                name = item.get('name', 'Unknown')
                qty = item.get('quantity', 1)
                price = item.get('price', 0)
                
                if name not in product_sales:
                    product_sales[name] = {
                        "name": name,
                        "quantity_sold": 0,
                        "revenue": 0
                    }
                
                product_sales[name]["quantity_sold"] += qty
                product_sales[name]["revenue"] += price * qty
    
    # Sort by revenue
    top_products = sorted(
        product_sales.values(),
        key=lambda x: x["revenue"],
        reverse=True
    )[:limit]
    
    return {
        "period_days": days,
        "top_products": top_products
    }


@router.get("/customer-stats")
def get_customer_stats(days: int = 30, db: Session = Depends(get_db)):
    """Get customer statistics"""
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    orders = db.query(ShopifyOrder).filter(
        ShopifyOrder.created_at >= start_date
    ).all()
    
    # Calculate customer metrics
    customer_orders = {}
    for order in orders:
        if order.customer_email:
            if order.customer_email not in customer_orders:
                customer_orders[order.customer_email] = {
                    "orders": 0,
                    "total_spent": 0
                }
            customer_orders[order.customer_email]["orders"] += 1
            customer_orders[order.customer_email]["total_spent"] += order.total_price or 0
    
    # Calculate stats
    total_customers = len(customer_orders)
    new_customers = len([c for c in customer_orders.values() if c["orders"] == 1])
    returning_customers = total_customers - new_customers
    
    avg_orders_per_customer = sum(c["orders"] for c in customer_orders.values()) / total_customers if total_customers > 0 else 0
    avg_customer_value = sum(c["total_spent"] for c in customer_orders.values()) / total_customers if total_customers > 0 else 0
    
    return {
        "period_days": days,
        "total_customers": total_customers,
        "new_customers": new_customers,
        "returning_customers": returning_customers,
        "avg_orders_per_customer": round(avg_orders_per_customer, 2),
        "avg_customer_value": round(avg_customer_value, 2)
    }


@router.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    
    order = db.query(ShopifyOrder).filter(ShopifyOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(404, "Order not found")
    
    db.delete(order)
    db.commit()
    
    return {"success": True}
