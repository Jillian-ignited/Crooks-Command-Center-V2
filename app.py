"""
Crooks & Castles Command Center V2 - Standalone Application
All functionality in a single file for easy deployment
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, abort
import json
import os
from datetime import datetime, timedelta, date
import uuid
from werkzeug.utils import secure_filename
import mimetypes
from PIL import Image, ImageOps
import hashlib
import shutil
import calendar

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'crooks_command_center_2025_enhanced')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist
os.makedirs('uploads/assets', exist_ok=True)
os.makedirs('uploads/intelligence', exist_ok=True)
os.makedirs('uploads/temp', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/assets', exist_ok=True)
os.makedirs('static/thumbnails', exist_ok=True)

# Global data storage
INTELLIGENCE_DATA = {
    'instagram_data': [],
    'hashtag_data': [],
    'tiktok_data': [],
    'competitive_rankings': {},
    'cultural_insights': {},
    'last_updated': None
}

MONITORED_BRANDS = [
    'crooksncastles', 'hellstar', 'supremenewyork', 'stussy', 'edhardy',
    'godspeed', 'essentials', 'lrgclothing', 'diamondsupplyco', 
    'reasonclothing', 'smokerisenewyork', 'vondutch'
]

STRATEGIC_HASHTAGS = [
    'streetwear', 'crooksandcastles', 'y2kfashion', 'vintagestreetwear',
    'streetweararchive', 'heritagebrand', 'supremedrop', 'hellstar',
    'fearofgod', 'diamondsupply', 'edhardy', 'vondutch',
    'streetwearculture', 'hypebeast', 'grailed'
]

# Asset categories
ASSET_CATEGORIES = {
    'logos_branding': {
        'name': 'Logos & Branding',
        'description': 'Primary brand marks, logos, and brand identity elements',
        'icon': '👑',
        'color': '#FFD700'
    },
    'heritage_archive': {
        'name': 'Heritage Archive',
        'description': 'Historical designs, vintage pieces, and archive collections',
        'icon': '📚',
        'color': '#8B4513'
    },
    'product_photography': {
        'name': 'Product Photography',
        'description': 'High-quality product shots, lifestyle imagery, and e-commerce assets',
        'icon': '📸',
        'color': '#FF6B6B'
    },
    'campaign_creative': {
        'name': 'Campaign Creative',
        'description': 'Marketing campaigns, seasonal collections, and promotional materials',
        'icon': '🎨',
        'color': '#4ECDC4'
    },
    'social_content': {
        'name': 'Social Content',
        'description': 'Social media assets, stories, posts, and digital content',
        'icon': '📱',
        'color': '#45B7D1'
    }
}

# User roles
USER_ROLES = {
    'ceo': {'name': 'CEO', 'color': '#FFD700', 'permissions': ['all']},
    'brand_manager': {'name': 'Brand Manager', 'color': '#FF6B6B', 'permissions': ['campaigns', 'assets', 'reports']},
    'creative_director': {'name': 'Creative Director', 'color': '#4ECDC4', 'permissions': ['assets', 'campaigns', 'approval']},
    'content_creator': {'name': 'Content Creator', 'color': '#45B7D1', 'permissions': ['assets', 'upload']},
    'social_media_manager': {'name': 'Social Media Manager', 'color': '#96CEB4', 'permissions': ['social', 'assets']},
    'data_analyst': {'name': 'Data Analyst', 'color': '#FFEAA7', 'permissions': ['reports', 'intelligence']},
    'marketing_coordinator': {'name': 'Marketing Coordinator', 'color': '#DDA0DD', 'permissions': ['campaigns', 'calendar']},
    'intern': {'name': 'Intern', 'color': '#F0A500', 'permissions': ['view']},
    'agency_partner': {'name': 'Agency Partner', 'color': '#E74C3C', 'permissions': ['reports', 'assets']}
}

def load_json_data(filename, default=None):
    """Load JSON data from file with fallback"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return default or {}

def save_json_data(filename, data):
    """Save JSON data to file"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except:
        return False

def generate_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    """Generate thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        return True
    except:
        return False

def get_file_hash(file_path):
    """Get SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except:
        return None

@app.route('/')
def dashboard():
    """Main dashboard"""
    # Get current user (simplified for standalone)
    current_user = {
        'id': 'brand_manager_1',
        'name': 'Team Member',
        'role': 'brand_manager',
        'department': 'Marketing',
        'avatar_color': '#FF6B6B'
    }
    
    # Dashboard metrics
    dashboard_data = {
        'competitive_rank': '#?/12',
        'cultural_trends': '0 trending',
        'active_projects': '1 projects',
        'intelligence_data': '0 records',
        'recent_activity': [
            {
                'action': 'Uploaded new product photography',
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M'),
                'icon': '📸'
            },
            {
                'action': 'Updated Archive Remastered project timeline',
                'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
                'icon': '📅'
            }
        ]
    }
    
    return render_template('standalone.html', 
                         current_user=current_user,
                         dashboard_data=dashboard_data,
                         asset_categories=ASSET_CATEGORIES,
                         user_roles=USER_ROLES)

@app.route('/api/intelligence/summary')
def intelligence_summary():
    """Get intelligence summary"""
    return jsonify({
        'competitive_rank': '#?/12',
        'rank_change': '+2 positions',
        'cultural_trends': '0 trending',
        'trend_velocity': '+15% velocity',
        'data_points': '0 records',
        'daily_increase': '+1.2K today',
        'avg_engagement': '2.4%',
        'engagement_change': '-0.3% vs last week',
        'last_updated': datetime.now().isoformat()
    })

@app.route('/upload/intelligence', methods=['POST'])
def upload_intelligence():
    """Upload intelligence data"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith(('.json', '.jsonl', '.csv')):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join('uploads/intelligence', filename)
        
        file.save(filepath)
        
        # Process the file (simplified)
        file_info = {
            'filename': filename,
            'original_name': file.filename,
            'size': os.path.getsize(filepath),
            'uploaded_at': datetime.now().isoformat(),
            'type': 'intelligence_data'
        }
        
        return jsonify({
            'message': 'Intelligence data uploaded successfully',
            'file_info': file_info
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload/asset', methods=['POST'])
def upload_asset():
    """Upload brand asset"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = os.path.splitext(filename)[1]
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join('uploads/assets', filename)
        
        file.save(filepath)
        
        # Generate thumbnail for images
        thumbnail_path = None
        if file_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_path = os.path.join('static/thumbnails', thumbnail_filename)
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            generate_thumbnail(filepath, thumbnail_path)
        
        file_info = {
            'filename': filename,
            'original_name': file.filename,
            'size': os.path.getsize(filepath),
            'uploaded_at': datetime.now().isoformat(),
            'type': 'brand_asset',
            'thumbnail': thumbnail_path
        }
        
        return jsonify({
            'message': 'Asset uploaded successfully',
            'file_info': file_info
        })
    
    return jsonify({'error': 'Upload failed'}), 400

@app.route('/api/assets')
def get_assets():
    """Get asset library"""
    assets = []
    assets_dir = 'uploads/assets'
    
    if os.path.exists(assets_dir):
        for filename in os.listdir(assets_dir):
            filepath = os.path.join(assets_dir, filename)
            if os.path.isfile(filepath):
                file_stat = os.stat(filepath)
                assets.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'type': 'asset'
                })
    
    return jsonify(assets)

@app.route('/api/calendar/events')
def get_calendar_events():
    """Get calendar events"""
    events = [
        {
            'title': 'Q4 Campaign Planning',
            'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'type': 'campaign',
            'priority': 'high'
        },
        {
            'title': 'Heritage Month Content Review',
            'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'type': 'content',
            'priority': 'medium'
        },
        {
            'title': 'Apify Data Analysis',
            'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'type': 'intelligence',
            'priority': 'high'
        }
    ]
    
    return jsonify(events)

@app.route('/api/workflows')
def get_workflows():
    """Get workflow status"""
    workflows = {
        'active': 0,
        'action_required': 0,
        'pending_approval': 0,
        'completed': 0,
        'workflows': []
    }
    
    return jsonify(workflows)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download file"""
    # Check in uploads directory
    for subdir in ['assets', 'intelligence', 'temp']:
        filepath = os.path.join('uploads', subdir, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
    
    return abort(404)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get port from environment (Render sets this)
    port_env = os.environ.get("PORT", "5000")
    
    # Handle Render's 'auto' port setting
    try:
        port = int(port_env)
    except (ValueError, TypeError):
        # If PORT is 'auto' or invalid, use default
        port = 5000
    
    app.run(host='0.0.0.0', port=port, debug=False)
