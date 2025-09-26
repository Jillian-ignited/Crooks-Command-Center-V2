# /backend/routers/shopify.py - FIXED SHOPIFY INTEGRATION - REAL DATA

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional, Dict, Any, List
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import statistics
import os
from collections import defaultdict
import asyncio

router = APIRouter()

# Shopify data directory
SHOPIFY_DATA_DIR = Path("data/shopify")
SHOPIFY_DATA_DIR.mkdir(parents=True, exist_ok=True)

def parse_shopify_csv(file_path: Path) -> List[Dict]:
    """Parse Shopify CSV exports with multiple format support"""
    try:
        df = pd.read_csv(file_path)
        
        # Common Shopify CSV column mappings
        column_mappings = {
            # Order exports
            'Name': 'order_name',
            'Email': 'customer_email', 
            'Financial Status': 'financial_status',
            'Fulfillment Status': 'fulfillment_status',
            'Total': 'total_price',
            'Subtotal': 'subtotal',
            'Taxes': 'total_tax',
            'Total Discounts': 'total_discounts',
            'Created at': 'created_at',
            'Updated at': 'updated_at',
            'Tags': 'tags',
            'Note': 'note',
            'Phone': 'phone',
            'Cancelled at': 'cancelled_at',
            'Payment Method': 'payment_method',
            'Payment Reference': 'payment_reference',
            'Refunded Amount': 'refunded_amount',
            'Vendor': 'vendor',
            'Outstanding Balance': 'outstanding_balance',
            'Employee': 'employee',
            'Location': 'location',
            'Device ID': 'device_id',
            'Id': 'order_id',
            'Currency': 'currency',
            
            # Product exports  
            'Handle': 'handle',
            'Title': 'title',
            'Body (HTML)': 'body_html',
            'Product Type': 'product_type',
            'Created At': 'created_at',
            'Updated At': 'updated_at',
            'Published': 'published',
            'Option1 Name': 'option1_name',
            'Option1 Value': 'option1_value',
            'Option2 Name': 'option2_name', 
            'Option2 Value': 'option2_value',
            'Variant SKU': 'sku',
            'Variant Grams': 'grams',
            'Variant Inventory Tracker': 'inventory_management',
            'Variant Inventory Qty': 'inventory_quantity',
            'Variant Inventory Policy': 'inventory_policy',
            'Variant Price': 'price',
            'Variant Compare At Price': 'compare_at_price',
            'Variant Requires Shipping': 'requires_shipping',
            'Variant Taxable': 'taxable',
            'Variant Barcode': 'barcode',
            'Image Src': 'image_src',
            'Image Alt Text': 'image_alt',
            'Variant Image': 'variant_image',
            'Variant Weight Unit': 'weight_unit',
            'Cost per item': 'cost',
            'Status': 'status',
            
            # Customer exports
            'First Name': 'first_name',
            'Last Name': 'last_name', 
            'Company': 'company',
            'Address1': 'address1',
            'Address2': 'address2',
            'City': 'city',
            'Province': 'province',
            'Country': 'country',
            'Zip': 'zip',
            'Accepts Marketing': 'accepts_marketing',
            'Total Spent': 'total_spent',
            'Total Orders': 'orders_count',
            'State': 'state',
            'Verified Email': 'verified_email'
        }
        
        # Apply column mappings
        for old_col, new_col in column_mappings.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Convert to records
        records = df.to_dict('records')
        
        # Clean up the data
        for record in records:
            # Convert date fields
            for date_field in ['created_at', 'updated_at', 'cancelled_at']:
                if date_field in record and record[date_field]:
                    try:
                        record[date_field] = pd.to_datetime(record[date_field]).isoformat()
                    except:
                        pass
            
            # Convert numeric fields
            for numeric_field in ['total_price', 'subtotal', 'total_tax', 'total_discounts', 'price', 'compare_at_price', 'total_spent']:
                if numeric_field in record and record[numeric_field]:
                    try:
                        # Remove currency symbols and convert
                        value = str(record[numeric_field]).replace('$', '').replace(',', '').strip()
                        record[numeric_field] = float(value) if value else 0
                    except:
                        record[numeric_field] = 0
        
        return records
        
    except Exception as e:
        print(f"Error parsing Shopify CSV {file_path}: {e}")
        return []

def load_all_shopify_data(days: Optional[int] = None) -> Dict[str, Any]:
    """Load all Shopify data from CSV and JSON files"""
    
    shopify_files = list(SHOPIFY_DATA_DIR.glob("*.csv")) + list(SHOPIFY_DATA_DIR.glob("*.json"))
    
    if not shopify_files:
        return {
            "status": "no_data",
            "message": "No Shopify data files found",
            "orders": [],
            "products": [],
            "customers": [],
            "analytics": {}
        }
    
    all_orders = []
    all_products = []
    all_customers = []
    
    # Set date filter if specified
    cutoff_date = None
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in shopify_files:
        try:
            if file_path.suffix == '.csv':
                records = parse_shopify_csv(file_path)
                
                # Categorize records based on detected columns
                for record in records:
                    if 'order_name' in record or 'total_price' in record:
                        # This looks like an order
                        if cutoff_date and 'created_at' in record:
                            try:
                                order_date = pd.to_datetime(record['created_at'])
                                if order_date >= cutoff_date:
                                    all_orders.append(record)
                            except:
                                all_orders.append(record)
                        else:
                            all_orders.append(record)
                    
                    elif 'handle' in record or 'title' in record:
                        # This looks like a product
                        all_products.append(record)
                    
                    elif 'first_name' in record or 'customer_email' in record:
                        # This looks like a customer
                        all_customers.append(record)
                    
                    else:
                        # Default to order if unclear
                        all_orders.append(record)
                        
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    if isinstance(data, dict):
                        # Handle Shopify API format
                        if 'orders' in data:
                            orders = data['orders']
                            if cutoff_date:
                                filtered_orders = []
                                for order in orders:
                                    try:
                                        order_date = pd.to_datetime(order.get('created_at'))
                                        if order_date >= cutoff_date:
                                            filtered_orders.append(order)
                                    except:
                                        filtered_orders.append(order)
                                all_orders.extend(filtered_orders)
                            else:
                                all_orders.extend(orders)
                        
                        if 'products' in data:
                            all_products.extend(data['products'])
                        
                        if 'customers' in data:
                            all_customers.extend(data['customers'])
                    
                    elif isinstance(data, list):
                        # Handle array format
                        all_orders.extend(data)
                        
        except Exception as e:
            print(f"Error loading Shopify file {file_path}: {e}")
            continue
    
    return {
        "status": "success",
        "message": f"Loaded {len(all_orders)} orders, {len(all_products)} products, {len(all_customers)} customers",
        "orders": all_orders,
        "products": all_products, 
        "customers": all_customers,
        "files_processed": len(shopify_files),
        "analytics": calculate_shopify_analytics(all_orders, all_products, all_customers)
    }

def calculate_shopify_analytics(orders: List[Dict], products: List[Dict], customers: List[Dict]) -> Dict[str, Any]:
    """Calculate comprehensive Shopify analytics"""
    
    if not orders:
        return {
            "revenue": {"total": 0, "average_order_value": 0},
            "order_metrics": {"total_orders": 0, "fulfilled_orders": 0},
            "customer_metrics": {"total_customers": 0, "returning_customers": 0},
            "product_metrics": {"total_products": 0, "avg_price": 0}
        }
    
    # Revenue Analytics
    total_revenue = 0
    valid_orders = []
    
    for order in orders:
        try:
            price = float(order.get('total_price', 0)) if order.get('total_price') else 0
            if price > 0:
                total_revenue += price
                valid_orders.append(order)
        except:
            continue
    
    avg_order_value = total_revenue / len(valid_orders) if valid_orders else 0
    
    # Order Status Analytics
    fulfilled_orders = sum(1 for order in orders if order.get('fulfillment_status') == 'fulfilled')
    
    # Customer Analytics
    unique_customers = set()
    for order in orders:
        email = order.get('customer_email')
        if email:
            unique_customers.add(email.lower())
    
    # Customer order frequency
    customer_order_counts = defaultdict(int)
    for order in orders:
        email = order.get('customer_email')
        if email:
            customer_order_counts[email.lower()] += 1
    
    returning_customers = sum(1 for count in customer_order_counts.values() if count > 1)
    
    # Product Analytics
    product_prices = []
    for product in products:
        try:
            price = float(product.get('price', 0)) if product.get('price') else 0
            if price > 0:
                product_prices.append(price)
        except:
            continue
    
    avg_product_price = statistics.mean(product_prices) if product_prices else 0
    
    # Time-based analytics
    daily_revenue = defaultdict(float)
    monthly_revenue = defaultdict(float)
    
    for order in valid_orders:
        try:
            created_at = order.get('created_at')
            if created_at:
                date = pd.to_datetime(created_at)
                day_key = date.strftime('%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                price = float(order.get('total_price', 0))
                
                daily_revenue[day_key] += price
                monthly_revenue[month_key] += price
        except:
            continue
    
    return {
        "revenue": {
            "total": round(total_revenue, 2),
            "average_order_value": round(avg_order_value, 2),
            "daily_breakdown": dict(daily_revenue),
            "monthly_breakdown": dict(monthly_revenue)
        },
        "order_metrics": {
            "total_orders": len(orders),
            "valid_orders": len(valid_orders),
            "fulfilled_orders": fulfilled_orders,
            "fulfillment_rate": round(fulfilled_orders / len(orders) * 100, 2) if orders else 0
        },
        "customer_metrics": {
            "total_customers": len(unique_customers),
            "returning_customers": returning_customers,
            "customer_retention_rate": round(returning_customers / len(unique_customers) * 100, 2) if unique_customers else 0,
            "avg_orders_per_customer": round(len(valid_orders) / len(unique_customers), 2) if unique_customers else 0
        },
        "product_metrics": {
            "total_products": len(products),
            "avg_price": round(avg_product_price, 2),
            "price_range": {
                "min": min(product_prices) if product_prices else 0,
                "max": max(product_prices) if product_prices else 0
            }
        }
    }

@router.get("/analytics")
async def get_shopify_analytics(days: Optional[int] = Query(default=None, description="Number of days to analyze")):
    """Get comprehensive Shopify analytics from uploaded data"""
    
    try:
        data = load_all_shopify_data(days)
        
        if data["status"] == "no_data":
            return {
                "success": False,
                "message": "No Shopify data found. Upload CSV or JSON files to /data/shopify/",
                "recommendations": [
                    "Export orders from Shopify admin: Orders → Export",
                    "Export products: Products → Export", 
                    "Export customers: Customers → Export",
                    "Upload files to /data/shopify/ directory"
                ]
            }
        
        return {
            "success": True,
            "data": data,
            "period": f"{days} days" if days else "All time",
            "message": data["message"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shopify analytics failed: {str(e)}")

@router.get("/orders")
async def get_orders(
    days: Optional[int] = Query(default=30, description="Number of days"),
    status: Optional[str] = Query(default=None, description="Filter by order status"),
    limit: int = Query(default=100, description="Maximum number of orders to return")
):
    """Get Shopify orders with filtering"""
    
    try:
        data = load_all_shopify_data(days)
        orders = data["orders"]
        
        # Apply status filter
        if status:
            orders = [order for order in orders if order.get('fulfillment_status', '').lower() == status.lower()]
        
        # Apply limit
        orders = orders[:limit]
        
        return {
            "success": True,
            "orders": orders,
            "total_count": len(data["orders"]),
            "filtered_count": len(orders),
            "filters": {"days": days, "status": status, "limit": limit}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orders retrieval failed: {str(e)}")

@router.get("/products")
async def get_products(limit: int = Query(default=100, description="Maximum number of products")):
    """Get Shopify products"""
    
    try:
        data = load_all_shopify_data()
        products = data["products"][:limit]
        
        return {
            "success": True,
            "products": products,
            "total_count": len(data["products"]),
            "message": f"Retrieved {len(products)} products"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Products retrieval failed: {str(e)}")

@router.get("/customers")
async def get_customers(limit: int = Query(default=100, description="Maximum number of customers")):
    """Get Shopify customers"""
    
    try:
        data = load_all_shopify_data()
        customers = data["customers"][:limit]
        
        return {
            "success": True,
            "customers": customers,
            "total_count": len(data["customers"]),
            "message": f"Retrieved {len(customers)} customers"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Customers retrieval failed: {str(e)}")

@router.post("/upload")
async def upload_shopify_data(file: UploadFile = File(...)):
    """Upload Shopify data file"""
    
    try:
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        # Save uploaded file
        file_path = SHOPIFY_DATA_DIR / file.filename
        
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate the file
        if file.filename.endswith('.csv'):
            records = parse_shopify_csv(file_path)
            record_count = len(records)
        else:
            with open(file_path, 'r') as f:
                data = json.load(f)
                record_count = len(data) if isinstance(data, list) else 1
        
        return {
            "success": True,
            "message": f"Successfully uploaded {file.filename}",
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "records": record_count,
                "path": str(file_path)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/status")
async def get_shopify_status():
    """Get Shopify integration status"""
    
    shopify_files = list(SHOPIFY_DATA_DIR.glob("*"))
    
    file_info = []
    for file_path in shopify_files:
        try:
            stats = file_path.stat()
            file_info.append({
                "name": file_path.name,
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "type": file_path.suffix
            })
        except:
            continue
    
    return {
        "status": "connected" if shopify_files else "no_data",
        "data_directory": str(SHOPIFY_DATA_DIR),
        "files": file_info,
        "total_files": len(shopify_files),
        "supported_formats": ["CSV", "JSON"],
        "endpoints": {
            "analytics": "/shopify/analytics",
            "orders": "/shopify/orders", 
            "products": "/shopify/products",
            "customers": "/shopify/customers",
            "upload": "/shopify/upload"
        }
    }
