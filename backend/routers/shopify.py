from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, text
from datetime import datetime, timezone, timedelta
from typing import Optional
import csv
import re
from io import StringIO

from ..database import get_db
from ..models import ShopifyMetric, ShopifyProduct, ShopifyOrder, ShopifyCustomer

router = APIRouter()


def try_decode(contents: bytes) -> str:
    """Try to decode bytes with multiple encodings"""
    for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            decoded = contents.decode(encoding)
            print(f"[Shopify] Successfully decoded with {encoding}")
            return decoded
        except:
            continue
    raise ValueError("Could not decode file with any supported encoding")


@router.get("/dashboard")
def get_shopify_dashboard(
    period: str = "30d",
    db: Session = Depends(get_db)
):
    """Get Shopify analytics dashboard"""
    
    days = int(period.replace('d', ''))
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    try:
        metrics = db.query(ShopifyMetric).filter(
            and_(
                ShopifyMetric.period_type == "daily",
                ShopifyMetric.period_start >= start_date,
                ShopifyMetric.period_start <= end_date
            )
        ).order_by(ShopifyMetric.period_start).all()
        
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
    """Get customer statistics from imported data"""
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    try:
        total_customers = db.query(ShopifyCustomer).count()
        new_customers = db.query(ShopifyCustomer).filter(
            ShopifyCustomer.first_order_date >= start_date
        ).count()
        returning_customers = db.query(ShopifyCustomer).filter(
            ShopifyCustomer.is_returning == True
        ).count()
        retention_rate = (returning_customers / total_customers * 100) if total_customers > 0 else 0
        
        return {
            "total_customers": total_customers,
            "new_customers": new_customers,
            "returning_customers": returning_customers,
            "customer_retention_rate": round(retention_rate, 2)
        }
    except Exception as e:
        print(f"[Shopify] Customer stats error: {e}")
        return {
            "total_customers": 0,
            "new_customers": 0,
            "returning_customers": 0,
            "customer_retention_rate": 0
        }


@router.get("/top-products")
def get_top_products(days: int = 30, limit: int = 10, db: Session = Depends(get_db)):
    """Get top selling products by revenue"""
    
    try:
        products = db.query(ShopifyProduct).filter(
            ShopifyProduct.total_sales > 0
        ).order_by(desc(ShopifyProduct.total_sales)).limit(limit).all()
        
        return {
            "products": [
                {
                    "title": p.title,
                    "vendor": p.vendor,
                    "type": p.product_type,
                    "total_sales": round(p.total_sales, 2),
                    "units_sold": p.units_sold,
                    "avg_price": round(p.total_sales / p.units_sold, 2) if p.units_sold > 0 else 0
                }
                for p in products
            ]
        }
    except Exception as e:
        print(f"[Shopify] Top products error: {e}")
        return {"products": []}


@router.get("/orders")
def get_recent_orders(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent orders from imported data"""
    
    try:
        orders = db.query(ShopifyOrder).order_by(
            desc(ShopifyOrder.order_date)
        ).limit(limit).all()
        
        return {
            "orders": [
                {
                    "id": o.order_name,
                    "customer_name": o.customer_name or "Guest",
                    "email": o.customer_email or "",
                    "total": round(o.total, 2) if o.total else 0,
                    "status": o.fulfillment_status or "unknown",
                    "items_count": o.line_items_count,
                    "created_at": o.order_date.isoformat() if o.order_date else ""
                }
                for o in orders
            ]
        }
    except Exception as e:
        print(f"[Shopify] Recent orders error: {e}")
        return {"orders": []}


@router.post("/import-metrics-csv")
async def import_shopify_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify metrics from CSV (sales/conversion data)"""
    
    try:
        contents = await file.read()
        decoded = try_decode(contents)
        
        print(f"[Shopify Import] File received: {file.filename}, Size: {len(contents)} bytes")
        
        csv_file = StringIO(decoded)
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames
        print(f"[Shopify Import] CSV Headers: {headers}")
        
        is_sales_export = 'Net sales' in headers or 'Total sales' in headers
        is_conversion_export = 'Conversion rate' in headers and 'Sessions' in headers
        is_orders_export = 'Average order value' in headers and 'Orders' in headers
        
        print(f"[Shopify Import] Detected - Sales: {is_sales_export}, Conversion: {is_conversion_export}, Orders: {is_orders_export}")
        
        created = 0
        updated = 0
        errors = []
        
        for idx, row in enumerate(reader, start=2):
            try:
                date_str = row.get('Day') or row.get('Date')
                
                if not date_str or not date_str.strip() or 'previous_period' in str(date_str).lower():
                    continue
                
                period_start = None
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y', '%B %d, %Y']
                
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
                
                existing = db.query(ShopifyMetric).filter(
                    ShopifyMetric.period_start == period_start
                ).first()
                
                if existing:
                    metric = existing
                else:
                    metric = ShopifyMetric(
                        period_type="daily",
                        period_start=period_start,
                        period_end=period_end,
                        total_orders=0,
                        total_revenue=0.0,
                        avg_order_value=0.0,
                        total_sessions=0,
                        conversion_rate=0.0
                    )
                
                if is_sales_export:
                    orders_str = row.get('Orders', '0')
                    net_sales_str = row.get('Net sales', '0')
                    
                    orders = int(float(orders_str.replace(',', '').strip()) if orders_str else 0)
                    revenue = float(net_sales_str.replace('$', '').replace(',', '').strip() if net_sales_str else 0)
                    
                    metric.total_orders = orders
                    metric.total_revenue = revenue
                    metric.avg_order_value = revenue / orders if orders > 0 else 0
                
                if is_conversion_export:
                    sessions_str = row.get('Sessions', '0')
                    conversion_str = row.get('Conversion rate', '0')
                    
                    sessions = int(float(sessions_str.replace(',', '').strip()) if sessions_str else 0)
                    conversion = float(conversion_str.replace('%', '').strip() if conversion_str else 0)
                    
                    metric.total_sessions = sessions
                    metric.conversion_rate = conversion
                
                if is_orders_export:
                    orders_str = row.get('Orders', '0')
                    aov_str = row.get('Average order value', '0')
                    
                    orders = int(float(orders_str.replace(',', '').strip()) if orders_str else 0)
                    aov = float(aov_str.replace('$', '').replace(',', '').strip() if aov_str else 0)
                    
                    metric.total_orders = orders
                    metric.avg_order_value = aov
                    
                    if metric.total_revenue == 0:
                        metric.total_revenue = orders * aov
                
                metric.total_orders = metric.total_orders or 0
                metric.total_revenue = metric.total_revenue or 0.0
                metric.total_sessions = metric.total_sessions or 0
                metric.conversion_rate = metric.conversion_rate or 0.0
                metric.avg_order_value = metric.avg_order_value or 0.0
                
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
                if len(errors) <= 5:
                    print(f"[Shopify Import] ❌ {error_msg}")
        
        db.commit()
        print(f"[Shopify Import] ✅ Success - Created: {created}, Updated: {updated}")
        
        return {
            "success": True,
            "message": f"✅ Imported metrics - Created {created}, Updated {updated}",
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


@router.post("/import-products-csv")
async def import_products_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify products from CSV export"""
    
    try:
        contents = await file.read()
        decoded = try_decode(contents)
        
        print(f"[Products Import] File received: {file.filename}, Size: {len(contents)} bytes")
        
        csv_file = StringIO(decoded)
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames
        print(f"[Products Import] CSV Headers: {headers}")
        
        created = 0
        updated = 0
        errors = []
        batch_size = 500
        batch = []
        
        for idx, row in enumerate(reader, start=2):
            try:
                title = row.get('Product title') or row.get('Title') or row.get('Product')
                
                if not title or not title.strip():
                    continue
                
                handle = title.lower().strip().replace(' ', '-').replace('/', '-').replace('&', 'and')
                handle = re.sub(r'[^a-z0-9-]', '', handle)
                
                vendor = row.get('Product vendor') or row.get('Vendor', '')
                product_type = row.get('Product type') or row.get('Type') or row.get('Product Type', '')
                
                net_items_sold = row.get('Net items sold') or row.get('Net quantity', '0')
                net_sales_str = row.get('Net sales', '0')
                
                units = int(float(str(net_items_sold).replace(',', '').strip()) if net_items_sold else 0)
                sales = float(str(net_sales_str).replace('$', '').replace(',', '').strip() if net_sales_str else 0)
                
                if units == 0 and sales == 0:
                    continue
                
                existing = db.query(ShopifyProduct).filter(
                    ShopifyProduct.handle == handle
                ).first()
                
                if existing:
                    existing.total_sales += sales
                    existing.units_sold += units
                    existing.vendor = vendor
                    existing.product_type = product_type
                    updated += 1
                else:
                    product = ShopifyProduct(
                        title=title,
                        handle=handle,
                        vendor=vendor,
                        product_type=product_type,
                        tags='',
                        variant_sku='',
                        variant_price=0,
                        total_sales=sales,
                        units_sold=units
                    )
                    batch.append(product)
                    created += 1
                
                if len(batch) >= batch_size:
                    db.add_all(batch)
                    db.commit()
                    print(f"[Products] Committed batch - Total created: {created}")
                    batch = []
                
                if idx % 1000 == 0:
                    print(f"[Products] Processed {idx} rows...")
                
            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                errors.append(error_msg)
                if len(errors) <= 5:
                    print(f"[Products Import] ❌ {error_msg}")
        
        if batch:
            db.add_all(batch)
            db.commit()
        
        db.commit()
        print(f"[Products Import] ✅ Success - Created: {created}, Updated: {updated}")
        
        return {
            "success": True,
            "message": f"✅ Imported products - Created {created}, Updated {updated}",
            "created": created,
            "updated": updated,
            "errors": errors[:5] if errors else [],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        db.rollback()
        error_msg = f"Import failed: {str(e)}"
        print(f"[Products Import] ❌ {error_msg}")
        raise HTTPException(500, error_msg)


@router.post("/import-orders-csv")
async def import_orders_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify orders from CSV export"""
    
    try:
        contents = await file.read()
        decoded = try_decode(contents)
        
        print(f"[Orders Import] File received: {file.filename}, Size: {len(contents)} bytes")
        
        csv_file = StringIO(decoded)
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames
        print(f"[Orders Import] CSV Headers: {headers}")
        
        created = 0
        updated = 0
        skipped = 0
        errors = []
        batch_size = 500
        batch = []
        
        for idx, row in enumerate(reader, start=2):
            try:
                order_name = row.get('Name')
                
                if not order_name:
                    skipped += 1
                    continue
                
                order_date_str = row.get('Created at')
                order_date = None
                
                if order_date_str:
                    date_formats = ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M', '%Y-%m-%d']
                    for fmt in date_formats:
                        try:
                            order_date = datetime.strptime(order_date_str.strip(), fmt)
                            break
                        except:
                            continue
                
                if not order_date:
                    order_date = datetime.now(timezone.utc)
                
                customer_name = f"{row.get('Billing Name', '')} {row.get('Shipping Name', '')}".strip()
                if not customer_name:
                    customer_name = row.get('Customer', 'Guest')
                
                customer_email = row.get('Email', '')
                financial_status = row.get('Financial Status', 'unknown')
                fulfillment_status = row.get('Fulfillment Status', 'unfulfilled')
                
                total_str = row.get('Total', '0')
                subtotal_str = row.get('Subtotal', '0')
                shipping_str = row.get('Shipping', '0')
                taxes_str = row.get('Taxes', '0')
                discount_str = row.get('Discount Amount', '0')
                
                total = float(total_str.replace('$', '').replace(',', '').strip() if total_str else 0)
                subtotal = float(subtotal_str.replace('$', '').replace(',', '').strip() if subtotal_str else 0)
                shipping = float(shipping_str.replace('$', '').replace(',', '').strip() if shipping_str else 0)
                taxes = float(taxes_str.replace('$', '').replace(',', '').strip() if taxes_str else 0)
                discount = float(discount_str.replace('$', '').replace(',', '').strip() if discount_str else 0)
                
                line_items = int(row.get('Lineitem quantity', 1))
                product_title = row.get('Lineitem name', '')
                
                existing = db.query(ShopifyOrder).filter(
                    ShopifyOrder.order_name == order_name
                ).first()
                
                if existing:
                    if product_title and product_title not in existing.product_titles:
                        existing.product_titles += f", {product_title}"
                        existing.line_items_count += line_items
                    skipped += 1
                else:
                    order = ShopifyOrder(
                        order_name=order_name,
                        order_date=order_date,
                        customer_name=customer_name,
                        customer_email=customer_email,
                        financial_status=financial_status,
                        fulfillment_status=fulfillment_status,
                        total=total,
                        subtotal=subtotal,
                        shipping=shipping,
                        taxes=taxes,
                        discount_amount=discount,
                        line_items_count=line_items,
                        product_titles=product_title
                    )
                    batch.append(order)
                    created += 1
                
                if len(batch) >= batch_size:
                    db.add_all(batch)
                    db.commit()
                    print(f"[Orders] Committed batch - Total created: {created}")
                    batch = []
                
                if idx % 1000 == 0:
                    print(f"[Orders] Processed {idx} rows...")
                
            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                errors.append(error_msg)
                if len(errors) <= 5:
                    print(f"[Orders Import] ❌ {error_msg}")
        
        if batch:
            db.add_all(batch)
            db.commit()
        
        db.commit()
        print(f"[Orders Import] ✅ Success - Created: {created}, Skipped: {skipped}")
        
        return {
            "success": True,
            "message": f"✅ Imported orders - Created {created}, Skipped {skipped} duplicates",
            "created": created,
            "updated": updated,
            "errors": errors[:5] if errors else [],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        db.rollback()
        error_msg = f"Import failed: {str(e)}"
        print(f"[Orders Import] ❌ {error_msg}")
        raise HTTPException(500, error_msg)


@router.post("/import-customers-csv")
async def import_customers_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Shopify customers from CSV export - handles large files"""
    
    try:
        contents = await file.read()
        decoded = try_decode(contents)
        
        print(f"[Customers Import] File received: {file.filename}, Size: {len(contents)} bytes")
        
        csv_file = StringIO(decoded)
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames
        print(f"[Customers Import] CSV Headers: {headers}")
        
        created = 0
        updated = 0
        errors = []
        batch_size = 1000
        batch = []
        
        for idx, row in enumerate(reader, start=2):
            try:
                email = row.get('Email')
                
                if not email:
                    continue
                
                first_name = row.get('First Name', '')
                last_name = row.get('Last Name', '')
                orders_count = int(row.get('Orders Count', 0))
                total_spent_str = row.get('Total Spent', '0')
                total_spent = float(total_spent_str.replace('$', '').replace(',', '').strip() if total_spent_str else 0)
                
                accepts_marketing = row.get('Accepts Marketing', 'no').lower() == 'yes'
                
                first_order_str = row.get('First Order Date')
                last_order_str = row.get('Last Order Date')
                
                first_order_date = None
                last_order_date = None
                
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
                
                if first_order_str:
                    for fmt in date_formats:
                        try:
                            first_order_date = datetime.strptime(first_order_str.strip(), fmt)
                            break
                        except:
                            continue
                
                if last_order_str:
                    for fmt in date_formats:
                        try:
                            last_order_date = datetime.strptime(last_order_str.strip(), fmt)
                            break
                        except:
                            continue
                
                is_returning = orders_count > 1
                
                existing = db.query(ShopifyCustomer).filter(
                    ShopifyCustomer.email == email
                ).first()
                
                if existing:
                    existing.orders_count = orders_count
                    existing.total_spent = total_spent
                    existing.is_returning = is_returning
                    if first_order_date:
                        existing.first_order_date = first_order_date
                    if last_order_date:
                        existing.last_order_date = last_order_date
                    updated += 1
                else:
                    customer = ShopifyCustomer(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        orders_count=orders_count,
                        total_spent=total_spent,
                        first_order_date=first_order_date,
                        last_order_date=last_order_date,
                        is_returning=is_returning,
                        accepts_marketing=accepts_marketing
                    )
                    batch.append(customer)
                    created += 1
                
                # Commit in batches
                if len(batch) >= batch_size:
                    db.add_all(batch)
                    db.commit()
                    print(f"[Customers] Committed batch of {len(batch)} - Total created: {created}")
                    batch = []
                
                # Progress logging every 5000 rows
                if idx % 5000 == 0:
                    print(f"[Customers] Processed {idx} rows...")
                
            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                errors.append(error_msg)
                if len(errors) <= 5:
                    print(f"[Customers Import] ❌ {error_msg}")
        
        # Commit remaining batch
        if batch:
            db.add_all(batch)
            db.commit()
            print(f"[Customers] Committed final batch of {len(batch)}")
        
        db.commit()
        print(f"[Customers Import] ✅ Success - Created: {created}, Updated: {updated}")
        
        return {
            "success": True,
            "message": f"✅ Imported customers - Created {created}, Updated {updated}",
            "created": created,
            "updated": updated,
            "errors": errors[:5] if errors else [],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        db.rollback()
        error_msg = f"Import failed: {str(e)}"
        print(f"[Customers Import] ❌ {error_msg}")
        raise HTTPException(500, error_msg)


@router.post("/migrate-tables")
def migrate_shopify_tables(db: Session = Depends(get_db)):
    """DANGER: Recreate all Shopify tables - will delete all data!"""
    
    try:
        db.execute(text("DROP TABLE IF EXISTS shopify_customers CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS shopify_orders CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS shopify_products CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS shopify_metrics CASCADE"))
        db.commit()
        
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
        
        db.execute(text("""
            CREATE TABLE shopify_products (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                handle VARCHAR UNIQUE NOT NULL,
                vendor VARCHAR,
                product_type VARCHAR,
                tags TEXT,
                variant_sku VARCHAR,
                variant_price FLOAT,
                total_sales FLOAT DEFAULT 0,
                units_sold INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.execute(text("""
            CREATE TABLE shopify_orders (
                id SERIAL PRIMARY KEY,
                order_name VARCHAR UNIQUE NOT NULL,
                order_date TIMESTAMP WITH TIME ZONE NOT NULL,
                customer_name VARCHAR,
                customer_email VARCHAR,
                financial_status VARCHAR,
                fulfillment_status VARCHAR,
                total FLOAT,
                subtotal FLOAT,
                shipping FLOAT,
                taxes FLOAT,
                discount_amount FLOAT,
                line_items_count INTEGER DEFAULT 1,
                product_titles TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.execute(text("""
            CREATE TABLE shopify_customers (
                id SERIAL PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                first_name VARCHAR,
                last_name VARCHAR,
                orders_count INTEGER DEFAULT 0,
                total_spent FLOAT DEFAULT 0,
                first_order_date TIMESTAMP WITH TIME ZONE,
                last_order_date TIMESTAMP WITH TIME ZONE,
                is_returning BOOLEAN DEFAULT FALSE,
                accepts_marketing BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.execute(text("CREATE INDEX ix_shopify_metrics_period_type ON shopify_metrics(period_type)"))
        db.execute(text("CREATE INDEX ix_shopify_metrics_period_start ON shopify_metrics(period_start)"))
        db.execute(text("CREATE INDEX ix_shopify_products_handle ON shopify_products(handle)"))
        db.execute(text("CREATE INDEX ix_shopify_orders_order_name ON shopify_orders(order_name)"))
        db.execute(text("CREATE INDEX ix_shopify_orders_order_date ON shopify_orders(order_date)"))
        db.execute(text("CREATE INDEX ix_shopify_customers_email ON shopify_customers(email)"))
        db.commit()
        
        return {
            "success": True,
            "message": "✅ All Shopify tables recreated successfully!"
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
