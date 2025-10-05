import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.sql import func
from database import Base

class MediaFile(Base):
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    category = Column(String, default="general")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String, nullable=True)
    meta_data = Column(JSON, default={})  # Changed from metadata

class IntelligenceFile(Base):
    __tablename__ = "intelligence_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    source = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    processed = Column(Boolean, default=False)
    insights = Column(JSON, default={})
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class ExecutiveMetric(Base):
    __tablename__ = "executive_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    period = Column(String, default="30d")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, default={})  # Changed from metadata

class ContentBrief(Base):
    __tablename__ = "content_briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    objective = Column(Text)
    audience = Column(String)
    tone = Column(String)
    channels = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="draft")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String, default="cultural")
    description = Column(Text)
    relevance = Column(String, default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

