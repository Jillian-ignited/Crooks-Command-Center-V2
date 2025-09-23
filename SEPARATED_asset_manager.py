"""
Separated Asset Management System
Handles data assets and media assets separately with thumbnail generation
Uses only real files and generates actual thumbnails
"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

class SeparatedAssetManager:
    def __init__(self):
        self.data_assets_path = 'uploads/intel/'
        self.media_assets_path = 'uploads/media/'
        self.thumbnails_path = 'uploads/thumbnails/'
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure all asset directories exist"""
        for path in [self.data_assets_path, self.media_assets_path, self.thumbnails_path]:
            os.makedirs(path, exist_ok=True)
    
    def generate_data_thumbnail(self, file_path, file_info):
        """Generate thumbnail for data assets (JSON, JSONL, CSV files)"""
        try:
            # Create a simple data visualization thumbnail
            img = Image.new('RGB', (200, 150), color='#1a1a1a')
            draw = ImageDraw.Draw(img)
            
            # Try to load a basic font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw file type indicator
            file_ext = Path(file_path).suffix.upper()
            draw.rectangle([10, 10, 190, 40], fill='#333333', outline='#555555')
            draw.text((15, 18), f"{file_ext} DATA", fill='#ffffff', font=font)
            
            # Draw file info
            draw.text((15, 50), f"Records: {file_info.get('record_count', 'Unknown')}", fill='#90EE90', font=small_font)
            draw.text((15, 65), f"Size: {file_info.get('file_size_mb', 0):.1f} MB", fill='#90EE90', font=small_font)
            draw.text((15, 80), f"Updated: {file_info.get('last_updated', 'Unknown')}", fill='#FFD700', font=small_font)
            
            # Draw data type icon
            draw.rectangle([15, 100, 185, 130], fill='#2a2a2a', outline='#444444')
            draw.text((20, 110), f"📊 {file_info.get('data_type', 'Dataset')}", fill='#ffffff', font=small_font)
            
            # Save thumbnail
            thumbnail_name = f"{Path(file_path).stem}_thumb.png"
            thumbnail_path = os.path.join(self.thumbnails_path, thumbnail_name)
            img.save(thumbnail_path)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"Error generating data thumbnail: {e}")
            return None
    
    def generate_media_thumbnail(self, file_path, file_info):
        """Generate thumbnail for media assets (images, videos)"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                # For images, create actual thumbnail
                with Image.open(file_path) as img:
                    img.thumbnail((200, 150), Image.Resampling.LANCZOS)
                    
                    # Create new image with padding if needed
                    thumb = Image.new('RGB', (200, 150), color='#000000')
                    
                    # Center the thumbnail
                    x = (200 - img.width) // 2
                    y = (150 - img.height) // 2
                    thumb.paste(img, (x, y))
                    
                    # Save thumbnail
                    thumbnail_name = f"{Path(file_path).stem}_thumb.png"
                    thumbnail_path = os.path.join(self.thumbnails_path, thumbnail_name)
                    thumb.save(thumbnail_path)
                    
                    return thumbnail_path
            else:
                # For other media types, create placeholder
                img = Image.new('RGB', (200, 150), color='#1a1a1a')
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                except:
                    font = ImageFont.load_default()
                
                # Draw media type indicator
                draw.rectangle([10, 10, 190, 140], fill='#333333', outline='#555555')
                
                media_icon = "🎥" if file_ext in ['.mp4', '.avi', '.mov'] else "🎵" if file_ext in ['.mp3', '.wav'] else "📄"
                draw.text((90, 60), media_icon, fill='#ffffff', font=font)
                draw.text((70, 90), file_ext.upper(), fill='#ffffff', font=font)
                
                # Save thumbnail
                thumbnail_name = f"{Path(file_path).stem}_thumb.png"
                thumbnail_path = os.path.join(self.thumbnails_path, thumbnail_name)
                img.save(thumbnail_path)
                
                return thumbnail_path
                
        except Exception as e:
            print(f"Error generating media thumbnail: {e}")
            return None
    
    def get_data_assets(self):
        """Get all data assets with metadata and thumbnails"""
        data_assets = []
        
        if os.path.exists(self.data_assets_path):
            for file_name in os.listdir(self.data_assets_path):
                file_path = os.path.join(self.data_assets_path, file_name)
                
                if os.path.isfile(file_path):
                    # Get file stats
                    stat = os.stat(file_path)
                    file_size_mb = stat.st_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Count records for data files
                    record_count = 0
                    data_type = "Unknown"
                    
                    if file_name.endswith('.jsonl'):
                        data_type = "JSONL Dataset"
                        try:
                            with open(file_path, 'r') as f:
                                for line in f:
                                    if line.strip():
                                        record_count += 1
                        except:
                            record_count = 0
                    elif file_name.endswith('.json'):
                        data_type = "JSON Data"
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    record_count = len(data)
                                else:
                                    record_count = 1
                        except:
                            record_count = 0
                    elif file_name.endswith('.csv'):
                        data_type = "CSV Dataset"
                        try:
                            with open(file_path, 'r') as f:
                                record_count = sum(1 for line in f) - 1  # Subtract header
                        except:
                            record_count = 0
                    
                    file_info = {
                        'record_count': record_count,
                        'file_size_mb': file_size_mb,
                        'last_updated': modified_time.strftime('%Y-%m-%d'),
                        'data_type': data_type
                    }
                    
                    # Generate thumbnail
                    thumbnail_path = self.generate_data_thumbnail(file_path, file_info)
                    
                    data_assets.append({
                        'name': file_name,
                        'path': file_path,
                        'type': 'data',
                        'data_type': data_type,
                        'size_mb': round(file_size_mb, 2),
                        'record_count': record_count,
                        'last_modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'thumbnail_path': thumbnail_path,
                        'thumbnail_available': thumbnail_path is not None,
                        'category': 'Intelligence Data'
                    })
        
        return data_assets
    
    def get_media_assets(self):
        """Get all media assets with metadata and thumbnails"""
        media_assets = []
        
        if os.path.exists(self.media_assets_path):
            for file_name in os.listdir(self.media_assets_path):
                file_path = os.path.join(self.media_assets_path, file_name)
                
                if os.path.isfile(file_path):
                    # Get file stats
                    stat = os.stat(file_path)
                    file_size_mb = stat.st_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Determine media type
                    file_ext = Path(file_path).suffix.lower()
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        media_type = "Image"
                        category = "Visual Assets"
                    elif file_ext in ['.mp4', '.avi', '.mov', '.webm']:
                        media_type = "Video"
                        category = "Video Assets"
                    elif file_ext in ['.mp3', '.wav', '.aac']:
                        media_type = "Audio"
                        category = "Audio Assets"
                    else:
                        media_type = "Other"
                        category = "Other Media"
                    
                    file_info = {
                        'media_type': media_type,
                        'file_size_mb': file_size_mb,
                        'last_updated': modified_time.strftime('%Y-%m-%d')
                    }
                    
                    # Generate thumbnail
                    thumbnail_path = self.generate_media_thumbnail(file_path, file_info)
                    
                    media_assets.append({
                        'name': file_name,
                        'path': file_path,
                        'type': 'media',
                        'media_type': media_type,
                        'size_mb': round(file_size_mb, 2),
                        'last_modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'thumbnail_path': thumbnail_path,
                        'thumbnail_available': thumbnail_path is not None,
                        'category': category
                    })
        
        return media_assets
    
    def get_thumbnail_base64(self, thumbnail_path):
        """Get thumbnail as base64 for web display"""
        try:
            if thumbnail_path and os.path.exists(thumbnail_path):
                with open(thumbnail_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
        except:
            pass
        return None

# API functions for integration
def get_separated_assets():
    """Get separated data and media assets with thumbnails"""
    try:
        manager = SeparatedAssetManager()
        
        data_assets = manager.get_data_assets()
        media_assets = manager.get_media_assets()
        
        return {
            'data_assets': {
                'count': len(data_assets),
                'total_size_mb': sum(asset['size_mb'] for asset in data_assets),
                'total_records': sum(asset.get('record_count', 0) for asset in data_assets),
                'assets': data_assets
            },
            'media_assets': {
                'count': len(media_assets),
                'total_size_mb': sum(asset['size_mb'] for asset in media_assets),
                'assets': media_assets
            },
            'thumbnails_generated': len([a for a in data_assets + media_assets if a['thumbnail_available']]),
            'last_scan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': f'Asset management error: {str(e)}',
            'data_assets': {'count': 0, 'assets': []},
            'media_assets': {'count': 0, 'assets': []},
            'thumbnails_generated': 0
        }

if __name__ == "__main__":
    # Test separated asset management
    assets = get_separated_assets()
    print("=== SEPARATED ASSET MANAGEMENT ===")
    print(f"Data Assets: {assets['data_assets']['count']} files, {assets['data_assets']['total_size_mb']:.1f} MB")
    print(f"Total Records: {assets['data_assets']['total_records']:,}")
    print(f"Media Assets: {assets['media_assets']['count']} files, {assets['media_assets']['total_size_mb']:.1f} MB")
    print(f"Thumbnails Generated: {assets['thumbnails_generated']}")
    
    print(f"\n=== DATA ASSETS ===")
    for asset in assets['data_assets']['assets']:
        thumb_status = "✓" if asset['thumbnail_available'] else "✗"
        print(f"{thumb_status} {asset['name']:40} | {asset['data_type']:15} | {asset['record_count']:4} records")
    
    print(f"\n=== MEDIA ASSETS ===")
    for asset in assets['media_assets']['assets']:
        thumb_status = "✓" if asset['thumbnail_available'] else "✗"
        print(f"{thumb_status} {asset['name']:40} | {asset['media_type']:10} | {asset['size_mb']:5.1f} MB")
