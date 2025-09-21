"""
Crooks & Castles Command Center V2 - Main Application
Enhanced collaborative platform with comprehensive file management and Apify integration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, abort
import json
import os
from datetime import datetime, timedelta, date
import pandas as pd
from calendar_manager import CrooksCalendarManager
from enhanced_asset_manager import EnhancedCrooksAssetManager
from file_manager import CrooksFileManager
from user_management import CrooksUserManager
from workflow_engine import CrooksWorkflowEngine
import uuid
from werkzeug.utils import secure_filename
import mimetypes

app = Flask(__name__)
app.secret_key = 'crooks_command_center_2025_enhanced'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize managers
calendar_manager = CrooksCalendarManager()
asset_manager = EnhancedCrooksAssetManager()
file_manager = CrooksFileManager()
user_manager = CrooksUserManager()
workflow_engine = CrooksWorkflowEngine()

# Ensure upload directories exist
os.makedirs('uploads/assets', exist_ok=True)
os.makedirs('uploads/intelligence', exist_ok=True)
os.makedirs('uploads/temp', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/assets', exist_ok=True)
os.makedirs('static/thumbnails', exist_ok=True)

# Competitive intelligence data storage
INTELLIGENCE_DATA = {
    'instagram_data': [],
    'hashtag_data': [],
    'tiktok_data': [],
    'competitive_rankings': {},
    'cultural_insights': {},
    'last_updated': None
}

# Brand monitoring configuration
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

TIKTOK_SEARCHES = [
    'crooks and castles', 'streetwear haul', 'streetwear drop', 'y2k fashion',
    'vintage streetwear', 'thrift streetwear', 'streetwear archive',
    'supreme unboxing', 'hellstar outfit', 'fear of god essentials'
]

@app.route('/')
def dashboard():
    """Main dashboard with collaborative features"""
    # Get current user (in production, this would come from authentication)
    session_id = session.get('session_id')
    current_user = None
    current_user_id = 'brand_manager_1'  # Default fallback
    
    if session_id:
        current_user = user_manager.get_user_by_session(session_id)
        if current_user:
            current_user_id = current_user['id']
    
    # Get user dashboard configuration
    user_dashboard_config = user_manager.get_user_dashboard_config(current_user_id)
    
    # Get collaborative dashboard data
    dashboard_data = asset_manager.get_collaborative_dashboard(current_user_id)
    
    # Get workflow dashboard data
    workflow_dashboard = workflow_engine.get_workflow_dashboard(current_user_id)
    
    # Get team collaboration data
    team_dashboard = user_manager.get_team_dashboard(current_user_id)
    
    # Get calendar data
    today = date.today()
    calendar_view = calendar_manager.get_calendar_view(today.year, today.month)
    upcoming_events = calendar_manager.get_upcoming_events(7)
    
    # Get strategic planning data
    strategic_calendar = calendar_manager.get_strategic_planning_calendar()
    
    # Get competitive intelligence summary
    intelligence_summary = get_intelligence_summary()
    
    # Get cultural radar data
    cultural_radar = get_cultural_radar_data()
    
    # Get file manager statistics
    file_stats = file_manager.get_storage_stats()
    
    return render_template('enhanced_collaborative_index.html',
                         dashboard_data=dashboard_data,
                         user_dashboard_config=user_dashboard_config,
                         workflow_dashboard=workflow_dashboard,
                         team_dashboard=team_dashboard,
                         calendar_view=calendar_view,
                         upcoming_events=upcoming_events,
                         strategic_calendar=strategic_calendar,
                         intelligence_summary=intelligence_summary,
                         cultural_radar=cultural_radar,
                         file_stats=file_stats,
                         monitored_brands=MONITORED_BRANDS,
                         strategic_hashtags=STRATEGIC_HASHTAGS,
                         asset_categories=asset_manager.asset_categories,
                         current_user=current_user)

# ============================================================================
# ASSET MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/assets/upload', methods=['POST'])
def upload_asset():
    """Upload new brand asset with thumbnail generation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Get form data
        category = request.form.get('category')
        subcategory = request.form.get('subcategory', '')
        user_id = request.form.get('user_id', session.get('user_id', 'unknown'))
        
        # Metadata
        metadata = {
            'name': request.form.get('name', file.filename),
            'description': request.form.get('description', ''),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
            'usage_rights': request.form.get('usage_rights', 'internal_use')
        }
        
        # Upload asset
        result = asset_manager.upload_asset_file(file, category, subcategory, user_id, metadata)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Asset uploaded successfully',
                'asset_id': result['asset_id'],
                'thumbnails_generated': result.get('thumbnails_generated', 0),
                'asset_data': result['asset_data']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/assets/download/<asset_id>')
def download_asset(asset_id):
    """Download an asset file"""
    try:
        user_id = session.get('user_id', 'viewer')
        result = asset_manager.download_asset(asset_id, user_id)
        
        if result['success']:
            return send_file(
                result['file_path'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype=result['mime_type']
            )
        else:
            return jsonify({'error': result['error']}), 404
            
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/assets/thumbnail/<asset_id>')
def get_asset_thumbnail(asset_id):
    """Get asset thumbnail"""
    size = request.args.get('size', '300x300')
    thumbnail_url = asset_manager.get_asset_thumbnail(asset_id, size)
    
    if thumbnail_url:
        return jsonify({'thumbnail_url': thumbnail_url})
    else:
        return jsonify({'error': 'Thumbnail not found'}), 404

@app.route('/api/assets')
def list_assets():
    """List assets with thumbnails"""
    category = request.args.get('category')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    result = asset_manager.list_assets_with_thumbnails(category, limit, offset)
    return jsonify(result)

@app.route('/api/assets/<asset_id>')
def get_asset_details(asset_id):
    """Get detailed asset information"""
    asset = asset_manager.get_asset_by_id(asset_id)
    if asset:
        return jsonify(asset)
    else:
        return jsonify({'error': 'Asset not found'}), 404

@app.route('/api/assets/<asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """Delete an asset"""
    try:
        user_id = session.get('user_id', 'viewer')
        result = asset_manager.delete_asset(asset_id, user_id)
        
        if result['success']:
            return jsonify({'message': result['message']})
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

# ============================================================================
# FILE MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """Upload file using file manager"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        category = request.form.get('category', 'temp')
        user_id = request.form.get('user_id', session.get('user_id', 'viewer'))
        user_role = request.form.get('user_role', 'viewer')
        
        metadata = {
            'description': request.form.get('description', ''),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else []
        }
        
        result = file_manager.upload_file(file, category, user_id, user_role, metadata)
        
        if result['success']:
            return jsonify({
                'success': True,
                'file_id': result['file_id'],
                'file_record': result['file_record'],
                'is_duplicate': result.get('is_duplicate', False)
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/files/download/<file_id>')
def download_file(file_id):
    """Download file using file manager"""
    try:
        user_role = session.get('user_role', 'viewer')
        result = file_manager.download_file(file_id, user_role)
        
        if result['success']:
            return send_file(
                result['file_path'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype=result['mime_type']
            )
        else:
            return jsonify({'error': result['error']}), 404
            
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/files')
def list_files():
    """List files with filtering"""
    category = request.args.get('category')
    user_role = session.get('user_role', 'viewer')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    result = file_manager.list_files(category, user_role, limit, offset)
    return jsonify(result)

@app.route('/api/files/search')
def search_files():
    """Search files"""
    query = request.args.get('query', '')
    category = request.args.get('category')
    user_role = session.get('user_role', 'viewer')
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
        
    results = file_manager.search_files(query, category, user_role)
    return jsonify({'results': results})

@app.route('/api/files/stats')
def get_file_stats():
    """Get file storage statistics"""
    stats = file_manager.get_storage_stats()
    return jsonify(stats)

# ============================================================================
# INTELLIGENCE DATA ROUTES
# ============================================================================

@app.route('/api/upload_intelligence', methods=['POST'])
def upload_intelligence():
    """Upload and process Apify intelligence data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        data_type = request.form.get('data_type')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not data_type or data_type not in ['instagram', 'hashtags', 'tiktok']:
            return jsonify({'error': 'Invalid data type'}), 400
            
        # Save uploaded file using file manager
        user_id = session.get('user_id', 'system')
        metadata = {
            'data_type': data_type,
            'description': f'{data_type.title()} intelligence data from Apify'
        }
        
        upload_result = file_manager.upload_file(file, 'intelligence', user_id, 'admin', metadata)
        
        if not upload_result['success']:
            return jsonify({'error': upload_result['error']}), 400
            
        # Process the intelligence data
        file_path = upload_result['file_record']['file_path']
        processed_data = process_intelligence_file(file_path, data_type)
        
        # Update global intelligence data
        INTELLIGENCE_DATA[f'{data_type}_data'] = processed_data
        INTELLIGENCE_DATA['last_updated'] = datetime.now().isoformat()
        
        # Generate insights
        if data_type == 'instagram':
            update_competitive_rankings(processed_data)
        elif data_type == 'hashtags':
            update_cultural_insights(processed_data)
        elif data_type == 'tiktok':
            update_tiktok_insights(processed_data)
            
        # Save processed data
        save_intelligence_data()
        
        return jsonify({
            'success': True,
            'message': f'{data_type.title()} data processed successfully',
            'records_processed': len(processed_data),
            'insights_generated': True,
            'file_id': upload_result['file_id']
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

# ============================================================================
# COLLABORATIVE PROJECT ROUTES
# ============================================================================

@app.route('/api/projects')
def get_projects():
    """Get all collaborative projects"""
    user_id = request.args.get('user_id', session.get('user_id', 'brand_manager_1'))
    projects = asset_manager.get_user_projects(user_id)
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create new collaborative project"""
    try:
        project_data = request.json
        project_id = asset_manager.create_project(project_data)
        return jsonify({'success': True, 'project_id': project_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CALENDAR ROUTES
# ============================================================================

@app.route('/api/calendar/events')
def get_calendar_events():
    """Get calendar events"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        events = calendar_manager.get_events_by_date_range(start, end)
    else:
        events = calendar_manager.get_upcoming_events(30)
        
    return jsonify(events)

@app.route('/api/calendar/events', methods=['POST'])
def create_calendar_event():
    """Create new calendar event"""
    try:
        event_data = request.json
        event_id = calendar_manager.add_event(event_data)
        return jsonify({'success': True, 'event_id': event_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# APPROVAL WORKFLOW ROUTES
# ============================================================================

@app.route('/api/approval/submit', methods=['POST'])
def submit_for_approval():
    """Submit asset for approval"""
    try:
        data = request.json
        asset_id = data.get('asset_id')
        user_id = data.get('user_id', session.get('user_id'))
        
        success = asset_manager.submit_for_approval(asset_id, user_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/approval/approve', methods=['POST'])
def approve_asset():
    """Approve an asset"""
    try:
        data = request.json
        asset_id = data.get('asset_id')
        user_id = data.get('user_id', session.get('user_id'))
        notes = data.get('notes', '')
        
        success = asset_manager.approve_asset(asset_id, user_id, notes)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# INTELLIGENCE SUMMARY ROUTES
# ============================================================================

@app.route('/api/intelligence/summary')
def get_intelligence_api():
    """Get intelligence summary via API"""
    return jsonify({
        'summary': get_intelligence_summary(),
        'cultural_radar': get_cultural_radar_data(),
        'competitive_rankings': INTELLIGENCE_DATA.get('competitive_rankings', {}),
        'last_updated': INTELLIGENCE_DATA.get('last_updated')
    })

@app.route('/api/team/dashboard/<user_id>')
def get_team_dashboard(user_id):
    """Get team member dashboard"""
    dashboard_data = asset_manager.get_collaborative_dashboard(user_id)
    return jsonify(dashboard_data)

# ============================================================================
# UTILITY FUNCTIONS (Intelligence Processing)
# ============================================================================

def process_intelligence_file(filepath, data_type):
    """Process uploaded JSONL intelligence file"""
    processed_data = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    
                    if data_type == 'instagram':
                        processed_item = process_instagram_data(data)
                    elif data_type == 'hashtags':
                        processed_item = process_hashtag_data(data)
                    elif data_type == 'tiktok':
                        processed_item = process_tiktok_data(data)
                    else:
                        continue
                        
                    if processed_item:
                        processed_data.append(processed_item)
                        
    except Exception as e:
        print(f"Error processing file: {e}")
        
    return processed_data

def process_instagram_data(data):
    """Process Instagram post data"""
    try:
        return {
            'id': data.get('id'),
            'username': data.get('ownerUsername'),
            'caption': data.get('caption', ''),
            'likes': data.get('likesCount', 0),
            'comments': data.get('commentsCount', 0),
            'timestamp': data.get('timestamp'),
            'url': data.get('url'),
            'hashtags': extract_hashtags(data.get('caption', '')),
            'engagement_rate': calculate_engagement_rate(data),
            'brand': identify_brand(data.get('ownerUsername'))
        }
    except Exception as e:
        print(f"Error processing Instagram data: {e}")
        return None

def process_hashtag_data(data):
    """Process hashtag monitoring data"""
    try:
        return {
            'hashtag': data.get('hashtag'),
            'post_count': data.get('postCount', 0),
            'recent_posts': data.get('recentPosts', []),
            'top_posts': data.get('topPosts', []),
            'engagement_avg': calculate_hashtag_engagement(data),
            'velocity': calculate_hashtag_velocity(data),
            'cultural_relevance': assess_cultural_relevance(data)
        }
    except Exception as e:
        print(f"Error processing hashtag data: {e}")
        return None

def process_tiktok_data(data):
    """Process TikTok content data"""
    try:
        return {
            'id': data.get('id'),
            'username': data.get('authorMeta', {}).get('name'),
            'description': data.get('text', ''),
            'likes': data.get('diggCount', 0),
            'shares': data.get('shareCount', 0),
            'comments': data.get('commentCount', 0),
            'views': data.get('playCount', 0),
            'hashtags': data.get('hashtags', []),
            'music': data.get('musicMeta', {}),
            'cultural_moment': assess_cultural_moment(data),
            'trend_potential': calculate_trend_potential(data)
        }
    except Exception as e:
        print(f"Error processing TikTok data: {e}")
        return None

def extract_hashtags(caption):
    """Extract hashtags from caption text"""
    import re
    if not caption:
        return []
    hashtags = re.findall(r'#(\w+)', caption.lower())
    return hashtags

def calculate_engagement_rate(data):
    """Calculate engagement rate for Instagram post"""
    likes = data.get('likesCount', 0)
    comments = data.get('commentsCount', 0)
    followers = data.get('ownerFollowersCount', 1)
    
    if followers == 0:
        return 0
        
    engagement_rate = ((likes + comments) / followers) * 100
    return round(engagement_rate, 2)

def identify_brand(username):
    """Identify which monitored brand the username belongs to"""
    username_lower = username.lower() if username else ''
    
    brand_mapping = {
        'crooksncastles': 'Crooks & Castles',
        'hellstar': 'Hellstar',
        'supremenewyork': 'Supreme',
        'stussy': 'Stussy',
        'edhardy': 'Ed Hardy',
        'godspeed': 'Godspeed',
        'essentials': 'Fear of God Essentials',
        'lrgclothing': 'LRG',
        'diamondsupplyco': 'Diamond Supply Co.',
        'reasonclothing': 'Reason Clothing',
        'smokerisenewyork': 'Smoke Rise',
        'vondutch': 'Von Dutch'
    }
    
    return brand_mapping.get(username_lower, username)

def calculate_hashtag_engagement(data):
    """Calculate average engagement for hashtag"""
    posts = data.get('recentPosts', [])
    if not posts:
        return 0
        
    total_engagement = sum(
        post.get('likesCount', 0) + post.get('commentsCount', 0)
        for post in posts
    )
    
    return round(total_engagement / len(posts), 2) if posts else 0

def calculate_hashtag_velocity(data):
    """Calculate hashtag velocity (growth rate)"""
    recent_posts = data.get('recentPosts', [])
    if len(recent_posts) < 2:
        return 0
        
    velocity = len(recent_posts) * 10
    return min(velocity, 500)

def assess_cultural_relevance(data):
    """Assess cultural relevance of hashtag"""
    hashtag = data.get('hashtag', '').lower()
    
    cultural_keywords = [
        'streetwear', 'fashion', 'style', 'outfit', 'vintage',
        'archive', 'drop', 'collab', 'culture', 'trend'
    ]
    
    relevance_score = sum(1 for keyword in cultural_keywords if keyword in hashtag)
    return min(relevance_score * 20, 100)

def assess_cultural_moment(data):
    """Assess if TikTok content represents a cultural moment"""
    likes = data.get('diggCount', 0)
    shares = data.get('shareCount', 0)
    comments = data.get('commentCount', 0)
    
    total_engagement = likes + (shares * 5) + (comments * 3)
    
    if total_engagement > 100000:
        return 'viral'
    elif total_engagement > 10000:
        return 'trending'
    elif total_engagement > 1000:
        return 'emerging'
    else:
        return 'standard'

def calculate_trend_potential(data):
    """Calculate trend potential score for TikTok content"""
    engagement = data.get('diggCount', 0) + data.get('shareCount', 0) * 2
    hashtag_count = len(data.get('hashtags', []))
    
    potential = (engagement / 1000) + (hashtag_count * 5)
    return min(round(potential, 1), 100)

def update_competitive_rankings(instagram_data):
    """Update competitive brand rankings based on Instagram data"""
    brand_metrics = {}
    
    for post in instagram_data:
        brand = post.get('brand')
        if not brand or brand not in brand_metrics:
            brand_metrics[brand] = {
                'total_posts': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_engagement': 0,
                'avg_engagement_rate': 0
            }
            
        metrics = brand_metrics[brand]
        metrics['total_posts'] += 1
        metrics['total_likes'] += post.get('likes', 0)
        metrics['total_comments'] += post.get('comments', 0)
        metrics['total_engagement'] += post.get('likes', 0) + post.get('comments', 0)
        
    # Calculate averages and rankings
    for brand, metrics in brand_metrics.items():
        if metrics['total_posts'] > 0:
            metrics['avg_likes'] = round(metrics['total_likes'] / metrics['total_posts'], 2)
            metrics['avg_comments'] = round(metrics['total_comments'] / metrics['total_posts'], 2)
            metrics['avg_engagement'] = round(metrics['total_engagement'] / metrics['total_posts'], 2)
            
    # Sort by average engagement
    sorted_brands = sorted(
        brand_metrics.items(),
        key=lambda x: x[1]['avg_engagement'],
        reverse=True
    )
    
    # Create rankings
    rankings = {}
    for i, (brand, metrics) in enumerate(sorted_brands, 1):
        rankings[brand] = {
            'rank': i,
            'metrics': metrics,
            'performance_tier': 'high' if i <= 4 else 'medium' if i <= 8 else 'low'
        }
        
    INTELLIGENCE_DATA['competitive_rankings'] = rankings

def update_cultural_insights(hashtag_data):
    """Update cultural insights based on hashtag data"""
    insights = {
        'trending_hashtags': [],
        'velocity_leaders': [],
        'cultural_themes': [],
        'opportunity_hashtags': []
    }
    
    # Sort hashtags by velocity
    sorted_hashtags = sorted(
        hashtag_data,
        key=lambda x: x.get('velocity', 0),
        reverse=True
    )
    
    # Top trending hashtags
    insights['trending_hashtags'] = [
        {
            'hashtag': h.get('hashtag'),
            'velocity': h.get('velocity'),
            'engagement': h.get('engagement_avg')
        }
        for h in sorted_hashtags[:5]
    ]
    
    # Velocity leaders (high growth)
    insights['velocity_leaders'] = [
        h for h in sorted_hashtags 
        if h.get('velocity', 0) > 100
    ][:3]
    
    # Cultural themes (high relevance)
    insights['cultural_themes'] = [
        h for h in hashtag_data
        if h.get('cultural_relevance', 0) > 60
    ][:5]
    
    # Opportunity hashtags (medium velocity, high relevance)
    insights['opportunity_hashtags'] = [
        h for h in hashtag_data
        if 50 <= h.get('velocity', 0) <= 200 and h.get('cultural_relevance', 0) > 40
    ][:3]
    
    INTELLIGENCE_DATA['cultural_insights'] = insights

def update_tiktok_insights(tiktok_data):
    """Update TikTok cultural insights"""
    viral_content = [
        post for post in tiktok_data
        if post.get('cultural_moment') in ['viral', 'trending']
    ]
    
    trending_sounds = {}
    for post in tiktok_data:
        music = post.get('music', {})
        if music and music.get('title'):
            sound = music.get('title')
            if sound not in trending_sounds:
                trending_sounds[sound] = 0
            trending_sounds[sound] += 1
            
    # Update TikTok insights in cultural data
    if 'tiktok_insights' not in INTELLIGENCE_DATA['cultural_insights']:
        INTELLIGENCE_DATA['cultural_insights']['tiktok_insights'] = {}
        
    INTELLIGENCE_DATA['cultural_insights']['tiktok_insights'] = {
        'viral_content_count': len(viral_content),
        'trending_sounds': dict(sorted(trending_sounds.items(), key=lambda x: x[1], reverse=True)[:5]),
        'cultural_moments': viral_content[:3],
        'trend_potential_avg': sum(p.get('trend_potential', 0) for p in tiktok_data) / len(tiktok_data) if tiktok_data else 0
    }

def get_intelligence_summary():
    """Get competitive intelligence summary"""
    rankings = INTELLIGENCE_DATA.get('competitive_rankings', {})
    
    # Find Crooks & Castles position
    crooks_data = rankings.get('Crooks & Castles', {})
    crooks_rank = crooks_data.get('rank', 'N/A')
    total_brands = len(rankings)
    
    # Get top performer
    top_performer = None
    for brand, data in rankings.items():
        if data.get('rank') == 1:
            top_performer = {
                'brand': brand,
                'avg_engagement': data.get('metrics', {}).get('avg_engagement', 0)
            }
            break
            
    # Data source counts
    data_sources = {
        'instagram': len(INTELLIGENCE_DATA.get('instagram_data', [])),
        'hashtags': len(INTELLIGENCE_DATA.get('hashtag_data', [])),
        'tiktok': len(INTELLIGENCE_DATA.get('tiktok_data', []))
    }
    
    return {
        'crooks_rank': crooks_rank,
        'total_brands': total_brands,
        'top_performer': top_performer,
        'data_sources': data_sources,
        'last_updated': INTELLIGENCE_DATA.get('last_updated'),
        'competitive_gaps': get_competitive_gaps(),
        'opportunities': get_strategic_opportunities()
    }

def get_cultural_radar_data():
    """Get cultural radar insights"""
    cultural_insights = INTELLIGENCE_DATA.get('cultural_insights', {})
    
    return {
        'trending_hashtags': cultural_insights.get('trending_hashtags', []),
        'velocity_leaders': cultural_insights.get('velocity_leaders', []),
        'cultural_themes': cultural_insights.get('cultural_themes', []),
        'opportunity_hashtags': cultural_insights.get('opportunity_hashtags', []),
        'tiktok_insights': cultural_insights.get('tiktok_insights', {}),
        'cultural_moments': [
            'Y2K Revival Momentum',
            'Archive Fashion Resurgence',
            'Sean Paul Collaboration Impact'
        ]
    }

def get_competitive_gaps():
    """Identify competitive gaps"""
    gaps = []
    
    rankings = INTELLIGENCE_DATA.get('competitive_rankings', {})
    crooks_data = rankings.get('Crooks & Castles', {})
    
    if crooks_data.get('rank', 999) > 5:
        gaps.append({
            'type': 'engagement',
            'description': 'Below top 5 in engagement metrics',
            'severity': 'medium'
        })
        
    # Check TikTok presence
    tiktok_insights = INTELLIGENCE_DATA.get('cultural_insights', {}).get('tiktok_insights', {})
    if tiktok_insights.get('viral_content_count', 0) == 0:
        gaps.append({
            'type': 'platform',
            'description': 'Limited TikTok viral content presence',
            'severity': 'high'
        })
        
    return gaps

def get_strategic_opportunities():
    """Get strategic opportunities"""
    opportunities = []
    
    # Check Y2K trend alignment
    cultural_insights = INTELLIGENCE_DATA.get('cultural_insights', {})
    trending_hashtags = cultural_insights.get('trending_hashtags', [])
    
    for hashtag_data in trending_hashtags:
        hashtag = hashtag_data.get('hashtag', '')
        if 'y2k' in hashtag.lower() or 'archive' in hashtag.lower():
            opportunities.append({
                'type': 'trend_alignment',
                'title': 'Y2K Archive Opportunity',
                'description': f"#{hashtag} trending with {hashtag_data.get('velocity')}% velocity",
                'priority': 'high',
                'action': 'Accelerate Archive Remastered collection'
            })
            break
            
    return opportunities

def save_intelligence_data():
    """Save intelligence data to file"""
    try:
        with open('data/intelligence_data.json', 'w') as f:
            json.dump(INTELLIGENCE_DATA, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving intelligence data: {e}")

def load_intelligence_data():
    """Load intelligence data from file"""
    try:
        if os.path.exists('data/intelligence_data.json'):
            with open('data/intelligence_data.json', 'r') as f:
                data = json.load(f)
                INTELLIGENCE_DATA.update(data)
    except Exception as e:
        print(f"Error loading intelligence data: {e}")

# Load intelligence data on startup
load_intelligence_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
