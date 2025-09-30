# backend/routers/upload_sidecar.py
# Real Intelligence router with actual data processing - NO MOCK DATA

import os
import uuid
import json
import csv
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import pandas as pd

# Proper OpenAI client initialization (fixed - no proxies)
try:
    from openai import OpenAI
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )
    AI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    print("[intelligence] OpenAI not available")
    openai_client = None
    AI_AVAILABLE = False
except Exception as e:
    print(f"[intelligence] OpenAI error: {e}")
    openai_client = None
    AI_AVAILABLE = False

router = APIRouter()

# Real upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "intelligence")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database connection (using the existing database setup)
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
    else:
        DB_AVAILABLE = False
        print("[intelligence] No database URL configured")
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
    """Upload and process real intelligence files"""
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Generate unique filename and save
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Read and save file content
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        print(f"[intelligence] Saved file: {file_path}")
        
        # Process the actual file content
        insights = await process_real_file_content(content, file.filename, source, brand)
        
        # Save to database if available
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
                print(f"[intelligence] Saved to database")
            except Exception as db_error:
                print(f"[intelligence] Database error: {db_error}")
        
        return {
            "success": True,
            "message": f"File '{file.filename}' processed successfully",
            "file_id": file_id,
            "insights": insights,
            "ai_analysis_available": AI_AVAILABLE
        }
        
    except Exception as e:
        print(f"[intelligence] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/summary")
async def get_intelligence_summary():
    """Get real intelligence summary from uploaded files"""
    
    try:
        # Get actual uploaded files
        uploaded_files = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    uploaded_files.append({
                        "filename": filename,
                        "size": file_stats.st_size,
                        "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "file_path": file_path
                    })
        
        # Process files to get real insights
        total_files = len(uploaded_files)
        total_size = sum(f["size"] for f in uploaded_files)
        
        # Analyze file types
        file_types = {}
        for f in uploaded_files:
            ext = os.path.splitext(f["filename"])[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # Get database summary if available
        db_summary = {}
        if DB_AVAILABLE:
            try:
                db_summary = get_database_summary()
            except Exception as e:
                print(f"[intelligence] Database summary error: {e}")
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "file_types": file_types,
            "recent_uploads": uploaded_files[-10:],  # Last 10 files
            "database_records": db_summary.get("total_records", 0),
            "ai_analysis_available": AI_AVAILABLE,
            "storage_location": UPLOAD_DIR
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/files")
async def get_uploaded_files():
    """Get list of actually uploaded files with real metadata"""
    
    try:
        files = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    
                    # Try to extract insights from file
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        file_insights = await analyze_file_content(content, filename)
                    except:
                        file_insights = {"error": "Could not analyze file"}
                    
                    files.append({
                        "filename": filename,
                        "size": file_stats.st_size,
                        "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "insights": file_insights
                    })
        
        return {
            "files": sorted(files, key=lambda x: x["uploaded_at"], reverse=True),
            "total_files": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")

async def process_real_file_content(content: bytes, filename: str, source: str, brand: str) -> Dict[str, Any]:
    """Process actual file content and extract real insights"""
    
    try:
        # Extract text from file based on type
        file_text = extract_text_content(content, filename)
        
        if not file_text:
            return {"error": "Could not extract text from file", "file_size": len(content)}
        
        # Analyze the actual content
        content_analysis = analyze_content_structure(file_text, filename)
        
        # Generate AI insights if available
        ai_insights = {}
        if AI_AVAILABLE and openai_client and len(file_text) > 50:
            try:
                ai_insights = await generate_real_ai_insights(file_text, source, brand)
            except Exception as e:
                ai_insights = {"ai_error": str(e)}
        
        return {
            "file_analysis": content_analysis,
            "ai_insights": ai_insights,
            "processing_timestamp": datetime.now().isoformat(),
            "source": source,
            "brand": brand
        }
        
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

def extract_text_content(content: bytes, filename: str) -> str:
    """Extract actual text content from uploaded files"""
    
    try:
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension in ['.txt', '.csv', '.tsv']:
            return content.decode('utf-8', errors='ignore')
        
        elif file_extension in ['.json', '.jsonl']:
            text_content = content.decode('utf-8', errors='ignore')
            # For JSONL files, process line by line
            if file_extension == '.jsonl':
                lines = text_content.strip().split('\n')
                processed_lines = []
                for line in lines:
                    try:
                        data = json.loads(line)
                        processed_lines.append(json.dumps(data, indent=2))
                    except:
                        processed_lines.append(line)
                return '\n'.join(processed_lines)
            return text_content
        
        else:
            # Try to decode as text
            return content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"[intelligence] Text extraction error: {e}")
        return ""

def analyze_content_structure(text: str, filename: str) -> Dict[str, Any]:
    """Analyze the actual structure and content of uploaded data"""
    
    try:
        analysis = {
            "filename": filename,
            "character_count": len(text),
            "line_count": len(text.split('\n')),
            "word_count": len(text.split()),
            "file_type": os.path.splitext(filename)[1].lower()
        }
        
        # Detect data format
        if filename.endswith('.json') or filename.endswith('.jsonl'):
            analysis.update(analyze_json_content(text))
        elif filename.endswith('.csv'):
            analysis.update(analyze_csv_content(text))
        else:
            analysis.update(analyze_text_content(text))
        
        return analysis
        
    except Exception as e:
        return {"error": f"Content analysis failed: {str(e)}"}

def analyze_json_content(text: str) -> Dict[str, Any]:
    """Analyze JSON/JSONL content for real insights"""
    
    try:
        analysis = {"data_type": "json"}
        
        # Try to parse as JSON
        lines = text.strip().split('\n')
        records = []
        
        for line in lines:
            try:
                data = json.loads(line)
                records.append(data)
            except:
                continue
        
        if records:
            analysis["total_records"] = len(records)
            
            # Analyze record structure
            if records:
                sample_record = records[0]
                analysis["fields"] = list(sample_record.keys()) if isinstance(sample_record, dict) else []
                
                # Look for common social media fields
                social_fields = ["text", "caption", "content", "message", "post"]
                text_fields = [f for f in analysis["fields"] if any(sf in f.lower() for sf in social_fields)]
                
                if text_fields:
                    # Extract actual text content for analysis
                    all_text = []
                    for record in records[:100]:  # Analyze first 100 records
                        for field in text_fields:
                            if field in record and record[field]:
                                all_text.append(str(record[field]))
                    
                    if all_text:
                        combined_text = ' '.join(all_text)
                        analysis["content_analysis"] = analyze_text_content(combined_text)
        
        return analysis
        
    except Exception as e:
        return {"json_analysis_error": str(e)}

def analyze_csv_content(text: str) -> Dict[str, Any]:
    """Analyze CSV content for real insights"""
    
    try:
        # Use pandas to analyze CSV structure
        from io import StringIO
        df = pd.read_csv(StringIO(text))
        
        analysis = {
            "data_type": "csv",
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist()
        }
        
        # Analyze data types
        analysis["column_types"] = df.dtypes.astype(str).to_dict()
        
        # Look for text columns that might contain social media content
        text_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                sample_values = df[col].dropna().head(5).tolist()
                avg_length = df[col].astype(str).str.len().mean()
                if avg_length > 20:  # Likely text content
                    text_columns.append(col)
        
        if text_columns:
            analysis["text_columns"] = text_columns
            # Analyze content from text columns
            all_text = []
            for col in text_columns[:2]:  # Analyze first 2 text columns
                text_values = df[col].dropna().astype(str).tolist()
                all_text.extend(text_values[:50])  # First 50 values
            
            if all_text:
                combined_text = ' '.join(all_text)
                analysis["content_analysis"] = analyze_text_content(combined_text)
        
        return analysis
        
    except Exception as e:
        return {"csv_analysis_error": str(e)}

def analyze_text_content(text: str) -> Dict[str, Any]:
    """Analyze actual text content for real insights"""
    
    try:
        words = text.lower().split()
        
        # Real keyword analysis
        analysis = {
            "total_words": len(words),
            "unique_words": len(set(words)),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0
        }
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', text)
        analysis["hashtags"] = list(set(hashtags))
        analysis["hashtag_count"] = len(hashtags)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', text)
        analysis["mentions"] = list(set(mentions))
        analysis["mention_count"] = len(mentions)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        analysis["urls"] = list(set(urls))
        analysis["url_count"] = len(urls)
        
        # Word frequency analysis (top 10 words)
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["top_words"] = dict(top_words)
        
        return analysis
        
    except Exception as e:
        return {"text_analysis_error": str(e)}

async def generate_real_ai_insights(text: str, source: str, brand: str) -> Dict[str, Any]:
    """Generate real AI insights using OpenAI (no mock data)"""
    
    if not AI_AVAILABLE or not openai_client:
        return {"note": "AI analysis not available"}
    
    try:
        # Limit text to avoid token limits
        text_sample = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""
        Analyze this real {source} data for {brand} and provide actionable insights:
        
        Data sample:
        {text_sample}
        
        Provide analysis in JSON format with:
        1. key_themes: Main topics and themes found
        2. sentiment: Overall sentiment analysis
        3. engagement_opportunities: Specific opportunities for {brand}
        4. content_recommendations: Actionable content suggestions
        5. competitive_insights: What this reveals about the market
        
        Be specific and actionable based on the actual data provided.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a data analyst specializing in social media intelligence for {brand}."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            insights = json.loads(ai_response)
        except:
            insights = {"analysis": ai_response}
        
        return {
            "ai_insights": insights,
            "model": "gpt-3.5-turbo",
            "generated_at": datetime.now().isoformat(),
            "text_analyzed_length": len(text_sample)
        }
        
    except Exception as e:
        return {"ai_error": f"AI analysis failed: {str(e)}"}

async def analyze_file_content(content: bytes, filename: str) -> Dict[str, Any]:
    """Quick analysis of file content for file listing"""
    
    try:
        text = extract_text_content(content, filename)
        if not text:
            return {"error": "Could not extract text"}
        
        # Basic analysis
        return {
            "size": len(content),
            "text_length": len(text),
            "lines": len(text.split('\n')),
            "words": len(text.split()),
            "file_type": os.path.splitext(filename)[1].lower()
        }
        
    except Exception as e:
        return {"error": str(e)}

def save_to_database(file_metadata: Dict[str, Any]):
    """Save file metadata to database"""
    
    if not DB_AVAILABLE:
        return
    
    try:
        with SessionLocal() as session:
            # Insert into intelligence_files table
            query = text("""
                INSERT INTO intelligence_files 
                (filename, source, brand, file_path, processed, insights)
                VALUES (:filename, :source, :brand, :file_path, :processed, :insights)
            """)
            
            session.execute(query, {
                "filename": file_metadata["filename"],
                "source": file_metadata["source"],
                "brand": file_metadata["brand"],
                "file_path": file_metadata["file_path"],
                "processed": file_metadata["processed"],
                "insights": json.dumps(file_metadata["insights"])
            })
            session.commit()
            
    except Exception as e:
        print(f"[intelligence] Database save error: {e}")

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
        "upload_directory_exists": os.path.exists(UPLOAD_DIR)
    }
