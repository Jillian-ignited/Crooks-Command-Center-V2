from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import json
from datetime import datetime, timedelta
import random

# Create router
router = APIRouter()

# Models
class ShopifyAnalytics(BaseModel):
    success: bool = True
    analytics: Dict[str, Any]

class ShopifyProduct(BaseModel):
    id: int
    title: str
    price: float
    inventory_quantity: int
    vendor: str
    product_type: str
    tags: List[str]
    created_at: str
    updated_at: str
    variants: List[Dict[str, Any]]
    images: List[Dict[str, Any]]

class ShopifyProducts(BaseModel):
    success: bool = True
    products: List[ShopifyProduct]
    total: int
    page: int
    limit: int

class ShopifyOrder(BaseModel):
    id: int
    order_number: int
    customer: Dict[str, Any]
    total_price: float
    subtotal_price: float
    total_tax: float
    shipping_cost: float
    discount_codes: List[Dict[str, Any]]
    line_items: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    financial_status: str
    fulfillment_status: str
    tags: List[str]

class ShopifyOrders(BaseModel):
    success: bool = True
    orders: List[ShopifyOrder]
    total: int
    page: int
    limit: int

class ShopifyCustomer(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    orders_count: int
    total_spent: float
    tags: List[str]
    addresses: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    segment: Optional[str]

class ShopifyCustomers(BaseModel):
    success: bool = True
    customers: List[ShopifyCustomer]
    total: int
    page: int
    limit: int

class ShopifyOverview(BaseModel):
    success: bool = True
    store_name: str
    total_products: int
    total_orders: int
    total_customers: int
    revenue: Dict[str, Any]
    top_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]
    analytics_summary: Dict[str, Any]

# Helper function to generate realistic Shopify data
def generate_shopify_data():
    # Generate analytics data
    analytics = {
        "summary": {
            "revenue": random.randint(50000, 150000),
            "orders": random.randint(500, 1500),
            "aov": random.randint(80, 120),
            "conversion_rate": round(random.uniform(1.5, 3.5), 2),
            "revenue_growth": round(random.uniform(-5, 15), 1),
            "orders_growth": round(random.uniform(-3, 12), 1)
        },
        "traffic": {
            "total_sessions": random.randint(10000, 30000),
            "unique_visitors": random.randint(8000, 25000),
            "bounce_rate": round(random.uniform(30, 60), 1),
            "avg_session_duration": round(random.uniform(120, 300), 1)
        },
        "products": {
            "total_products": random.randint(50, 150),
            "out_of_stock": random.randint(3, 15),
            "low_inventory": random.randint(5, 20)
        },
        "customers": {
            "total_customers": random.randint(1000, 5000),
            "new_customers": random.randint(100, 500),
            "returning_customers": random.randint(200, 800)
        }
    }
    
    # Generate products data
    products = []
    product_types = ["T-Shirt", "Hoodie", "Hat", "Jacket", "Pants", "Accessories"]
    vendors = ["Crooks & Castles", "In-House", "Collaborations", "Limited Edition"]
    
    for i in range(1, 21):
        product_type = random.choice(product_types)
        vendor = random.choice(vendors)
        price = round(random.uniform(29.99, 149.99), 2)
        inventory = random.randint(0, 50)
        
        products.append({
            "id": 1000 + i,
            "title": f"{vendor} {product_type} {random.choice(['Classic', 'Premium', 'Signature', 'Limited'])}",
            "price": price,
            "inventory_quantity": inventory,
            "vendor": vendor,
            "product_type": product_type,
            "tags": [product_type.lower(), vendor.lower().replace(" & ", "-"), "fw23"],
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "variants": [
                {
                    "id": 10000 + i,
                    "title": "Default",
                    "price": price,
                    "inventory_quantity": inventory
                }
            ],
            "images": [
                {
                    "id": 100000 + i,
                    "src": f"https://example.com/products/{1000 + i}/image.jpg",
                    "position": 1
                }
            ]
        })
    
    # Generate orders data
    orders = []
    statuses = ["paid", "pending", "refunded"]
    fulfillment = ["fulfilled", "partial", "unfulfilled"]
    
    for i in range(1, 16):
        order_date = datetime.now() - timedelta(days=random.randint(1, 30))
        subtotal = round(random.uniform(50, 300), 2)
        tax = round(subtotal * 0.08, 2)
        shipping = round(random.uniform(5, 15), 2)
        total = subtotal + tax + shipping
        
        orders.append({
            "id": 2000 + i,
            "order_number": 1000 + i,
            "customer": {
                "id": 3000 + random.randint(1, 20),
                "first_name": random.choice(["John", "Jane", "Michael", "Sarah", "David"]),
                "last_name": random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"]),
                "email": f"customer{3000 + random.randint(1, 20)}@example.com"
            },
            "total_price": total,
            "subtotal_price": subtotal,
            "total_tax": tax,
            "shipping_cost": shipping,
            "discount_codes": [],
            "line_items": [
                {
                    "id": 30000 + i,
                    "product_id": 1000 + random.randint(1, 20),
                    "title": f"{random.choice(vendors)} {random.choice(product_types)}",
                    "quantity": random.randint(1, 3),
                    "price": round(random.uniform(29.99, 149.99), 2)
                }
            ],
            "created_at": order_date.isoformat(),
            "updated_at": (order_date + timedelta(hours=random.randint(1, 24))).isoformat(),
            "financial_status": random.choice(statuses),
            "fulfillment_status": random.choice(fulfillment),
            "tags": ["online", "web"]
        })
    
    # Generate customers data
    customers = []
    segments = ["VIP", "Regular", "New", "At Risk", "Dormant"]
    
    for i in range(1, 21):
        orders_count = random.randint(1, 10)
        total_spent = round(random.uniform(50, 1000), 2)
        created_date = datetime.now() - timedelta(days=random.randint(30, 365))
        
        customers.append({
            "id": 3000 + i,
            "first_name": random.choice(["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"]),
            "last_name": random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]),
            "email": f"customer{3000 + i}@example.com",
            "phone": f"+1{random.randint(2000000000, 9999999999)}",
            "orders_count": orders_count,
            "total_spent": total_spent,
            "tags": [random.choice(["loyal", "returning", "new"])],
            "addresses": [
                {
                    "id": 40000 + i,
                    "address1": f"{random.randint(100, 999)} Main St",
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "province": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "zip": f"{random.randint(10000, 99999)}",
                    "country": "US",
                    "default": True
                }
            ],
            "created_at": created_date.isoformat(),
            "updated_at": (created_date + timedelta(days=random.randint(1, 30))).isoformat(),
            "segment": random.choice(segments)
        })
    
    # Generate store overview
    overview = {
        "store_name": "Crooks & Castles",
        "total_products": len(products),
        "total_orders": len(orders),
        "total_customers": len(customers),
        "revenue": {
            "total": sum(order["total_price"] for order in orders),
            "average_order_value": round(sum(order["total_price"] for order in orders) / len(orders), 2),
            "growth": round(random.uniform(-5, 15), 1)
        },
        "top_products": sorted(products, key=lambda x: x["inventory_quantity"], reverse=True)[:5],
        "recent_orders": sorted(orders, key=lambda x: x["created_at"], reverse=True)[:5],
        "analytics_summary": analytics["summary"]
    }
    
    return {
        "analytics": analytics,
        "products": products,
        "orders": orders,
        "customers": customers,
        "overview": overview
    }

# Cache the generated data
_shopify_data = generate_shopify_data()

# Root endpoint for Shopify
@router.get("/", response_model=ShopifyOverview)
async def get_shopify_overview():
    """
    Get an overview of the Shopify store including key metrics, top products, and recent orders.
    """
    return {"success": True, **_shopify_data["overview"]}

# Analytics endpoint
@router.get("/analytics", response_model=ShopifyAnalytics)
async def get_analytics():
    """
    Get Shopify analytics data including revenue, orders, and traffic metrics.
    """
    return {"success": True, "analytics": _shopify_data["analytics"]}

# Products endpoint
@router.get("/products", response_model=ShopifyProducts)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    product_type: Optional[str] = None,
    vendor: Optional[str] = None
):
    """
    Get Shopify products with optional filtering by product type and vendor.
    """
    products = _shopify_data["products"]
    
    # Apply filters
    if product_type:
        products = [p for p in products if p["product_type"].lower() == product_type.lower()]
    
    if vendor:
        products = [p for p in products if p["vendor"].lower() == vendor.lower()]
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_products = products[start_idx:end_idx]
    
    return {
        "success": True,
        "products": paginated_products,
        "total": len(products),
        "page": page,
        "limit": limit
    }

# Orders endpoint
@router.get("/orders", response_model=ShopifyOrders)
async def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None
):
    """
    Get Shopify orders with optional filtering by status.
    """
    orders = _shopify_data["orders"]
    
    # Apply filters
    if status:
        orders = [o for o in orders if o["financial_status"].lower() == status.lower()]
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_orders = orders[start_idx:end_idx]
    
    return {
        "success": True,
        "orders": paginated_orders,
        "total": len(orders),
        "page": page,
        "limit": limit
    }

# Customers endpoint
@router.get("/customers", response_model=ShopifyCustomers)
async def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    segment: Optional[str] = None
):
    """
    Get Shopify customers with optional filtering by segment.
    """
    customers = _shopify_data["customers"]
    
    # Apply filters
    if segment:
        customers = [c for c in customers if c.get("segment", "").lower() == segment.lower()]
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_customers = customers[start_idx:end_idx]
    
    return {
        "success": True,
        "customers": paginated_customers,
        "total": len(customers),
        "page": page,
        "limit": limit
    }

# Get a specific product by ID
@router.get("/products/{product_id}", response_model=dict)
async def get_product(product_id: int):
    """
    Get a specific Shopify product by ID.
    """
    products = _shopify_data["products"]
    product = next((p for p in products if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"success": True, "product": product}

# Get a specific order by ID
@router.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: int):
    """
    Get a specific Shopify order by ID.
    """
    orders = _shopify_data["orders"]
    order = next((o for o in orders if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"success": True, "order": order}

# Get a specific customer by ID
@router.get("/customers/{customer_id}", response_model=dict)
async def get_customer(customer_id: int):
    """
    Get a specific Shopify customer by ID.
    """
    customers = _shopify_data["customers"]
    customer = next((c for c in customers if c["id"] == customer_id), None)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {"success": True, "customer": customer}
