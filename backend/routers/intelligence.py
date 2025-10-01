# backend/routers/intelligence.py
# Intelligence router with real data processing - NO MOCK DATA

import os
import uuid
import json
import asyncio
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
        async with aiofiles.open(file_path, 'wb') as f:
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
            "message": f"File '{file.filename}' uploaded and analyzed successfully",
            "file_id": file_id,
            "insights": insights,
            "ai_analysis_available": AI_AVAILABLE,
            "file_size": len(content),
            "processing_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[intelligence] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/summary")
async def get_intelligence_summary():
    """Get comprehensive intelligence summary from real data"""
    
    try:
        print("[intelligence] Generating summary from real data")
        
        # Get actual uploaded files
        uploaded_files = []
        total_size = 0
        
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    file_info = {
                        "filename": filename,
                        "size": file_stats.st_size,
                        "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "file_path": file_path
                    }
                    uploaded_files.append(file_info)
                    total_size += file_stats.st_size
        
        # Analyze file types and sources
        file_types = {}
        sources = {}
        brands = {}
        
        for file_info in uploaded_files:
            # File type analysis
            ext = os.path.splitext(file_info["filename"])[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            
            # Try to extract metadata from filename or content
            try:
                # Quick content analysis for source detection
                with open(file_info["file_path"], 'rb') as f:
                    sample = f.read(1000).decode('utf-8', errors='ignore').lower()
                
                # Detect source from content
                if 'instagram' in sample or 'ig_' in sample:
                    sources['instagram'] = sources.get('instagram', 0) + 1
                elif 'tiktok' in sample or 'tt_' in sample:
                    sources['tiktok'] = sources.get('tiktok', 0) + 1
                elif 'shopify' in sample or 'orders' in sample:
                    sources['shopify'] = sources.get('shopify', 0) + 1
                else:
                    sources['manual_upload'] = sources.get('manual_upload', 0) + 1
                
                # Brand detection
                if 'crooks' in sample or 'castles' in sample:
                    brands['Crooks & Castles'] = brands.get('Crooks & Castles', 0) + 1
                else:
                    brands['Other'] = brands.get('Other', 0) + 1
                    
            except Exception as e:
                print(f"[intelligence] Content analysis error for {file_info['filename']}: {e}")
                sources['unknown'] = sources.get('unknown', 0) + 1
                brands['Unknown'] = brands.get('Unknown', 0) + 1
        
        # Get database summary
        db_summary = {}
        if DB_AVAILABLE:
            try:
                db_summary = get_database_summary()
            except Exception as e:
                print(f"[intelligence] Database summary error: {e}")
        
        # Generate insights summary
        insights_summary = generate_insights_summary(uploaded_files)
        
        summary = {
            "overview": {
                "total_files": len(uploaded_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_types": file_types,
                "data_sources": sources,
                "brands_analyzed": brands,
                "last_upload": uploaded_files[-1]["uploaded_at"] if uploaded_files else None
            },
            "database": {
                "records_stored": db_summary.get("total_records", 0),
                "database_available": DB_AVAILABLE
            },
            "ai_analysis": {
                "available": AI_AVAILABLE,
                "processed_files": len([f for f in uploaded_files if f.get("processed", False)])
            },
            "insights": insights_summary,
            "recent_uploads": uploaded_files[-5:] if uploaded_files else [],
            "storage_location": UPLOAD_DIR,
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        print(f"[intelligence] Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/files")
async def get_uploaded_files(limit: int = 50):
    """Get list of uploaded files with analysis"""
    
    try:
        files = []
        
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    
                    # Quick file analysis
                    try:
                        with open(file_path, 'rb') as f:
                            content_sample = f.read(2000)
                        file_analysis = analyze_file_quick(content_sample, filename)
                    except Exception as e:
                        file_analysis = {"error": f"Analysis failed: {str(e)}"}
                    
                    files.append({
                        "filename": filename,
                        "size": file_stats.st_size,
                        "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "analysis": file_analysis,
                        "file_path": file_path
                    })
        
        # Sort by upload time (newest first) and limit
        files.sort(key=lambda x: x["uploaded_at"], reverse=True)
        files = files[:limit]
        
        return {
            "files": files,
            "total_files": len(files),
            "ai_analysis_available": AI_AVAILABLE
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")

@router.get("/insights/{file_id}")
async def get_file_insights(file_id: str):
    """Get detailed insights for a specific file"""
    
    try:
        # Find file by ID (filename contains the ID)
        file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if file_id in filename:
                file_path = os.path.join(UPLOAD_DIR, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read and analyze file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        insights = await process_file_content(content, os.path.basename(file_path), "manual", "Crooks & Castles")
        
        return {
            "file_id": file_id,
            "filename": os.path.basename(file_path),
            "insights": insights,
            "file_size": len(content),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

async def process_file_content(content: bytes, filename: str, source: str, brand: str) -> Dict[str, Any]:
    """Process file content and extract real insights"""
    
    try:
        print(f"[intelligence] Processing {filename} ({len(content)} bytes)")
        
        # Extract text content
        text_content = extract_text_from_file(content, filename)
        
        if not text_content:
            return {
                "error": "Could not extract text content",
                "file_size": len(content),
                "filename": filename
            }
        
        # Analyze content structure
        content_analysis = analyze_content_structure(text_content, filename)
        
        # Generate AI insights if available
        ai_insights = {}
        if AI_AVAILABLE and openai_client and len(text_content) > 100:
            try:
                print(f"[intelligence] Generating AI insights for {filename}")
                ai_insights = await generate_ai_insights(text_content, source, brand)
            except Exception as e:
                print(f"[intelligence] AI analysis error: {e}")
                ai_insights = {"ai_error": str(e)}
        
        return {
            "filename": filename,
            "source": source,
            "brand": brand,
            "content_analysis": content_analysis,
            "ai_insights": ai_insights,
            "processing_timestamp": datetime.now().isoformat(),
            "text_length": len(text_content),
            "file_size": len(content)
        }
        
    except Exception as e:
        print(f"[intelligence] Processing error for {filename}: {e}")
        return {"error": f"Processing failed: {str(e)}"}

def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text content from various file formats"""
    
    try:
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension in ['.txt', '.csv', '.tsv']:
            return content.decode('utf-8', errors='ignore')
        
        elif file_extension in ['.json', '.jsonl']:
            text_content = content.decode('utf-8', errors='ignore')
            
            # For JSONL files, process each line
            if file_extension == '.jsonl':
                lines = text_content.strip().split('\n')
                processed_data = []
                
                for line in lines[:100]:  # Process first 100 lines
                    try:
                        data = json.loads(line)
                        processed_data.append(data)
                    except:
                        continue
                
                return json.dumps(processed_data, indent=2)
            
            return text_content
        
        else:
            # Try to decode as text
            return content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"[intelligence] Text extraction error: {e}")
        return ""

def analyze_content_structure(text: str, filename: str) -> Dict[str, Any]:
    """Analyze content structure and extract insights"""
    
    try:
        analysis = {
            "filename": filename,
            "character_count": len(text),
            "line_count": len(text.split('\n')),
            "word_count": len(text.split()),
            "file_type": os.path.splitext(filename)[1].lower()
        }
        
        # Detect content type and analyze accordingly
        if filename.endswith(('.json', '.jsonl')):
            analysis.update(analyze_json_structure(text))
        elif filename.endswith('.csv'):
            analysis.update(analyze_csv_structure(text))
        else:
            analysis.update(analyze_text_structure(text))
        
        return analysis
        
    except Exception as e:
        return {"analysis_error": str(e)}

def analyze_json_structure(text: str) -> Dict[str, Any]:
    """Analyze JSON/JSONL structure"""
    
    try:
        analysis = {"content_type": "json"}
        
        # Parse JSON data
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
            
            # Analyze structure
            if records and isinstance(records[0], dict):
                sample_record = records[0]
                analysis["fields"] = list(sample_record.keys())
                
                # Extract text content for analysis
                text_fields = []
                for field in analysis["fields"]:
                    if any(keyword in field.lower() for keyword in ['text', 'caption', 'content', 'message', 'description']):
                        text_fields.append(field)
                
                if text_fields:
                    analysis["text_fields"] = text_fields
                    
                    # Analyze text content
                    text_to_analyze = " ".join(str(sample_record.get(f, '')) for f in text_fields)
                    analysis.update(analyze_text_content(text_to_analyze))
        
        return analysis
        
    except Exception as e:
        return {"json_error": str(e)}

def analyze_csv_structure(text: str) -> Dict[str, Any]:
    """Analyze CSV structure"""
    
    try:
        from io import StringIO
        df = pd.read_csv(StringIO(text))
        
        analysis = {
            "content_type": "csv",
            "rows": len(df),
            "columns": list(df.columns)
        }
        
        # Analyze text content from all columns
        text_to_analyze = " ".join(df.to_string(index=False).split())
        analysis.update(analyze_text_content(text_to_analyze))
        
        return analysis
        
    except Exception as e:
        return {"csv_error": str(e)}

def analyze_text_structure(text: str) -> Dict[str, Any]:
    """Analyze plain text structure"""
    
    try:
        analysis = {"content_type": "text"}
        analysis.update(analyze_text_content(text))
        return analysis
    except Exception as e:
        return {"text_error": str(e)}

def analyze_text_content(text: str) -> Dict[str, Any]:
    """Analyze text content for insights"""
    
    try:
        words = text.lower().split()
        
        analysis = {
            "total_words": len(words),
            "unique_words": len(set(words)),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0
        }
        
        # Extract social media elements
        import re
        
        # Hashtags
        hashtags = re.findall(r'#\w+', text)
        analysis["hashtags"] = list(set(hashtags))
        analysis["hashtag_count"] = len(hashtags)
        
        # Mentions
        mentions = re.findall(r'@\w+', text)
        analysis["mentions"] = list(set(mentions))
        analysis["mention_count"] = len(mentions)
        
        # URLs
        urls = re.findall(r'http[s]?://\S+', text)
        analysis["urls"] = list(set(urls))
        analysis["url_count"] = len(urls)
        
        # Word frequency (top 10)
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["top_words"] = dict(top_words)
        
        # Brand mentions
        brand_keywords = ['crooks', 'castles', 'streetwear', 'fashion']
        brand_mentions = sum(words.count(keyword) for keyword in brand_keywords)
        analysis["brand_mentions"] = brand_mentions
        
        return analysis
        
    except Exception as e:
        return {"text_analysis_error": str(e)}

async def generate_ai_insights(text: str, source: str, brand: str) -> Dict[str, Any]:
    """Generate AI insights using OpenAI (fixed client)"""
    
    if not AI_AVAILABLE or not openai_client:
        return {"note": "AI analysis not available"}
    
    try:
        # Limit text to avoid token limits
        text_sample = text[:2500] if len(text) > 2500 else text
        
        prompt = f"""
        Analyze this {source} data for {brand} and provide actionable business insights:
        
        Data:
        {text_sample}
        
        Provide analysis in JSON format with these sections:
        1. key_themes: Main topics and themes identified
        2. sentiment: Overall sentiment analysis
        3. opportunities: Specific business opportunities for {brand}
        4. recommendations: Actionable recommendations
        5. competitive_insights: Market intelligence insights
        
        Focus on actionable insights that can drive business decisions.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a business intelligence analyst specializing in social media and e-commerce data for {brand}."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse JSON response
        try:
            insights = json.loads(ai_response)
        except:
            insights = {"analysis": ai_response}
        
        return {
            "ai_insights": insights,
            "model": "gpt-3.5-turbo",
            "generated_at": datetime.now().isoformat(),
            "text_analyzed_chars": len(text_sample)
        }
        
    except Exception as e:
        print(f"[intelligence] AI generation error: {e}")
        return {"ai_error": f"AI analysis failed: {str(e)}"}

def analyze_file_quick(content: bytes, filename: str) -> Dict[str, Any]:
    """Quick file analysis for file listing"""
    
    try:
        text = extract_text_from_file(content, filename)
        
        if not text:
            return {"error": "Could not extract text"}
        
        return {
            "file_size": len(content),
            "text_length": len(text),
            "lines": len(text.split('\n')),
            "words": len(text.split()),
            "file_type": os.path.splitext(filename)[1].lower(),
            "has_content": len(text) > 50
        }
        
    except Exception as e:
        return {"error": str(e)}

def generate_insights_summary(files: List[Dict]) -> Dict[str, Any]:
    """Generate summary insights across all files"""
    
    try:
        if not files:
            return {"note": "No files available for analysis"}
        
        total_size = sum(f.get("size", 0) for f in files)
        
        # File type distribution
        file_types = {}
        for f in files:
            ext = os.path.splitext(f["filename"])[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_type_distribution": file_types,
            "upload_trend": "Recent uploads available" if files else "No uploads",
            "analysis_coverage": f"{len(files)} files ready for analysis"
        }
        
    except Exception as e:
        return {"summary_error": str(e)}

def save_to_database(file_metadata: Dict[str, Any]):
    """Save file metadata to database"""
    
    if not DB_AVAILABLE:
        return
    
    try:
        with SessionLocal() as session:
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
        raise

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

