import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)

print("🔧 Fixing intelligence_files table schema...")

with engine.connect() as conn:
    # Add missing filename column
    try:
        conn.execute(text("""
            ALTER TABLE intelligence_files 
            ADD COLUMN IF NOT EXISTS filename TEXT NOT NULL DEFAULT '';
        """))
        conn.commit()
        print("✅ Added filename column")
    except Exception as e:
        print(f"⚠️ Error adding filename column: {e}")
    
    # Verify all columns exist
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'intelligence_files'
        ORDER BY ordinal_position;
    """))
    
    columns = [row[0] for row in result]
    print(f"📊 Current columns: {columns}")
    
    required_columns = [
        'id', 'filename', 'original_filename', 'source', 'brand',
        'file_path', 'file_size', 'file_type', 'description',
        'analysis_results', 'status', 'uploaded_at', 'processed_at', 'created_by'
    ]
    
    missing = [col for col in required_columns if col not in columns]
    if missing:
        print(f"⚠️ Missing columns: {missing}")
    else:
        print("✅ All required columns present")

print("🎉 Schema fix completed!")
