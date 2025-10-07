import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)

print("🔧 Creating deliverables table...")

with engine.connect() as conn:
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS deliverables (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER,
                phase VARCHAR(50) NOT NULL,
                phase_name VARCHAR(255),
                category VARCHAR(100) NOT NULL,
                task TEXT NOT NULL,
                asset_requirements TEXT,
                due_date TIMESTAMP WITH TIME ZONE,
                completed_date TIMESTAMP WITH TIME ZONE,
                status VARCHAR(50) DEFAULT 'not_started',
                owner VARCHAR(100),
                assigned_to VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("✅ Created deliverables table")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Create indexes
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_deliverables_status ON deliverables(status);
            CREATE INDEX IF NOT EXISTS idx_deliverables_due_date ON deliverables(due_date);
            CREATE INDEX IF NOT EXISTS idx_deliverables_phase ON deliverables(phase);
            CREATE INDEX IF NOT EXISTS idx_deliverables_campaign ON deliverables(campaign_id);
        """))
        conn.commit()
        print("✅ Created indexes")
    except Exception as e:
        print(f"⚠️ Index error: {e}")

print("🎉 Deliverables table ready!")
