#!/usr/bin/env python3
"""
Comprehensive database initialization script
Fixes all table schemas for the entire application
"""

import os
import sys
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    sys.exit(1)

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL)

# Create all table structures
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

class ShopifyUpload(Base):
    """Shopify data uploads"""
    __tablename__ = "shopify_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)
    upload_type = Column(String(100), default="general")  # orders, products, customers, etc.
    status = Column(String(50), default="uploaded")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    records_count = Column(Integer)
    processing_notes = Column(Text)

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

def main():
    try:
        with engine.connect() as conn:
            print("🔍 Checking existing tables...")
            
            # Get list of existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            existing_tables = [row[0] for row in result]
            print(f"📋 Found existing tables: {existing_tables}")
            
            # Create all tables (this will only create missing ones)
            print("🏗️ Creating/updating all tables...")
            Base.metadata.create_all(bind=engine)
            
            # Verify all tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            final_tables = [row[0] for row in result]
            print(f"\n✅ Final table list:")
            for table in final_tables:
                print(f"  - {table}")
            
            # Check intelligence_files table specifically
            print(f"\n🔍 Checking intelligence_files table structure...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'intelligence_files'
                ORDER BY ordinal_position;
            """))
            
            intelligence_columns = list(result)
            if intelligence_columns:
                print("📊 intelligence_files columns:")
                for col_name, data_type, nullable in intelligence_columns:
                    print(f"  - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
            else:
                print("❌ intelligence_files table not found!")
            
            # Check shopify_uploads table specifically  
            print(f"\n🔍 Checking shopify_uploads table structure...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'shopify_uploads'
                ORDER BY ordinal_position;
            """))
            
            shopify_columns = list(result)
            if shopify_columns:
                print("📊 shopify_uploads columns:")
                for col_name, data_type, nullable in shopify_columns:
                    print(f"  - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
            else:
                print("❌ shopify_uploads table not found!")
            
            print("\n🎉 Database initialization completed successfully!")
            print("💡 All modules should now work correctly")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
