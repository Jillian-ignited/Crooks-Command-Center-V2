from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/")
async def shopify_root():
    """Shopify root endpoint"""
    return {
        "success": True,
        "message": "Shopify API operational",
        "endpoints": ["/analytics", "/products", "/orders", "/customers"]
    }

@router.get("/analytics")
async def shopify_analytics(days: int = Query(30, description="Number of days to analyze")):
    """Get Shopify analytics data"""
    # Generate realistic Shopify analytics data
    today = datetime.now()
    
    # Generate daily sales data
    daily_sales = []
    for i in range(days):
        date = today - timedelta(days=i)
        daily_sales.append({
            "date": date.strftime("%Y-%m-%d"),
            "revenue": round(random.uniform(500, 2500), 2),
            "orders": random.randint(5, 25),
            "aov": round(random.uniform(80, 120), 2),
            "visitors": random.randint(100, 500),
            "conversion_rate": round(random.uniform(1.5, 4.5), 2)
        })
    
    # Sort by date ascending
    daily_sales.sort(key=lambda x: x["date"])
    
    # Calculate totals and averages
    total_revenue = sum(day["revenue"] for day in daily_sales)
    total_orders = sum(day["orders"] for day in daily_sales)
    total_visitors = sum(day["visitors"] for day in daily_sales)
    avg_aov = round(total_revenue / total_orders if total_orders > 0 else 0, 2)
    avg_conversion = round((total_orders / total_visitors * 100) if total_visitors > 0 else 0, 2)
    
    # Calculate previous period for comparison
    prev_start = today - timedelta(days=days*2)
    prev_end = today - timedelta(days=days)
    prev_revenue = round(total_revenue * random.uniform(0.8, 1.2), 2)
    prev_orders = round(total_orders * random.uniform(0.8, 1.2))
    
    # Calculate growth rates
    revenue_growth = round(((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0, 1)
    orders_growth = round(((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0, 1)
    
    return {
        "success": True,
        "analytics": {
            "summary": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "average_order_value": avg_aov,
                "conversion_rate": avg_conversion,
                "revenue_growth": revenue_growth,
                "orders_growth": orders_growth
            },
            "daily_data": daily_sales,
            "top_products": [
                {
                    "id": "prod_1",
                    "name": "Classic Logo Hoodie",
                    "sales": round(total_revenue * 0.25, 2),
                    "units": round(total_orders * 0.22),
                    "growth": round(random.uniform(-5, 15), 1)
                },
                {
                    "id": "prod_2",
                    "name": "Signature T-Shirt",
                    "sales": round(total_revenue * 0.18, 2),
                    "units": round(total_orders * 0.25),
                    "growth": round(random.uniform(-5, 15), 1)
                },
                {
                    "id": "prod_3",
                    "name": "Embroidered Cap",
                    "sales": round(total_revenue * 0.12, 2),
                    "units": round(total_orders * 0.15),
                    "growth": round(random.uniform(-5, 15), 1)
                },
                {
                    "id": "prod_4",
                    "name": "Logo Sweatpants",
                    "sales": round(total_revenue * 0.10, 2),
                    "units": round(total_orders * 0.08),
                    "growth": round(random.uniform(-5, 15), 1)
                },
                {
                    "id": "prod_5",
                    "name": "Varsity Jacket",
                    "sales": round(total_revenue * 0.08, 2),
                    "units": round(total_orders * 0.05),
                    "growth": round(random.uniform(-5, 15), 1)
                }
            ],
            "customer_segments": [
                {
                    "segment": "Returning Customers",
                    "revenue": round(total_revenue * 0.65, 2),
                    "orders": round(total_orders * 0.55),
                    "customers": round(total_orders * 0.45)
                },
                {
                    "segment": "New Customers",
                    "revenue": round(total_revenue * 0.35, 2),
                    "orders": round(total_orders * 0.45),
                    "customers": round(total_orders * 0.55)
                }
            ],
            "sales_channels": [
                {
                    "channel": "Online Store",
                    "revenue": round(total_revenue * 0.72, 2),
                    "orders": round(total_orders * 0.70)
                },
                {
                    "channel": "Instagram",
                    "revenue": round(total_revenue * 0.15, 2),
                    "orders": round(total_orders * 0.18)
                },
                {
                    "channel": "Facebook",
                    "revenue": round(total_revenue * 0.08, 2),
                    "orders": round(total_orders * 0.07)
                },
                {
                    "channel": "Wholesale",
                    "revenue": round(total_revenue * 0.05, 2),
                    "orders": round(total_orders * 0.05)
                }
            ],
            "period": {
                "start_date": (today - timedelta(days=days)).strftime("%Y-%m-%d"),
                "end_date": today.strftime("%Y-%m-%d"),
                "days": days
            }
        }
    }

@router.get("/products")
async def shopify_products(
    limit: int = Query(10, description="Number of products to return"),
    offset: int = Query(0, description="Offset for pagination"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get Shopify products"""
    # Generate product categories
    categories = ["Hoodies", "T-Shirts", "Hats", "Pants", "Jackets", "Accessories"]
    
    # Filter by category if provided
    filtered_categories = [category] if category and category in categories else categories
    
    # Generate products
    all_products = []
    product_id = 1
    
    for cat in filtered_categories:
        for i in range(5):  # 5 products per category
            price = round(random.uniform(29.99, 149.99), 2)
            all_products.append({
                "id": f"prod_{product_id}",
                "title": f"{['Classic', 'Signature', 'Premium', 'Limited', 'Exclusive'][i % 5]} {cat[:-1]}",
                "description": f"High-quality {cat.lower()} featuring the iconic Crooks & Castles design.",
                "price": price,
                "compare_at_price": round(price * 1.2, 2) if random.random() > 0.7 else None,
                "category": cat,
                "tags": ["bestseller" if random.random() > 0.8 else None, "new" if random.random() > 0.8 else None, "sale" if random.random() > 0.8 else None],
                "variants": random.randint(1, 5),
                "inventory_quantity": random.randint(0, 50),
                "image_url": f"https://example.com/products/{cat.lower()}/{i+1}.jpg",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "updated_at": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "status": "active" if random.random() > 0.1 else "draft"
            })
            product_id += 1
    
    # Apply pagination
    paginated_products = all_products[offset:offset+limit]
    
    return {
        "success": True,
        "products": paginated_products,
        "pagination": {
            "total": len(all_products),
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if offset + limit < len(all_products) else None
        }
    }

@router.get("/orders")
async def shopify_orders(
    limit: int = Query(10, description="Number of orders to return"),
    offset: int = Query(0, description="Offset for pagination"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get Shopify orders"""
    # Generate order statuses
    statuses = ["fulfilled", "unfulfilled", "partially_fulfilled", "cancelled"]
    
    # Filter by status if provided
    filtered_statuses = [status] if status and status in statuses else statuses
    
    # Generate orders
    all_orders = []
    
    for i in range(50):  # Generate 50 orders
        order_status = random.choice(filtered_statuses)
        order_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Generate line items
        line_items = []
        item_count = random.randint(1, 5)
        for j in range(item_count):
            price = round(random.uniform(29.99, 149.99), 2)
            quantity = random.randint(1, 3)
            line_items.append({
                "id": f"item_{i}_{j}",
                "product_id": f"prod_{random.randint(1, 30)}",
                "title": f"{['Classic', 'Signature', 'Premium', 'Limited', 'Exclusive'][j % 5]} {['Hoodie', 'T-Shirt', 'Hat', 'Pants', 'Jacket'][j % 5]}",
                "price": price,
                "quantity": quantity,
                "total": round(price * quantity, 2)
            })
        
        # Calculate totals
        subtotal = sum(item["total"] for item in line_items)
        tax = round(subtotal * 0.08, 2)
        shipping = round(random.uniform(5, 15), 2)
        total = round(subtotal + tax + shipping, 2)
        
        all_orders.append({
            "id": f"order_{i+1}",
            "order_number": f"#{10000 + i}",
            "customer": {
                "id": f"cust_{random.randint(1, 100)}",
                "name": f"{['John', 'Jane', 'Michael', 'Emily', 'David'][i % 5]} {['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'][i % 5]}",
                "email": f"customer{i}@example.com"
            },
            "created_at": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": order_status,
            "financial_status": "paid" if random.random() > 0.1 else "pending",
            "fulfillment_status": "fulfilled" if order_status == "fulfilled" else "unfulfilled",
            "currency": "USD",
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total,
            "item_count": item_count,
            "line_items": line_items,
            "shipping_address": {
                "address1": f"{random.randint(100, 999)} Main St",
                "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                "zip": f"{random.randint(10000, 99999)}",
                "country": "US"
            }
        })
    
    # Apply pagination
    paginated_orders = all_orders[offset:offset+limit]
    
    return {
        "success": True,
        "orders": paginated_orders,
        "pagination": {
            "total": len(all_orders),
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if offset + limit < len(all_orders) else None
        }
    }

@router.get("/customers")
async def shopify_customers(
    limit: int = Query(10, description="Number of customers to return"),
    offset: int = Query(0, description="Offset for pagination"),
    sort: Optional[str] = Query("orders_count", description="Sort by field")
):
    """Get Shopify customers"""
    # Generate customers
    all_customers = []
    
    for i in range(100):  # Generate 100 customers
        orders_count = random.randint(1, 20)
        total_spent = round(orders_count * random.uniform(50, 200), 2)
        
        all_customers.append({
            "id": f"cust_{i+1}",
            "first_name": random.choice(["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa", "William", "Elizabeth"]),
            "last_name": random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]),
            "email": f"customer{i+1}@example.com",
            "phone": f"+1{random.randint(2000000000, 9999999999)}",
            "orders_count": orders_count,
            "total_spent": total_spent,
            "average_order_value": round(total_spent / orders_count, 2),
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
            "last_order_date": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "accepts_marketing": random.choice([True, False]),
            "tags": random.sample(["vip", "repeat", "wholesale", "retail", "international"], k=random.randint(0, 3)),
            "address": {
                "address1": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Washington', 'Park'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd', 'Ln'])}",
                "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]),
                "state": random.choice(["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]),
                "zip": f"{random.randint(10000, 99999)}",
                "country": "US"
            }
        })
    
    # Sort customers
    if sort == "orders_count":
        all_customers.sort(key=lambda x: x["orders_count"], reverse=True)
    elif sort == "total_spent":
        all_customers.sort(key=lambda x: x["total_spent"], reverse=True)
    elif sort == "created_at":
        all_customers.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    paginated_customers = all_customers[offset:offset+limit]
    
    return {
        "success": True,
        "customers": paginated_customers,
        "pagination": {
            "total": len(all_customers),
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if offset + limit < len(all_customers) else None
        }
    }
