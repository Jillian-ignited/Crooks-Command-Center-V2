# backend/services/data_service.py
"""
Centralized data service for connecting all modules to real database data
Replaces mock data with actual uploaded data across the application
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None

logger = logging.getLogger(__name__)

class DataService:
    """Centralized service for accessing real data across all modules"""
    
    @staticmethod
    def get_shopify_metrics() -> Dict[str, Any]:
        """Get real Shopify metrics from uploaded data"""
        if not SessionLocal:
            return DataService._get_empty_shopify_metrics()
        
        try:
            with SessionLocal() as session:
                # Get latest shopify uploads
                result = session.execute(text("""
                    SELECT processing_result, uploaded_at, filename 
                    FROM shopify_uploads 
                    WHERE processing_result IS NOT NULL 
                    ORDER BY uploaded_at DESC 
                    LIMIT 10
                """))
                
                uploads = result.fetchall()
                
                if not uploads:
                    return DataService._get_empty_shopify_metrics()
                
                # Process the uploaded data
                total_sales = 0
                total_orders = 0
                total_traffic = 0
                conversion_data = []
                
                for upload in uploads:
                    try:
                        data = json.loads(upload.processing_result) if isinstance(upload.processing_result, str) else upload.processing_result
                        
                        # Extract metrics from processed data
                        if 'sales' in data:
                            total_sales += float(data.get('sales', 0))
                        if 'orders' in data:
                            total_orders += int(data.get('orders', 0))
                        if 'traffic' in data:
                            total_traffic += int(data.get('traffic', 0))
                        if 'conversion_rate' in data:
                            conversion_data.append(float(data.get('conversion_rate', 0)))
                            
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        logger.warning(f"Error processing upload data: {e}")
                        continue
                
                # Calculate averages and derived metrics
                avg_conversion = sum(conversion_data) / len(conversion_data) if conversion_data else 0
                aov = total_sales / total_orders if total_orders > 0 else 0
                
                return {
                    "total_sales": total_sales,
                    "total_orders": total_orders,
                    "conversion_rate": round(avg_conversion, 2),
                    "aov": round(aov, 2),
                    "traffic": total_traffic,
                    "status": "connected",
                    "data_sources": len(uploads),
                    "last_updated": uploads[0].uploaded_at.isoformat() if uploads else None
                }
                
        except Exception as e:
            logger.error(f"Error getting Shopify metrics: {e}")
            return DataService._get_empty_shopify_metrics()
    
    @staticmethod
    def _get_empty_shopify_metrics() -> Dict[str, Any]:
        """Return empty metrics when no data is available"""
        return {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": 0,
            "aov": 0,
            "traffic": 0,
            "status": "no_data",
            "data_sources": 0,
            "last_updated": None
        }
    
    @staticmethod
    def get_content_metrics() -> Dict[str, Any]:
        """Get real content metrics from database"""
        if not SessionLocal:
            return DataService._get_empty_content_metrics()
        
        try:
            with SessionLocal() as session:
                # Get content briefs
                result = session.execute(text("""
                    SELECT COUNT(*) as total_briefs,
                           SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_briefs,
                           MAX(created_at) as last_created
                    FROM content_briefs
                """))
                
                content_data = result.fetchone()
                
                # Get media files
                media_result = session.execute(text("""
                    SELECT COUNT(*) as total_media,
                           COUNT(CASE WHEN category = 'social_media' THEN 1 END) as social_media,
                           COUNT(CASE WHEN category = 'email' THEN 1 END) as email_campaigns
                    FROM media_files
                    WHERE uploaded_at >= NOW() - INTERVAL '30 days'
                """))
                
                media_data = media_result.fetchone()
                
                return {
                    "total_briefs": content_data.total_briefs or 0,
                    "completed_briefs": content_data.completed_briefs or 0,
                    "total_media": media_data.total_media or 0,
                    "social_media": media_data.social_media or 0,
                    "email_campaigns": media_data.email_campaigns or 0,
                    "last_created": content_data.last_created.isoformat() if content_data.last_created else None,
                    "engagement_rate": DataService._calculate_engagement_rate(),
                    "reach": DataService._calculate_reach()
                }
                
        except Exception as e:
            logger.error(f"Error getting content metrics: {e}")
            return DataService._get_empty_content_metrics()
    
    @staticmethod
    def _get_empty_content_metrics() -> Dict[str, Any]:
        """Return empty content metrics when no data is available"""
        return {
            "total_briefs": 0,
            "completed_briefs": 0,
            "total_media": 0,
            "social_media": 0,
            "email_campaigns": 0,
            "last_created": None,
            "engagement_rate": 0,
            "reach": 0
        }
    
    @staticmethod
    def _calculate_engagement_rate() -> float:
        """Calculate engagement rate from available data"""
        # This would connect to social media APIs or uploaded analytics
        # For now, return 0 if no data is available
        return 0.0
    
    @staticmethod
    def _calculate_reach() -> int:
        """Calculate reach from available data"""
        # This would connect to social media APIs or uploaded analytics
        # For now, return 0 if no data is available
        return 0
    
    @staticmethod
    def get_competitive_insights() -> Dict[str, Any]:
        """Get competitive analysis from intelligence uploads"""
        if not SessionLocal:
            return DataService._get_empty_competitive_insights()
        
        try:
            with SessionLocal() as session:
                result = session.execute(text("""
                    SELECT insights, brand, processed, uploaded_at
                    FROM intelligence_files
                    WHERE brand IS NOT NULL AND insights IS NOT NULL
                    ORDER BY uploaded_at DESC
                    LIMIT 20
                """))
                
                intelligence_data = result.fetchall()
                
                if not intelligence_data:
                    return DataService._get_empty_competitive_insights()
                
                # Process competitive insights
                brands_analyzed = len(set(row.brand for row in intelligence_data if row.brand))
                insights = []
                
                for row in intelligence_data:
                    if row.insights:
                        try:
                            insight_data = json.loads(row.insights) if isinstance(row.insights, str) else row.insights
                            if isinstance(insight_data, list):
                                insights.extend(insight_data)
                            elif isinstance(insight_data, dict):
                                insights.append(insight_data)
                        except (json.JSONDecodeError, TypeError):
                            continue
                
                return {
                    "brands_analyzed": brands_analyzed,
                    "insights": insights[:10],  # Return top 10 insights
                    "analysis": {
                        "market_position": "data_driven",
                        "differentiation": DataService._extract_differentiation(insights),
                        "opportunities": DataService._extract_opportunities(insights)
                    },
                    "last_updated": intelligence_data[0].uploaded_at.isoformat() if intelligence_data else None
                }
                
        except Exception as e:
            logger.error(f"Error getting competitive insights: {e}")
            return DataService._get_empty_competitive_insights()
    
    @staticmethod
    def _get_empty_competitive_insights() -> Dict[str, Any]:
        """Return empty competitive insights when no data is available"""
        return {
            "brands_analyzed": 0,
            "insights": [],
            "analysis": {
                "market_position": "no_data",
                "differentiation": [],
                "opportunities": []
            },
            "last_updated": None
        }
    
    @staticmethod
    def _extract_differentiation(insights: List[Dict]) -> List[str]:
        """Extract differentiation points from insights"""
        # Basic keyword extraction - can be enhanced with AI
        differentiators = []
        keywords = ["unique", "different", "distinctive", "heritage", "authentic"]
        
        for insight in insights:
            if isinstance(insight, dict):
                text = str(insight.get("description", "")).lower()
                for keyword in keywords:
                    if keyword in text and keyword not in differentiators:
                        differentiators.append(keyword)
        
        return differentiators[:5]  # Return top 5
    
    @staticmethod
    def _extract_opportunities(insights: List[Dict]) -> List[str]:
        """Extract opportunities from insights"""
        # Basic keyword extraction - can be enhanced with AI
        opportunities = []
        keywords = ["opportunity", "growth", "expansion", "digital", "social", "collaboration"]
        
        for insight in insights:
            if isinstance(insight, dict):
                text = str(insight.get("description", "")).lower()
                for keyword in keywords:
                    if keyword in text and keyword not in opportunities:
                        opportunities.append(f"{keyword} opportunity")
        
        return opportunities[:5]  # Return top 5
    
    @staticmethod
    def get_agency_projects() -> Dict[str, Any]:
        """Get real agency project data from content briefs"""
        if not SessionLocal:
            return DataService._get_empty_agency_projects()
        
        try:
            with SessionLocal() as session:
                result = session.execute(text("""
                    SELECT 
                        COUNT(*) as total_deliverables,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                        SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as not_started
                    FROM content_briefs
                """))
                
                project_data = result.fetchone()
                
                # Get upcoming deadlines from calendar events
                deadlines_result = session.execute(text("""
                    SELECT title, event_date, description, relevance
                    FROM calendar_events
                    WHERE event_date >= CURRENT_DATE
                    ORDER BY event_date ASC
                    LIMIT 5
                """))
                
                deadlines = deadlines_result.fetchall()
                
                total = project_data.total_deliverables or 0
                completed = project_data.completed or 0
                completion_rate = (completed / total * 100) if total > 0 else 0
                
                return {
                    "project_overview": {
                        "total_deliverables": total,
                        "completed": completed,
                        "in_progress": project_data.in_progress or 0,
                        "not_started": project_data.not_started or 0,
                        "overdue": 0,  # Would need deadline logic
                        "completion_rate": round(completion_rate, 1)
                    },
                    "upcoming_deadlines": [
                        {
                            "task": deadline.title,
                            "due_date": deadline.event_date.isoformat(),
                            "days_until_due": (deadline.event_date - datetime.now().date()).days,
                            "priority": "High" if deadline.relevance == "high" else "Medium",
                            "description": deadline.description
                        }
                        for deadline in deadlines
                    ],
                    "data_sources": "real_data",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting agency projects: {e}")
            return DataService._get_empty_agency_projects()
    
    @staticmethod
    def _get_empty_agency_projects() -> Dict[str, Any]:
        """Return empty agency projects when no data is available"""
        return {
            "project_overview": {
                "total_deliverables": 0,
                "completed": 0,
                "in_progress": 0,
                "not_started": 0,
                "overdue": 0,
                "completion_rate": 0.0
            },
            "upcoming_deadlines": [],
            "data_sources": "no_data",
            "last_updated": datetime.now().isoformat()
        }
    
    @staticmethod
    def calculate_trends(current_metrics: Dict, period_days: int = 30) -> Dict[str, Any]:
        """Calculate trend indicators by comparing current vs previous period"""
        if not SessionLocal:
            return {}
        
        try:
            with SessionLocal() as session:
                # Get historical executive metrics
                result = session.execute(text("""
                    SELECT metric_type, value, recorded_at
                    FROM executive_metrics
                    WHERE recorded_at >= NOW() - INTERVAL '%s days'
                    ORDER BY recorded_at DESC
                """), (period_days * 2,))  # Get 2x period for comparison
                
                historical_data = result.fetchall()
                
                # Calculate trends (simplified version)
                trends = {}
                for metric_name, current_value in current_metrics.items():
                    if isinstance(current_value, (int, float)):
                        # Find historical value for comparison
                        historical_values = [
                            row.value for row in historical_data 
                            if row.metric_type == metric_name
                        ]
                        
                        if historical_values:
                            avg_historical = sum(historical_values) / len(historical_values)
                            if avg_historical > 0:
                                change_percent = ((current_value - avg_historical) / avg_historical) * 100
                                trends[f"{metric_name}_trend"] = {
                                    "direction": "up" if change_percent > 0 else "down",
                                    "percentage": abs(round(change_percent, 1))
                                }
                
                return trends
                
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
