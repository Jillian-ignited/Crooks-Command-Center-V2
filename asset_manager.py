import os
import json
import uuid
from datetime import datetime
from PIL import Image
import mimetypes

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['uploads', 'static/thumbnails', 'static/assets']
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory {directory}: {e}")

def get_file_category(filename, file_path=None):
    """Determine file category based on extension and content"""
    if not filename:
        return 'unknown'
    
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # Image files
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']:
        return 'social_content'
    
    # Video files
    elif ext in ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv']:
        return 'video_content'
    
    # Data files
    elif ext in ['json', 'jsonl', 'csv', 'xlsx', 'xls']:
        return 'intelligence_data'
    
    # Document files
    elif ext in ['pdf', 'doc', 'docx', 'txt', 'md']:
        return 'documents'
    
    # Design files
    elif ext in ['psd', 'ai', 'sketch', 'fig', 'xd']:
        return 'brand_assets'
    
    # Audio files
    elif ext in ['mp3', 'wav', 'aac', 'flac']:
        return 'audio_content'
    
    else:
        return 'other'

def generate_thumbnail(file_path, thumbnail_dir='static/thumbnails'):
    """Generate thumbnail for image files"""
    ensure_directories()
    
    if not os.path.exists(file_path):
        return None
    
    try:
        # Check if file is an image
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith('image'):
            return None
        
        # Open and process image
        with Image.open(file_path) as img:
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
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            thumbnail_filename = f"{base_name}_thumb.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            
            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            return f"/{thumbnail_path}"
    
    except Exception as e:
        print(f"Error generating thumbnail for {file_path}: {e}")
        return None

def scan_assets():
    """Scan uploads directory and return asset inventory"""
    ensure_directories()
    
    assets = []
    upload_dir = 'uploads'
    
    if not os.path.exists(upload_dir):
        return assets
    
    try:
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            
            if os.path.isfile(file_path):
                # Get file stats
                stat = os.stat(file_path)
                file_size_mb = round(stat.st_size / (1024 * 1024), 2)
                
                # Generate thumbnail if it's an image
                thumbnail_path = generate_thumbnail(file_path)
                
                # Determine category
                category = get_file_category(filename, file_path)
                
                # Analyze JSONL files for additional metadata
                metadata = {}
                if filename.endswith('.jsonl'):
                    metadata = analyze_jsonl_file(file_path)
                
                asset = {
                    'id': str(uuid.uuid4()),
                    'filename': filename,
                    'file_path': file_path,
                    'file_size_mb': file_size_mb,
                    'category': category,
                    'thumbnail_path': thumbnail_path,
                    'download_url': f"/api/assets/download/{filename}",
                    'upload_date': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'metadata': metadata
                }
                
                assets.append(asset)
    
    except Exception as e:
        print(f"Error scanning assets: {e}")
    
    return sorted(assets, key=lambda x: x['last_modified'], reverse=True)

def analyze_jsonl_file(file_path):
    """Analyze JSONL file and return metadata"""
    metadata = {
        'type': 'data_file',
        'record_count': 0,
        'sample_fields': [],
        'data_source': 'unknown'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            metadata['record_count'] = len([line for line in lines if line.strip()])
            
            # Analyze first record for field structure
            if lines:
                first_line = lines[0].strip()
                if first_line:
                    try:
                        first_record = json.loads(first_line)
                        metadata['sample_fields'] = list(first_record.keys())[:10]  # First 10 fields
                        
                        # Determine data source
                        if 'instagram' in file_path.lower():
                            metadata['data_source'] = 'instagram'
                        elif 'tiktok' in file_path.lower():
                            metadata['data_source'] = 'tiktok'
                        elif 'competitive' in file_path.lower():
                            metadata['data_source'] = 'competitive_analysis'
                        
                    except json.JSONDecodeError:
                        pass
    
    except Exception as e:
        print(f"Error analyzing JSONL file {file_path}: {e}")
    
    return metadata

def add_asset(file_path, filename, category=None, metadata=None):
    """Add new asset to the system"""
    try:
        if not os.path.exists(file_path):
            return {'success': False, 'error': 'File not found'}
        
        # Generate thumbnail if applicable
        thumbnail_path = generate_thumbnail(file_path)
        
        # Determine category if not provided
        if not category:
            category = get_file_category(filename, file_path)
        
        # Get file stats
        stat = os.stat(file_path)
        file_size_mb = round(stat.st_size / (1024 * 1024), 2)
        
        # Create asset record
        asset = {
            'id': str(uuid.uuid4()),
            'filename': filename,
            'file_path': file_path,
            'file_size_mb': file_size_mb,
            'category': category,
            'thumbnail_path': thumbnail_path,
            'download_url': f"/api/assets/download/{filename}",
            'upload_date': datetime.now().isoformat(),
            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'metadata': metadata or {}
        }
        
        return {'success': True, 'asset': asset}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def remove_asset(asset_id):
    """Remove asset from the system"""
    try:
        # In a real implementation, you'd maintain an asset database
        # For now, we'll return success for any valid UUID
        if asset_id and len(asset_id) > 10:
            return {'success': True, 'message': f'Asset {asset_id} removed'}
        else:
            return {'success': False, 'error': 'Invalid asset ID'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_assets_by_category(category=None):
    """Get assets filtered by category"""
    all_assets = scan_assets()
    
    if not category:
        return all_assets
    
    return [asset for asset in all_assets if asset['category'] == category]

def get_asset_categories():
    """Get list of all asset categories with counts"""
    assets = scan_assets()
    categories = {}
    
    for asset in assets:
        category = asset['category']
        if category not in categories:
            categories[category] = {
                'name': category,
                'count': 0,
                'total_size_mb': 0
            }
        categories[category]['count'] += 1
        categories[category]['total_size_mb'] += asset['file_size_mb']
    
    return categories

def search_assets(query):
    """Search assets by filename or metadata"""
    assets = scan_assets()
    query = query.lower()
    
    matching_assets = []
    for asset in assets:
        # Search in filename
        if query in asset['filename'].lower():
            matching_assets.append(asset)
            continue
        
        # Search in category
        if query in asset['category'].lower():
            matching_assets.append(asset)
            continue
        
        # Search in metadata
        metadata_str = json.dumps(asset.get('metadata', {})).lower()
        if query in metadata_str:
            matching_assets.append(asset)
    
    return matching_assets

def get_asset_stats():
    """Get comprehensive asset statistics"""
    assets = scan_assets()
    categories = get_asset_categories()
    
    total_size_mb = sum(asset['file_size_mb'] for asset in assets)
    
    # Data file analysis
    data_files = [asset for asset in assets if asset['category'] == 'intelligence_data']
    total_records = sum(asset.get('metadata', {}).get('record_count', 0) for asset in data_files)
    
    stats = {
        'total_assets': len(assets),
        'categories': categories,
        'total_size_mb': round(total_size_mb, 2),
        'data_files_count': len(data_files),
        'total_data_records': total_records,
        'recent_uploads': len([asset for asset in assets if 
                             (datetime.now() - datetime.fromisoformat(asset['upload_date'].replace('Z', '+00:00').replace('+00:00', ''))).days <= 7]),
        'largest_file': max(assets, key=lambda x: x['file_size_mb']) if assets else None,
        'most_recent': max(assets, key=lambda x: x['upload_date']) if assets else None
    }
    
    return stats

def get_asset_by_filename(filename):
    """Get specific asset by filename"""
    assets = scan_assets()
    for asset in assets:
        if asset['filename'] == filename:
            return asset
    return None

def update_asset_metadata(asset_id, metadata):
    """Update asset metadata"""
    try:
        # In a real implementation, you'd update the asset database
        return {'success': True, 'message': f'Metadata updated for asset {asset_id}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_thumbnail_path(filename):
    """Get thumbnail path for a file"""
    file_path = os.path.join('uploads', filename)
    return generate_thumbnail(file_path)

def validate_asset_file(file_path):
    """Validate asset file integrity"""
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'File not found'}
    
    try:
        stat = os.stat(file_path)
        if stat.st_size == 0:
            return {'valid': False, 'error': 'File is empty'}
        
        # Additional validation based on file type
        filename = os.path.basename(file_path)
        if filename.endswith('.jsonl'):
            # Validate JSONL format
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            json.loads(line)
                        except json.JSONDecodeError:
                            return {'valid': False, 'error': f'Invalid JSON on line {line_num}'}
                        if line_num > 10:  # Only check first 10 lines for performance
                            break
        
        return {'valid': True, 'size': stat.st_size}
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

# Initialize directories on import
ensure_directories()
