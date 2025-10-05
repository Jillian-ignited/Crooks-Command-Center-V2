# backend/migrate_intelligence_files.py
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
    # Create the intelligence_files table with all required columns
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS intelligence_files (
            id SERIAL PRIMARY KEY,
            original_filename TEXT NOT NULL,
            source TEXT NOT NULL,
            brand TEXT NOT NULL,
            file_path TEXT NOT NULL,
            description TEXT,
            analysis_results JSONB,
            uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """))
    
    # Check if table exists but is missing columns, and add them
    try:
        # Try to add missing columns if they don't exist
        conn.execute(text("""
            ALTER TABLE intelligence_files 
            ADD COLUMN IF NOT EXISTS original_filename TEXT,
            ADD COLUMN IF NOT EXISTS analysis_results JSONB;
        """))
    except Exception as e:
        print(f"Note: Some columns may already exist: {e}")
    
    conn.commit()

print("✅ intelligence_files table created/updated with all required columns.")
