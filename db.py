# db.py
import os, psycopg2, psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL", "")

def conn():
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    if not DATABASE_URL:
        return
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
          id UUID PRIMARY KEY,
          title TEXT NOT NULL,
          content TEXT,
          platform TEXT,
          scheduled_at TIMESTAMPTZ,
          code_name TEXT,
          badge_score INT DEFAULT 0,
          hashtags TEXT,
          asset_id UUID,
          status TEXT DEFAULT 'draft',
          owner TEXT,
          due_date DATE,
          created_at TIMESTAMPTZ DEFAULT now(),
          updated_at TIMESTAMPTZ DEFAULT now()
        );
        CREATE TABLE IF NOT EXISTS assets (
          id UUID PRIMARY KEY,
          original_name TEXT,
          file_type TEXT,
          file_url TEXT,
          badge_score INT DEFAULT 0,
          assigned_code TEXT,
          created_at TIMESTAMPTZ DEFAULT now(),
          usage_count INT DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS deliverables (
          id TEXT PRIMARY KEY,            -- e.g. '2025-09'
          phase TEXT,
          budget TEXT,
          social_target INT,
          social_current INT,
          creative_target INT,
          creative_current INT,
          email_target INT,
          email_current INT,
          notes TEXT,
          updated_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        c.commit()
