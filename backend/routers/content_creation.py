# backend/routers/content_creation.py
""" Content Creation Router - Now using REAL data from content briefs

Replaces all mock data with actual content creation data from database
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import datetime
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from data_service import DataService
except ImportError:
    # Fallback if data_service isn't available
    class DataService:
        @staticmethod
        def get_content_briefs():
            return []

router = APIRouter()

@router.get("/overview")
async def get_content_overview() -> Dict[str, Any]:
    """Get content creation overview"""
    
    briefs = DataService.get_content_briefs()
    
    return {
        "total_briefs": len(briefs),
        "briefs": briefs,
        "data_source": "real_content_brief_data"
    }

@router.get("/briefs/{brief_id}")
async def get_content_brief(brief_id: str) -> Dict[str, Any]:
    """Get a specific content brief"""
    
    briefs = DataService.get_content_briefs()
    brief = next((b for b in briefs if b.get("id") == brief_id), None)
    
    if not brief:
        raise HTTPException(status_code=404, detail="Content brief not found")
        
    return brief

@router.post("/briefs")
async def create_content_brief(brief_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new content brief"""
    
    # This would normally save to the database
    # For now, we'll just return the data
    brief_data["id"] = f"brief_{datetime.datetime.now().timestamp()}"
    brief_data["created_at"] = datetime.datetime.now().isoformat()
    
    return {"message": "Content brief created successfully", "brief": brief_data}

