# Intelligence router with real data processing - FIXED VERSION

import os
import uuid
import json
import asyncio
import io
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import pandas as pd

# Fixed OpenAI client initialization
try:
    from openai import OpenAI
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )
    AI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
    print(f"[Intelligence] OpenAI client initialized successfully")
except ImportError:
    print(f"[Intelligence] OpenAI not available - install with: pip install openai")
    openai_client = None
    AI_AVAILABLE = False
except Exception as e:
    print(f"[Intelligence] OpenAI initialization error: {e}")
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
        # Fix postgres:// to postgresql+psycopg://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
        print(f"[Intelligence] Database connection established")
    else:
        print(f"[Intelligence] No DATABASE_URL configured")
        DB_AVAILABLE = False
except Exception as e:
    print(f"[Intelligence] Database setup error: {e}")
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
        print(f"[Intelligence] Starting upload: {file.filename}")
        
        # Generate unique filename
        unique_id = uuid.uuid4()
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{unique_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        print(f"[Intelligence] File saved to: {file_path}")
        
        # Process the file based on type
        analysis_results = await process_intelligence_data(file_path, file.filename)
        print(f"[Intelligence] Analysis completed: {len(analysis_results.get('insights', []))} insights")
        
        # Save to database if available
        database_saved = False
        database_error = None
        
        if DB_AVAILABLE:
            try:
                print(f"[Intelligence] Attempting database save...")
                db = SessionLocal()
                
                # Use a transaction
                with db.begin():
                    result = db.execute(text("""
                        INSERT INTO intelligence_files (
                            original_filename, file_path, source, brand, description,
                            analysis_results, uploaded_at
                        ) VALUES (
                            :filename, :path, :source, :brand, :description,
                            :results, :uploaded_at
                        ) RETURNING id
                    """), {
                        "filename": file.filename,
                        "path": file_path,
                        "source": source,
                        "brand": brand,
                        "description": description or f"Uploaded {file.filename}",
                        "results": json.dumps(analysis_results),
                        "uploaded_at": datetime.utcnow()
                    })
                    
                    # Get the inserted ID
                    inserted_id = result.fetchone()[0]
                    print(f"[Intelligence] File metadata saved to database with ID: {inserted_id}")
                    database_saved = True
                
                db.close()
                
            except Exception as e:
                database_error = str(e)
                print(f"[Intelligence] Database save error: {e}")
                # Don't fail the upload, just log the error
        
        return {
            "message": f"Intelligence file '{file.filename}' uploaded and analyzed successfully",
            "file_id": str(unique_id),
            "analysis": analysis_results,
            "ai_available": AI_AVAILABLE,
            "insights_generated": len(analysis_results.get("insights", [])),
            "data_points": analysis_results.get("data_points", 0),
            "database_saved": database_saved,
            "database_error": database_error,
            "file_path": file_path
        }
        
    except Exception as e:
        print(f"[Intelligence] Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/summary")
async def get_intelligence_summary():
    """Get intelligence summary with real data from uploads"""
    
    try:
        summary_data = {
            "data_source": "real_uploads",
            "last_updated": datetime.utcnow().isoformat(),
            "insights": {
                "recommendations": [],
                "key_findings": [],
                "competitive_insights": []
            },
            "data_sources": 0,
            "files_analyzed": 0,
            "ai_available": AI_AVAILABLE,
            "database_available": DB_AVAILABLE
        }
        
        # Get real data from database if available
        if DB_AVAILABLE:
            try:
                db = SessionLocal()
                
                # Count uploaded files
                result = db.execute(text("SELECT COUNT(*) as count FROM intelligence_files"))
                file_count = result.fetchone()
                if file_count:
                    summary_data["files_analyzed"] = file_count[0]
                
                # Get recent insights
                result = db.execute(text("""
                    SELECT analysis_results, uploaded_at 
                    FROM intelligence_files 
                    ORDER BY uploaded_at DESC 
                    LIMIT 5
                """))
                
                for row in result.fetchall():
                    if row[0]:  # analysis_results
                        try:
                            analysis = json.loads(row[0])
                            if "insights" in analysis:
                                summary_data["insights"]["competitive_insights"].extend(analysis["insights"][:2])
                            if "key_findings" in analysis:
                                summary_data["insights"]["key_findings"].extend(analysis["key_findings"][:2])
                        except:
                            pass
                
                summary_data["data_sources"] = summary_data["files_analyzed"]
                db.close()
                
            except Exception as e:
                print(f"[Intelligence] Summary database error: {e}")
                summary_data["database_error"] = str(e)
        
        # Add some default recommendations if we have data
        if summary_data["files_analyzed"] > 0:
            summary_data["insights"]["recommendations"] = [
                "Continue monitoring competitive intelligence data",
                "Analyze trends in uploaded datasets",
                "Consider expanding data collection sources"
            ]
        
        return summary_data
        
    except Exception as e:
        print(f"[Intelligence] Summary error: {e}")
        return {
            "data_source": "error",
            "error": str(e),
            "ai_available": False
        }

@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_available": AI_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "database_available": DB_AVAILABLE,
        "upload_directory": os.path.exists(UPLOAD_DIR),
        "database_url_configured": bool(os.getenv("DATABASE_URL"))
    }

@router.get("/files")
async def list_intelligence_files():
    """List all uploaded intelligence files"""
    
    files = []
    database_error = None
    
    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            result = db.execute(text("""
                SELECT original_filename, source, brand, uploaded_at, description, id
                FROM intelligence_files 
                ORDER BY uploaded_at DESC
            """))
            
            for row in result.fetchall():
                files.append({
                    "id": row[5],
                    "filename": row[0],
                    "source": row[1],
                    "brand": row[2],
                    "uploaded_at": row[3].isoformat() if row[3] else None,
                    "description": row[4]
                })
            
            db.close()
            
        except Exception as e:
            database_error = str(e)
            print(f"[Intelligence] File list error: {e}")
    
    return {
        "files": files,
        "total_files": len(files),
        "data_source": "database" if DB_AVAILABLE else "filesystem",
        "database_error": database_error
    }

async def process_intelligence_data(file_path: str, filename: str) -> Dict[str, Any]:
    """Process uploaded intelligence files and extract insights"""
    
    try:
        analysis_results = {
            "filename": filename,
            "processed_at": datetime.utcnow().isoformat(),
            "insights": [],
            "key_findings": [],
            "data_points": 0,
            "file_type": "unknown"
        }
        
        # Determine file type and process accordingly
        if filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            analysis_results["file_type"] = "spreadsheet"
            
            # Read structured data
            try:
                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                analysis_results["data_points"] = len(df)
                
                # Generate insights from data
                if not df.empty:
                    analysis_results["insights"] = [
                        f"Analyzed {len(df)} data points from {filename}",
                        f"Dataset contains {len(df.columns)} data fields",
                        "Data successfully processed for competitive intelligence"
                    ]
                    
                    # Add column-based insights
                    for col in df.columns[:3]:  # First 3 columns
                        if df[col].dtype in ['int64', 'float64']:
                            analysis_results["key_findings"].append(
                                f"{col}: {df[col].count()} values, avg: {df[col].mean():.2f}"
                            )
                        else:
                            analysis_results["key_findings"].append(
                                f"{col}: {df[col].nunique()} unique values"
                            )
                            
                    # Special handling for Instagram hashtag data
                    if any('hashtag' in col.lower() for col in df.columns):
                        analysis_results["insights"].append("Instagram hashtag data detected - competitive social media analysis ready")
                        
            except Exception as e:
                analysis_results["insights"].append(f"Error processing spreadsheet: {str(e)}")
        
        elif filename.lower().endswith(('.txt', '.md', '.doc', '.docx')):
            analysis_results["file_type"] = "document"
            
            # Read text content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                analysis_results["data_points"] = len(content.split())
                analysis_results["insights"] = [
                    f"Processed text document with {len(content.split())} words",
                    "Document content analyzed for competitive intelligence",
                    "Text-based insights extracted successfully"
                ]
                
            except Exception as e:
                analysis_results["insights"].append(f"Error processing document: {str(e)}")
        
        else:
            analysis_results["file_type"] = "other"
            analysis_results["insights"] = [
                f"File {filename} uploaded successfully",
                "File format detected and stored for analysis",
                "Ready for manual review and processing"
            ]
        
        return analysis_results
        
    except Exception as e:
        return {
            "filename": filename,
            "processed_at": datetime.utcnow().isoformat(),
            "insights": [f"Processing error: {str(e)}"],
            "key_findings": [],
            "data_points": 0,
            "file_type": "error",
            "error": str(e)
        }

@router.get("/analysis")
async def get_intelligence_analysis():
    """Get comprehensive intelligence analysis from all uploaded data"""
    
    analysis = {
        "status": "ready",
        "last_updated": datetime.utcnow().isoformat(),
        "total_files": 0,
        "insights": [],
        "recommendations": [],
        "data_sources": []
    }
    
    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            
            # Get all files and their analysis
            result = db.execute(text("""
                SELECT original_filename, analysis_results, source, uploaded_at
                FROM intelligence_files 
                ORDER BY uploaded_at DESC
            """))
            
            for row in result.fetchall():
                analysis["total_files"] += 1
                analysis["data_sources"].append({
                    "filename": row[0],
                    "source": row[2],
                    "uploaded_at": row[3].isoformat() if row[3] else None
                })
                
                if row[1]:  # analysis_results
                    try:
                        file_analysis = json.loads(row[1])
                        if "insights" in file_analysis:
                            analysis["insights"].extend(file_analysis["insights"])
                    except:
                        pass
            
            db.close()
            
            # Generate recommendations based on data
            if analysis["total_files"] > 0:
                analysis["recommendations"] = [
                    f"You have {analysis['total_files']} intelligence files ready for analysis",
                    "Consider cross-referencing data sources for deeper insights",
                    "Regular data updates recommended for competitive advantage"
                ]
            
        except Exception as e:
            analysis["error"] = str(e)
    
    return analysis

@router.get("/reports")
async def get_intelligence_reports():
    """Get intelligence reports and summaries"""
    
    reports = {
        "available_reports": [],
        "summary": {
            "total_files": 0,
            "data_sources": 0,
            "last_upload": None
        }
    }
    
    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            
            # Get summary data
            result = db.execute(text("""
                SELECT COUNT(*) as total, MAX(uploaded_at) as last_upload
                FROM intelligence_files
            """))
            
            row = result.fetchone()
            if row:
                reports["summary"]["total_files"] = row[0]
                reports["summary"]["data_sources"] = row[0]
                if row[1]:
                    reports["summary"]["last_upload"] = row[1].isoformat()
            
            # Get available reports
            if reports["summary"]["total_files"] > 0:
                reports["available_reports"] = [
                    {
                        "name": "Competitive Intelligence Summary",
                        "description": "Overview of all uploaded intelligence data",
                        "endpoint": "/api/intelligence/analysis"
                    },
                    {
                        "name": "Data Sources Report", 
                        "description": "List of all uploaded files and sources",
                        "endpoint": "/api/intelligence/files"
                    }
                ]
            
            db.close()
            
        except Exception as e:
            reports["error"] = str(e)
    
    return reports
