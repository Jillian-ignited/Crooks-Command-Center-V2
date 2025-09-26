from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import io
from typing import List

router = APIRouter()

# Ensure data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Enhanced file upload supporting multiple formats:
    - Social media data (JSON, JSONL)
    - Shopify reports (CSV, Excel)
    - Agency reports (CSV, Excel)
    """
    try:
        uploaded_files = []
        
        for file in files:
            if not file.filename:
                continue
                
            # Read file content
            content = await file.read()
            
            # Determine file type and process accordingly
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension in ['.json', '.jsonl']:
                # Process social media data
                processed_data = await process_social_media_data(content, file.filename)
                
            elif file_extension in ['.csv']:
                # Process CSV reports (Shopify, Agency, etc.)
                processed_data = await process_csv_report(content, file.filename)
                
            elif file_extension in ['.xlsx', '.xls']:
                # Process Excel reports
                processed_data = await process_excel_report(content, file.filename)
                
            else:
                continue  # Skip unsupported file types
            
            # Save processed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = file.filename.replace(" ", "_").replace("/", "_")
            output_filename = f"{safe_filename}_{timestamp}.json"
            output_path = DATA_DIR / output_filename
            
            with open(output_path, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            uploaded_files.append({
                "filename": file.filename,
                "processed_filename": output_filename,
                "records": len(processed_data) if isinstance(processed_data, list) else 1,
                "type": detect_data_type(file.filename, processed_data),
                "size": len(content)
            })
        
        return JSONResponse(content={
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
            "files": uploaded_files
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Upload failed: {str(e)}"
            },
            status_code=500
        )

async def process_social_media_data(content: bytes, filename: str) -> list:
    """Process JSON/JSONL social media data"""
    try:
        content_str = content.decode('utf-8')
        
        # Handle JSONL format (one JSON object per line)
        if filename.endswith('.jsonl'):
            data = []
            for line in content_str.strip().split('\n'):
                if line.strip():
                    data.append(json.loads(line))
            return data
        
        # Handle regular JSON format
        else:
            data = json.loads(content_str)
            if not isinstance(data, list):
                data = [data]
            return data
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")

async def process_csv_report(content: bytes, filename: str) -> list:
    """Process CSV reports from Shopify, agencies, etc."""
    try:
        content_str = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content_str))
        
        data = []
        for row in csv_reader:
            # Clean and standardize the data
            cleaned_row = {}
            for key, value in row.items():
                # Standardize column names
                clean_key = key.strip().lower().replace(' ', '_').replace('-', '_')
                cleaned_row[clean_key] = value.strip() if isinstance(value, str) else value
            
            # Add metadata
            cleaned_row['_source_file'] = filename
            cleaned_row['_upload_timestamp'] = datetime.now().isoformat()
            
            data.append(cleaned_row)
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")

async def process_excel_report(content: bytes, filename: str) -> list:
    """Process Excel reports from Shopify, agencies, etc."""
    try:
        # Read Excel file
        df = pd.read_excel(io.BytesIO(content))
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Add metadata
        df['_source_file'] = filename
        df['_upload_timestamp'] = datetime.now().isoformat()
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Excel format: {str(e)}")

def detect_data_type(filename: str, data: list) -> str:
    """Detect the type of data based on filename and content"""
    filename_lower = filename.lower()
    
    # Check filename patterns
    if 'shopify' in filename_lower or 'sales' in filename_lower or 'orders' in filename_lower:
        return 'shopify_data'
    elif 'agency' in filename_lower or 'deliverable' in filename_lower or 'project' in filename_lower:
        return 'agency_data'
    elif 'instagram' in filename_lower:
        return 'instagram_data'
    elif 'tiktok' in filename_lower:
        return 'tiktok_data'
    elif 'twitter' in filename_lower or 'x.com' in filename_lower:
        return 'twitter_data'
    
    # Check content structure for social media data
    if data and isinstance(data, list) and len(data) > 0:
        first_item = data[0]
        if isinstance(first_item, dict):
            # Look for social media indicators
            if any(key in first_item for key in ['likes', 'comments', 'shares', 'caption', 'hashtags']):
                return 'social_media_data'
            # Look for e-commerce indicators
            elif any(key in first_item for key in ['order_id', 'product_id', 'revenue', 'quantity']):
                return 'ecommerce_data'
            # Look for agency indicators
            elif any(key in first_item for key in ['project', 'deliverable', 'client', 'deadline']):
                return 'agency_data'
    
    return 'unknown_data'

@router.get("/overview")
async def get_data_overview():
    """Get overview of all uploaded data"""
    try:
        data_files = list(DATA_DIR.glob("*.json"))
        
        total_records = 0
        data_by_type = {}
        file_info = []
        
        for file_path in data_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    record_count = len(data)
                    total_records += record_count
                    
                    # Detect data type
                    data_type = detect_data_type(file_path.name, data)
                    if data_type not in data_by_type:
                        data_by_type[data_type] = 0
                    data_by_type[data_type] += record_count
                    
                    file_info.append({
                        "filename": file_path.name,
                        "records": record_count,
                        "type": data_type,
                        "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                    })
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        return JSONResponse(content={
            "success": True,
            "overview": {
                "total_files": len(data_files),
                "total_records": total_records,
                "data_by_type": data_by_type,
                "last_updated": datetime.now().isoformat()
            },
            "files": file_info,
            "data_available": total_records > 0
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to get overview: {str(e)}"
            },
            status_code=500
        )

@router.get("/status")
async def get_ingest_status():
    """Get current ingest status and capabilities"""
    return JSONResponse(content={
        "success": True,
        "status": {
            "supported_formats": [
                "JSON - Social media data",
                "JSONL - Social media data", 
                "CSV - Shopify reports, Agency reports",
                "Excel - Shopify reports, Agency reports"
            ],
            "data_types": [
                "Social Media (Instagram, TikTok, Twitter)",
                "E-commerce (Shopify sales, orders, products)",
                "Agency (Projects, deliverables, timelines)",
                "Custom data formats"
            ],
            "features": [
                "Multi-format upload support",
                "Automatic data type detection",
                "Data standardization and cleaning",
                "Unified analysis across all data sources"
            ]
        }
    })

@router.delete("/clear")
async def clear_all_data():
    """Clear all uploaded data (for testing/reset)"""
    try:
        data_files = list(DATA_DIR.glob("*.json"))
        deleted_count = 0
        
        for file_path in data_files:
            file_path.unlink()
            deleted_count += 1
        
        return JSONResponse(content={
            "success": True,
            "message": f"Cleared {deleted_count} data files"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"Failed to clear data: {str(e)}"
            },
            status_code=500
        )
