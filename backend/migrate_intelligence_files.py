# backend/migrate_intelligence_files_fixed.py
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your Render env vars.")

# Normalize scheme for SQLAlchemy + psycopg (Render sometimes uses 'postgres://')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, future=True)

with engine.connect() as conn:
    print("🔧 Starting intelligence_files table migration...")
    
    # Drop and recreate table to ensure clean state
    try:
        conn.execute(text("DROP TABLE IF EXISTS intelligence_files CASCADE;"))
        print("✅ Dropped existing intelligence_files table")
    except Exception as e:
        print(f"Note: Table may not have existed: {e}")
    
    # Create the intelligence_files table with ALL required columns
    conn.execute(text("""
        CREATE TABLE intelligence_files (
            id SERIAL PRIMARY KEY,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'manual_upload',
            brand TEXT NOT NULL DEFAULT 'Crooks & Castles',
            description TEXT,
            analysis_results JSONB,
            uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """))
    print("✅ Created intelligence_files table with all required columns")
    
    # Create indexes for better performance
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_intelligence_files_uploaded_at 
        ON intelligence_files(uploaded_at DESC);
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_intelligence_files_source 
        ON intelligence_files(source);
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_intelligence_files_brand 
        ON intelligence_files(brand);
    """))
    
    print("✅ Created performance indexes")
    
    # Verify table structure
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'intelligence_files' 
        ORDER BY ordinal_position;
    """))
    
    print("📋 Table structure:")
    for row in result.fetchall():
        print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
    
    conn.commit()

print("🎉 intelligence_files table migration completed successfully!")
print("📊 Table is ready for file uploads and analysis storage")
