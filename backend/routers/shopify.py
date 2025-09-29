from fastapi import APIRouter, Query

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
async def shopify_analytics(days: int = Query(30, description="Days to include in analytics")):
    """Get Shopify analytics data"""
    return {
        "success": True,
        "time_period": f"Last {days} days",
        "analytics": {
            "sales_overview": {
                "total_sales": 245750.50,
                "orders": 2450,
                "average_order_value": 100.31,
                "conversion_rate": "3.2%",
                "growth": "+12.5%"
            },
            "product_performance": {
                "top_sellers": [
                    {
                        "id": "prod1",
                        "name": "Signature Hoodie - Black",
                        "sales": 42500.00,
                        "units_sold": 425,
                        "conversion_rate": "4.8%"
                    },
                    {
                        "id": "prod2",
                        "name": "Logo T-Shirt - White",
                        "sales": 28750.00,
                        "units_sold": 575,
                        "conversion_rate": "5.2%"
                    },
                    {
                        "id": "prod3",
                        "name": "Cargo Pants - Olive",
                        "sales": 24000.00,
                        "units_sold": 240,
                        "conversion_rate": "3.8%"
                    },
                    {
                        "id": "prod4",
                        "name": "Snapback Cap - Black",
                        "sales": 15000.00,
                        "units_sold": 300,
                        "conversion_rate": "4.5%"
                    },
                    {
                        "id": "prod5",
                        "name": "Bomber Jacket - Navy",
                        "sales": 22500.00,
                        "units_sold": 150,
                        "conversion_rate": "3.2%"
                    }
                ],
                "inventory_status": {
                    "in_stock": 75,
                    "low_stock": 12,
                    "out_of_stock": 5
                }
            },
            "customer_insights": {
                "new_customers": 875,
                "returning_customers": 1575,
                "average_lifetime_value": 320.75,
                "demographics": {
                    "age": {
                        "18-24": "35%",
                        "25-34": "42%",
                        "35-44": "18%",
                        "45+": "5%"
                    },
                    "gender": {
                        "male": "65%",
                        "female": "32%",
                        "non_binary": "3%"
                    },
                    "top_locations": [
                        "Los Angeles",
                        "New York",
                        "Chicago",
                        "Atlanta",
                        "Toronto"
                    ]
                }
            },
            "traffic_sources": {
                "direct": "25%",
                "organic_search": "18%",
                "social_media": "32%",
                "email": "15%",
                "referral": "10%"
            },
            "checkout_analysis": {
                "cart_abandonment_rate": "68%",
                "checkout_completion_rate": "72%",
                "average_checkout_time": "3.5 minutes",
                "payment_methods": {
                    "credit_card": "65%",
                    "paypal": "20%",
                    "apple_pay": "10%",
                    "other": "5%"
                }
            }
        }
    }

@router.get("/products")
async def shopify_products():
    """Get Shopify products data"""
    return {
        "success": True,
        "products": [
            {
                "id": "prod1",
                "name": "Signature Hoodie - Black",
                "price": 100.00,
                "compare_at_price": 120.00,
                "status": "active",
                "inventory": 125,
                "category": "Hoodies",
                "tags": ["bestseller", "fall", "essentials"],
                "image": "/media/Product_Hoodie_Black_Front.jpg"
            },
            {
                "id": "prod2",
                "name": "Logo T-Shirt - White",
                "price": 50.00,
                "compare_at_price": 60.00,
                "status": "active",
                "inventory": 250,
                "category": "T-Shirts",
                "tags": ["bestseller", "essentials"],
                "image": "/media/Product_Tshirt_White_Front.jpg"
            },
            {
                "id": "prod3",
                "name": "Cargo Pants - Olive",
                "price": 100.00,
                "compare_at_price": 120.00,
                "status": "active",
                "inventory": 85,
                "category": "Pants",
                "tags": ["bestseller", "fall"],
                "image": "/media/Product_Cargo_Olive_Front.jpg"
            },
            {
                "id": "prod4",
                "name": "Snapback Cap - Black",
                "price": 50.00,
                "compare_at_price": 60.00,
                "status": "active",
                "inventory": 150,
                "category": "Accessories",
                "tags": ["bestseller", "essentials"],
                "image": "/media/Product_Cap_Black_Front.jpg"
            },
            {
                "id": "prod5",
                "name": "Bomber Jacket - Navy",
                "price": 150.00,
                "compare_at_price": 180.00,
                "status": "active",
                "inventory": 75,
                "category": "Jackets",
                "tags": ["fall", "new"],
                "image": "/media/Product_Bomber_Navy_Front.jpg"
            }
        ],
        "total": 5,
        "active": 5,
        "draft": 0
    }

@router.get("/orders")
async def shopify_orders():
    """Get Shopify orders data"""
    return {
        "success": True,
        "orders": [
            {
                "id": "ord1",
                "order_number": "#10045",
                "date": "2023-09-28T14:30:00",
                "customer": "John Smith",
                "email": "john.smith@example.com",
                "total": 250.00,
                "status": "Fulfilled",
                "payment_status": "Paid",
                "items": [
                    {
                        "product_id": "prod1",
                        "name": "Signature Hoodie - Black",
                        "quantity": 1,
                        "price": 100.00
                    },
                    {
                        "product_id": "prod2",
                        "name": "Logo T-Shirt - White",
                        "quantity": 3,
                        "price": 50.00
                    }
                ],
                "shipping_address": {
                    "address1": "123 Main St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip": "90001",
                    "country": "United States"
                }
            },
            {
                "id": "ord2",
                "order_number": "#10044",
                "date": "2023-09-28T12:15:00",
                "customer": "Jane Doe",
                "email": "jane.doe@example.com",
                "total": 200.00,
                "status": "Processing",
                "payment_status": "Paid",
                "items": [
                    {
                        "product_id": "prod3",
                        "name": "Cargo Pants - Olive",
                        "quantity": 2,
                        "price": 100.00
                    }
                ],
                "shipping_address": {
                    "address1": "456 Oak Ave",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "United States"
                }
            },
            {
                "id": "ord3",
                "order_number": "#10043",
                "date": "2023-09-28T10:45:00",
                "customer": "Michael Johnson",
                "email": "michael.johnson@example.com",
                "total": 350.00,
                "status": "Fulfilled",
                "payment_status": "Paid",
                "items": [
                    {
                        "product_id": "prod5",
                        "name": "Bomber Jacket - Navy",
                        "quantity": 1,
                        "price": 150.00
                    },
                    {
                        "product_id": "prod1",
                        "name": "Signature Hoodie - Black",
                        "quantity": 2,
                        "price": 100.00
                    }
                ],
                "shipping_address": {
                    "address1": "789 Pine St",
                    "city": "Chicago",
                    "state": "IL",
                    "zip": "60007",
                    "country": "United States"
                }
            }
        ],
        "total": 3,
        "fulfilled": 2,
        "processing": 1
    }

@router.get("/customers")
async def shopify_customers():
    """Get Shopify customers data"""
    return {
        "success": True,
        "customers": [
            {
                "id": "cust1",
                "name": "John Smith",
                "email": "john.smith@example.com",
                "orders": 5,
                "total_spent": 750.00,
                "average_order_value": 150.00,
                "first_order": "2023-05-15T10:30:00",
                "last_order": "2023-09-28T14:30:00",
                "location": "Los Angeles, CA"
            },
            {
                "id": "cust2",
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "orders": 3,
                "total_spent": 450.00,
                "average_order_value": 150.00,
                "first_order": "2023-06-20T15:45:00",
                "last_order": "2023-09-28T12:15:00",
                "location": "New York, NY"
            },
            {
                "id": "cust3",
                "name": "Michael Johnson",
                "email": "michael.johnson@example.com",
                "orders": 7,
                "total_spent": 1250.00,
                "average_order_value": 178.57,
                "first_order": "2023-03-10T09:15:00",
                "last_order": "2023-09-28T10:45:00",
                "location": "Chicago, IL"
            },
            {
                "id": "cust4",
                "name": "Sarah Williams",
                "email": "sarah.williams@example.com",
                "orders": 2,
                "total_spent": 300.00,
                "average_order_value": 150.00,
                "first_order": "2023-08-05T16:20:00",
                "last_order": "2023-09-27T11:30:00",
                "location": "Atlanta, GA"
            },
            {
                "id": "cust5",
                "name": "David Brown",
                "email": "david.brown@example.com",
                "orders": 4,
                "total_spent": 650.00,
                "average_order_value": 162.50,
                "first_order": "2023-07-12T14:10:00",
                "last_order": "2023-09-26T13:45:00",
                "location": "Toronto, ON"
            }
        ],
        "total": 5,
        "new_last_30_days": 2,
        "returning": 3
    }
