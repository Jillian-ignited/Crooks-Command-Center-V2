import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)

print("🔧 Creating Shopify tables...")

with engine.connect() as conn:
    # Create shopify_orders table
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS shopify_orders (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(100) UNIQUE NOT NULL,
                order_number VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE,
                total_price FLOAT,
                subtotal_price FLOAT,
                total_tax FLOAT,
                total_discounts FLOAT,
                customer_email VARCHAR(255),
                customer_id VARCHAR(100),
                financial_status VARCHAR(50),
                fulfillment_status VARCHAR(50),
                line_items JSONB,
                referring_site VARCHAR(255),
                landing_site VARCHAR(512),
                source_name VARCHAR(100),
                shipping_city VARCHAR(100),
                shipping_province VARCHAR(100),
                shipping_country VARCHAR(100),
                tags VARCHAR(512),
                note TEXT,
                updated_at TIMESTAMP WITH TIME ZONE,
                imported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("✅ Created shopify_orders table")
    except Exception as e:
        print(f"❌ Error creating shopify_orders: {e}")
        raise
    
    # Create shopify_metrics table
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS shopify_metrics (
                id SERIAL PRIMARY KEY,
                period_type VARCHAR(20) NOT NULL,
                period_start TIMESTAMP WITH TIME ZONE NOT NULL,
                period_end TIMESTAMP WITH TIME ZONE NOT NULL,
                total_revenue FLOAT DEFAULT 0,
                total_orders INTEGER DEFAULT 0,
                avg_order_value FLOAT DEFAULT 0,
                total_customers INTEGER DEFAULT 0,
                new_customers INTEGER DEFAULT 0,
                returning_customers INTEGER DEFAULT 0,
                total_items_sold INTEGER DEFAULT 0,
                calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("✅ Created shopify_metrics table")
    except Exception as e:
        print(f"❌ Error creating shopify_metrics: {e}")
        raise
    
    # Create indexes
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_shopify_orders_created 
            ON shopify_orders(created_at);
            
            CREATE INDEX IF NOT EXISTS idx_shopify_orders_customer 
            ON shopify_orders(customer_email);
            
            CREATE INDEX IF NOT EXISTS idx_shopify_metrics_period 
            ON shopify_metrics(period_type, period_start);
        """))
        conn.commit()
        print("✅ Created indexes")
    except Exception as e:
        print(f"⚠️ Index error: {e}")

print("🎉 Shopify tables ready!")
