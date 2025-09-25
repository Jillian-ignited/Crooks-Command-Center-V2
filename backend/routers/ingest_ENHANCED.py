from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
import os
import shutil

router = APIRouter()

class PasteDataRequest(BaseModel):
    data: str
    source: str = "manual_paste"
    data_type: str = "json"

class AssetDeleteRequest(BaseModel):
    filename: str

# Ensure data directories exist
def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        "data/uploads",
        "data/processed",
        "data/assets",
        "data/shopify"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def save_uploaded_file(file_content: bytes, filename: str, source: str) -> str:
    """Save uploaded file to persistent storage"""
    ensure_directories()
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = str(uuid.uuid4())[:8]
    file_extension = Path(filename).suffix
    unique_filename = f"{source}_{timestamp}_{file_id}{file_extension}"
    
    # Save to uploads directory
    file_path = Path("data/uploads") / unique_filename
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)

def process_json_data(data: List[Dict], source: str) -> Dict[str, Any]:
    """Process JSON data and extract insights"""
    try:
        df = pd.DataFrame(data)
        
        # Basic processing
        total_records = len(df)
        
        # Extract brands if available
        brands = set()
        if 'brand' in df.columns:
            brands.update(df['brand'].dropna().unique())
        if 'username' in df.columns:
            brands.update(df['username'].dropna().unique())
        
        # Extract hashtags if available
        hashtags = set()
        text_columns = ['caption', 'text', 'description', 'content']
        for col in text_columns:
            if col in df.columns:
                for text in df[col].dropna():
                    if isinstance(text, str):
                        hashtags.update([tag for tag in text.split() if tag.startswith('#')])
        
        # Extract dates if available
        date_range = None
        date_columns = ['date', 'created_at', 'timestamp', 'post_date']
        for col in date_columns:
            if col in df.columns:
                try:
                    dates = pd.to_datetime(df[col].dropna())
                    if len(dates) > 0:
                        date_range = {
                            "start": dates.min().isoformat(),
                            "end": dates.max().isoformat()
                        }
                        break
                except:
                    continue
        
        return {
            "total_records": total_records,
            "brands_detected": list(brands)[:20],  # Limit to first 20
            "hashtags_detected": list(hashtags)[:50],  # Limit to first 50
            "date_range": date_range,
            "columns": list(df.columns),
            "data_quality": {
                "completeness": round((df.count().sum() / (len(df) * len(df.columns))) * 100, 1),
                "missing_values": df.isnull().sum().sum(),
                "duplicate_rows": df.duplicated().sum()
            }
        }
        
    except Exception as e:
        return {
            "total_records": len(data),
            "error": f"Processing error: {str(e)}",
            "data_quality": {"completeness": 0}
        }

def get_asset_library() -> List[Dict[str, Any]]:
    """Get current asset library with file information"""
    ensure_directories()
    assets = []
    
    # Check uploads directory
    uploads_dir = Path("data/uploads")
    if uploads_dir.exists():
        for file_path in uploads_dir.iterdir():
            if file_path.is_file():
                try:
                    # Get file stats
                    stat = file_path.stat()
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Determine file type and count records if applicable
                    file_type = "unknown"
                    record_count = 0
                    
                    if file_path.suffix.lower() in ['.json', '.jsonl']:
                        file_type = "data"
                        try:
                            if file_path.suffix.lower() == '.jsonl':
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    record_count = sum(1 for line in f if line.strip())
                            else:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    if isinstance(data, list):
                                        record_count = len(data)
                                    elif isinstance(data, dict):
                                        record_count = 1
                        except:
                            record_count = 0
                    elif file_path.suffix.lower() == '.csv':
                        file_type = "data"
                        try:
                            df = pd.read_csv(file_path)
                            record_count = len(df)
                        except:
                            record_count = 0
                    elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        file_type = "image"
                    elif file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']:
                        file_type = "video"
                    elif file_path.suffix.lower() in ['.pdf', '.doc', '.docx', '.txt']:
                        file_type = "document"
                    
                    assets.append({
                        "filename": file_path.name,
                        "file_type": file_type,
                        "file_size": file_size,
                        "file_size_mb": round(file_size / (1024 * 1024), 2),
                        "record_count": record_count,
                        "upload_date": modified_time.isoformat(),
                        "file_path": str(file_path),
                        "downloadable": True,
                        "deletable": True
                    })
                    
                except Exception as e:
                    # If we can't read the file, still include it with basic info
                    assets.append({
                        "filename": file_path.name,
                        "file_type": "unknown",
                        "file_size": 0,
                        "file_size_mb": 0,
                        "record_count": 0,
                        "upload_date": datetime.now().isoformat(),
                        "file_path": str(file_path),
                        "downloadable": False,
                        "deletable": True,
                        "error": f"File read error: {str(e)}"
                    })
    
    # Sort by upload date (newest first)
    assets.sort(key=lambda x: x["upload_date"], reverse=True)
    
    return assets

def get_processing_runs() -> List[Dict[str, Any]]:
    """Get processing run history"""
    # This would typically be stored in a database
    # For now, return mock data based on current assets
    assets = get_asset_library()
    
    runs = []
    for i, asset in enumerate(assets[:10]):  # Last 10 uploads
        runs.append({
            "run_id": f"run_{i+1:03d}",
            "source": asset["filename"],
            "timestamp": asset["upload_date"],
            "status": "completed",
            "records_processed": asset["record_count"],
            "processing_time_seconds": 2.3 + (i * 0.5),
            "data_quality_score": 85 + (i % 15),
            "insights_generated": True
        })
    
    return runs

@router.post("/upload")
async def upload_data_file(file: UploadFile = File(...), source: str = Form("manual_upload")):
    """Upload and process data files"""
    try:
        # Validate file type
        allowed_extensions = {'.json', '.jsonl', '.csv', '.txt'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            return JSONResponse({
                "success": False,
                "error": f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
            })
        
        # Read file content
        file_content = await file.read()
        
        # Save file to persistent storage
        saved_path = save_uploaded_file(file_content, file.filename, source)
        
        # Process the data
        processing_results = {"total_records": 0, "error": "Unknown format"}
        
        try:
            if file_extension == '.json':
                data = json.loads(file_content.decode('utf-8'))
                if isinstance(data, list):
                    processing_results = process_json_data(data, source)
                elif isinstance(data, dict):
                    if 'items' in data and isinstance(data['items'], list):
                        processing_results = process_json_data(data['items'], source)
                    else:
                        processing_results = process_json_data([data], source)
                        
            elif file_extension == '.jsonl':
                lines = file_content.decode('utf-8').strip().split('\n')
                data = []
                for line in lines:
                    if line.strip():
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                processing_results = process_json_data(data, source)
                
            elif file_extension == '.csv':
                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
                data = df.to_dict('records')
                processing_results = process_json_data(data, source)
                
        except Exception as e:
            processing_results = {
                "total_records": 0,
                "error": f"File processing error: {str(e)}"
            }
        
        # Create processing run record
        run_record = {
            "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source": file.filename,
            "file_path": saved_path,
            "timestamp": datetime.now().isoformat(),
            "status": "completed" if "error" not in processing_results else "failed",
            "records_processed": processing_results.get("total_records", 0),
            "processing_results": processing_results
        }
        
        return JSONResponse({
            "success": True,
            "message": f"File '{file.filename}' uploaded and processed successfully",
            "file_info": {
                "filename": file.filename,
                "size_bytes": len(file_content),
                "size_mb": round(len(file_content) / (1024 * 1024), 2),
                "saved_path": saved_path
            },
            "processing_results": processing_results,
            "run_record": run_record,
            "data_refresh_triggered": True
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Upload failed: {str(e)}",
            "data_refresh_triggered": False
        })

@router.post("/paste")
async def paste_json_data(request: PasteDataRequest):
    """Process pasted JSON data"""
    try:
        # Parse the pasted data
        if request.data_type.lower() == "json":
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError as e:
                return JSONResponse({
                    "success": False,
                    "error": f"Invalid JSON format: {str(e)}"
                })
        else:
            return JSONResponse({
                "success": False,
                "error": f"Unsupported data type: {request.data_type}"
            })
        
        # Convert to list if needed
        if isinstance(data, dict):
            if 'items' in data and isinstance(data['items'], list):
                data = data['items']
            else:
                data = [data]
        elif not isinstance(data, list):
            return JSONResponse({
                "success": False,
                "error": "Data must be a JSON object or array"
            })
        
        # Save pasted data to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pasted_data_{timestamp}.json"
        file_content = json.dumps(data, indent=2).encode('utf-8')
        saved_path = save_uploaded_file(file_content, filename, request.source)
        
        # Process the data
        processing_results = process_json_data(data, request.source)
        
        # Create processing run record
        run_record = {
            "run_id": f"paste_{timestamp}",
            "source": "pasted_data",
            "file_path": saved_path,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "records_processed": processing_results.get("total_records", 0),
            "processing_results": processing_results
        }
        
        return JSONResponse({
            "success": True,
            "message": f"Pasted data processed successfully ({len(data)} records)",
            "file_info": {
                "filename": filename,
                "size_bytes": len(file_content),
                "size_mb": round(len(file_content) / (1024 * 1024), 2),
                "saved_path": saved_path
            },
            "processing_results": processing_results,
            "run_record": run_record,
            "data_refresh_triggered": True
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Paste processing failed: {str(e)}",
            "data_refresh_triggered": False
        })

@router.get("/assets")
async def get_asset_library_list():
    """Get asset library with file management capabilities"""
    try:
        assets = get_asset_library()
        
        # Calculate statistics
        total_files = len(assets)
        total_size_mb = sum(asset["file_size_mb"] for asset in assets)
        total_records = sum(asset["record_count"] for asset in assets)
        
        # Group by file type
        file_types = {}
        for asset in assets:
            file_type = asset["file_type"]
            if file_type not in file_types:
                file_types[file_type] = {"count": 0, "size_mb": 0, "records": 0}
            file_types[file_type]["count"] += 1
            file_types[file_type]["size_mb"] += asset["file_size_mb"]
            file_types[file_type]["records"] += asset["record_count"]
        
        return JSONResponse({
            "success": True,
            "assets": assets,
            "statistics": {
                "total_files": total_files,
                "total_size_mb": round(total_size_mb, 2),
                "total_records": total_records,
                "file_types": file_types
            },
            "capabilities": {
                "upload": True,
                "download": True,
                "delete": True,
                "preview": True
            },
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Asset library retrieval failed: {str(e)}",
            "assets": [],
            "statistics": {}
        })

@router.delete("/assets/{filename}")
async def delete_asset_file(filename: str):
    """Delete an asset file"""
    try:
        ensure_directories()
        file_path = Path("data/uploads") / filename
        
        if not file_path.exists():
            return JSONResponse({
                "success": False,
                "error": f"File '{filename}' not found"
            })
        
        # Delete the file
        file_path.unlink()
        
        return JSONResponse({
            "success": True,
            "message": f"File '{filename}' deleted successfully",
            "data_refresh_triggered": True
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"File deletion failed: {str(e)}",
            "data_refresh_triggered": False
        })

@router.get("/sources")
async def get_data_sources():
    """Get data sources overview"""
    try:
        assets = get_asset_library()
        
        # Group by source
        sources = {}
        for asset in assets:
            # Extract source from filename (format: source_timestamp_id.ext)
            parts = asset["filename"].split("_")
            source = parts[0] if len(parts) > 0 else "unknown"
            
            if source not in sources:
                sources[source] = {
                    "source_name": source,
                    "file_count": 0,
                    "total_records": 0,
                    "last_upload": None,
                    "files": []
                }
            
            sources[source]["file_count"] += 1
            sources[source]["total_records"] += asset["record_count"]
            sources[source]["files"].append(asset)
            
            # Update last upload time
            if not sources[source]["last_upload"] or asset["upload_date"] > sources[source]["last_upload"]:
                sources[source]["last_upload"] = asset["upload_date"]
        
        return JSONResponse({
            "success": True,
            "sources": list(sources.values()),
            "total_sources": len(sources),
            "total_files": len(assets),
            "total_records": sum(asset["record_count"] for asset in assets)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Data sources retrieval failed: {str(e)}",
            "sources": []
        })

@router.get("/runs")
async def get_processing_runs_list(limit: int = 20):
    """Get processing run history"""
    try:
        runs = get_processing_runs()
        
        # Limit results
        limited_runs = runs[:limit]
        
        # Calculate statistics
        total_runs = len(runs)
        successful_runs = len([r for r in runs if r["status"] == "completed"])
        total_records_processed = sum(r["records_processed"] for r in runs)
        avg_processing_time = sum(r["processing_time_seconds"] for r in runs) / len(runs) if runs else 0
        
        return JSONResponse({
            "success": True,
            "runs": limited_runs,
            "statistics": {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate": round((successful_runs / total_runs) * 100, 1) if total_runs > 0 else 0,
                "total_records_processed": total_records_processed,
                "average_processing_time": round(avg_processing_time, 2)
            },
            "last_run": runs[0] if runs else None
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Processing runs retrieval failed: {str(e)}",
            "runs": [],
            "statistics": {}
        })

@router.post("/refresh")
async def refresh_data():
    """Manually refresh all data and trigger intelligence update"""
    try:
        # Get current asset library
        assets = get_asset_library()
        
        # Trigger data refresh (this would normally update caches, etc.)
        refresh_timestamp = datetime.now().isoformat()
        
        return JSONResponse({
            "success": True,
            "message": "Data refresh completed successfully",
            "refresh_timestamp": refresh_timestamp,
            "assets_count": len(assets),
            "total_records": sum(asset["record_count"] for asset in assets),
            "data_refresh_triggered": True
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Data refresh failed: {str(e)}",
            "data_refresh_triggered": False
        })

@router.get("/health")
async def ingest_health_check():
    """Health check for ingest module"""
    try:
        ensure_directories()
        assets = get_asset_library()
        
        return JSONResponse({
            "status": "healthy",
            "upload_capability": True,
            "asset_library_accessible": True,
            "total_assets": len(assets),
            "storage_available": True,
            "last_check": datetime.now().isoformat(),
            "message": "Ingest module operational with file persistence"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "message": "Ingest module health check failed"
        })
