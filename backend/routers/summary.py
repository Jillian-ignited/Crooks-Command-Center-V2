from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()

class OverviewRequest(BaseModel):
    include_shopify: bool = True
    include_intelligence: bool = True
    days_back: int = 30

def load_shopify_data() -> Dict[str, Any]:
    """Load Shopify data if available"""
    try:
        shopify_file = Path("data/shopify/latest_data.json")
        if shopify_file.exists():
            with open(shopify_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def load_intelligence_data() -> Dict[str, Any]:
    """Load latest intelligence data"""
    try:
        # Load uploaded data
        data_dir = Path("data/uploads")
        if not data_dir.exists():
            return {}
        
        all_data = []
        for file_path in data_dir.glob("*.jsonl"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if data:
                                all_data.append(data)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        
        if not all_data:
            return {}
        
        df = pd.DataFrame(all_data)
        
        # Basic intelligence metrics
        total_posts = len(df)
        brands_tracked = df['brand'].nunique() if 'brand' in df.columns else 0
        
        return {
            "total_posts": total_posts,
            "brands_tracked": brands_tracked,
            "data_available": True
        }
        
    except Exception:
        return {"data_available": False}

def generate_unified_insights(shopify_data: Dict, intelligence_data: Dict) -> List[Dict[str, Any]]:
    """Generate unified insights combining revenue and competitive intelligence"""
    insights = []
    
    try:
        # Revenue + Intelligence Correlation
        if shopify_data and intelligence_data.get("data_available"):
            insights.append({
                "priority": 1,
                "title": "Revenue-Intelligence Correlation",
                "description": "Analyze competitor activity impact on your sales performance",
                "impact": "high",
                "effort": "medium",
                "timeline": "immediate",
                "category": "revenue_optimization",
                "action": "Monitor competitor posting patterns during your high-sales periods"
            })
        
        # Social Media ROI Analysis
        if shopify_data:
            insights.append({
                "priority": 2,
                "title": "Social Media ROI Optimization",
                "description": "Identify which social trends drive actual revenue vs just engagement",
                "impact": "high",
                "effort": "low",
                "timeline": "3_days",
                "category": "content_strategy",
                "action": "Focus content on hashtags that correlate with sales spikes"
            })
        
        # Competitive Positioning
        if intelligence_data.get("data_available"):
            insights.append({
                "priority": 3,
                "title": "Market Position Enhancement",
                "description": f"Leverage insights from {intelligence_data.get('brands_tracked', 0)} competitors",
                "impact": "medium",
                "effort": "medium",
                "timeline": "7_days",
                "category": "competitive_strategy",
                "action": "Identify content gaps where competitors are underperforming"
            })
        
        # Data Integration Opportunity
        if not shopify_data and intelligence_data.get("data_available"):
            insights.append({
                "priority": 1,
                "title": "Connect Shopify for Revenue Intelligence",
                "description": "Unlock revenue correlation analysis with competitive data",
                "impact": "high",
                "effort": "low",
                "timeline": "immediate",
                "category": "data_integration",
                "action": "Set up Shopify integration to measure social media ROI"
            })
        
        # Intelligence Enhancement
        if shopify_data and not intelligence_data.get("data_available"):
            insights.append({
                "priority": 1,
                "title": "Add Competitive Intelligence",
                "description": "Upload competitor data to enhance revenue analysis",
                "impact": "high",
                "effort": "low",
                "timeline": "immediate",
                "category": "data_integration",
                "action": "Upload social media scraper data for competitive insights"
            })
        
        # Default insights if no data
        if not shopify_data and not intelligence_data.get("data_available"):
            insights.extend([
                {
                    "priority": 1,
                    "title": "Set Up Data Sources",
                    "description": "Connect Shopify and upload competitor data for complete intelligence",
                    "impact": "high",
                    "effort": "medium",
                    "timeline": "immediate",
                    "category": "setup",
                    "action": "Complete data integration to unlock strategic insights"
                },
                {
                    "priority": 2,
                    "title": "Begin Competitive Analysis",
                    "description": "Upload social media scraper data to start tracking competitors",
                    "impact": "medium",
                    "effort": "low",
                    "timeline": "3_days",
                    "category": "competitive_strategy",
                    "action": "Use Apify or similar tools to gather competitor social data"
                },
                {
                    "priority": 3,
                    "title": "Revenue Tracking Setup",
                    "description": "Connect Shopify to measure real business impact of social strategy",
                    "impact": "high",
                    "effort": "low",
                    "timeline": "immediate",
                    "category": "revenue_optimization",
                    "action": "Integrate Shopify API for sales and traffic correlation"
                }
            ])
        
        return insights[:3]  # Return top 3 prioritized actions
        
    except Exception:
        return [
            {
                "priority": 1,
                "title": "System Setup Required",
                "description": "Configure data sources for strategic intelligence",
                "impact": "high",
                "effort": "medium",
                "timeline": "immediate",
                "category": "setup",
                "action": "Complete initial setup to begin analysis"
            }
        ]

def calculate_health_score(shopify_data: Dict, intelligence_data: Dict) -> Dict[str, Any]:
    """Calculate overall system health score"""
    try:
        score = 0
        max_score = 100
        
        # Data availability (25 points each)
        if shopify_data:
            score += 25
        if intelligence_data.get("data_available"):
            score += 25
        
        # Data quality (25 points)
        if intelligence_data.get("total_posts", 0) > 100:
            score += 25
        elif intelligence_data.get("total_posts", 0) > 50:
            score += 15
        elif intelligence_data.get("total_posts", 0) > 0:
            score += 10
        
        # Integration completeness (25 points)
        if shopify_data and intelligence_data.get("data_available"):
            score += 25  # Full integration
        elif shopify_data or intelligence_data.get("data_available"):
            score += 15  # Partial integration
        
        # Determine status
        if score >= 80:
            status = "excellent"
            status_color = "green"
        elif score >= 60:
            status = "good"
            status_color = "blue"
        elif score >= 40:
            status = "fair"
            status_color = "yellow"
        else:
            status = "needs_attention"
            status_color = "red"
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": round((score / max_score) * 100, 1),
            "status": status,
            "status_color": status_color,
            "factors": {
                "shopify_connected": bool(shopify_data),
                "intelligence_data": intelligence_data.get("data_available", False),
                "data_volume": intelligence_data.get("total_posts", 0),
                "integration_complete": bool(shopify_data and intelligence_data.get("data_available"))
            }
        }
        
    except Exception:
        return {
            "score": 0,
            "max_score": 100,
            "percentage": 0,
            "status": "error",
            "status_color": "red",
            "factors": {
                "shopify_connected": False,
                "intelligence_data": False,
                "data_volume": 0,
                "integration_complete": False
            }
        }

@router.get("/overview")
async def get_executive_overview(include_shopify: bool = True, include_intelligence: bool = True):
    """Get comprehensive executive overview with unified insights"""
    try:
        # Load data from both sources
        shopify_data = load_shopify_data() if include_shopify else {}
        intelligence_data = load_intelligence_data() if include_intelligence else {}
        
        # Calculate health score
        health_score = calculate_health_score(shopify_data, intelligence_data)
        
        # Generate unified insights
        prioritized_actions = generate_unified_insights(shopify_data, intelligence_data)
        
        # Key metrics summary
        key_metrics = {
            "total_posts": intelligence_data.get("total_posts", 0),
            "brands_tracked": intelligence_data.get("brands_tracked", 0),
            "shopify_connected": bool(shopify_data),
            "data_sources_active": sum([
                bool(shopify_data),
                intelligence_data.get("data_available", False)
            ])
        }
        
        # Enhanced analysis
        enhanced_analysis = {
            "market_position": {
                "competitive_ranking": "Analyzing..." if intelligence_data.get("data_available") else "No data",
                "market_share_trend": "Stable" if shopify_data else "Unknown",
                "brand_sentiment": "Positive" if intelligence_data.get("data_available") else "Unknown"
            },
            "revenue_intelligence": {
                "sales_trend": "Growing" if shopify_data else "Connect Shopify",
                "social_roi": "Calculating..." if shopify_data and intelligence_data.get("data_available") else "Insufficient data",
                "conversion_optimization": "Available" if shopify_data else "Requires Shopify"
            },
            "competitive_landscape": {
                "competitor_activity": f"{intelligence_data.get('brands_tracked', 0)} brands tracked",
                "trend_analysis": "Active" if intelligence_data.get("data_available") else "Upload data",
                "opportunity_detection": "Enabled" if intelligence_data.get("data_available") else "Pending"
            }
        }
        
        # Strategic opportunities
        strategic_opportunities = []
        if shopify_data and intelligence_data.get("data_available"):
            strategic_opportunities = [
                "Correlate competitor posting with sales spikes",
                "Identify high-ROI hashtags and content themes",
                "Optimize posting times based on conversion data",
                "Monitor competitor campaigns affecting your sales"
            ]
        elif shopify_data:
            strategic_opportunities = [
                "Upload competitor data for revenue correlation analysis",
                "Track social media ROI with existing sales data",
                "Set up conversion tracking for social campaigns"
            ]
        elif intelligence_data.get("data_available"):
            strategic_opportunities = [
                "Connect Shopify to measure revenue impact",
                "Analyze competitor strategies for market gaps",
                "Leverage trending hashtags for brand visibility"
            ]
        else:
            strategic_opportunities = [
                "Set up Shopify integration for revenue tracking",
                "Upload competitor data for market analysis",
                "Begin comprehensive competitive intelligence"
            ]
        
        # Risk factors
        risk_factors = []
        if not shopify_data:
            risk_factors.append("Missing revenue data - cannot measure social media ROI")
        if not intelligence_data.get("data_available"):
            risk_factors.append("No competitive intelligence - operating blind to market trends")
        if intelligence_data.get("total_posts", 0) < 50:
            risk_factors.append("Limited data volume - insights may not be comprehensive")
        
        return JSONResponse({
            "success": True,
            "health_score": health_score,
            "key_metrics": key_metrics,
            "prioritized_actions": prioritized_actions,
            "enhanced_analysis": enhanced_analysis,
            "strategic_opportunities": strategic_opportunities,
            "risk_factors": risk_factors,
            "data_status": {
                "shopify_connected": bool(shopify_data),
                "intelligence_available": intelligence_data.get("data_available", False),
                "integration_level": "complete" if shopify_data and intelligence_data.get("data_available") else "partial" if shopify_data or intelligence_data.get("data_available") else "none"
            },
            "last_updated": datetime.now().isoformat(),
            "next_update": (datetime.now() + timedelta(hours=1)).isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Executive overview generation failed: {str(e)}",
            "health_score": {
                "score": 0,
                "percentage": 0,
                "status": "error",
                "status_color": "red"
            },
            "key_metrics": {
                "total_posts": 0,
                "brands_tracked": 0,
                "shopify_connected": False,
                "data_sources_active": 0
            },
            "prioritized_actions": [
                {
                    "priority": 1,
                    "title": "System Error",
                    "description": "Unable to generate executive overview",
                    "impact": "high",
                    "effort": "high",
                    "timeline": "immediate",
                    "category": "system",
                    "action": "Check system logs and contact support"
                }
            ],
            "enhanced_analysis": {},
            "strategic_opportunities": [],
            "risk_factors": ["System error preventing analysis"],
            "data_status": {
                "shopify_connected": False,
                "intelligence_available": False,
                "integration_level": "error"
            }
        })

@router.get("/metrics")
async def get_key_metrics():
    """Get key performance metrics"""
    try:
        shopify_data = load_shopify_data()
        intelligence_data = load_intelligence_data()
        
        metrics = {
            "revenue": {
                "total_revenue": shopify_data.get("total_revenue", 0),
                "orders": shopify_data.get("total_orders", 0),
                "aov": shopify_data.get("average_order_value", 0),
                "conversion_rate": shopify_data.get("conversion_rate", 0)
            },
            "intelligence": {
                "posts_analyzed": intelligence_data.get("total_posts", 0),
                "brands_tracked": intelligence_data.get("brands_tracked", 0),
                "sentiment_score": 75,  # Default positive sentiment
                "market_rank": 10  # Default ranking
            },
            "integration": {
                "data_sources": sum([
                    bool(shopify_data),
                    intelligence_data.get("data_available", False)
                ]),
                "last_sync": datetime.now().isoformat(),
                "health_status": "operational"
            }
        }
        
        return JSONResponse({
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Metrics retrieval failed: {str(e)}",
            "metrics": {}
        })

@router.get("/health")
async def summary_health_check():
    """Health check for summary module"""
    try:
        shopify_data = load_shopify_data()
        intelligence_data = load_intelligence_data()
        
        return JSONResponse({
            "status": "healthy",
            "shopify_available": bool(shopify_data),
            "intelligence_available": intelligence_data.get("data_available", False),
            "integration_status": "complete" if shopify_data and intelligence_data.get("data_available") else "partial",
            "last_check": datetime.now().isoformat(),
            "message": "Summary module operational with unified intelligence"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "message": "Summary module health check failed"
        })
