import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
DB_AVAILABLE = False
engine = None

try:
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        DB_AVAILABLE = True
        print("[Database] Connection established")
    else:
        print("[Database] No DATABASE_URL found")
except Exception as e:
    print(f"[Database] Connection failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    if engine:
        Base.metadata.create_all(bind=engine)
        print("[Database] Tables initialized")

