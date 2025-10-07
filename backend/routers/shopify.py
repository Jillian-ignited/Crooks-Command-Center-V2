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
