from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
from datetime import datetime, timedelta, date
import pandas as pd
from calendar_manager import CrooksCalendarManager
from asset_manager import CrooksAssetManager
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'crooks_command_center_2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize managers
calendar_manager = CrooksCalendarManager()
asset_manager = CrooksAssetManager()

# Ensure upload directories exist
os.makedirs('uploads/assets', exist_ok=True)
os.makedirs('uploads/intelligence', exist_ok=True)
os.makedirs('data', exist_ok=True)

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
    current_user_id = session.get('user_id', 'brand_manager_1')
    
    # Get collaborative dashboard data
    dashboard_data = asset_manager.get_collaborative_dashboard(current_user_id)
    
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
    
    return render_template('index.html',
                         dashboard_data=dashboard_data,
                         calendar_view=calendar_view,
                         upcoming_events=upcoming_events,
                         strategic_calendar=strategic_calendar,
                         intelligence_summary=intelligence_summary,
                         cultural_radar=cultural_radar,
                         monitored_brands=MONITORED_BRANDS,
                         strategic_hashtags=STRATEGIC_HASHTAGS)

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
            
        # Save uploaded file
        filename = secure_filename(f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
        filepath = os.path.join('uploads/intelligence', filename)
        file.save(filepath)
        
        # Process the JSONL data
        processed_data = process_intelligence_file(filepath, data_type)
        
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
            'insights_generated': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

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
    # This would typically compare current vs previous period
    # For now, return a calculated velocity based on recent activity
    recent_posts = data.get('recentPosts', [])
    if len(recent_posts) < 2:
        return 0
        
    # Simple velocity calculation based on post frequency
    velocity = len(recent_posts) * 10  # Simplified calculation
    return min(velocity, 500)  # Cap at 500%

def assess_cultural_relevance(data):
    """Assess cultural relevance of hashtag"""
    hashtag = data.get('hashtag', '').lower()
    
    cultural_keywords = [
        'streetwear', 'fashion', 'style', 'outfit', 'vintage',
        'archive', 'drop', 'collab', 'culture', 'trend'
    ]
    
    relevance_score = sum(1 for keyword in cultural_keywords if keyword in hashtag)
    return min(relevance_score * 20, 100)  # Convert to percentage

def assess_cultural_moment(data):
    """Assess if TikTok content represents a cultural moment"""
    likes = data.get('diggCount', 0)
    shares = data.get('shareCount', 0)
    comments = data.get('commentCount', 0)
    
    # High engagement indicates potential cultural moment
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
    
    # Simple trend potential calculation
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
            
    return {
        'crooks_rank': crooks_rank,
        'total_brands': total_brands,
        'top_performer': top_performer,
        'last_updated': INTELLIGENCE_DATA.get('last_updated'),
        'data_sources': {
            'instagram': len(INTELLIGENCE_DATA.get('instagram_data', [])),
            'hashtags': len(INTELLIGENCE_DATA.get('hashtag_data', [])),
            'tiktok': len(INTELLIGENCE_DATA.get('tiktok_data', []))
        }
    }

def get_cultural_radar_data():
    """Get cultural radar insights"""
    cultural_insights = INTELLIGENCE_DATA.get('cultural_insights', {})
    
    return {
        'trending_hashtags': cultural_insights.get('trending_hashtags', []),
        'velocity_leaders': cultural_insights.get('velocity_leaders', []),
        'cultural_themes': cultural_insights.get('cultural_themes', []),
        'tiktok_insights': cultural_insights.get('tiktok_insights', {}),
        'strategic_opportunities': generate_strategic_opportunities()
    }

def generate_strategic_opportunities():
    """Generate strategic opportunities based on intelligence data"""
    opportunities = []
    
    # Check competitive gaps
    rankings = INTELLIGENCE_DATA.get('competitive_rankings', {})
    crooks_data = rankings.get('Crooks & Castles', {})
    
    if crooks_data.get('rank', 12) > 6:
        opportunities.append({
            'type': 'competitive_gap',
            'title': 'Engagement Rate Improvement',
            'description': 'Significant opportunity to improve competitive ranking through increased engagement',
            'priority': 'high',
            'action': 'Implement content frequency optimization'
        })
        
    # Check cultural trends
    cultural_insights = INTELLIGENCE_DATA.get('cultural_insights', {})
    trending_hashtags = cultural_insights.get('trending_hashtags', [])
    
    if trending_hashtags:
        top_trend = trending_hashtags[0]
        if 'y2k' in top_trend.get('hashtag', '').lower():
            opportunities.append({
                'type': 'cultural_trend',
                'title': 'Y2K Revival Opportunity',
                'description': f"#{top_trend.get('hashtag')} showing {top_trend.get('velocity')}% velocity",
                'priority': 'high',
                'action': 'Launch Archive Remastered collection'
            })
            
    # Check TikTok presence
    tiktok_insights = cultural_insights.get('tiktok_insights', {})
    if tiktok_insights.get('viral_content_count', 0) == 0:
        opportunities.append({
            'type': 'platform_gap',
            'title': 'TikTok Platform Expansion',
            'description': 'Zero viral content presence while competitors gain Gen Z mindshare',
            'priority': 'medium',
            'action': 'Develop TikTok content strategy'
        })
        
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

# API Routes for collaborative features

@app.route('/api/projects')
def get_projects():
    """Get all collaborative projects"""
    user_id = request.args.get('user_id', 'brand_manager_1')
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

@app.route('/api/assets')
def get_assets():
    """Get brand assets"""
    category = request.args.get('category')
    if category:
        assets = asset_manager.get_assets_by_category(category)
    else:
        assets = asset_manager.assets
    return jsonify(assets)

@app.route('/api/assets', methods=['POST'])
def upload_asset():
    """Upload new brand asset"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        asset_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'subcategory': request.form.get('subcategory'),
            'created_by': request.form.get('created_by', 'unknown')
        }
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads/assets', filename)
        file.save(filepath)
        
        asset_data['file_path'] = filepath
        asset_data['file_type'] = filename.split('.')[-1].lower()
        
        asset_id = asset_manager.add_asset(asset_data)
        return jsonify({'success': True, 'asset_id': asset_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/approval/submit', methods=['POST'])
def submit_for_approval():
    """Submit asset for approval"""
    try:
        data = request.json
        asset_id = data.get('asset_id')
        user_id = data.get('user_id')
        
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
        user_id = data.get('user_id')
        notes = data.get('notes', '')
        
        success = asset_manager.approve_asset(asset_id, user_id, notes)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load intelligence data on startup
load_intelligence_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
