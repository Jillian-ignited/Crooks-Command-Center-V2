#!/usr/bin/env python3
"""
Quick database fix for intelligence_files table
Adds missing columns without dropping existing data
"""

import os
from sqlalchemy import create_engine, text

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

print("🔧 Quick database fix starting...")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        
        # List of columns to add if they don't exist
        columns_to_add = [
            ("filename", "VARCHAR(255)"),
            ("original_filename", "VARCHAR(255)"),
            ("source", "VARCHAR(100) DEFAULT 'manual_upload'"),
            ("brand", "VARCHAR(100) DEFAULT 'Crooks & Castles'"),
            ("file_path", "VARCHAR(512)"),
            ("file_size", "INTEGER"),
            ("file_type", "VARCHAR(50)"),
            ("description", "TEXT"),
            ("analysis_results", "JSON"),
            ("status", "VARCHAR(50) DEFAULT 'uploaded'"),
            ("uploaded_at", "TIMESTAMP WITH TIME ZONE DEFAULT NOW()"),
            ("processed_at", "TIMESTAMP WITH TIME ZONE"),
            ("created_by", "VARCHAR(100)")
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                # Check if column exists
                result = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'intelligence_files' 
                    AND column_name = '{col_name}';
                """))
                
                if not result.fetchone():
                    # Column doesn't exist, add it
                    conn.execute(text(f"ALTER TABLE intelligence_files ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                    print(f"✅ Added column: {col_name}")
                else:
                    print(f"⚠️ Column already exists: {col_name}")
                    
            except Exception as e:
                print(f"❌ Failed to add {col_name}: {e}")
        
        # Verify the table structure
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'intelligence_files'
            ORDER BY ordinal_position;
        """))
        
        columns = [row[0] for row in result]
        print(f"📊 Final columns: {columns}")
        
        # Check if we have the required columns
        required = ['filename', 'original_filename', 'file_path']
        missing = [col for col in required if col not in columns]
        
        if missing:
            print(f"❌ Still missing: {missing}")
        else:
            print("✅ All required columns present")
            
except Exception as e:
    print(f"❌ Database fix failed: {e}")
    
print("🔧 Quick database fix completed")
