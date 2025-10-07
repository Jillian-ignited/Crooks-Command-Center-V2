import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

engine = create_engine(DATABASE_URL)

print("🔧 Recreating intelligence_files table with correct schema...")

with engine.connect() as conn:
    # Drop existing table
    try:
        conn.execute(text("DROP TABLE IF EXISTS intelligence_files CASCADE;"))
        conn.commit()
        print("✅ Dropped old intelligence_files table")
    except Exception as e:
        print(f"⚠️ Error dropping table: {e}")
    
    # Create table with ALL columns
    try:
        conn.execute(text("""
            CREATE TABLE intelligence_files (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                source VARCHAR(100) NOT NULL DEFAULT 'manual_upload',
                brand VARCHAR(100) NOT NULL DEFAULT 'Crooks & Castles',
                file_path VARCHAR(512) NOT NULL,
                file_size INTEGER,
                file_type VARCHAR(50),
                description TEXT,
                analysis_results JSONB,
                status VARCHAR(50) DEFAULT 'processed',
                uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                processed_at TIMESTAMP WITH TIME ZONE,
                created_by VARCHAR(100)
            );
        """))
        conn.commit()
        print("✅ Created intelligence_files table with all columns")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise
    
    # Create indexes for performance
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_intelligence_status 
            ON intelligence_files(status);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_intelligence_source 
            ON intelligence_files(source);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_intelligence_uploaded 
            ON intelligence_files(uploaded_at DESC);
        """))
        conn.commit()
        print("✅ Created indexes")
    except Exception as e:
        print(f"⚠️ Error creating indexes: {e}")
    
    # Verify table structure
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'intelligence_files'
        ORDER BY ordinal_position;
    """))
    
    print("\n📊 Table structure:")
    for row in result:
        print(f"  - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
    
print("\n🎉 intelligence_files table recreated successfully!")
