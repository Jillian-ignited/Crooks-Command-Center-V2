import os
import json
import uuid
from datetime import datetime
from PIL import Image
import base64

UPLOAD_FOLDER = 'uploads'
THUMBNAIL_FOLDER = os.path.join('static', 'thumbnails')
ASSET_DATA_FILE = os.path.join('data', 'assets.json')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(ASSET_DATA_FILE), exist_ok=True)

def scan_assets():
    """Scan upload folder and catalog all assets with metadata"""
    assets = []
    
    if not os.path.exists(UPLOAD_FOLDER):
        return assets
    
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith('.'):
                continue
                
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            if os.path.isfile(filepath):
                asset_info = get_asset_info(filename, filepath)
                if asset_info:
                    assets.append(asset_info)
    
    except Exception as e:
        print(f"Error scanning assets: {e}")
    
    return assets

def get_asset_info(filename, filepath):
    """Get detailed asset information including metadata and thumbnails"""
    try:
        # Get file stats
        stat = os.stat(filepath)
        file_size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Determine file type and category
        file_ext = os.path.splitext(filename)[1].lower()
        file_type, category = categorize_file(file_ext)
        
        asset_info = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "filepath": filepath,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "file_type": file_type,
            "category": category,
            "extension": file_ext,
            "modified_date": modified_time.isoformat(),
            "thumbnail_path": None,
            "download_url": f"/api/assets/download/{filename}"
        }
        
        # Generate thumbnail for images
        if file_type == "image":
            thumbnail_path = generate_thumbnail(filepath, filename)
            if thumbnail_path:
                asset_info["thumbnail_path"] = thumbnail_path
        
        # Add specific metadata based on file type
        if filename.endswith('.jsonl'):
            asset_info["metadata"] = analyze_jsonl_file(filepath)
        
        return asset_info
        
    except Exception as e:
        print(f"Error getting asset info for {filename}: {e}")
        return None

def categorize_file(file_ext):
    """Categorize file based on extension"""
    image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg']
    video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']
    audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
    document_exts = ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf']
    data_exts = ['.json', '.jsonl', '.csv', '.xlsx', '.xml']
    
    if file_ext in image_exts:
        return "image", "social_content"
    elif file_ext in video_exts:
        return "video", "video_content"
    elif file_ext in audio_exts:
        return "audio", "audio_content"
    elif file_ext in document_exts:
        return "document", "documents"
    elif file_ext in data_exts:
        return "data", "intelligence_data"
    else:
        return "other", "other"

def generate_thumbnail(filepath, filename, size=(150, 150)):
    """Generate thumbnail for image files with proper RGBA handling"""
    try:
        # Create thumbnail filename
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumb.jpg"  # Always save as JPG
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)
        
        # Open and process image
        with Image.open(filepath) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            
            return f"/static/thumbnails/{thumbnail_filename}"
            
    except Exception as e:
        print(f"Error generating thumbnail for {filename}: {e}")
        return None

def analyze_jsonl_file(filepath):
    """Analyze JSONL file to extract metadata"""
    try:
        line_count = 0
        sample_data = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                if line.strip():
                    line_count += 1
                    if line_num < 3:  # Sample first 3 lines
                        try:
                            data = json.loads(line.strip())
                            sample_data.append(data)
                        except:
                            continue
        
        # Determine data type based on content
        data_type = "unknown"
        if sample_data:
            first_item = sample_data[0]
            if 'ownerUsername' in first_item or 'caption' in first_item:
                data_type = "instagram_data"
            elif 'videoMeta' in first_item or 'musicMeta' in first_item:
                data_type = "tiktok_data"
            elif 'competitive' in filepath.lower():
                data_type = "competitive_data"
        
        return {
            "record_count": line_count,
            "data_type": data_type,
            "sample_fields": list(sample_data[0].keys()) if sample_data else [],
            "analysis_ready": line_count > 0
        }
        
    except Exception as e:
        print(f"Error analyzing JSONL file {filepath}: {e}")
        return {"error": str(e)}

def add_asset(file_path, filename, category="other", metadata=None):
    """Add new asset to the system"""
    try:
        # Move file to upload folder if not already there
        target_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if file_path != target_path:
            os.rename(file_path, target_path)
        
        # Get asset info
        asset_info = get_asset_info(filename, target_path)
        if not asset_info:
            return {"success": False, "error": "Failed to process asset"}
        
        # Override category if specified
        if category != "other":
            asset_info["category"] = category
        
        # Add custom metadata
        if metadata:
            asset_info["custom_metadata"] = metadata
        
        # Save asset data
        save_asset_data(asset_info)
        
        return {"success": True, "asset": asset_info}
        
    except Exception as e:
        print(f"Error adding asset: {e}")
        return {"success": False, "error": str(e)}

def remove_asset(asset_id):
    """Remove asset from system"""
    try:
        # Load current assets
        assets = load_asset_data()
        
        # Find and remove asset
        asset_to_remove = None
        for i, asset in enumerate(assets):
            if asset.get("id") == asset_id:
                asset_to_remove = assets.pop(i)
                break
        
        if not asset_to_remove:
            return {"success": False, "error": "Asset not found"}
        
        # Remove files
        try:
            # Remove main file
            if os.path.exists(asset_to_remove["filepath"]):
                os.remove(asset_to_remove["filepath"])
            
            # Remove thumbnail
            if asset_to_remove.get("thumbnail_path"):
                thumbnail_file = asset_to_remove["thumbnail_path"].replace("/static/thumbnails/", "")
                thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_file)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
        except Exception as e:
            print(f"Error removing files: {e}")
        
        # Save updated asset data
        save_assets_data(assets)
        
        return {"success": True, "removed_asset": asset_to_remove}
        
    except Exception as e:
        print(f"Error removing asset: {e}")
        return {"success": False, "error": str(e)}

def get_assets_by_category(category=None):
    """Get assets filtered by category"""
    assets = scan_assets()
    
    if category:
        assets = [asset for asset in assets if asset.get("category") == category]
    
    # Sort by modified date (newest first)
    assets.sort(key=lambda x: x.get("modified_date", ""), reverse=True)
    
    return assets

def get_asset_categories():
    """Get all available asset categories with counts"""
    assets = scan_assets()
    categories = {}
    
    for asset in assets:
        category = asset.get("category", "other")
        if category not in categories:
            categories[category] = {"count": 0, "size_mb": 0}
        
        categories[category]["count"] += 1
        categories[category]["size_mb"] += asset.get("file_size_mb", 0)
    
    # Round sizes
    for category in categories:
        categories[category]["size_mb"] = round(categories[category]["size_mb"], 2)
    
    return categories

def search_assets(query, category=None):
    """Search assets by filename or metadata"""
    assets = get_assets_by_category(category)
    
    if not query:
        return assets
    
    query_lower = query.lower()
    filtered_assets = []
    
    for asset in assets:
        # Search in filename
        if query_lower in asset.get("filename", "").lower():
            filtered_assets.append(asset)
            continue
        
        # Search in metadata
        metadata = asset.get("metadata", {})
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if query_lower in str(value).lower():
                    filtered_assets.append(asset)
                    break
    
    return filtered_assets

def save_asset_data(asset_info):
    """Save individual asset data"""
    try:
        assets = load_asset_data()
        
        # Update existing or add new
        updated = False
        for i, existing_asset in enumerate(assets):
            if existing_asset.get("filename") == asset_info.get("filename"):
                assets[i] = asset_info
                updated = True
                break
        
        if not updated:
            assets.append(asset_info)
        
        save_assets_data(assets)
        return True
        
    except Exception as e:
        print(f"Error saving asset data: {e}")
        return False

def load_asset_data():
    """Load asset data from file"""
    try:
        if os.path.exists(ASSET_DATA_FILE):
            with open(ASSET_DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading asset data: {e}")
        return []

def save_assets_data(assets):
    """Save all assets data to file"""
    try:
        with open(ASSET_DATA_FILE, 'w') as f:
            json.dump(assets, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving assets data: {e}")
        return False

def get_asset_stats():
    """Get asset statistics"""
    assets = scan_assets()
    categories = get_asset_categories()
    
    total_size = sum(asset.get("file_size_mb", 0) for asset in assets)
    
    return {
        "total_assets": len(assets),
        "total_size_mb": round(total_size, 2),
        "categories": categories,
        "recent_uploads": assets[:5] if assets else []
    }
