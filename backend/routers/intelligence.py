# backend/routers/intelligence.py
# Intelligence router with real data processing - NO MOCK DATA

import os
import uuid
import json
import asyncio
import io  # Added missing import
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import pandas as pd

# Fixed OpenAI client initialization (no proxies parameter)
try:
    from openai import OpenAI
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )
    AI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
    print("[intelligence] OpenAI client initialized successfully")
except ImportError:
    print("[intelligence] OpenAI not available - install with: pip install openai")
    openai_client = None
    AI_AVAILABLE = False
except Exception as e:
    print(f"[intelligence] OpenAI initialization error: {e}")
    openai_client = None
    AI_AVAILABLE = False

router = APIRouter()

# Upload directory setup
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "intelligence")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database setup
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
        print("[intelligence] Database connection established")
    else:
        DB_AVAILABLE = False
        print("[intelligence] No DATABASE_URL configured")
except Exception as e:
    print(f"[intelligence] Database setup error: {e}")
    DB_AVAILABLE = False

@router.post("/upload")
async def upload_intelligence_file(
    file: UploadFile = File(...),
    source: str = Form("manual_upload"),
    brand: str = Form("Crooks & Castles"),
    description: Optional[str] = Form(None)
):
    """Upload and process intelligence files with real data analysis"""
    
    try:
        print(f"[intelligence] Starting upload: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Read and save file
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        print(f"[intelligence] File saved: {file_path} ({len(content)} bytes)")

        # Process file content for real insights
        insights = await process_file_content(content, file.filename, source, brand)

        # Save to database
        file_metadata = {
            "filename": file.filename,
            "source": source,
            "brand": brand,
            "file_path": file_path,
            "processed": True,
            "insights": insights
        }
        
        if DB_AVAILABLE:
            try:
                save_to_database(file_metadata)
                print(f"[intelligence] Saved to database successfully")
            except Exception as db_error:
                print(f"[intelligence] Database save error: {db_error}")

        return {
            "success": True,
            "message": f"File ‘{file.filename}’ uploaded and analyzed successfully",
            "file_id": file_id,
            "insights": insights,
            "ai_analysis_available": AI_AVAILABLE,
            "file_size": len(content),
        }

    except Exception as e:
        print(f"[intelligence] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

async def process_file_content(content: bytes, filename: str, source: str, brand: str) -> List[Dict[str, Any]]:
    """Process file content and extract insights"""
    
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension in [".csv", ".xlsx"]:
        return await process_structured_data(content, file_extension)
    elif file_extension in [".txt", ".md", ".pdf"]:
        return await process_unstructured_data(content, file_extension)
    else:
        return [{
            "type": "unsupported_file",
            "message": f"File type ‘{file_extension}’ not supported for analysis",
            "filename": filename
        }]

async def process_structured_data(content: bytes, file_extension: str) -> List[Dict[str, Any]]:
    """Process structured data (CSV, Excel) for insights"""
    
    try:
        if file_extension == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # Basic data profiling
        insights = [
            {
                "type": "data_profile",
                "rows": len(df),
                "columns": list(df.columns),
                "missing_values": df.isnull().sum().to_dict()
            }
        ]

        # Generate summary statistics
        insights.append({
            "type": "summary_statistics",
            "description": "Summary statistics for numeric columns",
            "stats": df.describe().to_dict()
        })

        # Use AI for deeper insights if available
        if AI_AVAILABLE:
            ai_insights = await get_ai_insights(df.to_string())
            insights.extend(ai_insights)

        return insights

    except Exception as e:
        return [{
            "type": "processing_error",
            "message": f"Error processing structured data: {e}"
        }]

async def process_unstructured_data(content: bytes, file_extension: str) -> List[Dict[str, Any]]:
    """Process unstructured data (text, PDF) for insights"""
    
    try:
        # For simplicity, we treat all as text. PDF extraction would need a library like PyPDF2.
        text_content = content.decode("utf-8", errors="ignore")

        insights = [
            {
                "type": "text_summary",
                "word_count": len(text_content.split()),
                "char_count": len(text_content)
            }
        ]

        # Use AI for deeper insights if available
        if AI_AVAILABLE:
            ai_insights = await get_ai_insights(text_content)
            insights.extend(ai_insights)

        return insights

    except Exception as e:
        return [{
            "type": "processing_error",
            "message": f"Error processing unstructured data: {e}"
        }]

async def get_ai_insights(text_data: str) -> List[Dict[str, Any]]:
    """Use OpenAI to get deeper insights from text data"""
    
    if not openai_client:
        return []

    try:
        prompt = f"""Analyze the following data and provide key insights, trends, and a summary.

        Data:
        {text_data[:4000]}  # Limit token usage

        Provide your analysis as a list of insights in JSON format. Each insight should have a a ‘type’ and ‘description’.
        Example: [{"type": "key_finding", "description": "Sales increased by 20% in Q3"}] 
        """

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst providing insights in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )

        # Extract and parse the JSON response
        if response.choices and response.choices[0].message.content:
            insights_json = response.choices[0].message.content
            # Basic parsing - a more robust solution would handle malformed JSON
            try:
                return json.loads(insights_json)
            except json.JSONDecodeError:
                return [{
                    "type": "ai_parsing_error",
                    "description": "Failed to parse AI response as JSON",
                    "raw_response": insights_json
                }]
        else:
            return []

    except Exception as e:
        print(f"[intelligence] OpenAI analysis error: {e}")
        return [{
            "type": "ai_error",
            "message": f"An error occurred during AI analysis: {e}"
        }]

def save_to_database(file_metadata: Dict):
    """Save file metadata and insights to the database"""
    
    with SessionLocal() as session:
        # Check if table exists, create if not
        try:
            session.execute(text("SELECT 1 FROM intelligence_files LIMIT 1"))
        except Exception:
            session.rollback()
            # This is a simplified table creation - use Alembic for production
            create_table_sql = text("""
            CREATE TABLE intelligence_files (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255),
                source VARCHAR(255),
                brand VARCHAR(255),
                file_path VARCHAR(255),
                processed BOOLEAN,
                insights JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            session.execute(create_table_sql)
            session.commit()
            print("[intelligence] Created intelligence_files table")

        # Insert new record
        insert_sql = text("""
        INSERT INTO intelligence_files (filename, source, brand, file_path, processed, insights)
        VALUES (:filename, :source, :brand, :file_path, :processed, :insights)
        """)
        
        session.execute(insert_sql, {
            "filename": file_metadata["filename"],
            "source": file_metadata["source"],
            "brand": file_metadata["brand"],
            "file_path": file_metadata["file_path"],
            "processed": file_metadata["processed"],
            "insights": json.dumps(file_metadata["insights"])
        })
        session.commit()

def get_database_summary() -> Dict[str, Any]:
    """Get summary from database"""
    
    if not DB_AVAILABLE:
        return {}

    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT COUNT(*) FROM intelligence_files")).fetchone()
            return {"total_records": result[0] if result else 0}
    except Exception as e:
        print(f"[intelligence] Database summary error: {e}")
        return {}

@router.get("/health")
async def intelligence_health():
    """Health check for intelligence module"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "database_available": DB_AVAILABLE,
        "upload_directory": UPLOAD_DIR,
        "upload_directory_exists": os.path.exists(UPLOAD_DIR),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

