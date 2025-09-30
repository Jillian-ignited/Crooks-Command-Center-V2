# backend/routers/upload_sidecar.py
# Fixed Intelligence router with proper AI client initialization

import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import aiofiles

# Proper OpenAI client initialization without proxies
try:
    from openai import OpenAI
    # Initialize OpenAI client properly - no proxies parameter
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )
    AI_AVAILABLE = True
except ImportError:
    print("[intelligence] OpenAI not available - AI analysis will be disabled")
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

# Mock database for storing file metadata (in production, use real database)
UPLOADED_FILES = []

@router.post("/upload")
async def upload_intelligence_file(
    file: UploadFile = File(...),
    source: str = Form("manual_upload"),
    brand: str = Form("Crooks & Castles"),
    description: Optional[str] = Form(None)
):
    """Upload and process intelligence files with AI analysis"""
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        print(f"[intelligence] Saved file to {file_path}")
        
        # Create file metadata
        file_metadata = {
            "id": file_id,
            "filename": file.filename,
            "source": source,
            "brand": brand,
            "description": description,
            "file_path": file_path,
            "file_size": len(content),
            "uploaded_at": datetime.now().isoformat(),
            "processed": False,
            "insights": {}
        }
        
        # Try to save to database (this is where the original error occurred)
        try:
            # Import database functions here to avoid circular imports
            from ..services.database import save_intelligence_file
            db_result = save_intelligence_file(file_metadata)
            print(f"[intelligence] Saved to database: {db_result}")
        except Exception as db_error:
            print(f"[intelligence] Database save error: {db_error}")
            # Continue without database - store in memory for now
            UPLOADED_FILES.append(file_metadata)
        
        # Process file content and generate insights
        try:
            insights = await process_file_content(content, file.filename, source, brand)
            file_metadata["insights"] = insights
            file_metadata["processed"] = True
            print(f"[intelligence] Generated insights for {file.filename}")
        except Exception as process_error:
            print(f"[intelligence] Processing error: {process_error}")
            file_metadata["insights"] = {"error": f"Processing failed: {str(process_error)}"}
        
        return {
            "success": True,
            "message": f"File '{file.filename}' uploaded and processed successfully",
            "file_id": file_id,
            "metadata": file_metadata,
            "ai_analysis_available": AI_AVAILABLE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[intelligence] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/summary")
async def get_intelligence_summary():
    """Get intelligence summary and insights"""
    
    try:
        # Get files from database or memory
        files = UPLOADED_FILES  # In production, query from database
        
        total_files = len(files)
        processed_files = len([f for f in files if f.get("processed", False)])
        
        # Calculate insights summary
        insights_summary = {
            "total_files": total_files,
            "processed_files": processed_files,
            "pending_files": total_files - processed_files,
            "sources": {},
            "brands": {},
            "recent_uploads": []
        }
        
        # Aggregate by source and brand
        for file_data in files:
            source = file_data.get("source", "unknown")
            brand = file_data.get("brand", "unknown")
            
            insights_summary["sources"][source] = insights_summary["sources"].get(source, 0) + 1
            insights_summary["brands"][brand] = insights_summary["brands"].get(brand, 0) + 1
            
            # Add to recent uploads (last 10)
            if len(insights_summary["recent_uploads"]) < 10:
                insights_summary["recent_uploads"].append({
                    "filename": file_data.get("filename", ""),
                    "source": source,
                    "brand": brand,
                    "uploaded_at": file_data.get("uploaded_at", ""),
                    "processed": file_data.get("processed", False)
                })
        
        # Add AI insights if available
        if AI_AVAILABLE and processed_files > 0:
            insights_summary["ai_insights"] = generate_summary_insights(files)
        
        return insights_summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get intelligence summary: {str(e)}")

@router.get("/files")
async def get_uploaded_files(limit: int = 50):
    """Get list of uploaded intelligence files"""
    
    try:
        files = UPLOADED_FILES[-limit:]  # Get most recent files
        
        return {
            "files": files,
            "total_files": len(UPLOADED_FILES),
            "ai_analysis_available": AI_AVAILABLE
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")

@router.get("/insights/{file_id}")
async def get_file_insights(file_id: str):
    """Get detailed insights for a specific file"""
    
    try:
        # Find file by ID
        file_data = None
        for f in UPLOADED_FILES:
            if f.get("id") == file_id:
                file_data = f
                break
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": file_id,
            "filename": file_data.get("filename", ""),
            "metadata": file_data,
            "insights": file_data.get("insights", {}),
            "processed": file_data.get("processed", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file insights: {str(e)}")

async def process_file_content(content: bytes, filename: str, source: str, brand: str) -> Dict[str, Any]:
    """Process file content and generate insights using AI"""
    
    try:
        # Determine file type and extract text
        file_text = extract_text_from_file(content, filename)
        
        if not file_text:
            return {"error": "Could not extract text from file"}
        
        # Generate AI insights if available
        if AI_AVAILABLE and openai_client:
            ai_insights = await generate_ai_insights(file_text, source, brand)
        else:
            ai_insights = {"note": "AI analysis not available"}
        
        # Generate basic insights
        basic_insights = generate_basic_insights(file_text, source, brand)
        
        return {
            "basic_analysis": basic_insights,
            "ai_analysis": ai_insights,
            "file_stats": {
                "character_count": len(file_text),
                "word_count": len(file_text.split()),
                "line_count": len(file_text.split('\n'))
            },
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text content from various file types"""
    
    try:
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension in ['.txt', '.csv', '.json', '.jsonl']:
            # Text-based files
            return content.decode('utf-8', errors='ignore')
        elif file_extension == '.json':
            # JSON files - pretty print
            data = json.loads(content.decode('utf-8'))
            return json.dumps(data, indent=2)
        else:
            # Try to decode as text
            return content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"[intelligence] Text extraction error: {e}")
        return ""

async def generate_ai_insights(text: str, source: str, brand: str) -> Dict[str, Any]:
    """Generate AI-powered insights using OpenAI (fixed client initialization)"""
    
    if not AI_AVAILABLE or not openai_client:
        return {"error": "AI analysis not available"}
    
    try:
        # Create AI prompt for analysis
        prompt = f"""
        Analyze this {source} data for {brand} and provide insights:
        
        Data:
        {text[:2000]}...  # Limit text to avoid token limits
        
        Please provide:
        1. Key themes and topics
        2. Sentiment analysis
        3. Actionable insights for {brand}
        4. Recommendations for content strategy
        
        Format as JSON with clear sections.
        """
        
        # Make API call with proper client (no proxies parameter)
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an expert social media analyst for {brand}, a streetwear brand."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to text
        try:
            insights = json.loads(ai_response)
        except:
            insights = {"analysis": ai_response}
        
        return {
            "insights": insights,
            "model_used": "gpt-3.5-turbo",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[intelligence] AI analysis error: {e}")
        return {"error": f"AI analysis failed: {str(e)}"}

def generate_basic_insights(text: str, source: str, brand: str) -> Dict[str, Any]:
    """Generate basic insights without AI"""
    
    try:
        words = text.lower().split()
        
        # Basic keyword analysis
        brand_mentions = words.count(brand.lower().replace(" ", "").replace("&", ""))
        
        # Common social media keywords
        engagement_keywords = ["like", "comment", "share", "follow", "tag"]
        engagement_count = sum(words.count(keyword) for keyword in engagement_keywords)
        
        # Sentiment indicators (basic)
        positive_words = ["good", "great", "awesome", "love", "amazing", "best"]
        negative_words = ["bad", "hate", "terrible", "worst", "awful"]
        
        positive_count = sum(words.count(word) for word in positive_words)
        negative_count = sum(words.count(word) for word in negative_words)
        
        return {
            "source": source,
            "brand": brand,
            "brand_mentions": brand_mentions,
            "engagement_indicators": engagement_count,
            "sentiment_indicators": {
                "positive_words": positive_count,
                "negative_words": negative_count,
                "sentiment_score": (positive_count - negative_count) / max(len(words), 1)
            },
            "data_quality": {
                "has_content": len(text) > 100,
                "structured_data": source in ["instagram", "tiktok", "shopify"],
                "text_length": len(text)
            }
        }
        
    except Exception as e:
        return {"error": f"Basic analysis failed: {str(e)}"}

def generate_summary_insights(files: List[Dict]) -> Dict[str, Any]:
    """Generate summary insights across all files"""
    
    try:
        processed_files = [f for f in files if f.get("processed", False)]
        
        if not processed_files:
            return {"note": "No processed files available for analysis"}
        
        # Aggregate insights
        total_brand_mentions = 0
        total_engagement = 0
        sources_analyzed = set()
        
        for file_data in processed_files:
            insights = file_data.get("insights", {})
            basic = insights.get("basic_analysis", {})
            
            total_brand_mentions += basic.get("brand_mentions", 0)
            total_engagement += basic.get("engagement_indicators", 0)
            sources_analyzed.add(file_data.get("source", "unknown"))
        
        return {
            "summary": {
                "total_files_analyzed": len(processed_files),
                "sources_covered": list(sources_analyzed),
                "total_brand_mentions": total_brand_mentions,
                "total_engagement_indicators": total_engagement,
                "avg_brand_mentions_per_file": total_brand_mentions / len(processed_files) if processed_files else 0
            },
            "recommendations": [
                "Continue monitoring social media mentions for brand sentiment",
                "Focus on high-engagement content types identified in analysis",
                "Track competitor activity in similar data sources",
                "Develop content strategy based on trending topics"
            ]
        }
        
    except Exception as e:
        return {"error": f"Summary generation failed: {str(e)}"}

# Health check endpoint
@router.get("/health")
async def intelligence_health():
    """Health check for intelligence module"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "upload_directory": UPLOAD_DIR,
        "total_files": len(UPLOADED_FILES)
    }
