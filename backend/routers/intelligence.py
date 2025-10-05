# backend/routers/intelligence_minimal_fix.py
"""
Minimal Intelligence Router Fix
SAFE VERSION - Just fixes database issues without complex enhancements
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
import os
import json
import aiofiles
from datetime import datetime
import hashlib
from typing import Optional

# Initialize router
router = APIRouter()

# Database setup (SAFE - same as existing)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# OpenAI setup (SAFE - same as existing)
try:
    from openai import OpenAI
    client = OpenAI()  # Uses OPENAI_API_KEY from environment
    AI_AVAILABLE = True
    print("[Intelligence] OpenAI client initialized successfully")
except Exception as e:
    print(f"[Intelligence] OpenAI initialization failed: {e}")
    AI_AVAILABLE = False

# Database connection (SAFE - same as existing)
try:
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL, future=True)
        print("[Intelligence] Database connection established")
        DB_AVAILABLE = True
    else:
        print("[Intelligence] No DATABASE_URL found")
        DB_AVAILABLE = False
except Exception as e:
    print(f"[Intelligence] Database connection failed: {e}")
    DB_AVAILABLE = False

# SAFE: Preserve existing upload directory logic
UPLOAD_DIR = "/tmp/intelligence_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_basic_insights(filename: str, file_size: int) -> dict:
    """Generate basic insights without complex processing"""
    
    filename_lower = filename.lower()
    
    # Basic insights based on filename
    if 'instagram' in filename_lower:
        return {
            "data_type": "Instagram Data",
            "insights": [
                f"Instagram competitive intelligence file uploaded: {filename}",
                "Data ready for hashtag and engagement analysis",
                "File contains social media competitive research",
                "Ready for cross-platform trend analysis"
            ],
            "recommendations": [
                "🎯 Analyze hashtag performance for content strategy",
                "📸 Review engagement patterns for optimal posting",
                "🔄 Compare with your brand's social media metrics",
                "📊 Use insights to inform content calendar"
            ]
        }
    elif 'tiktok' in filename_lower:
        return {
            "data_type": "TikTok Data", 
            "insights": [
                f"TikTok competitive intelligence file uploaded: {filename}",
                "Video performance data ready for analysis",
                "Contains engagement metrics and trend data",
                "Ready for short-form content strategy insights"
            ],
            "recommendations": [
                "🎬 Analyze video performance patterns",
                "🎵 Review trending audio and hashtags",
                "⚡ Optimize video length and format",
                "🏙️ Leverage location-based trends"
            ]
        }
    elif filename_lower.endswith('.csv'):
        return {
            "data_type": "Sales/Analytics Data",
            "insights": [
                f"Sales analytics file uploaded: {filename}",
                "Revenue and performance data ready for analysis", 
                "Contains business metrics for trend analysis",
                "Ready for sales performance insights"
            ],
            "recommendations": [
                "💰 Identify peak sales periods",
                "📦 Analyze top-performing products",
                "📈 Correlate with marketing campaigns",
                "🔄 Connect social media trends to sales"
            ]
        }
    else:
        return {
            "data_type": "Competitive Intelligence",
            "insights": [
                f"Competitive intelligence file uploaded: {filename}",
                f"File size: {file_size:,} bytes",
                "Data ready for competitive analysis",
                "Available for cross-platform insights"
            ],
            "recommendations": [
                "📊 Review competitive landscape data",
                "🎯 Identify market opportunities", 
                "🔄 Compare with your brand performance",
                "📈 Use insights for strategic planning"
            ]
        }

@router.get("/health")
async def health_check():
    """Health check endpoint - UNCHANGED"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "database_available": DB_AVAILABLE,
        "upload_directory": os.path.exists(UPLOAD_DIR)
    }

@router.post("/upload")
async def upload_intelligence_file(
    file: UploadFile = File(...),
    source: str = Form("manual_upload"),
    brand: str = Form("Crooks & Castles"),
    description: Optional[str] = Form(None)
):
    """MINIMAL FIX: Upload endpoint that focuses on database reliability"""
    
    try:
        # SAFE: Basic validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # SAFE: Read file content (with size limit to prevent crashes)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # SAFE: Generate file path
        file_hash = hashlib.md5(content).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_hash}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # SAFE: Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # MINIMAL: Generate basic insights (no complex processing)
        ai_analysis = generate_basic_insights(file.filename, len(content))
        
        # SAFE: Database operation with proper error handling
        database_saved = False
        database_error = None
        
        try:
            if DB_AVAILABLE and engine:
                with engine.connect() as db:
                    with db.begin():
                        result = db.execute(text("""
                            INSERT INTO intelligence_files 
                            (original_filename, file_path, source, brand, description, analysis_results, uploaded_at)
                            VALUES (:filename, :path, :source, :brand, :description, :analysis, NOW())
                            RETURNING id
                        """), {
                            "filename": file.filename,
                            "path": file_path,
                            "source": source,
                            "brand": brand,
                            "description": description or f"Competitive intelligence: {file.filename}",
                            "analysis": json.dumps(ai_analysis)
                        })
                        inserted_id = result.fetchone()[0]
                        database_saved = True
                        print(f"[Intelligence] File saved to database with ID: {inserted_id}")
        except Exception as db_error:
            database_error = str(db_error)
            print(f"[Intelligence] Database save failed: {db_error}")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_size": len(content),
            "file_path": file_path,
            "database_saved": database_saved,
            "database_error": database_error,
            "ai_analysis": ai_analysis,
            "upload_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[Intelligence] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/files")
async def list_intelligence_files():
    """List uploaded intelligence files - FIXED for database column issues"""
    
    try:
        if not DB_AVAILABLE or not engine:
            return {
                "files": [],
                "total_files": 0,
                "data_source": "no_database",
                "database_error": "Database not available"
            }
        
        with engine.connect() as db:
            # SAFE: Query only columns that should exist
            result = db.execute(text("""
                SELECT original_filename, source, brand, uploaded_at, description, id, analysis_results
                FROM intelligence_files 
                ORDER BY uploaded_at DESC
            """))
            
            files = []
            for row in result.fetchall():
                file_data = {
                    "id": row[5],
                    "filename": row[0],
                    "source": row[1],
                    "brand": row[2],
                    "uploaded_at": row[3].isoformat() if row[3] else None,
                    "description": row[4]
                }
                
                # Include AI analysis if available
                if row[6]:  # analysis_results
                    try:
                        analysis = json.loads(row[6])
                        file_data["ai_insights"] = analysis.get("insights", [])
                        file_data["recommendations"] = analysis.get("recommendations", [])
                        file_data["data_type"] = analysis.get("data_type", "Unknown")
                    except:
                        pass
                
                files.append(file_data)
            
            return {
                "files": files,
                "total_files": len(files),
                "data_source": "database"
            }
            
    except Exception as e:
        return {
            "files": [],
            "total_files": 0,
            "data_source": "error",
            "database_error": str(e)
        }

@router.get("/summary")
async def get_intelligence_summary():
    """Get intelligence summary - SAFE version"""
    
    try:
        if not DB_AVAILABLE or not engine:
            return {
                "status": "ready",
                "ai_available": AI_AVAILABLE,
                "database_available": False,
                "insights": ["Upload competitive intelligence files to see AI insights"],
                "recommendations": ["Connect database to enable file tracking and analysis"],
                "total_files_analyzed": 0
            }
        
        with engine.connect() as db:
            result = db.execute(text("""
                SELECT analysis_results, original_filename
                FROM intelligence_files 
                WHERE analysis_results IS NOT NULL
                ORDER BY uploaded_at DESC
            """))
            
            all_insights = []
            all_recommendations = []
            data_sources = []
            
            for row in result.fetchall():
                try:
                    analysis = json.loads(row[0])
                    all_insights.extend(analysis.get("insights", []))
                    all_recommendations.extend(analysis.get("recommendations", []))
                    data_sources.append(analysis.get("data_type", "Unknown"))
                except:
                    continue
            
            if not all_insights:
                all_insights = ["Upload competitive intelligence files to see AI insights"]
                all_recommendations = ["Upload Instagram, TikTok, or sales data for personalized recommendations"]
            
            return {
                "status": "ready",
                "ai_available": AI_AVAILABLE,
                "database_available": True,
                "insights": all_insights,
                "recommendations": all_recommendations,
                "data_sources": list(set(data_sources)),
                "total_files_analyzed": len(data_sources)
            }
            
    except Exception as e:
        return {
            "status": "error",
            "ai_available": AI_AVAILABLE,
            "database_available": False,
            "insights": [f"Database error: {str(e)}"],
            "recommendations": ["Check database connection and table structure"],
            "total_files_analyzed": 0
        }

@router.get("/analysis")
async def get_analysis():
    """Get analysis results - preserves existing functionality"""
    return await get_intelligence_summary()
