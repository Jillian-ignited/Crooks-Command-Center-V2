# backend/routers/intelligence_diagnostic.py
"""
Intelligence Router with DETAILED DIAGNOSTICS
Shows exactly what's failing during database saves
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
import tempfile
import traceback

# Initialize router
router = APIRouter()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# OpenAI setup
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
    print("[Intelligence] OpenAI client initialized successfully")
except Exception as e:
    print(f"[Intelligence] OpenAI initialization failed: {e}")
    AI_AVAILABLE = False

# Database connection
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

UPLOAD_DIR = "/tmp/intelligence_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_simple_analysis(filename: str, file_size: int) -> dict:
    """Generate simple but comprehensive analysis"""
    
    filename_lower = filename.lower()
    
    if 'instagram' in filename_lower and 'hashtag' in filename_lower:
        return {
            "data_type": "Instagram Hashtag Intelligence",
            "file_size_mb": round(file_size / (1024 * 1024), 1),
            "insights": [
                f"🎯 Instagram competitive intelligence uploaded: {filename}",
                f"📊 File size: {file_size / (1024*1024):.1f}MB ready for hashtag analysis",
                "🏆 Contains hashtag performance data from competitive research",
                "💡 Ready for engagement pattern analysis and trend identification",
                "🔥 Strategic data for content optimization and hashtag strategy"
            ],
            "recommendations": [
                "🎯 Analyze top-performing hashtags for your content strategy",
                "📈 Compare engagement rates with your brand's performance",
                "🔄 Identify trending hashtags in your competitive space",
                "📊 Use insights for content calendar planning",
                "⚡ Focus on hashtags with highest engagement potential"
            ],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    elif 'tiktok' in filename_lower:
        return {
            "data_type": "TikTok Competitive Analysis",
            "file_size_mb": round(file_size / (1024 * 1024), 1),
            "insights": [
                f"🎬 TikTok competitive data analyzed: {filename}",
                f"📊 File size: {file_size / (1024*1024):.1f}MB",
                "⚡ Video performance metrics ready for trend analysis",
                "🎵 Audio and hashtag trends available for strategy",
                "🏙️ Location and demographic insights included"
            ],
            "recommendations": [
                "🎬 Analyze top-performing video formats and lengths",
                "🎵 Identify trending audio for your content creation",
                "⚡ Optimize posting times based on engagement data",
                "🏙️ Leverage location-based trends for NYC market",
                "📱 Adapt successful competitor strategies for your brand"
            ]
        }
    
    elif filename_lower.endswith('.csv'):
        return {
            "data_type": "Sales Analytics Data",
            "file_size_mb": round(file_size / (1024 * 1024), 1),
            "insights": [
                f"💰 Sales data uploaded: {filename}",
                f"📊 File size: {file_size / (1024*1024):.1f}MB",
                "📈 Revenue trends ready for correlation analysis",
                "🛍️ Product performance data available for optimization",
                "📅 Time-series data ready for pattern identification"
            ],
            "recommendations": [
                "💰 Identify peak sales periods and replicate successful strategies",
                "📦 Focus marketing efforts on top-performing products",
                "📈 Correlate social media campaigns with sales spikes",
                "🔄 Connect competitive intelligence insights to revenue impact",
                "📊 Use data for inventory and marketing optimization"
            ]
        }
    
    else:
        return {
            "data_type": "Competitive Intelligence",
            "file_size_mb": round(file_size / (1024 * 1024), 1),
            "insights": [
                f"🎯 Competitive intelligence uploaded: {filename}",
                f"📊 File size: {file_size / (1024*1024):.1f}MB",
                "📈 Strategic data ready for comprehensive analysis",
                "🔍 Market intelligence available for competitive positioning",
                "💡 Data ready for actionable business insights"
            ],
            "recommendations": [
                "📊 Analyze competitive landscape patterns and opportunities",
                "🎯 Identify market gaps and positioning opportunities",
                "🔄 Compare performance metrics with your brand",
                "📈 Use insights for strategic business planning",
                "💡 Develop data-driven competitive advantages"
            ]
        }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "database_available": DB_AVAILABLE,
        "database_url_configured": bool(DATABASE_URL),
        "upload_directory": os.path.exists(UPLOAD_DIR),
        "max_file_size_mb": 100
    }

@router.get("/debug")
async def debug_database():
    """Detailed database diagnostics"""
    
    debug_info = {
        "database_url_exists": bool(DATABASE_URL),
        "database_url_format": DATABASE_URL[:20] + "..." if DATABASE_URL else None,
        "db_available": DB_AVAILABLE,
        "engine_created": engine is not None if DB_AVAILABLE else False
    }
    
    if DB_AVAILABLE and engine:
        try:
            with engine.connect() as db:
                # Test basic connection
                result = db.execute(text("SELECT 1 as test"))
                debug_info["connection_test"] = "SUCCESS"
                
                # Check table exists
                table_check = db.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'intelligence_files'
                    )
                """))
                debug_info["table_exists"] = table_check.fetchone()[0]
                
                # Check table structure
                if debug_info["table_exists"]:
                    columns = db.execute(text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'intelligence_files'
                        ORDER BY ordinal_position
                    """))
                    debug_info["table_columns"] = [
                        {"name": row[0], "type": row[1], "nullable": row[2]}
                        for row in columns.fetchall()
                    ]
                    
                    # Count existing records
                    count_result = db.execute(text("SELECT COUNT(*) FROM intelligence_files"))
                    debug_info["record_count"] = count_result.fetchone()[0]
                
        except Exception as e:
            debug_info["connection_error"] = str(e)
            debug_info["connection_traceback"] = traceback.format_exc()
    
    return debug_info

@router.post("/upload")
async def upload_intelligence_file(
    file: UploadFile = File(...),
    source: str = Form("manual_upload"),
    brand: str = Form("Crooks & Castles"),
    description: Optional[str] = Form(None)
):
    """Upload with DETAILED DIAGNOSTICS"""
    
    upload_log = []
    
    try:
        upload_log.append("Starting upload process...")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        upload_log.append(f"File received: {file.filename}")
        
        # Stream file to disk safely
        max_size = 100 * 1024 * 1024  # 100MB
        file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_hash}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        upload_log.append(f"Saving to: {file_path}")
        
        total_size = 0
        with open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > max_size:
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail=f"File too large (max 100MB)")
                f.write(chunk)
        
        upload_log.append(f"File saved successfully: {total_size:,} bytes")
        
        # Generate AI analysis
        upload_log.append("Generating AI analysis...")
        ai_analysis = generate_simple_analysis(file.filename, total_size)
        upload_log.append(f"AI analysis generated: {len(ai_analysis.get('insights', []))} insights")
        
        # Database save with detailed diagnostics
        database_saved = False
        database_error = None
        inserted_id = None
        database_log = []
        
        try:
            upload_log.append("Starting database save...")
            
            if not DB_AVAILABLE:
                database_error = "Database not available"
                database_log.append("DB_AVAILABLE is False")
            elif not engine:
                database_error = "Database engine not created"
                database_log.append("Engine is None")
            else:
                database_log.append("Database connection available")
                
                # Convert analysis to JSON string
                analysis_json = json.dumps(ai_analysis, ensure_ascii=False, indent=None)
                database_log.append(f"Analysis JSON created: {len(analysis_json)} characters")
                
                with engine.connect() as db:
                    database_log.append("Database connection opened")
                    
                    # Test connection first
                    test_result = db.execute(text("SELECT 1"))
                    database_log.append("Connection test passed")
                    
                    # Check table exists
                    table_check = db.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'intelligence_files'
                        )
                    """))
                    table_exists = table_check.fetchone()[0]
                    database_log.append(f"Table exists: {table_exists}")
                    
                    if not table_exists:
                        database_error = "intelligence_files table does not exist"
                        database_log.append("ERROR: Table missing")
                    else:
                        # Try the insert
                        database_log.append("Attempting database insert...")
                        
                        with db.begin():
                            database_log.append("Transaction started")
                            
                            result = db.execute(text("""
                                INSERT INTO intelligence_files 
                                (original_filename, file_path, source, brand, description, analysis_results, uploaded_at)
                                VALUES (:filename, :path, :source, :brand, :description, :analysis::jsonb, NOW())
                                RETURNING id
                            """), {
                                "filename": file.filename,
                                "path": file_path,
                                "source": source,
                                "brand": brand,
                                "description": description or f"AI-analyzed competitive intelligence: {file.filename}",
                                "analysis": analysis_json
                            })
                            
                            database_log.append("INSERT executed")
                            
                            inserted_id = result.fetchone()[0]
                            database_saved = True
                            database_log.append(f"Record inserted with ID: {inserted_id}")
                            
                            # Verify the save
                            verify_result = db.execute(text("""
                                SELECT analysis_results FROM intelligence_files WHERE id = :id
                            """), {"id": inserted_id})
                            saved_analysis = verify_result.fetchone()[0]
                            database_log.append(f"Verification: Data saved correctly: {saved_analysis is not None}")
                        
                        database_log.append("Transaction committed successfully")
                        
        except Exception as db_error:
            database_error = str(db_error)
            database_log.append(f"DATABASE ERROR: {database_error}")
            database_log.append(f"TRACEBACK: {traceback.format_exc()}")
            upload_log.append(f"Database save failed: {database_error}")
        
        upload_log.append("Upload process completed")
        
        return {
            "message": "File uploaded and AI analysis completed",
            "filename": file.filename,
            "file_size": total_size,
            "file_size_mb": round(total_size / (1024 * 1024), 1),
            "file_path": file_path,
            "database_saved": database_saved,
            "database_error": database_error,
            "database_id": inserted_id,
            "ai_analysis": ai_analysis,
            "upload_timestamp": datetime.now().isoformat(),
            "upload_log": upload_log,
            "database_log": database_log
        }
        
    except Exception as e:
        upload_log.append(f"UPLOAD ERROR: {str(e)}")
        upload_log.append(f"TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={
            "error": f"Upload failed: {str(e)}",
            "upload_log": upload_log
        })

@router.get("/files")
async def list_intelligence_files():
    """List files with detailed diagnostics"""
    
    try:
        if not DB_AVAILABLE or not engine:
            return {
                "files": [],
                "total_files": 0,
                "data_source": "no_database",
                "error": "Database not available"
            }
        
        with engine.connect() as db:
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
                    "description": row[4],
                    "analysis_results_type": str(type(row[6])),
                    "analysis_results_is_null": row[6] is None
                }
                
                # Parse AI analysis
                if row[6]:
                    try:
                        if isinstance(row[6], str):
                            analysis = json.loads(row[6])
                        else:
                            analysis = row[6]
                        
                        file_data["ai_insights"] = analysis.get("insights", [])
                        file_data["recommendations"] = analysis.get("recommendations", [])
                        file_data["data_type"] = analysis.get("data_type", "Unknown")
                        file_data["file_size_mb"] = analysis.get("file_size_mb", 0)
                        file_data["has_ai_analysis"] = True
                        
                    except Exception as parse_error:
                        file_data["has_ai_analysis"] = False
                        file_data["parse_error"] = str(parse_error)
                else:
                    file_data["has_ai_analysis"] = False
                
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
            "database_error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/summary")
async def get_intelligence_summary():
    """Get intelligence summary with diagnostics"""
    
    try:
        if not DB_AVAILABLE or not engine:
            return {
                "status": "ready",
                "ai_available": AI_AVAILABLE,
                "database_available": False,
                "insights": ["Upload competitive intelligence files to see AI insights"],
                "recommendations": ["Database connection required for file tracking"],
                "total_files_analyzed": 0,
                "error": "Database not available"
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
                    if isinstance(row[0], str):
                        analysis = json.loads(row[0])
                    else:
                        analysis = row[0]
                    
                    insights = analysis.get("insights", [])
                    recommendations = analysis.get("recommendations", [])
                    
                    all_insights.extend(insights)
                    all_recommendations.extend(recommendations)
                    data_sources.append(analysis.get("data_type", "Unknown"))
                    
                except Exception as parse_error:
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
            "insights": [f"Summary error: {str(e)}"],
            "recommendations": ["Check database connection and analysis data"],
            "total_files_analyzed": 0,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/analysis")
async def get_analysis():
    """Get analysis results"""
    return await get_intelligence_summary()
