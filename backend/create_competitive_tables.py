import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)

print("🔧 Creating Competitive Intelligence tables...")

with engine.connect() as conn:
    # We already have competitive_intel table, let's just ensure it exists
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS competitive_intel (
                id SERIAL PRIMARY KEY,
                competitor VARCHAR(100) NOT NULL,
                data_source VARCHAR(100) NOT NULL,
                content_type VARCHAR(100),
                raw_data JSONB NOT NULL,
                analysis JSONB,
                sentiment VARCHAR(50),
                engagement_score FLOAT,
                collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("✅ Competitive intel table ready")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Create indexes for better performance
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_competitive_competitor 
            ON competitive_intel(competitor);
            
            CREATE INDEX IF NOT EXISTS idx_competitive_source 
            ON competitive_intel(data_source);
            
            CREATE INDEX IF NOT EXISTS idx_competitive_collected 
            ON competitive_intel(collected_at);
        """))
        conn.commit()
        print("✅ Created indexes")
    except Exception as e:
        print(f"⚠️ Index error: {e}")

print("🎉 Competitive Intelligence tables ready!")
