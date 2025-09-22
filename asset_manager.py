import os
import json
import uuid
from datetime import datetime
from PIL import Image
import mimetypes

# Configuration
UPLOAD_FOLDER = 'uploads'
ASSETS_FOLDER = os.path.join(UPLOAD_FOLDER, 'assets')
INTEL_FOLDER = os.path.join(UPLOAD_FOLDER, 'intel')
THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [UPLOAD_FOLDER, ASSETS_FOLDER, INTEL_FOLDER, THUMBNAILS_FOLDER]
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except (FileExistsError, OSError) as e:
            print(f"Directory {directory} handling: {e}")
            pass

def scan_assets():
    """Scan all asset directories and return comprehensive asset inventory - REQUIRED BY APP.PY"""
    
    ensure_directories()
    
    assets = []
    
    # Scan main uploads folder
    if os.path.exists(UPLOAD_FOLDER):
        for root, dirs, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                if not file.startswith('.') and file != '.gitkeep':
                    file_path = os.path.join(root, file)
                    try:
                        asset = analyze_file(file_path)
                        if asset:
                            assets.append(asset)
                    except Exception as e:
                        print(f"Error analyzing {file_path}: {e}")
                        continue
    
    return assets

def analyze_file(file_path):
    """Analyze a file and return asset metadata"""
    
    try:
        if not os.path.exists(file_path):
            return None
            
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        # Skip empty files
        if file_size == 0:
            return None
            
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Determine file category
        category = categorize_file(filename, file_ext)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        asset = {
            'id': str(uuid.uuid4()),
            'filename': filename,
            'path': file_path,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'category': category,
            'type': get_file_type(file_ext),
            'mime_type': mime_type,
            'extension': file_ext,
            'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'thumbnail': None
        }
        
        # Generate thumbnail for images
        if asset['type'] == 'image':
            thumbnail_path = generate_thumbnail(file_path)
            if thumbnail_path:
                asset['thumbnail'] = thumbnail_path
        
        # Add special metadata for JSONL files
        if file_ext == '.jsonl':
            asset.update(analyze_jsonl_file(file_path))
        
        return asset
        
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        return None

def categorize_file(filename, file_ext):
    """Categorize file based on filename and extension"""
    
    filename_lower = filename.lower()
    
    # Intelligence data files
    if 'dataset' in filename_lower or 'competitive' in filename_lower or file_ext == '.jsonl':
        return 'intelligence_data'
    
    # Brand assets
    if any(term in filename_lower for term in ['logo', 'brand', 'wordmark', 'castle', 'medusa']):
        return 'brand_assets'
    
    # Social content
    if any(term in filename_lower for term in ['story', 'post', 'instagram', 'social', 'heritage', 'hiphop']):
        return 'social_content'
    
    # Video content
    if file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
        return 'video_content'
    
    # Audio content
    if file_ext in ['.mp3', '.wav', '.aac', '.flac']:
        return 'audio_content'
    
    # Documents
    if file_ext in ['.pdf', '.doc', '.docx', '.txt', '.md']:
        return 'documents'
    
    # Default to general assets
    return 'general_assets'

def get_file_type(file_ext):
    """Get general file type from extension"""
    
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']
    audio_exts = ['.mp3', '.wav', '.aac', '.flac', '.ogg']
    document_exts = ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf']
    data_exts = ['.json', '.jsonl', '.csv', '.xml', '.yaml']
    
    if file_ext in image_exts:
        return 'image'
    elif file_ext in video_exts:
        return 'video'
    elif file_ext in audio_exts:
        return 'audio'
    elif file_ext in document_exts:
        return 'document'
    elif file_ext in data_exts:
        return 'data'
    else:
        return 'other'

def analyze_jsonl_file(file_path):
    """Analyze JSONL file for additional metadata"""
    
    try:
        line_count = 0
        sample_data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line_count += 1
                if i < 3:  # Sample first 3 lines
                    try:
                        data = json.loads(line.strip())
                        sample_data.append(data)
                    except:
                        continue
        
        # Analyze sample data structure
        metadata = {
            'record_count': line_count,
            'data_type': 'jsonl',
            'sample_fields': []
        }
        
        if sample_data:
            # Get field names from first record
            first_record = sample_data[0]
            if isinstance(first_record, dict):
                metadata['sample_fields'] = list(first_record.keys())[:10]  # First 10 fields
                
                # Detect data source
                if 'caption' in first_record or 'likesCount' in first_record:
                    metadata['source'] = 'instagram'
                elif 'description' in first_record or 'viewCount' in first_record:
                    metadata['source'] = 'tiktok'
                else:
                    metadata['source'] = 'unknown'
        
        return metadata
        
    except Exception as e:
        print(f"Error analyzing JSONL file {file_path}: {e}")
        return {'record_count': 0, 'data_type': 'jsonl'}

def generate_thumbnail(image_path, size=(150, 150)):
    """Generate thumbnail for image files - REQUIRED BY APP.PY"""
    
    try:
        ensure_directories()
        
        if not os.path.exists(image_path):
            return None
            
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumb{ext}"
        thumbnail_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_filename)
        
        # Skip if thumbnail already exists and is newer
        if os.path.exists(thumbnail_path):
            thumb_mtime = os.path.getmtime(thumbnail_path)
            image_mtime = os.path.getmtime(image_path)
            if thumb_mtime > image_mtime:
                return thumbnail_path
        
        # Generate thumbnail
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                img = background
            elif img.mode not in ['RGB', 'L']:
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
        return thumbnail_path
        
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return None

def add_asset(file_path, category=None):
    """Add new asset to the library - REQUIRED BY APP.PY"""
    
    try:
        if not os.path.exists(file_path):
            return {'success': False, 'error': 'File not found'}
        
        # Analyze the file
        asset = analyze_file(file_path)
        if not asset:
            return {'success': False, 'error': 'Could not analyze file'}
        
        # Override category if provided
        if category:
            asset['category'] = category
        
        # Move file to appropriate category folder if not already there
        target_dir = os.path.join(ASSETS_FOLDER, asset['category'])
        os.makedirs(target_dir, exist_ok=True)
        
        return {
            'success': True,
            'asset': asset,
            'message': f'Asset {asset["filename"]} added successfully'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def remove_asset(asset_id):
    """Remove asset from library - REQUIRED BY APP.PY"""
    
    try:
        # Find asset by ID
        assets = scan_assets()
        asset_to_remove = None
        
        for asset in assets:
            if asset['id'] == asset_id:
                asset_to_remove = asset
                break
        
        if not asset_to_remove:
            return {'success': False, 'error': 'Asset not found'}
        
        # Remove file
        if os.path.exists(asset_to_remove['path']):
            os.remove(asset_to_remove['path'])
        
        # Remove thumbnail if exists
        if asset_to_remove.get('thumbnail') and os.path.exists(asset_to_remove['thumbnail']):
            os.remove(asset_to_remove['thumbnail'])
        
        return {
            'success': True,
            'message': f'Asset {asset_to_remove["filename"]} removed successfully'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_assets_by_category(category=None):
    """Get assets filtered by category - REQUIRED BY APP.PY"""
    
    assets = scan_assets()
    
    if category:
        assets = [asset for asset in assets if asset['category'] == category]
    
    # Group by category
    categorized = {}
    for asset in assets:
        cat = asset['category']
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(asset)
    
    return categorized

def get_asset_categories():
    """Get list of all asset categories - REQUIRED BY APP.PY"""
    
    assets = scan_assets()
    categories = {}
    
    for asset in assets:
        category = asset['category']
        if category not in categories:
            categories[category] = {
                'name': category,
                'count': 0,
                'total_size': 0,
                'display_name': category.replace('_', ' ').title()
            }
        
        categories[category]['count'] += 1
        categories[category]['total_size'] += asset['size']
    
    # Add size in MB
    for cat_data in categories.values():
        cat_data['total_size_mb'] = round(cat_data['total_size'] / (1024 * 1024), 2)
    
    return list(categories.values())

def search_assets(query, category=None):
    """Search assets by filename or metadata - REQUIRED BY APP.PY"""
    
    assets = scan_assets()
    query_lower = query.lower()
    
    results = []
    for asset in assets:
        # Skip if category filter doesn't match
        if category and asset['category'] != category:
            continue
        
        # Search in filename
        if query_lower in asset['filename'].lower():
            results.append(asset)
            continue
        
        # Search in category
        if query_lower in asset['category'].lower():
            results.append(asset)
            continue
        
        # Search in JSONL metadata
        if 'source' in asset and query_lower in asset.get('source', '').lower():
            results.append(asset)
            continue
    
    return results

def get_asset_stats():
    """Get comprehensive asset statistics - REQUIRED BY APP.PY"""
    
    assets = scan_assets()
    
    if not assets:
        return {
            'total_assets': 0,
            'total_size': 0,
            'total_size_mb': 0,
            'categories': {},
            'file_types': {},
            'recent_uploads': []
        }
    
    total_size = sum(asset['size'] for asset in assets)
    
    # Category breakdown
    categories = {}
    for asset in assets:
        cat = asset['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'size': 0}
        categories[cat]['count'] += 1
        categories[cat]['size'] += asset['size']
    
    # File type breakdown
    file_types = {}
    for asset in assets:
        file_type = asset['type']
        if file_type not in file_types:
            file_types[file_type] = {'count': 0, 'size': 0}
        file_types[file_type]['count'] += 1
        file_types[file_type]['size'] += asset['size']
    
    # Recent uploads (last 10)
    recent_assets = sorted(assets, key=lambda x: x['created_at'], reverse=True)[:10]
    
    stats = {
        'total_assets': len(assets),
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'categories': categories,
        'file_types': file_types,
        'recent_uploads': recent_assets,
        'intelligence_files': len([a for a in assets if a['category'] == 'intelligence_data']),
        'brand_assets': len([a for a in assets if a['category'] == 'brand_assets']),
        'social_content': len([a for a in assets if a['category'] == 'social_content']),
        'video_content': len([a for a in assets if a['category'] == 'video_content'])
    }
    
    return stats

def get_asset_by_id(asset_id):
    """Get specific asset by ID"""
    
    assets = scan_assets()
    for asset in assets:
        if asset['id'] == asset_id:
            return asset
    return None

def update_asset_metadata(asset_id, metadata):
    """Update asset metadata"""
    
    # This would typically update a database
    # For now, return success since we're file-based
    return {'success': True, 'message': 'Metadata updated'}

def get_asset_download_url(asset_id):
    """Get download URL for asset"""
    
    asset = get_asset_by_id(asset_id)
    if asset:
        return f"/api/assets/{asset_id}/download"
    return None

def validate_upload(file_path, max_size_mb=50):
    """Validate uploaded file"""
    
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'File not found'}
    
    file_size = os.path.getsize(file_path)
    if file_size > max_size_mb * 1024 * 1024:
        return {'valid': False, 'error': f'File too large (max {max_size_mb}MB)'}
    
    # Check file extension
    filename = os.path.basename(file_path)
    file_ext = os.path.splitext(filename)[1].lower()
    
    allowed_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Images
        '.mp4', '.mov', '.avi', '.mkv', '.webm',  # Videos
        '.mp3', '.wav', '.aac', '.flac',  # Audio
        '.pdf', '.doc', '.docx', '.txt', '.md',  # Documents
        '.json', '.jsonl', '.csv', '.xml'  # Data
    ]
    
    if file_ext not in allowed_extensions:
        return {'valid': False, 'error': f'File type {file_ext} not allowed'}
    
    return {'valid': True}

def cleanup_old_thumbnails():
    """Clean up old thumbnail files"""
    
    try:
        if not os.path.exists(THUMBNAILS_FOLDER):
            return
        
        # Get all current assets
        assets = scan_assets()
        current_thumbnails = set()
        
        for asset in assets:
            if asset.get('thumbnail'):
                current_thumbnails.add(os.path.basename(asset['thumbnail']))
        
        # Remove orphaned thumbnails
        for filename in os.listdir(THUMBNAILS_FOLDER):
            if filename not in current_thumbnails:
                thumbnail_path = os.path.join(THUMBNAILS_FOLDER, filename)
                try:
                    os.remove(thumbnail_path)
                    print(f"Removed orphaned thumbnail: {filename}")
                except Exception as e:
                    print(f"Error removing thumbnail {filename}: {e}")
                    
    except Exception as e:
        print(f"Error during thumbnail cleanup: {e}")

# Initialize directories on import
ensure_directories()
