# /backend/routers/executive.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import re

router = APIRouter()

# Data directories
SHOPIFY_DATA_DIR = Path("data/shopify")
COMPETITIVE_DATA_DIR = Path("data/competitive") 
UPLOADS_DIR = Path("data/uploads")

# Ensure directories exist
for dir_path in [SHOPIFY_DATA_DIR, COMPETITIVE_DATA_DIR, UPLOADS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def load_shopify_data(days: int = 30) -> Dict[str, Any]:
    """Load real Shopify sales data"""
    shopify_files = list(SHOPIFY_DATA_DIR.glob("*.csv")) + list(SHOPIFY_DATA_DIR.glob("*.json"))
    
    if not shopify_files:
        return {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": 0,
            "aov": 0,
            "traffic": 0,
            "status": "no_data"
        }
    
    all_orders = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in shopify_files:
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                all_orders.extend(df.to_dict('records'))
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_orders.extend(data)
                    else:
                        all_orders.append(data)
        except Exception as e:
            continue
    
    if not all_orders:
        return {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": 0,
            "aov": 0,
            "traffic": 0,
            "status": "no_recent_data"
        }
    
    # Calculate real metrics
    recent_orders = []
    for order in all_orders:
        try:
            order_date = pd.to_datetime(order.get('created_at', order.get('date', datetime.now())))
            if order_date >= cutoff_date:
                recent_orders.append(order)
        except:
            recent_orders.append(order)
    
    if not recent_orders:
        return {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": 0,
            "aov": 0,
            "traffic": 0,
            "status": "no_recent_data"
        }
    
    total_sales = sum([
        float(order.get('total_price', order.get('total', order.get('amount', 0))))
        for order in recent_orders
    ])
    
    total_orders = len(recent_orders)
    aov = total_sales / max(total_orders, 1)
    
    return {
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "conversion_rate": 0,  # Would need traffic data
        "aov": round(aov, 2),
        "traffic": 0,
        "status": "active"
    }

def load_competitive_data() -> Dict[str, Any]:
    """Load competitive intelligence data"""
    comp_files = list(COMPETITIVE_DATA_DIR.glob("*.json")) + list(COMPETITIVE_DATA_DIR.glob("*.csv")) + list(UPLOADS_DIR.glob("*.json")) + list(UPLOADS_DIR.glob("*.csv"))
    
    if not comp_files:
        return {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "status": "no_data"
        }
    
    all_competitor_data = []
    for file_path in comp_files:
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                all_competitor_data.extend(df.to_dict('records'))
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_competitor_data.extend(data)
                    else:
                        all_competitor_data.append(data)
        except Exception as e:
            continue
    
    if not all_competitor_data:
        return {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "status": "no_data"
        }
    
    # Group by brand
    brand_data = defaultdict(list)
    for item in all_competitor_data:
        brand = str(item.get('brand', '')).lower().strip()
        brand_data[brand].append(item)
    
    if not brand_data:
        return {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "status": "no_data"
        }
    
    # Calculate metrics
    brand_metrics = {}
    for brand, posts in brand_data.items():
        if not posts:
            continue
        
        total_engagement = []
        for post in posts:
            likes = int(post.get('likes', 0))
            comments = int(post.get('comments', 0))
            shares = int(post.get('shares', 0))
            total_engagement.append(likes + comments + shares)
        
        brand_metrics[brand] = {
            "total_posts": len(posts),
            "avg_engagement": statistics.mean(total_engagement) if total_engagement else 0,
            "total_engagement": sum(total_engagement)
        }
    
    # Calculate rankings
    ranked_brands = sorted(
        brand_metrics.items(),
        key=lambda x: x[1]['avg_engagement'],
        reverse=True
    )
    
    crooks_rank = None
    for rank, (brand, _) in enumerate(ranked_brands, 1):
        if 'crooks' in brand or 'castles' in brand:
            crooks_rank = rank
            break
    
    return {
        "brands_analyzed": len(brand_metrics),
        "crooks_rank": crooks_rank,
        "market_share": {},
        "performance_comparison": {},
        "status": "active"
    }

def generate_recommendations(shopify_data: Dict, competitive_data: Dict) -> List[Dict[str, Any]]:
    """Generate strategic recommendations"""
    recommendations = []
    
    if shopify_data.get('status') == 'no_data':
        recommendations.append({
            "title": "Upload Shopify Sales Data",
            "description": "No Shopify data found. Upload sales reports to enable revenue analytics.",
            "priority": "critical",
            "expected_impact": "Enables full revenue intelligence",
            "time_to_implement": "1 day"
        })
    
    if competitive_data.get('status') == 'no_data':
        recommendations.append({
            "title": "Upload Competitive Intelligence Data", 
            "description": "No competitive data found. Upload competitor analysis to enable market positioning insights.",
            "priority": "high",
            "expected_impact": "Enables competitive analysis and market positioning",
            "time_to_implement": "1 day"
        })
    
    if shopify_data.get('aov', 0) < 75:
        recommendations.append({
            "title": "Increase Average Order Value",
            "description": f"Current AOV: ${shopify_data.get('aov', 0):.2f}. Industry average: $75-120.",
            "priority": "medium",
            "expected_impact": "15-25% revenue increase",
            "time_to_implement": "2-4 weeks"
        })
    
    crooks_rank = competitive_data.get('crooks_rank')
    if crooks_rank and crooks_rank > 3:
        recommendations.append({
            "title": "Improve Competitive Position",
            "description": f"Currently ranked #{crooks_rank} vs competitors. Focus on engagement improvements.",
            "priority": "high", 
            "expected_impact": "Improved market share and brand visibility",
            "time_to_implement": "4-8 weeks"
        })
    
    return recommendations

@router.get("/overview")
async def get_executive_overview(days: int = Query(30, ge=1, le=365)):
    """Get executive overview with real data integration"""
    try:
        shopify_data = load_shopify_data(days)
        competitive_data = load_competitive_data()
        recommendations = generate_recommendations(shopify_data, competitive_data)
        
        alerts = []
        if shopify_data.get('status') == 'no_data':
            alerts.append({
                "level": "critical",
                "message": "No Shopify sales data available",
                "action": "Upload Shopify sales reports"
            })
        
        if competitive_data.get('status') == 'no_data':
            alerts.append({
                "level": "warning",
                "message": "No competitive intelligence data loaded", 
                "action": "Upload competitive analysis data"
            })
        
        data_sources = {
            "shopify": shopify_data.get('status') == 'active',
            "competitive": competitive_data.get('status') == 'active',
            "social": False  # Would check for social data
        }
        
        return {
            "success": True,
            "timeframe_days": days,
            "shopify_metrics": shopify_data,
            "competitive_analysis": competitive_data,
            "recommendations": recommendations,
            "alerts": alerts,
            "data_sources": data_sources,
            "analysis_confidence": {
                "revenue": 95 if shopify_data.get('status') == 'active' else 0,
                "competitive": 85 if competitive_data.get('brands_analyzed', 0) > 0 else 0,
                "trending": 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive overview failed: {str(e)}")

@router.get("/data-sources")
async def get_data_sources_status():
    """Get status of all data sources"""
    try:
        shopify_files = len(list(SHOPIFY_DATA_DIR.glob("*")))
        competitive_files = len(list(COMPETITIVE_DATA_DIR.glob("*")))
        
        return {
            "shopify": {
                "files": shopify_files,
                "status": "active" if shopify_files > 0 else "missing"
            },
            "competitive": {
                "files": competitive_files,
                "status": "active" if competitive_files > 0 else "missing"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
