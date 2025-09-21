"""
Crooks & Castles Command Center V2 - Complete Strategic Management Platform
Real data analysis, strategic calendar, agency tracking, and asset management
"""

from flask import Flask, Response, request, jsonify, send_file, abort
import json
import os
from datetime import datetime, timedelta
import uuid
from werkzeug.utils import secure_filename
import hashlib
from collections import defaultdict, Counter
import statistics
import glob

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'crooks_command_center_2025_enhanced')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist
os.makedirs('uploads/assets', exist_ok=True)
os.makedirs('uploads/intelligence', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/thumbnails', exist_ok=True)

# Monitored brands and hashtags
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

ASSET_CATEGORIES = {
    'logos_branding': {'name': 'Logos & Branding', 'icon': '👑', 'color': '#FFD700'},
    'heritage_archive': {'name': 'Heritage Archive', 'icon': '📚', 'color': '#8B4513'},
    'product_photography': {'name': 'Product Photography', 'icon': '📸', 'color': '#FF6B6B'},
    'campaign_creative': {'name': 'Campaign Creative', 'icon': '🎨', 'color': '#4ECDC4'},
    'social_content': {'name': 'Social Content', 'icon': '📱', 'color': '#45B7D1'}
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

def recover_existing_assets():
    """Scan uploads directory and recover existing assets"""
    recovered_assets = {}
    
    # Scan uploads/assets directory
    asset_files = glob.glob('uploads/assets/*')
    
    for filepath in asset_files:
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            file_stats = os.stat(filepath)
            
            asset_id = str(uuid.uuid4())
            asset_info = {
                'id': asset_id,
                'filename': filename,
                'original_name': filename.split('_', 2)[-1] if '_' in filename else filename,  # Remove timestamp prefix
                'size': file_stats.st_size,
                'uploaded_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'file_type': os.path.splitext(filename)[1].lower(),
                'category': 'social_content',  # Default category
                'download_count': 0,
                'recovered': True
            }
            recovered_assets[asset_id] = asset_info
    
    return recovered_assets

def process_intelligence_data(file_path, file_type):
    """Process uploaded intelligence data"""
    try:
        if file_type == 'jsonl':
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line.strip()))
            return data
        elif file_type == 'json':
            with open(file_path, 'r') as f:
                return json.load(f)
    except:
        return []

def analyze_competitive_rankings(intelligence_data):
    """Analyze real data to generate competitive rankings"""
    instagram_data = intelligence_data.get('instagram_data', [])
    
    if not instagram_data:
        return []
    
    # Analyze by brand
    brand_metrics = defaultdict(lambda: {
        'posts': 0,
        'total_likes': 0,
        'total_comments': 0,
        'total_views': 0,
        'engagement_rates': []
    })
    
    for post in instagram_data:
        username = post.get('ownerUsername', '').lower()
        if username in MONITORED_BRANDS:
            likes = post.get('likesCount', 0)
            comments = post.get('commentsCount', 0)
            views = post.get('videoViewCount', 0) or post.get('videoPlayCount', 0)
            
            brand_metrics[username]['posts'] += 1
            brand_metrics[username]['total_likes'] += likes
            brand_metrics[username]['total_comments'] += comments
            brand_metrics[username]['total_views'] += views
            
            # Calculate engagement rate for this post
            total_engagement = likes + comments
            if views > 0:
                engagement_rate = (total_engagement / views) * 100
                brand_metrics[username]['engagement_rates'].append(engagement_rate)
    
    # Calculate final metrics and rank
    rankings = []
    for brand, metrics in brand_metrics.items():
        if metrics['posts'] > 0:
            avg_likes = metrics['total_likes'] / metrics['posts']
            avg_comments = metrics['total_comments'] / metrics['posts']
            avg_engagement = avg_likes + avg_comments
            
            avg_engagement_rate = 0
            if metrics['engagement_rates']:
                avg_engagement_rate = statistics.mean(metrics['engagement_rates'])
            
            rankings.append({
                'brand': brand,
                'posts': metrics['posts'],
                'avg_likes': int(avg_likes),
                'avg_comments': int(avg_comments),
                'avg_engagement': int(avg_engagement),
                'engagement_rate': round(avg_engagement_rate, 2),
                'total_views': metrics['total_views']
            })
    
    # Sort by average engagement
    rankings.sort(key=lambda x: x['avg_engagement'], reverse=True)
    
    # Add rank
    for i, ranking in enumerate(rankings):
        ranking['rank'] = i + 1
    
    return rankings

def analyze_trending_hashtags(intelligence_data):
    """Analyze hashtag data to find trending topics"""
    hashtag_data = intelligence_data.get('hashtag_data', [])
    
    if not hashtag_data:
        return []
    
    hashtag_metrics = defaultdict(lambda: {
        'count': 0,
        'total_likes': 0,
        'total_comments': 0,
        'recent_posts': []
    })
    
    # Analyze hashtag performance
    for post in hashtag_data:
        hashtags = post.get('hashtags', [])
        likes = post.get('likesCount', 0)
        comments = post.get('commentsCount', 0)
        timestamp = post.get('timestamp', '')
        
        for hashtag in hashtags:
            if hashtag.lower() in [h.lower() for h in STRATEGIC_HASHTAGS]:
                hashtag_metrics[hashtag]['count'] += 1
                hashtag_metrics[hashtag]['total_likes'] += likes
                hashtag_metrics[hashtag]['total_comments'] += comments
                hashtag_metrics[hashtag]['recent_posts'].append({
                    'likes': likes,
                    'comments': comments,
                    'timestamp': timestamp
                })
    
    # Calculate trending metrics
    trending = []
    for hashtag, metrics in hashtag_metrics.items():
        if metrics['count'] >= 3:  # Minimum threshold
            avg_engagement = (metrics['total_likes'] + metrics['total_comments']) / metrics['count']
            
            # Determine momentum based on recent activity
            recent_posts = sorted(metrics['recent_posts'], key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            recent_avg = sum(p['likes'] + p['comments'] for p in recent_posts) / len(recent_posts) if recent_posts else 0
            
            momentum = 'rising' if recent_avg > avg_engagement * 0.8 else 'stable'
            
            trending.append({
                'hashtag': hashtag,
                'posts': metrics['count'],
                'avg_engagement': int(avg_engagement),
                'total_engagement': metrics['total_likes'] + metrics['total_comments'],
                'momentum': momentum
            })
    
    trending.sort(key=lambda x: x['avg_engagement'], reverse=True)
    return trending[:10]

def get_strategic_calendar_2025():
    """Get strategic calendar events for 2025"""
    today = datetime.now()
    
    # Strategic events for Crooks & Castles 2025
    events = [
        {
            'id': '1',
            'title': 'Q1 Heritage Collection Launch',
            'date': '2025-01-15',
            'type': 'product_launch',
            'priority': 'high',
            'description': 'Launch of Archive Remastered collection featuring classic designs',
            'status': 'planning',
            'agency': 'Internal Team'
        },
        {
            'id': '2',
            'title': 'Valentine\'s Day Campaign',
            'date': '2025-02-01',
            'type': 'campaign',
            'priority': 'medium',
            'description': 'Limited edition couples collection and social campaign',
            'status': 'in_progress',
            'agency': 'Social Media Agency'
        },
        {
            'id': '3',
            'title': 'Spring/Summer 2025 Collection',
            'date': '2025-03-20',
            'type': 'product_launch',
            'priority': 'high',
            'description': 'Major seasonal collection launch with influencer partnerships',
            'status': 'planning',
            'agency': 'Creative Agency + Influencer Network'
        },
        {
            'id': '4',
            'title': 'Coachella Partnership Activation',
            'date': '2025-04-11',
            'type': 'event',
            'priority': 'high',
            'description': 'Festival partnership and exclusive merchandise drop',
            'status': 'confirmed',
            'agency': 'Event Marketing Agency'
        },
        {
            'id': '5',
            'title': 'Mother\'s Day Limited Edition',
            'date': '2025-05-01',
            'type': 'campaign',
            'priority': 'medium',
            'description': 'Special Mother\'s Day collection and gifting campaign',
            'status': 'planning',
            'agency': 'Internal Team'
        },
        {
            'id': '6',
            'title': 'Summer Solstice Collection',
            'date': '2025-06-21',
            'type': 'product_launch',
            'priority': 'medium',
            'description': 'Summer-themed limited edition pieces',
            'status': 'concept',
            'agency': 'Design Agency'
        },
        {
            'id': '7',
            'title': 'Back-to-School Campaign',
            'date': '2025-08-01',
            'type': 'campaign',
            'priority': 'high',
            'description': 'Target Gen Z with school-focused streetwear campaign',
            'status': 'planning',
            'agency': 'Youth Marketing Agency'
        },
        {
            'id': '8',
            'title': 'Fall/Winter 2025 Collection',
            'date': '2025-09-15',
            'type': 'product_launch',
            'priority': 'high',
            'description': 'Major seasonal collection with heritage focus',
            'status': 'concept',
            'agency': 'Creative Agency'
        },
        {
            'id': '9',
            'title': 'Halloween Limited Drop',
            'date': '2025-10-15',
            'type': 'product_launch',
            'priority': 'medium',
            'description': 'Spooky-themed limited edition collection',
            'status': 'concept',
            'agency': 'Internal Team'
        },
        {
            'id': '10',
            'title': 'Black Friday/Cyber Monday',
            'date': '2025-11-29',
            'type': 'campaign',
            'priority': 'high',
            'description': 'Major sales event with exclusive releases',
            'status': 'planning',
            'agency': 'E-commerce Agency'
        },
        {
            'id': '11',
            'title': 'Holiday 2025 Collection',
            'date': '2025-12-01',
            'type': 'product_launch',
            'priority': 'high',
            'description': 'Premium holiday collection and gift sets',
            'status': 'concept',
            'agency': 'Creative Agency'
        }
    ]
    
    # Add weekly Apify data collection
    apify_events = []
    current_date = datetime(2025, 1, 1)
    while current_date.year == 2025:
        if current_date.weekday() == 6:  # Sunday
            apify_events.append({
                'id': f'apify_{current_date.strftime("%Y%m%d")}',
                'title': 'Apify Data Collection',
                'date': current_date.strftime('%Y-%m-%d'),
                'type': 'intelligence',
                'priority': 'high',
                'description': 'Weekly competitive intelligence data collection and analysis',
                'status': 'scheduled',
                'agency': 'Internal Analytics'
            })
        current_date += timedelta(days=7)
    
    events.extend(apify_events[:20])  # Limit to first 20 weeks
    
    return events

def get_agency_performance_tracking():
    """Get agency performance metrics"""
    return {
        'active_campaigns': [
            {
                'name': 'Valentine\'s Day Campaign',
                'agency': 'Social Media Agency',
                'budget': 50000,
                'spent': 32000,
                'performance': {
                    'impressions': 2500000,
                    'engagement_rate': 4.2,
                    'conversion_rate': 2.8,
                    'roi': 3.2
                },
                'status': 'in_progress',
                'deliverables': {
                    'completed': 8,
                    'pending': 3,
                    'overdue': 1
                }
            },
            {
                'name': 'Heritage Collection Launch',
                'agency': 'Creative Agency',
                'budget': 75000,
                'spent': 15000,
                'performance': {
                    'impressions': 0,
                    'engagement_rate': 0,
                    'conversion_rate': 0,
                    'roi': 0
                },
                'status': 'planning',
                'deliverables': {
                    'completed': 3,
                    'pending': 7,
                    'overdue': 0
                }
            }
        ],
        'agency_scorecards': [
            {
                'agency': 'Social Media Agency',
                'overall_score': 8.5,
                'metrics': {
                    'delivery_timeliness': 9.0,
                    'creative_quality': 8.0,
                    'performance_results': 8.5,
                    'communication': 9.0
                },
                'active_campaigns': 1,
                'total_budget': 50000
            },
            {
                'agency': 'Creative Agency',
                'overall_score': 7.8,
                'metrics': {
                    'delivery_timeliness': 7.5,
                    'creative_quality': 9.0,
                    'performance_results': 7.0,
                    'communication': 8.0
                },
                'active_campaigns': 1,
                'total_budget': 75000
            }
        ]
    }

def get_crooks_position(rankings):
    """Find Crooks & Castles position in rankings"""
    for i, ranking in enumerate(rankings):
        if 'crooks' in ranking['brand'].lower():
            return i + 1, ranking
    return None, None

# Complete HTML template with strategic calendar and agency tracking
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Crooks & Castles Command Center V2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            padding: 1.5rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.5rem;
            font-weight: 800;
        }
        
        .crown {
            font-size: 2rem;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px #FFD700; }
            to { text-shadow: 0 0 20px #FFD700, 0 0 30px #FFD700; }
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF6B6B;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
        }
        
        .main-content {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .nav-tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid rgba(255, 215, 0, 0.3);
            overflow-x: auto;
        }
        
        .nav-tab {
            background: none;
            border: none;
            color: #ccc;
            padding: 1rem 1.5rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
            font-size: 1rem;
            font-weight: 600;
            white-space: nowrap;
        }
        
        .nav-tab.active, .nav-tab:hover {
            color: #FFD700;
            border-bottom-color: #FFD700;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2);
        }
        
        .metric-title {
            font-size: 0.9rem;
            color: #FFD700;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        
        .metric-subtitle {
            font-size: 0.8rem;
            color: #ccc;
        }
        
        .section {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #FFD700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .upload-area {
            border: 2px dashed rgba(255, 215, 0, 0.5);
            border-radius: 12px;
            padding: 3rem;
            text-align: center;
            margin: 1rem 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #FFD700;
            background: rgba(255, 215, 0, 0.1);
        }
        
        .upload-area.dragover {
            border-color: #FFD700;
            background: rgba(255, 215, 0, 0.2);
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .btn {
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        
        .activity-icon {
            font-size: 1.5rem;
        }
        
        .activity-text {
            flex: 1;
        }
        
        .activity-time {
            font-size: 0.8rem;
            color: #ccc;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            margin-right: 0.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }
        
        .asset-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .asset-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .asset-item:hover {
            transform: translateY(-3px);
        }
        
        .brand-ranking {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        
        .brand-ranking.highlight {
            background: rgba(255, 215, 0, 0.2);
            border: 1px solid rgba(255, 215, 0, 0.5);
        }
        
        .campaign-card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #FFD700;
        }
        
        .campaign-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .campaign-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #FFD700;
        }
        
        .campaign-status {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .status-planning { background: rgba(255, 193, 7, 0.2); color: #FFC107; }
        .status-in_progress { background: rgba(33, 150, 243, 0.2); color: #2196F3; }
        .status-confirmed { background: rgba(76, 175, 80, 0.2); color: #4CAF50; }
        .status-concept { background: rgba(156, 39, 176, 0.2); color: #9C27B0; }
        
        .performance-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .performance-metric {
            text-align: center;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }
        
        .performance-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #FFD700;
        }
        
        .performance-label {
            font-size: 0.8rem;
            color: #ccc;
            margin-top: 0.25rem;
        }
        
        .calendar-event {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-left: 4px solid #FFD700;
        }
        
        .event-date {
            font-size: 0.8rem;
            color: #FFD700;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .event-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .event-description {
            font-size: 0.9rem;
            color: #ccc;
        }
        
        .success-message {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid rgba(76, 175, 80, 0.5);
            color: #4CAF50;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            display: none;
        }
        
        .error-message {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid rgba(244, 67, 54, 0.5);
            color: #f44336;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            display: none;
        }
        
        .no-data {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 2rem;
        }
        
        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .main-content {
                padding: 1rem;
            }
            
            .header {
                padding: 1rem;
                flex-direction: column;
                gap: 1rem;
            }
            
            .performance-metrics {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <span class="crown">👑</span>
            <span>Crooks & Castles Command Center V2</span>
        </div>
        <div class="user-info">
            <div class="user-avatar">BM</div>
            <div>
                <div style="font-weight: 600;">Brand Manager</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Strategic Command</div>
            </div>
        </div>
    </div>

    <div class="main-content">
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">📊 Command</button>
            <button class="nav-tab" onclick="showTab('calendar')">📅 Strategic Calendar</button>
            <button class="nav-tab" onclick="showTab('agency')">🎯 Agency Tracking</button>
            <button class="nav-tab" onclick="showTab('intelligence')">🔍 Intelligence</button>
            <button class="nav-tab" onclick="showTab('competitive')">🏆 Competitive</button>
            <button class="nav-tab" onclick="showTab('assets')">🎨 Assets</button>
        </div>

        <!-- Command Dashboard -->
        <div id="dashboard" class="tab-content active">
            <div class="dashboard-grid">
                <div class="metric-card">
                    <div class="metric-title">Competitive Position</div>
                    <div class="metric-value" id="competitive-rank">Loading...</div>
                    <div class="metric-subtitle" id="rank-change">Analyzing data...</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Active Campaigns</div>
                    <div class="metric-value" id="active-campaigns">2</div>
                    <div class="metric-subtitle">$125K total budget</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Strategic Events</div>
                    <div class="metric-value" id="strategic-events">11</div>
                    <div class="metric-subtitle">2025 roadmap</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Intelligence Data</div>
                    <div class="metric-value" id="intelligence-data">0 records</div>
                    <div class="metric-subtitle"><span class="status-indicator"></span>Real-time analysis</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">⚡ Command Overview</div>
                <div id="command-overview">
                    <div class="activity-item">
                        <div class="activity-icon">🚀</div>
                        <div class="activity-text">
                            <strong>Valentine's Day Campaign</strong>
                            <div style="font-size: 0.8rem; color: #ccc;">In progress - Social Media Agency</div>
                        </div>
                        <div class="activity-time">64% budget used</div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">📅</div>
                        <div class="activity-text">
                            <strong>Q1 Heritage Collection Launch</strong>
                            <div style="font-size: 0.8rem; color: #ccc;">Jan 15, 2025 - Planning phase</div>
                        </div>
                        <div class="activity-time">20% budget used</div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">📊</div>
                        <div class="activity-text">
                            <strong>Weekly Apify Data Collection</strong>
                            <div style="font-size: 0.8rem; color: #ccc;">Competitive intelligence monitoring</div>
                        </div>
                        <div class="activity-time">Automated</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Strategic Calendar -->
        <div id="calendar" class="tab-content">
            <div class="section">
                <div class="section-title">📅 2025 Strategic Calendar</div>
                <div id="calendar-events">
                    <div class="calendar-event">
                        <div class="event-date">January 15, 2025</div>
                        <div class="event-title">Q1 Heritage Collection Launch</div>
                        <div class="event-description">Launch of Archive Remastered collection featuring classic designs</div>
                    </div>
                    <div class="calendar-event">
                        <div class="event-date">February 1, 2025</div>
                        <div class="event-title">Valentine's Day Campaign</div>
                        <div class="event-description">Limited edition couples collection and social campaign</div>
                    </div>
                    <div class="calendar-event">
                        <div class="event-date">March 20, 2025</div>
                        <div class="event-title">Spring/Summer 2025 Collection</div>
                        <div class="event-description">Major seasonal collection launch with influencer partnerships</div>
                    </div>
                    <div class="calendar-event">
                        <div class="event-date">April 11, 2025</div>
                        <div class="event-title">Coachella Partnership Activation</div>
                        <div class="event-description">Festival partnership and exclusive merchandise drop</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Agency Tracking -->
        <div id="agency" class="tab-content">
            <div class="section">
                <div class="section-title">🎯 Active Campaign Performance</div>
                <div id="active-campaign-performance">
                    <div class="campaign-card">
                        <div class="campaign-header">
                            <div class="campaign-title">Valentine's Day Campaign</div>
                            <div class="campaign-status status-in_progress">In Progress</div>
                        </div>
                        <div><strong>Agency:</strong> Social Media Agency</div>
                        <div><strong>Budget:</strong> $50,000 | <strong>Spent:</strong> $32,000 (64%)</div>
                        <div class="performance-metrics">
                            <div class="performance-metric">
                                <div class="performance-value">2.5M</div>
                                <div class="performance-label">Impressions</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">4.2%</div>
                                <div class="performance-label">Engagement</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">2.8%</div>
                                <div class="performance-label">Conversion</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">3.2x</div>
                                <div class="performance-label">ROI</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="campaign-card">
                        <div class="campaign-header">
                            <div class="campaign-title">Heritage Collection Launch</div>
                            <div class="campaign-status status-planning">Planning</div>
                        </div>
                        <div><strong>Agency:</strong> Creative Agency</div>
                        <div><strong>Budget:</strong> $75,000 | <strong>Spent:</strong> $15,000 (20%)</div>
                        <div class="performance-metrics">
                            <div class="performance-metric">
                                <div class="performance-value">3/10</div>
                                <div class="performance-label">Deliverables</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">Jan 15</div>
                                <div class="performance-label">Launch Date</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">On Track</div>
                                <div class="performance-label">Timeline</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">High</div>
                                <div class="performance-label">Priority</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">📊 Agency Scorecards</div>
                <div id="agency-scorecards">
                    <div class="campaign-card">
                        <div class="campaign-header">
                            <div class="campaign-title">Social Media Agency</div>
                            <div class="campaign-status status-confirmed">8.5/10</div>
                        </div>
                        <div class="performance-metrics">
                            <div class="performance-metric">
                                <div class="performance-value">9.0</div>
                                <div class="performance-label">Timeliness</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">8.0</div>
                                <div class="performance-label">Quality</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">8.5</div>
                                <div class="performance-label">Results</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">9.0</div>
                                <div class="performance-label">Communication</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="campaign-card">
                        <div class="campaign-header">
                            <div class="campaign-title">Creative Agency</div>
                            <div class="campaign-status status-planning">7.8/10</div>
                        </div>
                        <div class="performance-metrics">
                            <div class="performance-metric">
                                <div class="performance-value">7.5</div>
                                <div class="performance-label">Timeliness</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">9.0</div>
                                <div class="performance-label">Quality</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">7.0</div>
                                <div class="performance-label">Results</div>
                            </div>
                            <div class="performance-metric">
                                <div class="performance-value">8.0</div>
                                <div class="performance-label">Communication</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Intelligence Tab -->
        <div id="intelligence" class="tab-content">
            <div class="grid-2">
                <div class="section">
                    <div class="section-title">📊 Upload Intelligence Data</div>
                    <p>Upload your Apify JSONL files for competitive analysis and cultural insights.</p>
                    
                    <div class="upload-area" onclick="document.getElementById('intelligence-upload').click()">
                        <div class="upload-icon">📈</div>
                        <div><strong>Drop JSONL files here or click to upload</strong></div>
                        <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #ccc;">
                            Supported: Instagram, Hashtag, TikTok JSONL files
                        </div>
                    </div>
                    <input type="file" id="intelligence-upload" style="display: none;" accept=".jsonl,.json,.csv" onchange="uploadFile(this, 'intelligence')">
                    
                    <div class="success-message" id="intelligence-success"></div>
                    <div class="error-message" id="intelligence-error"></div>
                </div>

                <div class="section">
                    <div class="section-title">🎯 Data Analysis Status</div>
                    <div id="analysis-status">
                        <div class="no-data">No data uploaded yet</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Competitive Tab -->
        <div id="competitive" class="tab-content">
            <div class="section">
                <div class="section-title">🏆 Real Brand Rankings</div>
                <div id="brand-rankings">
                    <div class="no-data">Upload Instagram data to see real competitive rankings</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">📈 Trending Hashtags</div>
                <div id="trending-hashtags">
                    <div class="no-data">Upload hashtag data to see trending topics</div>
                </div>
            </div>
        </div>

        <!-- Assets Tab -->
        <div id="assets" class="tab-content">
            <div class="section">
                <div class="section-title">🎨 Asset Library</div>
                <p>Upload and manage brand assets. <strong>Scanning for existing assets...</strong></p>
                
                <div class="upload-area" onclick="document.getElementById('asset-upload').click()">
                    <div class="upload-icon">🖼️</div>
                    <div><strong>Drop assets here or click to upload</strong></div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #ccc;">
                        Images, Videos, Documents, Design Files
                    </div>
                </div>
                <input type="file" id="asset-upload" style="display: none;" multiple onchange="uploadFile(this, 'asset')">
                
                <div class="success-message" id="asset-success"></div>
                <div class="error-message" id="asset-error"></div>
            </div>

            <div class="section">
                <div class="section-title">📁 Asset Categories</div>
                <div class="asset-grid">
                    <div class="asset-item">
                        <div style="font-size: 2rem;">👑</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Logos & Branding</div>
                        <div style="font-size: 0.8rem; color: #ccc;" id="logos-count">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">📚</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Heritage Archive</div>
                        <div style="font-size: 0.8rem; color: #ccc;" id="heritage-count">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">📸</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Product Photography</div>
                        <div style="font-size: 0.8rem; color: #ccc;" id="product-count">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">🎨</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Campaign Creative</div>
                        <div style="font-size: 0.8rem; color: #ccc;" id="campaign-count">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">📱</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Social Content</div>
                        <div style="font-size: 0.8rem; color: #ccc;" id="social-count">0 assets</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">📋 All Assets</div>
                <div id="all-assets">
                    <div class="no-data">Scanning for existing assets...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Tab switching functionality
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.classList.add('active');
        }

        // File upload functionality
        function uploadFile(input, type) {
            const files = input.files;
            if (files.length === 0) return;

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);
            }

            const endpoint = type === 'intelligence' ? '/upload/intelligence' : '/upload/asset';
            const successElement = document.getElementById(type + '-success');
            const errorElement = document.getElementById(type + '-error');
            
            // Hide previous messages
            successElement.style.display = 'none';
            errorElement.style.display = 'none';
            
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    errorElement.textContent = 'Upload failed: ' + data.error;
                    errorElement.style.display = 'block';
                } else {
                    successElement.textContent = data.message || 'Upload successful!';
                    successElement.style.display = 'block';
                    refreshData();
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                errorElement.textContent = 'Upload failed. Please try again.';
                errorElement.style.display = 'block';
            });
        }

        // Drag and drop functionality
        document.querySelectorAll('.upload-area').forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                const input = area.nextElementSibling;
                input.files = files;
                
                const type = input.id.includes('intelligence') ? 'intelligence' : 'asset';
                uploadFile(input, type);
            });
        });

        // Refresh all data
        function refreshData() {
            // Get intelligence summary
            fetch('/api/intelligence/summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('competitive-rank').textContent = data.competitive_rank || 'No data';
                    document.getElementById('rank-change').textContent = data.rank_change || 'Upload data to analyze';
                    document.getElementById('intelligence-data').textContent = data.data_points || '0 records';
                    
                    // Update analysis status
                    const statusDiv = document.getElementById('analysis-status');
                    if (data.has_data) {
                        statusDiv.innerHTML = `
                            <div class="activity-item">
                                <div class="activity-icon">📊</div>
                                <div class="activity-text">
                                    <strong>Instagram Data:</strong> ${data.instagram_count || 0} posts analyzed
                                </div>
                            </div>
                            <div class="activity-item">
                                <div class="activity-icon">📈</div>
                                <div class="activity-text">
                                    <strong>Hashtag Data:</strong> ${data.hashtag_count || 0} posts analyzed
                                </div>
                            </div>
                            <div class="activity-item">
                                <div class="activity-icon">🎵</div>
                                <div class="activity-text">
                                    <strong>TikTok Data:</strong> ${data.tiktok_count || 0} posts analyzed
                                </div>
                            </div>
                        `;
                    }
                });
            
            // Get competitive rankings
            fetch('/api/competitive/rankings')
                .then(response => response.json())
                .then(data => {
                    const rankingsDiv = document.getElementById('brand-rankings');
                    if (data.rankings && data.rankings.length > 0) {
                        rankingsDiv.innerHTML = data.rankings.map(ranking => `
                            <div class="brand-ranking ${ranking.brand.includes('crooks') ? 'highlight' : ''}">
                                <div>
                                    <strong>${ranking.rank}. ${ranking.brand}</strong>
                                    <div style="font-size: 0.8rem; color: #ccc;">${ranking.posts} posts analyzed</div>
                                </div>
                                <div style="text-align: right;">
                                    <div>${ranking.avg_engagement.toLocaleString()} avg engagement</div>
                                    <div style="font-size: 0.8rem; color: #4CAF50;">${ranking.engagement_rate}% rate</div>
                                </div>
                            </div>
                        `).join('');
                    }
                });
            
            // Get trending hashtags
            fetch('/api/cultural/trends')
                .then(response => response.json())
                .then(data => {
                    const trendingDiv = document.getElementById('trending-hashtags');
                    if (data.trending_hashtags && data.trending_hashtags.length > 0) {
                        trendingDiv.innerHTML = data.trending_hashtags.map(hashtag => `
                            <div class="activity-item">
                                <div class="activity-icon">📈</div>
                                <div class="activity-text">
                                    <strong>#${hashtag.hashtag}</strong>
                                    <div style="font-size: 0.8rem; color: #ccc;">${hashtag.posts} posts, ${hashtag.avg_engagement.toLocaleString()} avg engagement</div>
                                </div>
                                <div class="activity-time">${hashtag.momentum}</div>
                            </div>
                        `).join('');
                    }
                });
            
            // Get assets (including recovered ones)
            fetch('/api/assets')
                .then(response => response.json())
                .then(data => {
                    const assets = data.assets || [];
                    document.getElementById('logos-count').textContent = assets.filter(a => a.category === 'logos_branding').length + ' assets';
                    document.getElementById('heritage-count').textContent = assets.filter(a => a.category === 'heritage_archive').length + ' assets';
                    document.getElementById('product-count').textContent = assets.filter(a => a.category === 'product_photography').length + ' assets';
                    document.getElementById('campaign-count').textContent = assets.filter(a => a.category === 'campaign_creative').length + ' assets';
                    document.getElementById('social-count').textContent = assets.filter(a => a.category === 'social_content').length + ' assets';
                    
                    // Update all assets display
                    const allAssetsDiv = document.getElementById('all-assets');
                    if (assets.length > 0) {
                        allAssetsDiv.innerHTML = assets.map(asset => 
                            `<div class="activity-item">
                                <div class="activity-icon">📁</div>
                                <div class="activity-text">
                                    <strong>${asset.original_name}</strong>
                                    <div style="font-size: 0.8rem; color: #ccc;">${(asset.size / 1024 / 1024).toFixed(2)} MB ${asset.recovered ? '(Recovered)' : ''}</div>
                                </div>
                                <div class="activity-time">
                                    <a href="/download/${asset.filename}" class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Download</a>
                                </div>
                            </div>`
                        ).join('');
                    } else {
                        allAssetsDiv.innerHTML = '<div class="no-data">No assets found. Upload your first asset above!</div>';
                    }
                });
        }

        // Auto-refresh data every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial data load
        refreshData();
    </script>
</body>
</html>"""

@app.route('/')
def dashboard():
    """Main command center dashboard"""
    return Response(HTML_TEMPLATE, mimetype='text/html')

@app.route('/api/intelligence/summary')
def intelligence_summary():
    """Get intelligence summary with real analysis"""
    intelligence_data = load_json_data('data/intelligence_data.json', {})
    
    instagram_count = len(intelligence_data.get('instagram_data', []))
    hashtag_count = len(intelligence_data.get('hashtag_data', []))
    tiktok_count = len(intelligence_data.get('tiktok_data', []))
    total_records = instagram_count + hashtag_count + tiktok_count
    
    # Analyze competitive position
    rankings = analyze_competitive_rankings(intelligence_data)
    crooks_position, crooks_data = get_crooks_position(rankings)
    
    # Analyze trending hashtags
    trending = analyze_trending_hashtags(intelligence_data)
    
    return jsonify({
        'competitive_rank': f"#{crooks_position}/{len(rankings)}" if crooks_position else "Not ranked",
        'rank_change': f"Based on {instagram_count} posts" if instagram_count > 0 else "No data",
        'trending_count': len(trending),
        'trending_info': f"{len(trending)} hashtags trending" if trending else "No trending data",
        'data_points': f"{total_records} records",
        'last_updated': intelligence_data.get('last_updated'),
        'has_data': total_records > 0,
        'instagram_count': instagram_count,
        'hashtag_count': hashtag_count,
        'tiktok_count': tiktok_count
    })

@app.route('/upload/intelligence', methods=['POST'])
def upload_intelligence():
    """Upload and process intelligence data with analysis"""
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
        
        # Process the data
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        processed_data = process_intelligence_data(filepath, file_ext)
        
        # Update intelligence data
        intelligence_data = load_json_data('data/intelligence_data.json', {
            'instagram_data': [],
            'hashtag_data': [],
            'tiktok_data': [],
            'last_updated': None
        })
        
        if 'instagram' in file.filename.lower():
            intelligence_data['instagram_data'].extend(processed_data)
        elif 'hashtag' in file.filename.lower():
            intelligence_data['hashtag_data'].extend(processed_data)
        elif 'tiktok' in file.filename.lower():
            intelligence_data['tiktok_data'].extend(processed_data)
        
        intelligence_data['last_updated'] = datetime.now().isoformat()
        save_json_data('data/intelligence_data.json', intelligence_data)
        
        # Generate insights immediately
        rankings = analyze_competitive_rankings(intelligence_data)
        trending = analyze_trending_hashtags(intelligence_data)
        
        return jsonify({
            'message': f'Intelligence data uploaded and analyzed! Processed {len(processed_data)} records.',
            'processed_records': len(processed_data),
            'analysis': {
                'competitive_rankings': len(rankings),
                'trending_hashtags': len(trending)
            }
        })
    
    return jsonify({'error': 'Invalid file type. Please upload JSONL, JSON, or CSV files.'}), 400

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
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join('uploads/assets', unique_filename)
        
        file.save(filepath)
        
        asset_id = str(uuid.uuid4())
        asset_info = {
            'id': asset_id,
            'filename': unique_filename,
            'original_name': file.filename,
            'size': os.path.getsize(filepath),
            'uploaded_at': datetime.now().isoformat(),
            'file_type': file_ext.lower(),
            'category': 'social_content',  # Default category
            'download_count': 0
        }
        
        # Save to asset library
        asset_library = load_json_data('data/asset_library.json', {'assets': {}})
        asset_library['assets'][asset_id] = asset_info
        save_json_data('data/asset_library.json', asset_library)
        
        return jsonify({
            'message': f'Asset "{file.filename}" uploaded successfully!',
            'asset_info': asset_info
        })
    
    return jsonify({'error': 'Upload failed'}), 400

@app.route('/api/assets')
def get_assets():
    """Get asset library including recovered assets"""
    # Load existing asset library
    asset_library = load_json_data('data/asset_library.json', {'assets': {}})
    
    # Recover any existing assets not in the library
    recovered_assets = recover_existing_assets()
    
    # Merge recovered assets with existing library
    all_assets = {**asset_library.get('assets', {}), **recovered_assets}
    
    # Update the asset library with recovered assets
    if recovered_assets:
        asset_library['assets'] = all_assets
        save_json_data('data/asset_library.json', asset_library)
    
    assets = list(all_assets.values())
    assets.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
    
    return jsonify({
        'assets': assets,
        'total': len(assets),
        'recovered': len(recovered_assets),
        'categories': ASSET_CATEGORIES
    })

@app.route('/api/competitive/rankings')
def competitive_rankings():
    """Get real competitive rankings"""
    intelligence_data = load_json_data('data/intelligence_data.json', {})
    rankings = analyze_competitive_rankings(intelligence_data)
    
    return jsonify({
        'rankings': rankings,
        'total_brands': len(rankings),
        'last_updated': intelligence_data.get('last_updated')
    })

@app.route('/api/cultural/trends')
def cultural_trends():
    """Get real trending hashtags"""
    intelligence_data = load_json_data('data/intelligence_data.json', {})
    trending = analyze_trending_hashtags(intelligence_data)
    
    return jsonify({
        'trending_hashtags': trending,
        'last_updated': intelligence_data.get('last_updated')
    })

@app.route('/api/calendar/events')
def get_calendar_events():
    """Get strategic calendar events for 2025"""
    events = get_strategic_calendar_2025()
    return jsonify(events)

@app.route('/api/agency/performance')
def get_agency_performance():
    """Get agency performance tracking data"""
    performance_data = get_agency_performance_tracking()
    return jsonify(performance_data)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download file with tracking"""
    for subdir in ['assets', 'intelligence']:
        filepath = os.path.join('uploads', subdir, filename)
        if os.path.exists(filepath):
            # Update download count if it's an asset
            if subdir == 'assets':
                asset_library = load_json_data('data/asset_library.json', {'assets': {}})
                for asset_id, asset_info in asset_library.get('assets', {}).items():
                    if asset_info.get('filename') == filename:
                        asset_info['download_count'] = asset_info.get('download_count', 0) + 1
                        asset_info['last_accessed'] = datetime.now().isoformat()
                        save_json_data('data/asset_library.json', asset_library)
                        break
            
            return send_file(filepath, as_attachment=True)
    
    return abort(404)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'features': {
            'strategic_calendar': True,
            'agency_tracking': True,
            'intelligent_analysis': True,
            'asset_recovery': True,
            'real_data_processing': True,
            'competitive_rankings': True
        }
    })

if __name__ == '__main__':
    # Get port from environment
    port_env = os.environ.get("PORT", "5000")
    
    try:
        port = int(port_env)
    except (ValueError, TypeError):
        port = 5000
    
    app.run(host='0.0.0.0', port=port, debug=False)
