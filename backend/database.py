import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

# CRITICAL FIX #5: Handle Render PostgreSQL URL format
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    if os.getenv("ENVIRONMENT") == "production":
        raise ValueError("DATABASE_URL required in production!")
    else:
        DATABASE_URL = "sqlite:///./test.db"
        print("[Database] ⚠️ Using SQLite - DEVELOPMENT ONLY")

# CRITICAL FIX #5: Convert postgres:// to postgresql+psycopg://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    print("[Database] Fixed postgres:// to postgresql+psycopg://")

DB_AVAILABLE = False
engine = None
SessionLocal = None

# CRITICAL FIX #8: Better connection pool configuration
try:
    if DATABASE_URL:
        # Connection pool settings for Render
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,           # Max 5 connections in pool
            max_overflow=10,       # Max 10 additional connections
            pool_recycle=3600,     # Recycle connections after 1 hour
            connect_args={
                "connect_timeout": 10,
            } if "postgresql" in DATABASE_URL else {}
        )
        
        # CRITICAL FIX #7: Test connection immediately
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
        print("[Database] ✅ Connection established")
        
except Exception as e:
    print(f"[Database] ❌ Connection failed: {e}")
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError(f"Database required in production: {e}")
    else:
        print("[Database] ⚠️ Continuing without database (development mode)")

# CRITICAL FIX #11: Better error handling in get_db
def get_db():
    """Dependency for FastAPI routes with proper error handling"""
    if not DB_AVAILABLE or engine is None or SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable. Please check configuration."
        )
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

# backend/database.py - UPDATE THE init_db FUNCTION

def init_db():
    """Initialize database tables"""
    if not DB_AVAILABLE or engine is None:
        print("[Database] ⚠️ Skipping - database not available")
        return
        
    try:
        # Import Base from models
        from .models import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("[Database] ✅ Tables initialized:")
        for table in Base.metadata.tables.keys():
            print(f"  - {table}")
            
    except Exception as e:
        print(f"[Database] ❌ Initialization failed: {e}")
        raise
