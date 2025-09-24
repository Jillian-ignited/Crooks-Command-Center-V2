from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import json
import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any, List
import uuid
from datetime import datetime
import shutil

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Store processing runs in memory (could be moved to database later)
processing_runs = []
data_sources = []

def save_uploaded_file(file: UploadFile, source: str) -> Dict[str, Any]:
    """Save uploaded file to persistent storage"""
    try:
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        unique_filename = f"{source}_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = file_path.stat().st_size
        
        return {
            "success": True,
            "filename": unique_filename,
            "original_name": file.filename,
            "path": str(file_path),
            "size": file_size,
            "source": source
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def process_uploaded_data(file_path: Path, source: str) -> Dict[str, Any]:
    """Process uploaded data and extract metrics"""
    try:
        file_extension = file_path.suffix.lower()
        
        # Process different file types
        if file_extension == '.jsonl':
            # Process JSONL file
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            
            df = pd.DataFrame(data)
            
        elif file_extension == '.json':
            # Process JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'items' in data:
                    df = pd.DataFrame(data['items'])
                elif 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    df = pd.DataFrame([data])
            else:
                df = pd.DataFrame()
                
        elif file_extension == '.csv':
            # Process CSV file
            df = pd.read_csv(file_path)
            
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_extension}"
            }
        
        # Extract metrics from processed data
        total_records = len(df)
        
        # Try to identify brands
        brands = []
        brand_columns = ['brand', 'Brand', 'account', 'username', 'author']
        for col in brand_columns:
            if col in df.columns:
                brands = df[col].dropna().unique().tolist()
                break
        
        # Try to identify text content for sentiment analysis
        text_content = []
        text_columns = ['caption', 'description', 'text', 'content', 'message']
        for col in text_columns:
            if col in df.columns:
                text_content.extend(df[col].dropna().astype(str).tolist())
        
        # Try to extract hashtags
        hashtags = []
        hashtag_columns = ['hashtags', 'tags']
        for col in hashtag_columns:
            if col in df.columns:
                for hashtag_str in df[col].dropna():
                    if isinstance(hashtag_str, str):
                        import re
                        found_hashtags = re.findall(r'#\w+', hashtag_str.lower())
                        hashtags.extend(found_hashtags)
        
        # Get unique hashtags
        unique_hashtags = list(set(hashtags))
        
        return {
            "success": True,
            "total_records": total_records,
            "brands_found": len(brands),
            "brand_list": brands[:10],  # First 10 brands
            "text_content_count": len(text_content),
            "hashtags_found": len(unique_hashtags),
            "top_hashtags": unique_hashtags[:10],  # First 10 hashtags
            "columns": df.columns.tolist(),
            "sample_data": df.head(3).to_dict('records') if not df.empty else []
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/upload")
async def upload_data(file: UploadFile = File(...), source: str = Form(...)):
    """Upload and process data files with persistent storage"""
    
    # Validate file type
    allowed_extensions = ['.json', '.jsonl', '.csv']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save file to persistent storage
    save_result = save_uploaded_file(file, source)
    
    if not save_result["success"]:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {save_result['error']}")
    
    # Process the saved file
    file_path = Path(save_result["path"])
    process_result = process_uploaded_data(file_path, source)
    
    if not process_result["success"]:
        # Clean up file if processing failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to process file: {process_result['error']}")
    
    # Create processing run record
    run_id = str(uuid.uuid4())
    processing_run = {
        "id": run_id,
        "source": source,
        "filename": save_result["original_name"],
        "saved_filename": save_result["filename"],
        "file_path": save_result["path"],
        "file_size": save_result["size"],
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "total_records": process_result["total_records"],
        "brands_found": process_result["brands_found"],
        "text_content_count": process_result["text_content_count"],
        "hashtags_found": process_result["hashtags_found"]
    }
    
    processing_runs.append(processing_run)
    
    # Update or create data source record
    existing_source = next((s for s in data_sources if s["name"] == source), None)
    if existing_source:
        existing_source["last_updated"] = datetime.now().isoformat()
        existing_source["total_files"] += 1
        existing_source["total_records"] += process_result["total_records"]
    else:
        data_sources.append({
            "name": source,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_files": 1,
            "total_records": process_result["total_records"],
            "status": "active"
        })
    
    return JSONResponse({
        "success": True,
        "message": "File uploaded and processed successfully",
        "run_id": run_id,
        "file_info": {
            "original_name": save_result["original_name"],
            "saved_name": save_result["filename"],
            "size": save_result["size"],
            "path": save_result["path"]
        },
        "processing_results": process_result,
        "data_refresh_triggered": True  # Indicates dashboard should refresh
    })

@router.post("/paste")
async def paste_data(data: dict):
    """Process pasted JSON data with persistent storage"""
    
    try:
        source = data.get("source", "manual_paste")
        json_data = data.get("data")
        
        if not json_data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Save pasted data to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source}_paste_{timestamp}_{uuid.uuid4().hex[:8]}.json"
        file_path = UPLOAD_DIR / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        # Process the saved data
        process_result = process_uploaded_data(file_path, source)
        
        if not process_result["success"]:
            # Clean up file if processing failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to process data: {process_result['error']}")
        
        # Create processing run record
        run_id = str(uuid.uuid4())
        file_size = file_path.stat().st_size
        
        processing_run = {
            "id": run_id,
            "source": source,
            "filename": "pasted_data.json",
            "saved_filename": filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "total_records": process_result["total_records"],
            "brands_found": process_result["brands_found"],
            "text_content_count": process_result["text_content_count"],
            "hashtags_found": process_result["hashtags_found"]
        }
        
        processing_runs.append(processing_run)
        
        # Update or create data source record
        existing_source = next((s for s in data_sources if s["name"] == source), None)
        if existing_source:
            existing_source["last_updated"] = datetime.now().isoformat()
            existing_source["total_files"] += 1
            existing_source["total_records"] += process_result["total_records"]
        else:
            data_sources.append({
                "name": source,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_files": 1,
                "total_records": process_result["total_records"],
                "status": "active"
            })
        
        return JSONResponse({
            "success": True,
            "message": "Data pasted and processed successfully",
            "run_id": run_id,
            "file_info": {
                "saved_name": filename,
                "size": file_size,
                "path": str(file_path)
            },
            "processing_results": process_result,
            "data_refresh_triggered": True  # Indicates dashboard should refresh
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process pasted data: {str(e)}")

@router.get("/sources")
async def get_data_sources():
    """Get all data sources"""
    return JSONResponse({
        "sources": data_sources,
        "total_sources": len(data_sources)
    })

@router.get("/runs")
async def get_processing_runs():
    """Get all processing runs"""
    return JSONResponse({
        "runs": processing_runs,
        "total_runs": len(processing_runs)
    })

@router.get("/runs/{run_id}")
async def get_processing_run(run_id: str):
    """Get specific processing run details"""
    run = next((r for r in processing_runs if r["id"] == run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Processing run not found")
    
    return JSONResponse(run)

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete uploaded file"""
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Remove file
        file_path.unlink()
        
        # Remove from processing runs
        global processing_runs
        processing_runs = [r for r in processing_runs if r["saved_filename"] != filename]
        
        return JSONResponse({
            "success": True,
            "message": f"File {filename} deleted successfully",
            "data_refresh_triggered": True  # Indicates dashboard should refresh
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    upload_dir_exists = UPLOAD_DIR.exists()
    total_files = len(list(UPLOAD_DIR.glob("*"))) if upload_dir_exists else 0
    
    return JSONResponse({
        "status": "healthy",
        "upload_directory": str(UPLOAD_DIR),
        "upload_directory_exists": upload_dir_exists,
        "total_files": total_files,
        "total_sources": len(data_sources),
        "total_runs": len(processing_runs),
        "timestamp": datetime.now().isoformat()
    })

@router.post("/refresh")
async def trigger_refresh():
    """Manually trigger dashboard refresh"""
    return JSONResponse({
        "success": True,
        "message": "Dashboard refresh triggered",
        "timestamp": datetime.now().isoformat(),
        "data_refresh_triggered": True
    })
