# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create Base directly here to avoid import issues
Base = declarative_base()

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
    analysis_results = Column(JSON)
    status = Column(String(50), default="processed")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True))
    created_by = Column(String(100))


class Campaign(Base):
    """Marketing campaigns with AI content suggestions"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    theme = Column(String(255))
    
    # Dates
    launch_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    status = Column(String(50), default="planning")
    
    # Cultural context
    cultural_moment = Column(String(255))
    target_audience = Column(Text)
    
    # AI suggestions
    content_suggestions = Column(JSON)
    
    # Brand
    brand = Column(String(100), default="Crooks & Castles")
    
    # Notes
    notes = Column(Text)


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
    file_metadata = Column(JSON, default={})


class ExecutiveMetric(Base):
    """Executive dashboard metrics"""
    __tablename__ = "executive_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    metric_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    period = Column(String(50), default="30d")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    metric_metadata = Column(JSON, default={})


class ContentBrief(Base):
    """Content creation briefs"""
    __tablename__ = "content_briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    objective = Column(Text)
    audience = Column(String(255))
    tone = Column(String(100))
    channels = Column(JSON, default=[])
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CalendarEvent(Base):
    """Cultural calendar events"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String(100), default="cultural")
    description = Column(Text)
    relevance = Column(String(50), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShopifyData(Base):
    """Shopify analytics data"""
    __tablename__ = "shopify_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(100), nullable=False)
    raw_data = Column(JSON, nullable=False)
    processed_data = Column(JSON)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))


class CompetitiveIntel(Base):
    """Competitive intelligence data"""
    __tablename__ = "competitive_intel"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor = Column(String(100), nullable=False)
    data_source = Column(String(100), nullable=False)
    content_type = Column(String(100))
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
    status = Column(String(50), default="active")
    budget = Column(Float)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    team_members = Column(JSON, default=[])
    deliverables = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
class Deliverable(Base):
    """Agency deliverables tracker - flexible phases"""
    __tablename__ = "deliverables"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer)  # Optional link to campaign
    
    # Phase info (not date-locked)
    phase = Column(String(50), nullable=False)  # "Phase 1", "Phase 2", "Phase 3"
    phase_name = Column(String(255))  # "Foundation & Awareness", etc.
    
    # Task details
    category = Column(String(100), nullable=False)
    task = Column(Text, nullable=False)
    asset_requirements = Column(Text)
    
    # Dates (flexible)
    due_date = Column(DateTime(timezone=True))
    completed_date = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(50), default="not_started")  # not_started, in_progress, complete, blocked
    
    # Ownership
    owner = Column(String(100))  # High Voltage or You
    assigned_to = Column(String(100))  # Specific person
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
class ShopifyOrder(Base):
    """Individual Shopify orders for detailed tracking"""
    __tablename__ = "shopify_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True)
    order_number = Column(String(50))
    
    # Order details
    created_at = Column(DateTime(timezone=True))
    total_price = Column(Float)
    subtotal_price = Column(Float)
    total_tax = Column(Float)
    total_discounts = Column(Float)
    
    # Customer
    customer_email = Column(String(255))
    customer_id = Column(String(100))
    
    # Fulfillment
    financial_status = Column(String(50))
    fulfillment_status = Column(String(50))
    
    # Products
    line_items = Column(JSON)  # Array of products in order
    
    # Marketing
    referring_site = Column(String(255))
    landing_site = Column(String(512))
    source_name = Column(String(100))
    
    # Location
    shipping_city = Column(String(100))
    shipping_province = Column(String(100))
    shipping_country = Column(String(100))
    
    # Metadata
    tags = Column(String(512))
    note = Column(Text)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class ShopifyMetrics(Base):
    """Aggregated Shopify metrics by day/week/month"""
    __tablename__ = "shopify_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Float, default=0)
    total_orders = Column(Integer, default=0)
    avg_order_value = Column(Float, default=0)
    
    # Customer metrics
    total_customers = Column(Integer, default=0)
    new_customers = Column(Integer, default=0)
    returning_customers = Column(Integer, default=0)
    
    # Product metrics
    total_items_sold = Column(Integer, default=0)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
class ShopifyOrder(Base):
    """Individual Shopify orders for detailed tracking"""
    __tablename__ = "shopify_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True)
    order_number = Column(String(50))
    
    # Order details
    created_at = Column(DateTime(timezone=True))
    total_price = Column(Float)
    subtotal_price = Column(Float)
    total_tax = Column(Float)
    total_discounts = Column(Float)
    
    # Customer
    customer_email = Column(String(255))
    customer_id = Column(String(100))
    
    # Fulfillment
    financial_status = Column(String(50))
    fulfillment_status = Column(String(50))
    
    # Products
    line_items = Column(JSON)
    
    # Marketing
    referring_site = Column(String(255))
    landing_site = Column(String(512))
    source_name = Column(String(100))
    
    # Location
    shipping_city = Column(String(100))
    shipping_province = Column(String(100))
    shipping_country = Column(String(100))
    
    # Metadata
    tags = Column(String(512))
    note = Column(Text)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class ShopifyMetrics(Base):
    """Aggregated Shopify metrics by day/week/month"""
    __tablename__ = "shopify_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    period_type = Column(String(20), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Float, default=0)
    total_orders = Column(Integer, default=0)
    avg_order_value = Column(Float, default=0)
    
    # Customer metrics
    total_customers = Column(Integer, default=0)
    new_customers = Column(Integer, default=0)
    returning_customers = Column(Integer, default=0)
    
    # Product metrics
    total_items_sold = Column(Integer, default=0)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
class ShopifyOrder(Base):
    """Individual Shopify orders for detailed tracking"""
    __tablename__ = "shopify_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True)
    order_number = Column(String(50))
    
    # Order details
    created_at = Column(DateTime(timezone=True))
    total_price = Column(Float)
    subtotal_price = Column(Float)
    total_tax = Column(Float)
    total_discounts = Column(Float)
    
    # Customer
    customer_email = Column(String(255))
    customer_id = Column(String(100))
    
    # Fulfillment
    financial_status = Column(String(50))
    fulfillment_status = Column(String(50))
    
    # Products
    line_items = Column(JSON)
    
    # Marketing
    referring_site = Column(String(255))
    landing_site = Column(String(512))
    source_name = Column(String(100))
    
    # Location
    shipping_city = Column(String(100))
    shipping_province = Column(String(100))
    shipping_country = Column(String(100))
    
    # Metadata
    tags = Column(String(512))
    note = Column(Text)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class ShopifyMetrics(Base):
    """Aggregated Shopify metrics by day/week/month"""
    __tablename__ = "shopify_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    period_type = Column(String(20), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Float, default=0)
    total_orders = Column(Integer, default=0)
    avg_order_value = Column(Float, default=0)
    
    # Customer metrics
    total_customers = Column(Integer, default=0)
    new_customers = Column(Integer, default=0)
    returning_customers = Column(Integer, default=0)
    
    # Product metrics
    total_items_sold = Column(Integer, default=0)
    
    # Conversion metrics
    total_sessions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
