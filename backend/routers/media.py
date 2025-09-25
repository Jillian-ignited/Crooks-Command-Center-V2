from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid
import json
import mimetypes

router = APIRouter()

# Supported file types
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'
}
SUPPORTED_VIDEO_TYPES = {
    'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm', 'video/mkv'
}
SUPPORTED_AUDIO_TYPES = {
    'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/aac'
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def ensure_media_directories():
    """Ensure media directories exist"""
    base_dir = Path("media")
    directories = {
        "images": base_dir / "images",
        "videos": base_dir / "videos", 
        "audio": base_dir / "audio",
        "thumbnails": base_dir / "thumbnails"
    }
    
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return directories

def get_file_type(content_type: str) -> str:
    """Determine file type category"""
    if content_type in SUPPORTED_IMAGE_TYPES:
        return "image"
    elif content_type in SUPPORTED_VIDEO_TYPES:
        return "video"
    elif content_type in SUPPORTED_AUDIO_TYPES:
        return "audio"
    else:
        return "unknown"

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension"""
    file_ext = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{file_ext}"

def save_media_metadata(file_info: dict) -> None:
    """Save media metadata to JSON file"""
    metadata_file = Path("media") / "metadata.json"
    
    # Load existing metadata
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {"files": []}
    
    # Add new file info
    metadata["files"].append(file_info)
    metadata["last_updated"] = datetime.now().isoformat()
    
    # Save updated metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

@router.post("/upload")
async def upload_media(
    files: List[UploadFile] = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload multiple media files (images, videos, audio)"""
    try:
        directories = ensure_media_directories()
        uploaded_files = []
        
        for file in files:
            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File {file.filename} is too large. Maximum size is 100MB."
                )
            
            # Check file type
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            file_type = get_file_type(content_type)
            
            if file_type == "unknown":
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {content_type}"
                )
            
            # Generate unique filename
            unique_filename = generate_unique_filename(file.filename)
            
            # Determine save directory
            if file_type == "image":
                save_dir = directories["images"]
            elif file_type == "video":
                save_dir = directories["videos"]
            elif file_type == "audio":
                save_dir = directories["audio"]
            
            file_path = save_dir / unique_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Create file info
            file_info = {
                "id": str(uuid.uuid4()),
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "file_path": str(file_path),
                "file_type": file_type,
                "content_type": content_type,
                "file_size": len(file_content),
                "category": category,
                "tags": tags.split(',') if tags else [],
                "description": description,
                "uploaded_at": datetime.now().isoformat(),
                "url": f"/media/file/{unique_filename}"
            }
            
            # Save metadata
            save_media_metadata(file_info)
            uploaded_files.append(file_info)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/list")
async def list_media(
    file_type: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = None
):
    """List all uploaded media files with optional filtering"""
    try:
        metadata_file = Path("media") / "metadata.json"
        
        if not metadata_file.exists():
            return JSONResponse(content={
                "success": True,
                "files": [],
                "total": 0
            })
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        files = metadata.get("files", [])
        
        # Apply filters
        if file_type:
            files = [f for f in files if f.get("file_type") == file_type]
        
        if category:
            files = [f for f in files if f.get("category") == category]
        
        # Apply limit
        if limit:
            files = files[:limit]
        
        return JSONResponse(content={
            "success": True,
            "files": files,
            "total": len(files)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list media: {str(e)}")

@router.get("/file/{filename}")
async def get_media_file(filename: str):
    """Serve a media file"""
    try:
        # Check in all media directories
        directories = ensure_media_directories()
        
        for dir_path in directories.values():
            file_path = dir_path / filename
            if file_path.exists():
                return FileResponse(
                    path=str(file_path),
                    filename=filename,
                    media_type=mimetypes.guess_type(filename)[0]
                )
        
        raise HTTPException(status_code=404, detail="File not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}")

@router.get("/info/{filename}")
async def get_media_info(filename: str):
    """Get metadata for a specific media file"""
    try:
        metadata_file = Path("media") / "metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="No media metadata found")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        files = metadata.get("files", [])
        file_info = next((f for f in files if f.get("stored_filename") == filename), None)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File metadata not found")
        
        return JSONResponse(content={
            "success": True,
            "file_info": file_info
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

@router.delete("/file/{filename}")
async def delete_media_file(filename: str):
    """Delete a media file and its metadata"""
    try:
        # Find and delete the physical file
        directories = ensure_media_directories()
        file_deleted = False
        
        for dir_path in directories.values():
            file_path = dir_path / filename
            if file_path.exists():
                file_path.unlink()
                file_deleted = True
                break
        
        if not file_deleted:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Update metadata
        metadata_file = Path("media") / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Remove file from metadata
            metadata["files"] = [f for f in metadata.get("files", []) if f.get("stored_filename") != filename]
            metadata["last_updated"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return JSONResponse(content={
            "success": True,
            "message": f"File {filename} deleted successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/stats")
async def get_media_stats():
    """Get statistics about uploaded media"""
    try:
        metadata_file = Path("media") / "metadata.json"
        
        if not metadata_file.exists():
            return JSONResponse(content={
                "success": True,
                "stats": {
                    "total_files": 0,
                    "images": 0,
                    "videos": 0,
                    "audio": 0,
                    "total_size_mb": 0
                }
            })
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        files = metadata.get("files", [])
        
        stats = {
            "total_files": len(files),
            "images": len([f for f in files if f.get("file_type") == "image"]),
            "videos": len([f for f in files if f.get("file_type") == "video"]),
            "audio": len([f for f in files if f.get("file_type") == "audio"]),
            "total_size_bytes": sum(f.get("file_size", 0) for f in files),
        }
        
        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/bulk-delete")
async def bulk_delete_media(filenames: List[str]):
    """Delete multiple media files"""
    try:
        directories = ensure_media_directories()
        deleted_files = []
        failed_files = []
        
        for filename in filenames:
            try:
                # Find and delete the physical file
                file_deleted = False
                for dir_path in directories.values():
                    file_path = dir_path / filename
                    if file_path.exists():
                        file_path.unlink()
                        file_deleted = True
                        deleted_files.append(filename)
                        break
                
                if not file_deleted:
                    failed_files.append({"filename": filename, "error": "File not found"})
                    
            except Exception as e:
                failed_files.append({"filename": filename, "error": str(e)})
        
        # Update metadata
        if deleted_files:
            metadata_file = Path("media") / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Remove deleted files from metadata
                metadata["files"] = [f for f in metadata.get("files", []) if f.get("stored_filename") not in deleted_files]
                metadata["last_updated"] = datetime.now().isoformat()
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
        
        return JSONResponse(content={
            "success": True,
            "deleted_files": deleted_files,
            "failed_files": failed_files,
            "message": f"Successfully deleted {len(deleted_files)} files"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")
