#!/usr/bin/env python3
"""
Database table creation script for Crooks Command Center
Add this to your GitHub repo and run on Render to create missing tables
"""

import os
import sys

def install_dependencies():
    """Install required packages if not available"""
    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
    except ImportError:
        print("📦 Installing required packages...")
        os.system("pip install sqlalchemy psycopg2-binary")
        import sqlalchemy
        from sqlalchemy import create_engine, text
    
    return create_engine, text

def get_database_url():
    """Get database URL from Render environment variables"""
    # Render typically uses DATABASE_URL
    db_url = (
        os.getenv('DATABASE_URL') or 
        os.getenv('POSTGRES_URL') or 
        os.getenv('DB_URL') or
        os.getenv('RENDER_DATABASE_URL') or
        os.getenv('POSTGRESQL_URL')
    )
    
    if not db_url:
        print("❌ No database URL found!")
        print("Available environment variables:")
        for key in os.environ:
            if 'DATABASE' in key.upper() or 'POSTGRES' in key.upper():
                print(f"  {key}={os.environ[key][:50]}...")
        return None
    
    # Handle different URL formats
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def create_intelligence_table(create_engine, text, db_url):
    """Create the intelligence_files table"""
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS intelligence_files (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        source VARCHAR(100) NOT NULL,
        brand VARCHAR(100),
        file_path VARCHAR(500) NOT NULL,
        processed BOOLEAN DEFAULT FALSE,
        insights JSON DEFAULT '{}',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP NULL,
        file_size BIGINT,
        content_type VARCHAR(100),
        status VARCHAR(50) DEFAULT 'uploaded',
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # SQL to create indexes
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_intelligence_files_source ON intelligence_files(source);
    CREATE INDEX IF NOT EXISTS idx_intelligence_files_brand ON intelligence_files(brand);
    CREATE INDEX IF NOT EXISTS idx_intelligence_files_processed ON intelligence_files(processed);
    CREATE INDEX IF NOT EXISTS idx_intelligence_files_status ON intelligence_files(status);
    CREATE INDEX IF NOT EXISTS idx_intelligence_files_uploaded_at ON intelligence_files(uploaded_at);
    """
    
    # SQL to create update trigger
    create_trigger_sql = """
    CREATE OR REPLACE FUNCTION update_intelligence_files_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trigger_intelligence_files_updated_at ON intelligence_files;
    CREATE TRIGGER trigger_intelligence_files_updated_at
        BEFORE UPDATE ON intelligence_files
        FOR EACH ROW
        EXECUTE FUNCTION update_intelligence_files_updated_at();
    """
    
    try:
        print(f"🔗 Connecting to database...")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            print("✅ Connected to database successfully!")
            
            # Create table
            print("📝 Creating intelligence_files table...")
            conn.execute(text(create_table_sql))
            
            # Create indexes
            print("📊 Creating indexes...")
            conn.execute(text(create_indexes_sql))
            
            # Create trigger
            print("⚡ Creating update trigger...")
            conn.execute(text(create_trigger_sql))
            
            # Commit changes
            conn.commit()
            
            print("✅ Successfully created intelligence_files table!")
            
            # Verify table exists
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'intelligence_files'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            if columns:
                print(f"\n📋 Table verified with {len(columns)} columns:")
                for col_name, col_type in columns[:5]:  # Show first 5 columns
                    print(f"  ✓ {col_name}: {col_type}")
                if len(columns) > 5:
                    print(f"  ... and {len(columns) - 5} more columns")
            
            return True
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("🚀 Crooks Command Center - Database Setup")
    print("=" * 50)
    print("This script creates the missing intelligence_files table")
    print()
    
    # Install dependencies
    create_engine, text = install_dependencies()
    
    # Get database URL
    db_url = get_database_url()
    if not db_url:
        print("\n💡 This script should be run on Render where DATABASE_URL is available")
        sys.exit(1)
    
    print(f"🔗 Found database URL: {db_url.split('@')[0]}@***")
    
    # Create table
    success = create_intelligence_table(create_engine, text, db_url)
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("\n✅ Next steps:")
        print("1. Your intelligence_files table is now ready")
        print("2. Restart your FastAPI server (if needed)")
        print("3. Try uploading files in the Intelligence module")
        print("4. Files should now save without PostgreSQL errors")
    else:
        print("\n💥 Database setup failed!")
        print("Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
