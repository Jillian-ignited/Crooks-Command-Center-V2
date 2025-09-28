from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import json, statistics
import pandas as pd
from collections import defaultdict

router = APIRouter(tags=["executive"])

@router.get("/")
@router.get("")
async def executive_root() -> Dict[str, Any]:
    """Executive root endpoint - FIXES 404"""
    return await get_executive_overview()

@router.get("/dashboard")
@router.get("/dashboard/")
async def executive_dashboard() -> Dict[str, Any]:
    """Executive dashboard endpoint"""
    return await get_executive_overview()

@router.get("/overview")
async def get_executive_overview(days: int = Query(30, ge=1, le=365)) -> Dict[str, Any]:
    """Get executive overview"""
    return {
        "success": True,
        "timeframe_days": days,
        "shopify_metrics": {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": 0,
            "aov": 0,
            "traffic": 0,
            "status": "no_data"
        },
        "competitive_analysis": {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "status": "no_data"
        },
        "recommendations": [
            {"title": "Upload Shopify Sales Data", "description": "No Shopify data found.", "priority": "critical", "expected_impact": "Enables revenue intelligence", "time_to_implement": "1 day"},
            {"title": "Upload Competitive Intelligence Data", "description": "No competitive data found.", "priority": "high", "expected_impact": "Enables market positioning", "time_to_implement": "1 day"},
            {"title": "Increase AOV", "description": "Current AOV: $0.00. Target $75–120.", "priority": "medium", "expected_impact": "15–25% revenue lift", "time_to_implement": "2–4 weeks"}
        ],
        "alerts": [
            {"level": "critical", "message": "No Shopify sales data", "action": "Upload sales reports"},
            {"level": "warning", "message": "No competitive data", "action": "Upload competitor data"}
        ],
        "data_sources": {"shopify": False, "competitive": False, "social": False},
        "analysis_confidence": {"revenue": 0, "competitive": 0, "trending": 0},
        "last_updated": datetime.now().isoformat()
    }

@router.get("/data-sources")
async def get_data_sources_status() -> Dict[str, Any]:
    """Get data sources status"""
    return {
        "success": True,
        "data_sources": {
            "shopify": {"connected": False, "last_sync": None, "records": 0},
            "competitive": {"connected": False, "last_sync": None, "records": 0},
            "social": {"connected": False, "last_sync": None, "records": 0}
        }
    }
