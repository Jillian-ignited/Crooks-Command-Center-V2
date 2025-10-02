from sqlalchemy import create_engine, text
import os

# Grab your Render DATABASE_URL (already in your env vars)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your Render env vars.")

engine = create_engine(DATABASE_URL)

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