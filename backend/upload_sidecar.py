from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional, List

router = APIRouter()

@router.get("/")
async def upload_root():
    """Upload root endpoint"""
    return {
        "success": True,
        "message": "Upload API operational",
        "endpoints": ["/file", "/files", "/status", "/history"]
    }

@router.post("/file")
async def upload_file(file: UploadFile = File(...),
                     category: str = Form(...),
                     tags: Optional[str] = Form(None),
                     description: Optional[str] = Form(None)):
    """Upload single file"""
    return {
        "success": True,
        "message": "File uploaded successfully",
        "file_info": {
            "id": "file_12345",
            "filename": file.filename,
            "original_name": file.filename,
            "content_type": file.content_type,
            "size": "2.5 MB",  # Mock size
            "category": category,
            "tags": tags.split(",") if tags else [],
            "description": description,
            "uploaded_at": "2023-09-29T10:00:00",
            "url": f"/uploads/{file.filename}"
        }
    }

@router.post("/files")
async def upload_files(files: List[UploadFile] = File(...),
                      category: str = Form(...),
                      tags: Optional[str] = Form(None),
                      description: Optional[str] = Form(None)):
    """Upload multiple files"""
    return {
        "success": True,
        "message": f"{len(files)} files uploaded successfully",
        "files_info": [
            {
                "id": f"file_{i+1}",
                "filename": file.filename,
                "original_name": file.filename,
                "content_type": file.content_type,
                "size": "2.5 MB",  # Mock size
                "category": category,
                "tags": tags.split(",") if tags else [],
                "description": description,
                "uploaded_at": "2023-09-29T10:00:00",
                "url": f"/uploads/{file.filename}"
            } for i, file in enumerate(files)
        ],
        "batch_id": "batch_12345"
    }

@router.get("/status/{file_id}")
async def upload_status(file_id: str):
    """Get upload status"""
    return {
        "success": True,
        "status": {
            "file_id": file_id,
            "status": "Completed",
            "filename": "marketing_report.pdf",
            "content_type": "application/pdf",
            "size": "2.5 MB",
            "uploaded_at": "2023-09-29T10:00:00",
            "processed_at": "2023-09-29T10:01:30",
            "url": f"/uploads/{file_id}",
            "thumbnail": f"/uploads/thumbnails/{file_id}"
        }
    }

@router.get("/history")
async def upload_history():
    """Get upload history"""
    return {
        "success": True,
        "history": [
            {
                "id": "file_12345",
                "filename": "marketing_report.pdf",
                "content_type": "application/pdf",
                "size": "2.5 MB",
                "category": "Documents",
                "tags": ["marketing", "report", "q3"],
                "uploaded_at": "2023-09-29T10:00:00",
                "status": "Completed",
                "url": "/uploads/marketing_report.pdf"
            },
            {
                "id": "file_12344",
                "filename": "product_photo.jpg",
                "content_type": "image/jpeg",
                "size": "1.8 MB",
                "category": "Images",
                "tags": ["product", "hoodie", "black"],
                "uploaded_at": "2023-09-28T14:30:00",
                "status": "Completed",
                "url": "/uploads/product_photo.jpg"
            },
            {
                "id": "file_12343",
                "filename": "customer_data.xlsx",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "size": "3.2 MB",
                "category": "Data",
                "tags": ["customers", "analysis", "q3"],
                "uploaded_at": "2023-09-27T09:15:00",
                "status": "Completed",
                "url": "/uploads/customer_data.xlsx"
            },
            {
                "id": "file_12342",
                "filename": "campaign_video.mp4",
                "content_type": "video/mp4",
                "size": "85.2 MB",
                "category": "Media",
                "tags": ["campaign", "video", "fall"],
                "uploaded_at": "2023-09-26T16:45:00",
                "status": "Completed",
                "url": "/uploads/campaign_video.mp4"
            },
            {
                "id": "file_12341",
                "filename": "social_analytics.json",
                "content_type": "application/json",
                "size": "4.5 MB",
                "category": "Data",
                "tags": ["social", "analytics", "q3"],
                "uploaded_at": "2023-09-25T11:30:00",
                "status": "Completed",
                "url": "/uploads/social_analytics.json"
            }
        ],
        "total": 5,
        "completed": 5,
        "failed": 0
    }
