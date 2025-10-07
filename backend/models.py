from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class IntelligenceFile(Base):
    __tablename__ = "intelligence_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    original_filename = Column(String)
    source = Column(String, index=True)
    brand = Column(String, index=True, nullable=True)
    file_path = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    description = Column(Text, nullable=True)
    analysis_results = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String, nullable=True)


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="planning")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)
    budget = Column(Float, nullable=True)
    target_audience = Column(String, nullable=True)
    channels = Column(JSON, nullable=True)
    kpis = Column(JSON, nullable=True)
    ai_suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Deliverable(Base):
    __tablename__ = "deliverables"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    type = Column(String)
    status = Column(String, default="not_started")
    priority = Column(String, default="medium")
    assigned_to = Column(String, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    phase = Column(String, nullable=True)
    dependencies = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    campaign = relationship("Campaign", backref="deliverables")


class ShopifyOrder(Base):
    __tablename__ = "shopify_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    order_number = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), index=True)
    total_price = Column(Float)
    subtotal_price = Column(Float, nullable=True)
    total_tax = Column(Float, nullable=True)
    total_discounts = Column(Float, nullable=True)
    customer_email = Column(String, index=True, nullable=True)
    customer_id = Column(String, nullable=True)
    financial_status = Column(String, nullable=True)
    fulfillment_status = Column(String, nullable=True)
    line_items = Column(JSON, nullable=True)
    referring_site = Column(String, nullable=True)
    landing_site = Column(String, nullable=True)
    source_name = Column(String, nullable=True)
    shipping_city = Column(String, nullable=True)
    shipping_province = Column(String, nullable=True)
    shipping_country = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    imported_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ShopifyMetrics(Base):
    __tablename__ = "shopify_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    period_type = Column(String, index=True)
    period_start = Column(DateTime(timezone=True), index=True)
    period_end = Column(DateTime(timezone=True))
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)
    total_sessions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CompetitiveData(Base):
    __tablename__ = "competitive_data"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor = Column(String, index=True)
    platform = Column(String, index=True)
    content_type = Column(String)
    engagement_count = Column(Integer, default=0)
    post_url = Column(String)
    caption = Column(Text)
    hashtags = Column(JSON)
    post_date = Column(DateTime(timezone=True))
    threat_level = Column(String, index=True)
    sentiment = Column(String)
    raw_data = Column(JSON)
    scraped_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
