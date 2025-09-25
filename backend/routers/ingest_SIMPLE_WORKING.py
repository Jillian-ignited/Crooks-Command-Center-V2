from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import json
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

router = APIRouter(tags=["ingest"])

# Simple, working data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), source: str = Form("manual")):
    """Simple, working file upload that actually processes JSONL files"""
    try:
        # Read the uploaded file
        content = await file.read()
        
        # Parse JSONL content
        lines = content.decode('utf-8').strip().split('\n')
        data = []
        
        for line in lines:
            if line.strip():
                try:
                    record = json.loads(line)
                    data.append(record)
                except json.JSONDecodeError:
                    continue
        
        if not data:
            return JSONResponse({
                "success": False,
                "error": "No valid JSON records found in file"
            })
        
        # Save processed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source}_{file.filename}_{timestamp}.json"
        filepath = DATA_DIR / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully processed {len(data)} records",
            "filename": filename,
            "records_processed": len(data),
            "file_path": str(filepath)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        })

@router.get("/overview")
async def get_overview():
    """Simple overview that actually shows uploaded data"""
    try:
        # Find all JSON files
        json_files = list(DATA_DIR.glob("*.json"))
        
        if not json_files:
            return JSONResponse({
                "success": True,
                "total_posts": 0,
                "total_files": 0,
                "message": "No data uploaded yet"
            })
        
        total_posts = 0
        all_data = []
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                        total_posts += len(data)
                    else:
                        all_data.append(data)
                        total_posts += 1
            except:
                continue
        
        # Calculate basic metrics
        engagement_rates = []
        for record in all_data:
            if 'engagement_rate' in record:
                engagement_rates.append(record['engagement_rate'])
            elif 'likes' in record and 'followers' in record and record['followers'] > 0:
                engagement_rates.append((record['likes'] / record['followers']) * 100)
        
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        return JSONResponse({
            "success": True,
            "total_posts": total_posts,
            "total_files": len(json_files),
            "average_engagement": round(avg_engagement, 2),
            "top_content": all_data[:5] if all_data else [],
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Overview failed: {str(e)}"
        })

@router.get("/data/list")
async def list_data_files():
    """List all uploaded data files"""
    try:
        json_files = list(DATA_DIR.glob("*.json"))
        
        files_info = []
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 1
                
                files_info.append({
                    "filename": file_path.name,
                    "records": record_count,
                    "size": file_path.stat().st_size,
                    "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                })
            except:
                continue
        
        return JSONResponse({
            "success": True,
            "files": files_info,
            "total_files": len(files_info)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"List failed: {str(e)}"
        })

@router.delete("/data/{filename}")
async def delete_data_file(filename: str):
    """Delete a data file"""
    try:
        file_path = DATA_DIR / filename
        
        if not file_path.exists():
            return JSONResponse({
                "success": False,
                "error": "File not found"
            })
        
        file_path.unlink()
        
        return JSONResponse({
            "success": True,
            "message": f"File {filename} deleted successfully"
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Delete failed: {str(e)}"
        })
