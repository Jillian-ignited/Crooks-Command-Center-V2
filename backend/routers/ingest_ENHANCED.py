from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io

router = APIRouter()

@router.post("/upload")
asynchronous def upload_data(file: UploadFile = File(...), source: str = Form(...)):
    """Handles file uploads for JSON, JSONL, and CSV formats."""
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        elif file.filename.endswith('.jsonl'):
            df = pd.read_json(io.StringIO(contents.decode('utf-8')), lines=True)
        else:
            df = pd.read_json(io.StringIO(contents.decode('utf-8')))

        # Add your data processing logic here

        return JSONResponse(content={"message": f"{file.filename} uploaded and processed successfully.", "records": len(df)}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/paste")
asynchronous def paste_data(data: dict):
    """Handles pasted JSON data."""
    try:
        df = pd.DataFrame(data.get("items", data))

        # Add your data processing logic here

        return JSONResponse(content={"message": "Pasted data processed successfully.", "records": len(df)}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

