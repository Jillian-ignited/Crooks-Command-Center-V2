from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import mimetypes
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
from pathlib import Path

router = APIRouter()

# Media storage paths
MEDIA_DIR = "data/media"
IMAGES_DIR = os.path.join(MEDIA_DIR, "images")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "videos")
AUDIO_DIR = os.path.join(MEDIA_DIR, "audio")
DOCUMENTS_DIR = os.path.join(MEDIA_DIR, "documents")
MEDIA_INDEX_FILE = os.path.join(MEDIA_DIR, "media_index.json")

# Supported file types
SUPPORTED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
SUPPORTED_VIDEO_TYPES = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
SUPPORTED_AUDIO_TYPES = {'.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a'}
SUPPORTED_DOCUMENT_TYPES = {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'}

def ensure_media_directories():
    """Ensure all media directories exist"""
    directories = [MEDIA_DIR, IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, DOCUMENTS_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_file_category(filename: str) -> str:
    """Determine file category based on extension"""
    ext = Path(filename).suffix.lower()
    
    if ext in SUPPORTED_IMAGE_TYPES:
        return "image"
    elif ext in SUPPORTED_VIDEO_TYPES:
        return "video"
    elif ext in SUPPORTED_AUDIO_TYPES:
        return "audio"
    elif ext in SUPPORTED_DOCUMENT_TYPES:
        return "document"
    else:
        return "other"

def get_storage_directory(category: str) -> str:
    """Get storage directory for file category"""
    directories = {
        "image": IMAGES_DIR,
        "video": VIDEOS_DIR,
        "audio": AUDIO_DIR,
        "document": DOCUMENTS_DIR,
        "other": MEDIA_DIR
    }
    return directories.get(category, MEDIA_DIR)

def load_media_index() -> List[Dict]:
    """Load media index from file"""
    try:
        if os.path.exists(MEDIA_INDEX_FILE):
            with open(MEDIA_INDEX_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading media index: {e}")
    return []

def save_media_index(media_list: List[Dict]):
    """Save media index to file"""
    try:
        ensure_media_directories()
        with open(MEDIA_INDEX_FILE, 'w') as f:
            json.dump(media_list, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving media index: {e}")

def add_to_media_index(media_info: Dict):
    """Add media file to index"""
    media_list = load_media_index()
    media_list.append(media_info)
    save_media_index(media_list)

def remove_from_media_index(file_id: str):
    """Remove media file from index"""
    media_list = load_media_index()
    media_list = [item for item in media_list if item.get('file_id') != file_id]
    save_media_index(media_list)

def get_file_metadata(file_path: str, original_filename: str) -> Dict[str, Any]:
    """Extract basic file metadata"""
    try:
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        metadata = {
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "mime_type": mime_type,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        
        # Add category-specific metadata
        category = get_file_category(original_filename)
        
        if category == "image":
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode
                    })
            except Exception:
                pass
        
        elif category == "video":
            # Basic video metadata (could be enhanced with ffprobe)
            metadata.update({
                "duration": "Unknown",
                "resolution": "Unknown",
                "codec": "Unknown"
            })
        
        return metadata
        
    except Exception as e:
        return {
            "size": 0,
            "size_mb": 0,
            "mime_type": "unknown",
            "error": str(e)
        }

@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...), 
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Upload media file (image, video, audio, document)"""
    try:
        ensure_media_directories()
        
        # Validate file type
        category = get_file_category(file.filename)
        if category == "other":
            return JSONResponse(content={
                "success": False,
                "message": f"Unsupported file type: {Path(file.filename).suffix}"
            }, status_code=400)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        stored_filename = f"{timestamp}_{file_id}{file_extension}"
        
        # Determine storage directory
        storage_dir = get_storage_directory(category)
        file_path = os.path.join(storage_dir, stored_filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Extract metadata
        metadata = get_file_metadata(file_path, file.filename)
        
        # Create media info
        media_info = {
            "file_id": file_id,
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "title": title or file.filename,
            "description": description or "",
            "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
            "category": category,
            "file_path": file_path,
            "relative_path": os.path.relpath(file_path, MEDIA_DIR),
            "uploaded_at": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Add to index
        add_to_media_index(media_info)
        
        return JSONResponse(content={
            "success": True,
            "message": f"{category.title()} uploaded successfully",
            "file_id": file_id,
            "filename": stored_filename,
            "category": category,
            "size_mb": metadata.get("size_mb", 0),
            "media_info": media_info
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Upload failed: {str(e)}"
        }, status_code=500)

@router.get("/library")
async def get_media_library(category: Optional[str] = None):
    """Get media library with optional category filter"""
    try:
        media_list = load_media_index()
        
        # Filter by category if specified
        if category:
            media_list = [item for item in media_list if item.get("category") == category]
        
        # Sort by upload date (newest first)
        media_list = sorted(media_list, key=lambda x: x.get("uploaded_at", ""), reverse=True)
        
        # Calculate summary stats
        stats = {
            "total_files": len(media_list),
            "categories": {},
            "total_size_mb": 0
        }
        
        for item in media_list:
            cat = item.get("category", "other")
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
            stats["total_size_mb"] += item.get("metadata", {}).get("size_mb", 0)
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        return JSONResponse(content={
            "success": True,
            "media_library": media_list,
            "stats": stats
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Error loading media library: {str(e)}",
            "media_library": [],
            "stats": {}
        }, status_code=500)

@router.get("/download/{file_id}")
async def download_media(file_id: str):
    """Download media file by ID"""
    try:
        media_list = load_media_index()
        media_item = next((item for item in media_list if item["file_id"] == file_id), None)
        
        if not media_item:
            raise HTTPException(status_code=404, detail="Media file not found")
        
        file_path = media_item["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Physical file not found")
        
        return FileResponse(
            path=file_path,
            filename=media_item["original_filename"],
            media_type=media_item.get("metadata", {}).get("mime_type", "application/octet-stream")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.delete("/delete/{file_id}")
async def delete_media(file_id: str):
    """Delete media file by ID"""
    try:
        media_list = load_media_index()
        media_item = next((item for item in media_list if item["file_id"] == file_id), None)
        
        if not media_item:
            return JSONResponse(content={
                "success": False,
                "message": "Media file not found"
            }, status_code=404)
        
        # Delete physical file
        file_path = media_item["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from index
        remove_from_media_index(file_id)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Media file '{media_item['original_filename']}' deleted successfully"
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Delete failed: {str(e)}"
        }, status_code=500)

@router.put("/update/{file_id}")
async def update_media_info(
    file_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Update media file information"""
    try:
        media_list = load_media_index()
        media_item = next((item for item in media_list if item["file_id"] == file_id), None)
        
        if not media_item:
            return JSONResponse(content={
                "success": False,
                "message": "Media file not found"
            }, status_code=404)
        
        # Update fields
        if title is not None:
            media_item["title"] = title
        if description is not None:
            media_item["description"] = description
        if tags is not None:
            media_item["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        media_item["updated_at"] = datetime.now().isoformat()
        
        # Save updated index
        save_media_index(media_list)
        
        return JSONResponse(content={
            "success": True,
            "message": "Media information updated successfully",
            "media_info": media_item
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Update failed: {str(e)}"
        }, status_code=500)

@router.get("/categories")
async def get_media_categories():
    """Get available media categories with counts"""
    try:
        media_list = load_media_index()
        
        categories = {}
        for item in media_list:
            cat = item.get("category", "other")
            if cat not in categories:
                categories[cat] = {
                    "count": 0,
                    "total_size_mb": 0,
                    "supported_types": []
                }
            categories[cat]["count"] += 1
            categories[cat]["total_size_mb"] += item.get("metadata", {}).get("size_mb", 0)
        
        # Add supported file types
        type_mapping = {
            "image": list(SUPPORTED_IMAGE_TYPES),
            "video": list(SUPPORTED_VIDEO_TYPES),
            "audio": list(SUPPORTED_AUDIO_TYPES),
            "document": list(SUPPORTED_DOCUMENT_TYPES)
        }
        
        for cat in categories:
            categories[cat]["supported_types"] = type_mapping.get(cat, [])
            categories[cat]["total_size_mb"] = round(categories[cat]["total_size_mb"], 2)
        
        return JSONResponse(content={
            "success": True,
            "categories": categories
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Error loading categories: {str(e)}",
            "categories": {}
        }, status_code=500)

@router.get("/health")
async def media_health_check():
    """Health check for media service"""
    try:
        ensure_media_directories()
        
        # Count files in each directory
        stats = {}
        for category, directory in [
            ("images", IMAGES_DIR),
            ("videos", VIDEOS_DIR),
            ("audio", AUDIO_DIR),
            ("documents", DOCUMENTS_DIR)
        ]:
            if os.path.exists(directory):
                file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
                stats[category] = file_count
            else:
                stats[category] = 0
        
        # Check index file
        index_exists = os.path.exists(MEDIA_INDEX_FILE)
        indexed_files = len(load_media_index()) if index_exists else 0
        
        return JSONResponse(content={
            "status": "healthy",
            "media_directory": MEDIA_DIR,
            "directories_created": True,
            "index_file_exists": index_exists,
            "indexed_files": indexed_files,
            "file_counts": stats,
            "supported_types": {
                "images": list(SUPPORTED_IMAGE_TYPES),
                "videos": list(SUPPORTED_VIDEO_TYPES),
                "audio": list(SUPPORTED_AUDIO_TYPES),
                "documents": list(SUPPORTED_DOCUMENT_TYPES)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)
