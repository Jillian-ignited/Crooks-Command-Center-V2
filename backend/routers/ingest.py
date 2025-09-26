"""
Enhanced ingest router with overview data aggregation
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List
import os
from pathlib import Path

router = APIRouter()

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle ObjectId and datetime objects"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

def ensure_data_directory():
    """Ensure data directory exists"""
    # Use absolute path relative to the backend directory
    backend_dir = Path(__file__).parent.parent
    data_dir = backend_dir / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

def save_processed_data(df: pd.DataFrame, source: str, filename: str) -> Dict[str, Any]:
    """Save processed data to file and return metadata"""
    data_dir = ensure_data_directory()
    
    # Create a safe filename
    safe_filename = f"{source}_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = data_dir / safe_filename
    
    # Convert DataFrame to dict and handle serialization
    data_dict = df.to_dict('records')
    
    # Save to file with custom encoder
    with open(file_path, 'w') as f:
        json.dump(data_dict, f, cls=JSONEncoder, indent=2)
    
    return {
        "file_path": str(file_path),
        "records_count": len(df),
        "columns": list(df.columns),
        "source": source,
        "processed_at": datetime.now().isoformat()
    }

@router.post("/upload")
async def upload_data(file: UploadFile = File(...), source: str = Form("upload")):
    """Handles file uploads for JSON, JSONL, and CSV formats."""
    try:
        print(f"Processing file upload: {file.filename}")
        contents = await file.read()
        print(f"File size: {len(contents)} bytes")
        
        # Process different file types
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        elif file.filename.endswith('.jsonl'):
            print("Processing JSONL file...")
            df = pd.read_json(io.StringIO(contents.decode('utf-8')), lines=True)
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.StringIO(contents.decode('utf-8')))
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Unsupported file format. Please use CSV, JSON, or JSONL."
                },
                status_code=400
            )

        print(f"DataFrame created with {len(df)} rows and {len(df.columns)} columns")
        
        # Save processed data
        metadata = save_processed_data(df, source, file.filename)
        print(f"Data saved to: {metadata['file_path']}")
        
        # Return serializable response
        response_data = {
            "success": True,
            "message": f"{file.filename} uploaded and processed successfully.",
            "metadata": metadata,
            "records_processed": len(df),
            "columns": list(df.columns)
        }
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "error": f"Upload failed: {str(e)}"
            },
            status_code=500
        )

@router.post("/paste")
async def paste_data(data: dict):
    """Handles pasted JSON data."""
    try:
        # Handle different data structures
        if "items" in data:
            df = pd.DataFrame(data["items"])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])

        # Save processed data
        metadata = save_processed_data(df, "paste", "pasted_data")
        
        # Return serializable response
        response_data = {
            "success": True,
            "message": "Pasted data processed successfully.",
            "metadata": metadata
        }
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Paste processing failed: {str(e)}"
            },
            status_code=500
        )

@router.get("/overview")
async def get_overview_data():
    """Get aggregated overview data from all processed files"""
    try:
        data_dir = ensure_data_directory()
        all_data = []
        total_posts = 0
        total_engagement = 0
        engagement_count = 0
        
        # Load all JSON files
        for file_path in data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                        total_posts += len(data)
                        
                        # Calculate engagement if available
                        for item in data:
                            if 'engagement_rate' in item and item['engagement_rate']:
                                total_engagement += float(item['engagement_rate'])
                                engagement_count += 1
                            elif 'likes' in item and 'views' in item and item['views'] > 0:
                                engagement_rate = (item['likes'] / item['views']) * 100
                                total_engagement += engagement_rate
                                engagement_count += 1
                    else:
                        all_data.append(data)
                        total_posts += 1
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
        
        # Calculate metrics
        avg_engagement = (total_engagement / engagement_count) if engagement_count > 0 else 0
        
        # Get top performing content
        top_content = []
        if all_data:
            # Sort by engagement metrics
            sorted_data = sorted(all_data, key=lambda x: x.get('likes', 0) + x.get('shares', 0), reverse=True)
            top_content = sorted_data[:5]
        
        return JSONResponse(content={
            "success": True,
            "overview": {
                "total_posts": total_posts,
                "avg_engagement": round(avg_engagement, 2),
                "total_files": len(list(data_dir.glob("*.json"))),
                "last_updated": datetime.now().isoformat()
            },
            "top_content": top_content,
            "data_available": len(all_data) > 0
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get overview data: {str(e)}"
            },
            status_code=500
        )

@router.get("/data/list")
async def list_processed_data():
    """List all processed data files"""
    try:
        data_dir = ensure_data_directory()
        files = []
        
        for file_path in data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    files.append({
                        "filename": file_path.name,
                        "records": len(data) if isinstance(data, list) else 1,
                        "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                        "size": file_path.stat().st_size
                    })
            except Exception as e:
                # Skip files that can't be read
                continue
        
        return JSONResponse(content={
            "success": True,
            "files": files,
            "total_files": len(files)
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to list data files: {str(e)}"
            },
            status_code=500
        )

@router.get("/data/{filename}")
async def get_processed_data(filename: str):
    """Get specific processed data file"""
    try:
        data_dir = ensure_data_directory()
        file_path = data_dir / filename
        
        if not file_path.exists():
            return JSONResponse(
                content={
                    "success": False,
                    "error": "File not found"
                },
                status_code=404
            )
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return JSONResponse(content={
            "success": True,
            "filename": filename,
            "data": data,
            "records": len(data) if isinstance(data, list) else 1
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to retrieve data: {str(e)}"
            },
            status_code=500
        )

@router.delete("/data/{filename}")
async def delete_processed_data(filename: str):
    """Delete a processed data file"""
    try:
        data_dir = ensure_data_directory()
        file_path = data_dir / filename
        
        if not file_path.exists():
            return JSONResponse(
                content={
                    "success": False,
                    "error": "File not found"
                },
                status_code=404
            )
        
        file_path.unlink()
        
        return JSONResponse(content={
            "success": True,
            "message": f"File {filename} deleted successfully"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            },
            status_code=500
        )

@router.get("/status")
async def get_ingest_status():
    """Get current ingest system status"""
    try:
        data_dir = ensure_data_directory()
        json_files = list(data_dir.glob("*.json"))
        
        total_records = 0
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    total_records += len(data) if isinstance(data, list) else 1
            except:
                continue
        
        return JSONResponse(content={
            "success": True,
            "status": {
                "total_files": len(json_files),
                "total_records": total_records,
                "data_directory": str(data_dir),
                "last_check": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get status: {str(e)}"
            },
            status_code=500
        )
