# /backend/routers/media.py - CRITICAL MEDIA MANAGEMENT - ASSET PROCESSING & STORAGE

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, Dict, Any, List
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid
import mimetypes
from PIL import Image, ImageOps
import io
import base64
from collections import defaultdict

router = APIRouter()

# Media directories
MEDIA_BASE_DIR = Path("data/media")
UPLOADS_DIR = MEDIA_BASE_DIR / "uploads"
PROCESSED_DIR = MEDIA_BASE_DIR / "processed"
THUMBNAILS_DIR = MEDIA_BASE_DIR / "thumbnails"
ASSETS_DIR = MEDIA_BASE_DIR / "assets"

# Create all media directories
for dir_path in [MEDIA_BASE_DIR, UPLOADS_DIR, PROCESSED_DIR, THUMBNAILS_DIR, ASSETS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Supported file types
SUPPORTED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
SUPPORTED_VIDEO_TYPES = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
SUPPORTED_AUDIO_TYPES = {'.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a'}
SUPPORTED_DOCUMENT_TYPES = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.csv', '.xlsx'}

ALL_SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | SUPPORTED_VIDEO_TYPES | SUPPORTED_AUDIO_TYPES | SUPPORTED_DOCUMENT_TYPES

# Media metadata storage
METADATA_FILE = MEDIA_BASE_DIR / "metadata.json"

def load_metadata() -> Dict[str, Any]:
    """Load media metadata from JSON file"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_metadata(metadata: Dict[str, Any]):
    """Save media metadata to JSON file"""
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving metadata: {e}")

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}_{unique_id}{ext}"

def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get comprehensive file information"""
    try:
        stats = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        file_info = {
            "filename": file_path.name,
            "size": stats.st_size,
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "mime_type": mime_type or "unknown",
            "extension": file_path.suffix.lower(),
            "path": str(file_path.relative_to(MEDIA_BASE_DIR))
        }
        
        # Add type-specific info
        if file_path.suffix.lower() in SUPPORTED_IMAGE_TYPES:
            try:
                with Image.open(file_path) as img:
                    file_info.update({
                        "type": "image",
                        "dimensions": {"width": img.width, "height": img.height},
                        "format": img.format,
                        "mode": img.mode
                    })
            except:
                file_info["type"] = "image"
                
        elif file_path.suffix.lower() in SUPPORTED_VIDEO_TYPES:
            file_info["type"] = "video"
            
        elif file_path.suffix.lower() in SUPPORTED_AUDIO_TYPES:
            file_info["type"] = "audio"
            
        elif file_path.suffix.lower() in SUPPORTED_DOCUMENT_TYPES:
            file_info["type"] = "document"
            
        else:
            file_info["type"] = "other"
        
        return file_info
        
    except Exception as e:
        return {"error": f"Failed to get file info: {str(e)}"}

def create_thumbnail(image_path: Path, thumbnail_size: tuple = (300, 300)) -> Optional[Path]:
    """Create thumbnail for image files"""
    try:
        thumbnail_path = THUMBNAILS_DIR / f"thumb_{image_path.stem}.jpg"
        
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            
        return thumbnail_path
        
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")
        return None

def process_image(image_path: Path, operations: Dict[str, Any]) -> Optional[Path]:
    """Process image with various operations"""
    try:
        processed_path = PROCESSED_DIR / f"processed_{image_path.name}"
        
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Apply operations
            if operations.get('resize'):
                size = operations['resize']
                img = img.resize((size['width'], size['height']), Image.Resampling.LANCZOS)
            
            if operations.get('crop'):
                crop = operations['crop']
                img = img.crop((crop['x'], crop['y'], crop['x'] + crop['width'], crop['y'] + crop['height']))
            
            if operations.get('rotate'):
                img = img.rotate(operations['rotate'], expand=True)
            
            if operations.get('flip_horizontal'):
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            
            if operations.get('flip_vertical'):
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
            if operations.get('grayscale'):
                img = img.convert('L').convert('RGB')
            
            if operations.get('optimize'):
                img = ImageOps.exif_transpose(img)  # Auto-orient based on EXIF
            
            # Save processed image
            quality = operations.get('quality', 85)
            img.save(processed_path, "JPEG", quality=quality, optimize=True)
            
        return processed_path
        
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

@router.post("/upload")
async def upload_media(
    files: List[UploadFile] = File(...),
    category: str = Form(default="general"),
    tags: str = Form(default=""),
    description: str = Form(default="")
):
    """Upload multiple media files with metadata"""
    
    uploaded_files = []
    metadata = load_metadata()
    
    for file in files:
        try:
            # Validate file type
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALL_SUPPORTED_TYPES:
                uploaded_files.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": f"Unsupported file type: {file_ext}"
                })
                continue
            
            # Generate unique filename
            unique_filename = generate_unique_filename(file.filename)
            file_path = UPLOADS_DIR / unique_filename
            
            # Save file
            with open(file_path, 'wb') as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Get file info
            file_info = get_file_info(file_path)
            
            # Create thumbnail for images
            thumbnail_path = None
            if file_ext in SUPPORTED_IMAGE_TYPES:
                thumbnail_path = create_thumbnail(file_path)
            
            # Store metadata
            file_id = str(uuid.uuid4())
            metadata[file_id] = {
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "file_info": file_info,
                "category": category,
                "tags": [tag.strip() for tag in tags.split(',') if tag.strip()],
                "description": description,
                "uploaded_at": datetime.now().isoformat(),
                "thumbnail_path": str(thumbnail_path.relative_to(MEDIA_BASE_DIR)) if thumbnail_path else None,
                "processed_versions": []
            }
            
            uploaded_files.append({
                "file_id": file_id,
                "filename": file.filename,
                "stored_as": unique_filename,
                "status": "success",
                "size": file_info.get("size_mb", 0),
                "type": file_info.get("type", "unknown"),
                "thumbnail_created": thumbnail_path is not None
            })
            
        except Exception as e:
            uploaded_files.append({
                "filename": file.filename,
                "status": "error", 
                "message": str(e)
            })
    
    # Save updated metadata
    save_metadata(metadata)
    
    return {
        "success": True,
        "message": f"Processed {len(files)} files",
        "results": uploaded_files,
        "summary": {
            "successful": len([f for f in uploaded_files if f.get("status") == "success"]),
            "failed": len([f for f in uploaded_files if f.get("status") == "error"])
        }
    }

@router.get("/list")
async def list_media(
    category: Optional[str] = Query(default=None),
    file_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50),
    offset: int = Query(default=0)
):
    """List media files with filtering and pagination"""
    
    metadata = load_metadata()
    
    # Filter files
    filtered_files = []
    for file_id, file_meta in metadata.items():
        # Apply category filter
        if category and file_meta.get("category") != category:
            continue
        
        # Apply type filter
        if file_type and file_meta.get("file_info", {}).get("type") != file_type:
            continue
        
        file_meta["file_id"] = file_id
        filtered_files.append(file_meta)
    
    # Sort by upload date (newest first)
    filtered_files.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    
    # Apply pagination
    total_count = len(filtered_files)
    paginated_files = filtered_files[offset:offset + limit]
    
    return {
        "success": True,
        "files": paginated_files,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        },
        "filters": {
            "category": category,
            "file_type": file_type
        }
    }

@router.get("/download/{file_id}")
async def download_media(file_id: str):
    """Download media file by ID"""
    
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_meta = metadata[file_id]
    file_path = UPLOADS_DIR / file_meta["stored_filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=file_meta["original_filename"],
        media_type=file_meta["file_info"].get("mime_type", "application/octet-stream")
    )

@router.get("/thumbnail/{file_id}")
async def get_thumbnail(file_id: str):
    """Get thumbnail for media file"""
    
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_meta = metadata[file_id]
    thumbnail_rel_path = file_meta.get("thumbnail_path")
    
    if not thumbnail_rel_path:
        raise HTTPException(status_code=404, detail="Thumbnail not available")
    
    thumbnail_path = MEDIA_BASE_DIR / thumbnail_rel_path
    
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    return FileResponse(
        path=str(thumbnail_path),
        media_type="image/jpeg"
    )

@router.post("/process/{file_id}")
async def process_media(
    file_id: str,
    operations: Dict[str, Any]
):
    """Process media file with specified operations"""
    
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_meta = metadata[file_id]
    original_path = UPLOADS_DIR / file_meta["stored_filename"]
    
    if not original_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found")
    
    # Currently only support image processing
    if file_meta["file_info"].get("type") != "image":
        raise HTTPException(status_code=400, detail="Processing only supported for images")
    
    try:
        processed_path = process_image(original_path, operations)
        
        if not processed_path:
            raise HTTPException(status_code=500, detail="Image processing failed")
        
        # Update metadata with processed version
        processed_info = get_file_info(processed_path)
        processed_version = {
            "filename": processed_path.name,
            "operations": operations,
            "created_at": datetime.now().isoformat(),
            "file_info": processed_info
        }
        
        file_meta["processed_versions"].append(processed_version)
        metadata[file_id] = file_meta
        save_metadata(metadata)
        
        return {
            "success": True,
            "message": "Image processed successfully",
            "processed_version": processed_version,
            "download_url": f"/media/processed/{processed_path.name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/processed/{filename}")
async def download_processed(filename: str):
    """Download processed media file"""
    
    file_path = PROCESSED_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Processed file not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="image/jpeg"
    )

@router.delete("/delete/{file_id}")
async def delete_media(file_id: str):
    """Delete media file and all associated files"""
    
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_meta = metadata[file_id]
    
    try:
        # Delete original file
        original_path = UPLOADS_DIR / file_meta["stored_filename"]
        if original_path.exists():
            original_path.unlink()
        
        # Delete thumbnail
        thumbnail_rel_path = file_meta.get("thumbnail_path")
        if thumbnail_rel_path:
            thumbnail_path = MEDIA_BASE_DIR / thumbnail_rel_path
            if thumbnail_path.exists():
                thumbnail_path.unlink()
        
        # Delete processed versions
        for version in file_meta.get("processed_versions", []):
            processed_path = PROCESSED_DIR / version["filename"]
            if processed_path.exists():
                processed_path.unlink()
        
        # Remove from metadata
        del metadata[file_id]
        save_metadata(metadata)
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "file_id": file_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/analytics")
async def get_media_analytics():
    """Get media analytics and statistics"""
    
    metadata = load_metadata()
    
    # File type distribution
    type_counts = defaultdict(int)
    category_counts = defaultdict(int)
    total_size = 0
    upload_dates = []
    
    for file_meta in metadata.values():
        file_info = file_meta.get("file_info", {})
        file_type = file_info.get("type", "unknown")
        category = file_meta.get("category", "general")
        size = file_info.get("size", 0)
        uploaded_at = file_meta.get("uploaded_at")
        
        type_counts[file_type] += 1
        category_counts[category] += 1
        total_size += size
        
        if uploaded_at:
            upload_dates.append(uploaded_at)
    
    # Recent uploads (last 7 days)
    recent_cutoff = datetime.now() - datetime.timedelta(days=7)
    recent_uploads = sum(1 for date_str in upload_dates 
                        if datetime.fromisoformat(date_str.replace('Z', '+00:00')) > recent_cutoff)
    
    return {
        "success": True,
        "analytics": {
            "total_files": len(metadata),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": dict(type_counts),
            "categories": dict(category_counts),
            "recent_uploads_7_days": recent_uploads,
            "storage_locations": {
                "uploads": len(list(UPLOADS_DIR.glob("*"))),
                "thumbnails": len(list(THUMBNAILS_DIR.glob("*"))),
                "processed": len(list(PROCESSED_DIR.glob("*")))
            }
        }
    }

@router.get("/status")
async def get_media_status():
    """Get media management system status"""
    
    return {
        "status": "operational",
        "directories": {
            "uploads": str(UPLOADS_DIR),
            "processed": str(PROCESSED_DIR),
            "thumbnails": str(THUMBNAILS_DIR),
            "assets": str(ASSETS_DIR)
        },
        "supported_formats": {
            "images": list(SUPPORTED_IMAGE_TYPES),
            "videos": list(SUPPORTED_VIDEO_TYPES),
            "audio": list(SUPPORTED_AUDIO_TYPES),
            "documents": list(SUPPORTED_DOCUMENT_TYPES)
        },
        "features": [
            "Multi-file upload",
            "Automatic thumbnail generation",
            "Image processing (resize, crop, rotate)",
            "Metadata management",
            "Category and tag organization",
            "Analytics and reporting"
        ],
        "endpoints": {
            "upload": "/media/upload",
            "list": "/media/list",
            "download": "/media/download/{file_id}",
            "thumbnail": "/media/thumbnail/{file_id}",
            "process": "/media/process/{file_id}",
            "delete": "/media/delete/{file_id}",
            "analytics": "/media/analytics"
        }
    }
