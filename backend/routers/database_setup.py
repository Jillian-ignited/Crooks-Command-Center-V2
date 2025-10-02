# backend/routers/database_setup.py
""" Database Setup Router - Initializes the database with necessary tables
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter()

@router.get("/init_db")
def init_db(db: Session = Depends(database.get_db)):
    """Initialize the database with all tables"""
    try:
        models.Base.metadata.create_all(bind=database.engine)
        return {"message": "Database initialized successfully"}
    except Exception as e:
        return {"message": f"Database initialization failed: {e}"}

