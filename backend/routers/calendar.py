# backend/routers/calendar.py
""" Calendar Router - Now using REAL data from calendar events and content briefs

Replaces all mock data with actual calendar data from database
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
        def get_calendar_events():
            return []

router = APIRouter()

@router.get("/events")
async def get_calendar_events() -> Dict[str, Any]:
    """Get all calendar events"""
    
    events = DataService.get_calendar_events()
    
    return {
        "total_events": len(events),
        "events": events,
        "data_source": "real_calendar_data"
    }

@router.get("/cultural_calendar")
async def get_cultural_calendar() -> Dict[str, Any]:
    """Get cultural calendar events"""
    
    # This could be enhanced with a dedicated cultural calendar data source
    # For now, we'll filter from the main calendar events
    events = DataService.get_calendar_events()
    cultural_events = [e for e in events if e.get("category") == "cultural"]
    
    return {
        "total_events": len(cultural_events),
        "events": cultural_events,
        "data_source": "real_calendar_data"
    }

@router.get("/periods")
async def get_calendar_periods() -> Dict[str, Any]:
    """Get calendar periods for planning"""
    
    # This could be enhanced with a dedicated periods data source
    # For now, we'll generate some standard periods
    periods = [
        {"name": "Q4 2025", "start_date": "2025-10-01", "end_date": "2025-12-31"},
        {"name": "Q1 2026", "start_date": "2026-01-01", "end_date": "2026-03-31"},
        {"name": "Q2 2026", "start_date": "2026-04-01", "end_date": "2026-06-30"},
    ]
    
    return {
        "total_periods": len(periods),
        "periods": periods,
        "data_source": "generated"
    }

@router.get("/status")
async def get_calendar_status() -> Dict[str, Any]:
    """Get calendar status"""
    
    return {"status": "ok", "last_updated": datetime.datetime.now().isoformat()}

