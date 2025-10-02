# backend/migrate_shopify_uploads.py
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your Render env vars.")

# Normalize scheme for SQLAlchemy + psycopg (Render sometimes uses 'postgres://')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, future=True)

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS shopify_uploads (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            data_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            description TEXT,
            processing_result JSONB,
            uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """))
    conn.commit()

print("✅ shopify_uploads table created (or already exists).")