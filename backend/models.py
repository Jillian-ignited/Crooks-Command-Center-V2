# CRITICAL FIX #6: Create proper database models
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class IntelligenceFile(Base):
    """Intelligence file uploads with AI analysis"""
    __tablename__ = "intelligence_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    source = Column(String(100), default="manual_upload", nullable=False)
    brand = Column(String(100), default="Crooks & Castles", nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    description = Column(Text)
    analysis_results = Column(JSON)  # Store AI analysis as JSON
    status = Column(String(50), default="processed")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True))
    created_by = Column(String(100))

class MediaFile(Base):
    """Media file uploads"""
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    public_url = Column(String(512))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    category = Column(String(100), default="general")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String(100))
    metadata = Column(JSON, default={})

class ExecutiveMetric(Base):
    """Executive dashboard metrics"""
    __tablename__ = "executive_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    metric_type = Column(String(100), nullable=False)  # sales, orders, engagement, etc.
    value = Column(Float, nullable=False)
    period = Column(String(50), default="30d")  # 1d, 7d, 30d, 90d
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})

class ContentBrief(Base):
    """Content creation briefs"""
    __tablename__ = "content_briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    objective = Column(Text)
    audience = Column(String(255))
    tone = Column(String(100))
    channels = Column(JSON, default=[])  # social platforms
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CalendarEvent(Base):
    """Cultural calendar events"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String(100), default="cultural")  # cultural, holiday, brand, etc.
    description = Column(Text)
    relevance = Column(String(50), default="medium")  # low, medium, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ShopifyData(Base):
    """Shopify analytics data"""
    __tablename__ = "shopify_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(100), nullable=False)  # orders, products, customers
    raw_data = Column(JSON, nullable=False)
    processed_data = Column(JSON)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

class CompetitiveIntel(Base):
    """Competitive intelligence data"""
    __tablename__ = "competitive_intel"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor = Column(String(100), nullable=False)
    data_source = Column(String(100), nullable=False)  # instagram, tiktok, manual
    content_type = Column(String(100))  # post, story, ad, etc.
    raw_data = Column(JSON, nullable=False)
    analysis = Column(JSON)
    sentiment = Column(String(50))
    engagement_score = Column(Float)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())

class AgencyProject(Base):
    """Agency project management"""
    __tablename__ = "agency_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    client = Column(String(100), nullable=False)
    status = Column(String(50), default="active")  # active, completed, paused
    budget = Column(Float)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    team_members = Column(JSON, default=[])
    deliverables = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
