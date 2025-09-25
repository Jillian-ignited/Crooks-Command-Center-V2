from fastapi import APIRouter, File, UploadFile, Form, HTTPException
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
    data_dir = Path("data")
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
async def upload_data(file: UploadFile = File(...), source: str = Form(...)):
    """Handles file uploads for JSON, JSONL, and CSV formats."""
    try:
        contents = await file.read()
        
        # Process different file types
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        elif file.filename.endswith('.jsonl'):
            df = pd.read_json(io.StringIO(contents.decode('utf-8')), lines=True)
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.StringIO(contents.decode('utf-8')))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please use CSV, JSON, or JSONL.")

        # Save processed data
        metadata = save_processed_data(df, source, file.filename)
        
        # Return serializable response
        response_data = {
            "success": True,
            "message": f"{file.filename} uploaded and processed successfully.",
            "metadata": metadata
        }
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
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
            raise HTTPException(status_code=404, detail="File not found")
        
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
            raise HTTPException(status_code=404, detail="File not found")
        
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

@router.get("/stats")
async def get_data_stats():
    """Get statistics about processed data"""
    try:
        data_dir = ensure_data_directory()
        total_files = 0
        total_records = 0
        total_size = 0
        
        for file_path in data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    total_files += 1
                    total_records += len(data) if isinstance(data, list) else 1
                    total_size += file_path.stat().st_size
            except Exception:
                continue
        
        return JSONResponse(content={
            "success": True,
            "stats": {
                "total_files": total_files,
                "total_records": total_records,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get stats: {str(e)}"
            },
            status_code=500
        )
