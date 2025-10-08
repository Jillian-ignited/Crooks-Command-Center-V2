from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db

router = APIRouter()


@router.post("/migrate-all-tables")
def migrate_all_tables(db: Session = Depends(get_db)):
    """DANGER: Recreate ALL tables - will delete all data!"""
    
    try:
        print("[Migration] Starting full database migration...")
        
        # Drop all tables in reverse dependency order
        tables_to_drop = [
            "deliverables",
            "campaigns",
            "intelligence",
            "shopify_metrics",
            "competitor_intel",
            "executive_metrics",
            "alerts"
        ]
        
        for table in tables_to_drop:
            db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            print(f"[Migration] Dropped {table}")
        
        db.commit()
        print("[Migration] All old tables dropped")
        
        # Create campaigns table
        db.execute(text("""
            CREATE TABLE campaigns (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                description TEXT,
                status VARCHAR DEFAULT 'planning',
                start_date TIMESTAMP WITH TIME ZONE,
                end_date TIMESTAMP WITH TIME ZONE,
                budget FLOAT,
                target_audience VARCHAR,
                channels JSONB,
                kpis JSONB,
                ai_suggestions JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("CREATE INDEX ix_campaigns_id ON campaigns(id)"))
        db.execute(text("CREATE INDEX ix_campaigns_name ON campaigns(name)"))
        print("[Migration] ✅ campaigns table created")
        
        # Create deliverables table
        db.execute(text("""
            CREATE TABLE deliverables (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER REFERENCES campaigns(id),
                title VARCHAR NOT NULL,
                description TEXT,
                type VARCHAR,
                deliverable_type VARCHAR DEFAULT 'agency_output',
                status VARCHAR DEFAULT 'not_started',
                priority VARCHAR DEFAULT 'medium',
                assigned_to VARCHAR,
                due_date TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                phase VARCHAR,
                dependencies JSONB,
                blocks JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("CREATE INDEX ix_deliverables_id ON deliverables(id)"))
        db.execute(text("CREATE INDEX ix_deliverables_title ON deliverables(title)"))
        db.execute(text("CREATE INDEX ix_deliverables_phase ON deliverables(phase)"))
        db.execute(text("CREATE INDEX ix_deliverables_status ON deliverables(status)"))
        db.execute(text("CREATE INDEX ix_deliverables_deliverable_type ON deliverables(deliverable_type)"))
        print("[Migration] ✅ deliverables table created")
        
        # Create intelligence table
        db.execute(text("""
            CREATE TABLE intelligence (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                content TEXT NOT NULL,
                source_type VARCHAR,
                category VARCHAR,
                tags JSONB,
                ai_summary TEXT,
                ai_insights JSONB,
                sentiment VARCHAR,
                priority VARCHAR DEFAULT 'medium',
                status VARCHAR DEFAULT 'new',
                file_url VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("CREATE INDEX ix_intelligence_id ON intelligence(id)"))
        db.execute(text("CREATE INDEX ix_intelligence_title ON intelligence(title)"))
        db.execute(text("CREATE INDEX ix_intelligence_category ON intelligence(category)"))
        db.execute(text("CREATE INDEX ix_intelligence_created_at ON intelligence(created_at)"))
        print("[Migration] ✅ intelligence table created")
        
        # Create shopify_metrics table
        db.execute(text("""
            CREATE TABLE shopify_metrics (
                id SERIAL PRIMARY KEY,
                period_type VARCHAR NOT NULL,
                period_start TIMESTAMP WITH TIME ZONE NOT NULL,
                period_end TIMESTAMP WITH TIME ZONE NOT NULL,
                total_orders INTEGER DEFAULT 0,
                total_revenue FLOAT DEFAULT 0,
                avg_order_value FLOAT DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                conversion_rate FLOAT DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("CREATE INDEX ix_shopify_metrics_id ON shopify_metrics(id)"))
        db.execute(text("CREATE INDEX ix_shopify_metrics_period_type ON shopify_metrics(period_type)"))
        db.execute(text("CREATE INDEX ix_shopify_metrics_period_start ON shopify_metrics(period_start)"))
        print("[Migration] ✅ shopify_metrics table created")
        
        # Create competitor_intel table
        db.execute(text("""
            CREATE TABLE competitor_intel (
                id SERIAL PRIMARY KEY,
                competitor_name VARCHAR NOT NULL,
                category VARCHAR,
                data_type VARCHAR,
                content TEXT,
                source_url VARCHAR,
                sentiment VARCHAR,
                ai_analysis TEXT,
                priority VARCHAR DEFAULT 'medium',
                tags JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("CREATE INDEX ix_competitor_intel_id ON competitor_intel(id)"))
        db.execute(text("CREATE INDEX ix_competitor_intel_competitor_name ON competitor_intel(competitor_name)"))
        db.execute(text("CREATE INDEX ix_competitor_intel_created_at ON competitor_intel(created_at)"))
        print("[Migration] ✅ competitor_intel table created")
        
        # Create executive_metrics table
        db.execute(text("""
            CREATE TABLE executive_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR NOT NULL,
                metric_value FLOAT NOT NULL,
                metric_change FLOAT,
                period_type VARCHAR DEFAULT 'monthly',
                period_start TIMESTAMP WITH TIME ZONE NOT NULL,
                period_end TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("CREATE INDEX ix_executive_metrics_id ON executive_metrics(id)"))
        db.execute(text("CREATE INDEX ix_executive_metrics_metric_name ON executive_metrics(metric_name)"))
        db.execute(text("CREATE INDEX ix_executive_metrics_period_start ON executive_metrics(period_start)"))
        print("[Migration] ✅ executive_metrics table created")
        
        # Create alerts table
        db.execute(text("""
            CREATE TABLE alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR NOT NULL,
                severity VARCHAR DEFAULT 'info',
                title VARCHAR NOT NULL,
                message TEXT NOT NULL,
                related_entity_type VARCHAR,
                related_entity_id INTEGER,
                is_read BOOLEAN DEFAULT FALSE,
                is_dismissed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP WITH TIME ZONE
            )
        """))
        db.execute(text("CREATE INDEX ix_alerts_id ON alerts(id)"))
        db.execute(text("CREATE INDEX ix_alerts_created_at ON alerts(created_at)"))
        print("[Migration] ✅ alerts table created")
        
        db.commit()
        print("[Migration] All tables committed successfully!")
        
        return {
            "success": True,
            "message": "✅ ALL TABLES CREATED SUCCESSFULLY!",
            "tables_created": [
                "campaigns",
                "deliverables", 
                "intelligence",
                "shopify_metrics",
                "competitor_intel",
                "executive_metrics",
                "alerts"
            ]
        }
        
    except Exception as e:
        db.rollback()
        print(f"[Migration] ❌ Migration failed: {e}")
        raise HTTPException(500, f"Migration failed: {str(e)}")


@router.get("/check-tables")
def check_tables(db: Session = Depends(get_db)):
    """Check which tables exist in the database"""
    
    try:
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        
        expected_tables = [
            "campaigns",
            "deliverables",
            "intelligence", 
            "shopify_metrics",
            "competitor_intel",
            "executive_metrics",
            "alerts"
        ]
        
        missing_tables = [t for t in expected_tables if t not in tables]
        
        return {
            "existing_tables": tables,
            "expected_tables": expected_tables,
            "missing_tables": missing_tables,
            "all_tables_exist": len(missing_tables) == 0
        }
        
    except Exception as e:
        raise HTTPException(500, f"Check failed: {str(e)}")
