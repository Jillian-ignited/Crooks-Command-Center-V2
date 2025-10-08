import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

# Drop and recreate deliverables table
with engine.connect() as conn:
    print("🗑️  Dropping old deliverables table...")
    conn.execute(text("DROP TABLE IF EXISTS deliverables CASCADE"))
    conn.commit()
    
    print("✅ Creating new deliverables table...")
    conn.execute(text("""
        CREATE TABLE deliverables (
            id SERIAL PRIMARY KEY,
            campaign_id INTEGER REFERENCES campaigns(id),
            title VARCHAR NOT NULL,
            description TEXT,
            type VARCHAR,
            deliverable_type VARCHAR DEFAULT 'agency_output',
            status VARCHAR DEFAULT 'not_started',
            priority VARCHAR DEFAULT 'medium',
            assigned_to VARCHAR,
            due_date TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            phase VARCHAR,
            dependencies JSONB,
            blocks JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))
    conn.commit()
    
    print("📊 Creating indexes...")
    conn.execute(text("CREATE INDEX ix_deliverables_id ON deliverables(id)"))
    conn.execute(text("CREATE INDEX ix_deliverables_title ON deliverables(title)"))
    conn.execute(text("CREATE INDEX ix_deliverables_phase ON deliverables(phase)"))
    conn.execute(text("CREATE INDEX ix_deliverables_status ON deliverables(status)"))
    conn.execute(text("CREATE INDEX ix_deliverables_deliverable_type ON deliverables(deliverable_type)"))
    conn.commit()
    
    print("🎉 Deliverables table recreated successfully!")
