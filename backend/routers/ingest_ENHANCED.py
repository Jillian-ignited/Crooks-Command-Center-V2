from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import json
import io

router = APIRouter()

@router.post("/upload")
async def upload_data(file: UploadFile = File(...), source: str = Form("manual")):
    """Handles file uploads for JSON, JSONL, and CSV formats."""
    try:
        contents = await file.read()
        content_str = contents.decode('utf-8')
        
        # Process different file formats
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content_str))
            data = df.to_dict('records')
        elif file.filename.endswith('.jsonl'):
            lines = content_str.strip().split('\n')
            data = [json.loads(line) for line in lines if line.strip()]
        else:  # JSON
            parsed_data = json.loads(content_str)
            if isinstance(parsed_data, list):
                data = parsed_data
            elif isinstance(parsed_data, dict) and 'items' in parsed_data:
                data = parsed_data['items']
            else:
                data = [parsed_data]

        # Basic data validation
        if not data:
            raise HTTPException(status_code=400, detail="No valid data found in file")

        # Here you would add your data processing logic
        # For now, we'll just return success with record count
        
        return JSONResponse(
            content={
                "status": "success",
                "message": f"File '{file.filename}' uploaded and processed successfully",
                "records_processed": len(data),
                "source": source,
                "filename": file.filename
            }, 
            status_code=200
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Empty CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.post("/paste")
async def paste_data(data: dict):
    """Handles pasted JSON data."""
    try:
        # Extract items from the data
        if 'items' in data:
            items = data['items']
        elif isinstance(data, list):
            items = data
        else:
            items = [data]

        # Basic validation
        if not items:
            raise HTTPException(status_code=400, detail="No valid data items found")

        # Here you would add your data processing logic
        # For now, we'll just return success with record count
        
        return JSONResponse(
            content={
                "status": "success", 
                "message": "Pasted data processed successfully",
                "records_processed": len(items),
                "source": "paste"
            }, 
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/sources")
async def get_sources():
    """Get all data sources."""
    # This would typically query your database
    # For now, return mock data
    return JSONResponse(
        content={
            "sources": [
                {
                    "name": "Instagram Data",
                    "type": "JSONL",
                    "runs": 3,
                    "total_items": 194
                },
                {
                    "name": "TikTok Data", 
                    "type": "JSONL",
                    "runs": 2,
                    "total_items": 351
                }
            ]
        }
    )

@router.get("/runs")
async def get_runs(limit: int = 10):
    """Get processing runs."""
    # This would typically query your database
    # For now, return mock data
    return JSONResponse(
        content={
            "runs": [
                {
                    "id": 1,
                    "source": "manual_upload",
                    "status": "completed",
                    "items": 194,
                    "created_at": "2025-09-24T12:00:00Z"
                },
                {
                    "id": 2,
                    "source": "paste_data",
                    "status": "completed", 
                    "items": 351,
                    "created_at": "2025-09-24T11:30:00Z"
                }
            ]
        }
    )
