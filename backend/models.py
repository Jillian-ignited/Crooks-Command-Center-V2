from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()


class Campaign(Base):
    """Marketing campaigns with AI-generated suggestions"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    status = Column(String, default="planning")  # planning, active, completed, paused
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    budget = Column(Float)
    target_audience = Column(String)
    channels = Column(JSON)  # ['instagram', 'tiktok', 'email']
    kpis = Column(JSON)  # Key performance indicators
    ai_suggestions = Column(JSON)  # AI-generated campaign ideas
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Deliverable(Base):
    """Two-way deliverable tracking: brand inputs and agency outputs"""
    __tablename__ = "deliverables"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    type = Column(String)  # ad_creative, social_content, email, etc.
    deliverable_type = Column(String, default="agency_output", index=True)  # 'brand_input' or 'agency_output'
    status = Column(String, default="not_started", index=True)  # not_started, in_progress, completed, blocked, ready
    priority = Column(String, default="medium")  # high, medium, low
    assigned_to = Column(String)
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    phase = Column(String, index=True)  # Phase 1, Phase 2, Phase 3
    dependencies = Column(JSON)  # List of deliverable IDs this depends on
    blocks = Column(JSON)  # List of deliverable titles this unlocks
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    campaign = relationship("Campaign", backref="deliverables")


class Intelligence(Base):
    """Intelligence uploads with Claude AI analysis"""
    __tablename__ = "intelligence"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_type = Column(String)  # pdf, txt, csv, url, manual
    category = Column(String, index=True)  # market_research, competitor_analysis, customer_feedback, etc.
    tags = Column(JSON)  # ['streetwear', 'pricing', 'competitor']
    ai_summary = Column(Text)  # Claude-generated summary
    ai_insights = Column(JSON)  # Structured insights from Claude
    sentiment = Column(String)  # positive, negative, neutral, mixed
    priority = Column(String, default="medium")  # high, medium, low
    status = Column(String, default="new")  # new, reviewed, archived
    file_url = Column(String)  # For uploaded files
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ShopifyMetric(Base):
    """Shopify analytics metrics"""
    __tablename__ = "shopify_metrics"

    id = Column(Integer, primary_key=True, index=True)
    period_type = Column(String, nullable=False, index=True)  # 'daily', 'weekly', 'monthly'
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metrics
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)
    total_sessions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ShopifyProduct(Base):
    """Shopify product sales tracking"""
    __tablename__ = "shopify_products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    handle = Column(String, unique=True, index=True)
    vendor = Column(String)
    product_type = Column(String)
    tags = Column(Text)
    variant_sku = Column(String)
    variant_price = Column(Float)
    total_sales = Column(Float, default=0.0)
    units_sold = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ShopifyOrder(Base):
    """Shopify order details"""
    __tablename__ = "shopify_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_name = Column(String, unique=True, index=True)  # e.g. "#1001"
    order_date = Column(DateTime(timezone=True), nullable=False, index=True)
    customer_name = Column(String)
    customer_email = Column(String)
    financial_status = Column(String)  # paid, pending, refunded
    fulfillment_status = Column(String)  # fulfilled, unfulfilled, partial
    total = Column(Float)
    subtotal = Column(Float)
    shipping = Column(Float)
    taxes = Column(Float)
    discount_amount = Column(Float)
    line_items_count = Column(Integer, default=1)
    product_titles = Column(Text)  # Comma-separated product names
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ShopifyCustomer(Base):
    """Shopify customer tracking"""
    __tablename__ = "shopify_customers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    orders_count = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    first_order_date = Column(DateTime(timezone=True))
    last_order_date = Column(DateTime(timezone=True))
    is_returning = Column(Boolean, default=False)
    accepts_marketing = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class CompetitorIntel(Base):
    """Competitive intelligence tracking"""
    __tablename__ = "competitor_intel"

    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String, nullable=False, index=True)
    category = Column(String)  # pricing, product, marketing, social
    data_type = Column(String)  # price_point, campaign, product_launch, social_post
    content = Column(Text)
    source_url = Column(String)
    sentiment = Column(String)  # threat, opportunity, neutral
    ai_analysis = Column(Text)  # Claude analysis
    priority = Column(String, default="medium")
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExecutiveMetric(Base):
    """Executive dashboard KPIs"""
    __tablename__ = "executive_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False, index=True)  # revenue, orders, aov, etc.
    metric_value = Column(Float, nullable=False)
    metric_change = Column(Float)  # Percentage change vs previous period
    period_type = Column(String, default="monthly")  # daily, weekly, monthly, quarterly
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)  # deliverable_overdue, budget_alert, opportunity, threat
    severity = Column(String, default="info")  # critical, warning, info
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String)  # deliverable, campaign, competitor
    related_entity_id = Column(Integer)
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    read_at = Column(DateTime(timezone=True))
