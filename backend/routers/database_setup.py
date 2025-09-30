from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import datetime

router = APIRouter()

@router.get("/create-tables")
async def create_database_tables() -> Dict[str, Any]:
    """One-time endpoint to create missing database tables"""
    
    try:
        # Import SQLAlchemy
        try:
            from sqlalchemy import create_engine, text
        except ImportError:
            return {
                "success": False,
                "error": "SQLAlchemy not installed",
                "message": "Please install: pip install sqlalchemy psycopg2-binary"
            }
        
        # Get database URL
        db_url = (
            os.getenv('DATABASE_URL') or 
            os.getenv('POSTGRES_URL') or 
            os.getenv('DB_URL') or
            os.getenv('RENDER_DATABASE_URL')
        )
        
        if not db_url:
            return {
                "success": False,
                "error": "No database URL found",
                "message": "DATABASE_URL environment variable not set"
            }
        
        # Handle postgres:// vs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        # Create engine and connect
        engine = create_engine(db_url)
        
        # SQL to create the intelligence_files table
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
        
        # Execute the SQL
        with engine.connect() as conn:
            # Create table
            conn.execute(text(create_table_sql))
            
            # Create indexes
            conn.execute(text(create_indexes_sql))
            
            # Commit changes
            conn.commit()
            
            # Verify table exists
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'intelligence_files'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            
            return {
                "success": True,
                "message": "Database tables created successfully!",
                "table_created": "intelligence_files",
                "columns_count": len(columns),
                "columns": [{"name": col[0], "type": col[1]} for col in columns[:5]],  # First 5 columns
                "timestamp": datetime.datetime.now().isoformat(),
                "next_steps": [
                    "Your Intelligence module should now work",
                    "Try uploading a file to test",
                    "This endpoint can be safely called multiple times"
                ]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create database tables",
            "troubleshooting": [
                "Check that DATABASE_URL is correct",
                "Ensure database server is running",
                "Verify database user has CREATE TABLE permissions"
            ]
        }

@router.get("/check-tables")
async def check_database_tables() -> Dict[str, Any]:
    """Check if required database tables exist"""
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            return {"success": False, "error": "No DATABASE_URL found"}
        
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if intelligence_files table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'intelligence_files'
                );
            """))
            
            table_exists = result.fetchone()[0]
            
            if table_exists:
                # Get column count
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = 'intelligence_files';
                """))
                column_count = result.fetchone()[0]
                
                return {
                    "success": True,
                    "intelligence_files_exists": True,
                    "columns_count": column_count,
                    "status": "✅ Database is ready",
                    "message": "All required tables exist"
                }
            else:
                return {
                    "success": True,
                    "intelligence_files_exists": False,
                    "status": "❌ Missing tables",
                    "message": "intelligence_files table does not exist",
                    "action_needed": "Visit /api/database-setup/create-tables to create it"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check database tables"
        }
