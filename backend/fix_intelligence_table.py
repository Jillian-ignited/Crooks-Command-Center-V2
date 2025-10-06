#!/usr/bin/env python3
"""
Database migration script to fix intelligence_files table schema
Run this once to update the table structure
"""

import os
import sys
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Add backend to path for imports
sys.path.append('/opt/render/project/src/backend')

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    sys.exit(1)

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL)

# Create the correct table structure
Base = declarative_base()

class IntelligenceFile(Base):
    """Intelligence file uploads with AI analysis - CORRECTED SCHEMA"""
    __tablename__ = "intelligence_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    source = Column(String(100), default="manual_upload", nullable=False)
    brand = Column(String(100), default="Crooks & Castles", nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    description = Column(Text)
    analysis_results = Column(JSON)  # Store AI analysis as JSON
    status = Column(String(50), default="processed")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True))
    created_by = Column(String(100))

def main():
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'intelligence_files'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("📋 Table exists, checking schema...")
                
                # Check if filename column exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'intelligence_files' 
                    AND column_name = 'filename';
                """))
                filename_exists = result.fetchone()
                
                if not filename_exists:
                    print("🔧 Adding missing filename column...")
                    conn.execute(text("""
                        ALTER TABLE intelligence_files 
                        ADD COLUMN filename VARCHAR(255);
                    """))
                    conn.commit()
                    print("✅ Added filename column")
                else:
                    print("✅ Filename column already exists")
                
                # Check other critical columns
                missing_columns = []
                required_columns = [
                    ('original_filename', 'VARCHAR(255)'),
                    ('source', 'VARCHAR(100)'),
                    ('brand', 'VARCHAR(100)'),
                    ('file_path', 'VARCHAR(512)'),
                    ('file_size', 'INTEGER'),
                    ('file_type', 'VARCHAR(50)'),
                    ('description', 'TEXT'),
                    ('analysis_results', 'JSON'),
                    ('status', 'VARCHAR(50)'),
                    ('uploaded_at', 'TIMESTAMP WITH TIME ZONE'),
                    ('processed_at', 'TIMESTAMP WITH TIME ZONE'),
                    ('created_by', 'VARCHAR(100)')
                ]
                
                for col_name, col_type in required_columns:
                    result = conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'intelligence_files' 
                        AND column_name = '{col_name}';
                    """))
                    if not result.fetchone():
                        missing_columns.append((col_name, col_type))
                
                # Add missing columns
                for col_name, col_type in missing_columns:
                    print(f"🔧 Adding missing column: {col_name}")
                    conn.execute(text(f"""
                        ALTER TABLE intelligence_files 
                        ADD COLUMN {col_name} {col_type};
                    """))
                    conn.commit()
                    print(f"✅ Added {col_name} column")
                
                if not missing_columns:
                    print("✅ All required columns exist")
                
            else:
                print("🆕 Creating new intelligence_files table...")
                Base.metadata.create_all(bind=engine)
                print("✅ Table created successfully")
            
            # Verify the table structure
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'intelligence_files'
                ORDER BY ordinal_position;
            """))
            
            print("\n📊 Current table structure:")
            for row in result:
                print(f"  - {row[0]}: {row[1]}")
            
            print("\n🎉 Database migration completed successfully!")
            print("💡 You can now upload files to the Intelligence module")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
