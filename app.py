from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = 'crooks-castles-command-center-2025'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jsonl', 'json', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Crooks & Castles Brand Configuration
CROOKS_BRAND_CONFIG = {
    'company_name': 'Crooks & Castles',
    'industry': 'Streetwear Fashion',
    'founded': 2002,
    'brand_codes': [
        'Hustle → Heritage',
        'Code Over Clothes', 
        'Streets → Castles',
        'Icons Reborn'
    ],
    'competitors': [
        'Supreme', 'Stussy', 'Fear of God Essentials', 'Hellstar',
        'Diamond Supply Co.', 'LRG', 'Ed Hardy', 'Von Dutch',
        'Reason Clothing', 'Godspeed', 'Smoke Rise'
    ],
    'strategic_hashtags': [
        'streetwear', 'crooksandcastles', 'y2kfashion', 'vintagestreetwear',
        'streetweararchive', 'streetweardrop', 'heritagebrand', 'supremedrop',
        'hellstar', 'fearofgod', 'diamondsupply', 'edhardy', 'vondutch',
        'streetwearculture', 'hypebeast'
    ],
    'tiktok_searches': [
        'crooks and castles', 'streetwear haul', 'streetwear drop',
        'y2k fashion', 'vintage streetwear', 'thrift streetwear',
        'streetwear archive', 'supreme unboxing', 'hellstar outfit',
        'fear of god essentials'
    ]
}

@app.route('/')
def dashboard():
    """Main Crooks & Castles Command Center Dashboard"""
    return render_template('index.html', 
                         brand_config=CROOKS_BRAND_CONFIG,
                         page_title='Crooks & Castles Command Center V2')

@app.route('/api/upload', methods=['POST'])
def upload_intelligence_data():
    """Upload and process competitive intelligence data from Apify scrapers"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the uploaded data
            analysis = process_intelligence_file(filepath, filename)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': analysis,
                'message': f'Successfully processed {analysis["total_records"]} records'
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

def process_intelligence_file(filepath, filename):
    """Process uploaded intelligence data and generate competitive analysis"""
    
    # Determine data type and load data
    if filename.endswith('.jsonl'):
        data = load_jsonl_data(filepath)
    elif filename.endswith('.json'):
        with open(filepath, 'r') as f:
            data = json.load(f)
    else:
        # CSV processing
        df = pd.read_csv(filepath)
        data = df.to_dict('records')
    
    # Detect data source type
    data_type = detect_data_source(data, filename)
    
    # Generate analysis based on data type
    if data_type == 'instagram':
        analysis = analyze_instagram_data(data)
    elif data_type == 'hashtags':
        analysis = analyze_hashtag_data(data)
    elif data_type == 'tiktok':
        analysis = analyze_tiktok_data(data)
    else:
        analysis = {'total_records': len(data), 'data_type': 'unknown'}
    
    analysis['data_type'] = data_type
    analysis['total_records'] = len(data)
    analysis['processed_at'] = datetime.now().isoformat()
    
    return analysis

def load_jsonl_data(filepath):
    """Load JSONL data from Apify scrapers"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return data

def detect_data_source(data, filename):
    """Detect whether data is from Instagram, hashtag, or TikTok scraper"""
    if not data:
        return 'unknown'
    
    sample = data[0]
    
    # TikTok detection
    if 'videoUrl' in sample or 'musicMeta' in sample or 'diggCount' in sample:
        return 'tiktok'
    
    # Hashtag detection
    if 'hashtag' in sample or (isinstance(sample.get('url', ''), str) and '/explore/tags/' in sample.get('url', '')):
        return 'hashtags'
    
    # Default to Instagram
    return 'instagram'

def analyze_instagram_data(data):
    """Analyze Instagram competitive intelligence data"""
    brand_metrics = {}
    cultural_moments = []
    
    for post in data:
        brand = extract_brand_from_post(post)
        
        if brand not in brand_metrics:
            brand_metrics[brand] = {
                'posts': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_engagement': 0,
                'followers': post.get('ownerFollowersCount', 0)
            }
        
        likes = post.get('likesCount', 0)
        comments = post.get('commentsCount', 0)
        engagement = likes + comments
        
        brand_metrics[brand]['posts'] += 1
        brand_metrics[brand]['total_likes'] += likes
        brand_metrics[brand]['total_comments'] += comments
        brand_metrics[brand]['total_engagement'] += engagement
        
        # Identify viral content (cultural moments)
        if engagement > 1000:
            cultural_moments.append({
                'brand': brand,
                'content': post.get('caption', 'No caption')[:100],
                'engagement': engagement,
                'url': post.get('url', ''),
                'timestamp': post.get('timestamp', '')
            })
    
    # Calculate competitive rankings
    rankings = []
    for brand, metrics in brand_metrics.items():
        if metrics['posts'] > 0:
            avg_engagement = metrics['total_engagement'] / metrics['posts']
            rankings.append({
                'brand': brand,
                'rank': 0,  # Will be set after sorting
                'posts': metrics['posts'],
                'avg_engagement': round(avg_engagement),
                'total_engagement': metrics['total_engagement'],
                'followers': metrics['followers']
            })
    
    # Sort by average engagement and assign ranks
    rankings.sort(key=lambda x: x['avg_engagement'], reverse=True)
    for i, ranking in enumerate(rankings):
        ranking['rank'] = i + 1
    
    # Find Crooks & Castles position
    crooks_rank = next((r for r in rankings if 'crooks' in r['brand'].lower()), None)
    
    return {
        'brand_metrics': brand_metrics,
        'competitive_rankings': rankings,
        'cultural_moments': sorted(cultural_moments, key=lambda x: x['engagement'], reverse=True)[:10],
        'crooks_position': crooks_rank,
        'strategic_insights': generate_instagram_insights(rankings, crooks_rank)
    }

def analyze_hashtag_data(data):
    """Analyze hashtag trend data for cultural radar"""
    hashtag_metrics = {}
    trending_themes = []
    
    for post in data:
        hashtag = post.get('hashtag') or extract_hashtag_from_url(post.get('url', ''))
        
        if hashtag not in hashtag_metrics:
            hashtag_metrics[hashtag] = {
                'posts': 0,
                'total_engagement': 0,
                'velocity': calculate_hashtag_velocity(hashtag, data)
            }
        
        engagement = (post.get('likesCount', 0) + post.get('commentsCount', 0))
        hashtag_metrics[hashtag]['posts'] += 1
        hashtag_metrics[hashtag]['total_engagement'] += engagement
    
    # Create trending themes
    for hashtag, metrics in hashtag_metrics.items():
        if metrics['posts'] >= 2:  # Minimum threshold
            trending_themes.append({
                'theme': hashtag,
                'posts': metrics['posts'],
                'velocity': metrics['velocity'],
                'avg_engagement': round(metrics['total_engagement'] / metrics['posts']) if metrics['posts'] > 0 else 0
            })
    
    # Sort by velocity
    trending_themes.sort(key=lambda x: x['velocity'], reverse=True)
    
    return {
        'hashtag_metrics': hashtag_metrics,
        'trending_themes': trending_themes[:10],
        'cultural_insights': generate_hashtag_insights(trending_themes)
    }

def analyze_tiktok_data(data):
    """Analyze TikTok cultural intelligence data"""
    cultural_insights = []
    sound_trends = {}
    creator_insights = {}
    
    for video in data:
        engagement = (video.get('diggCount', 0) + 
                     video.get('shareCount', 0) + 
                     video.get('commentCount', 0))
        
        # High-engagement content analysis
        if engagement > 5000:
            cultural_insights.append({
                'description': video.get('text', 'No description')[:100],
                'engagement': engagement,
                'author': video.get('authorMeta', {}).get('nickName', 'Unknown'),
                'views': video.get('playCount', 0),
                'hashtags': video.get('hashtags', [])
            })
        
        # Sound trend analysis
        music_meta = video.get('musicMeta', {})
        if music_meta:
            music_title = music_meta.get('musicName', 'Unknown')
            if music_title not in sound_trends:
                sound_trends[music_title] = {'count': 0, 'total_engagement': 0}
            sound_trends[music_title]['count'] += 1
            sound_trends[music_title]['total_engagement'] += engagement
    
    # Sort cultural insights by engagement
    cultural_insights.sort(key=lambda x: x['engagement'], reverse=True)
    
    return {
        'cultural_insights': cultural_insights[:10],
        'sound_trends': dict(sorted(sound_trends.items(), 
                                  key=lambda x: x[1]['total_engagement'], 
                                  reverse=True)[:5]),
        'tiktok_intelligence': generate_tiktok_insights(cultural_insights)
    }

def extract_brand_from_post(post):
    """Extract brand name from Instagram post data"""
    # Try username first
    if post.get('ownerUsername'):
        return post['ownerUsername']
    
    # Try URL extraction
    url = post.get('url', '')
    if url:
        match = re.search(r'instagram\.com/([^/]+)', url)
        if match:
            return match.group(1)
    
    return 'Unknown'

def extract_hashtag_from_url(url):
    """Extract hashtag from Instagram hashtag URL"""
    if '/explore/tags/' in url:
        match = re.search(r'/explore/tags/([^/]+)', url)
        if match:
            return match.group(1)
    return 'unknown'

def calculate_hashtag_velocity(hashtag, data):
    """Calculate hashtag velocity (simulated for demo)"""
    # In production, this would calculate actual velocity based on timestamps
    # For demo, return simulated velocity based on hashtag characteristics
    velocity_map = {
        'y2kfashion': 340,
        'streetweararchive': 280,
        'vintagestreetwear': 220,
        'streetweardrop': 180,
        'crooksandcastles': 150
    }
    return velocity_map.get(hashtag, 100 + hash(hashtag) % 200)

def generate_instagram_insights(rankings, crooks_rank):
    """Generate strategic insights from Instagram competitive analysis"""
    insights = []
    
    if crooks_rank:
        if crooks_rank['rank'] > 6:
            top_performer = rankings[0] if rankings else None
            if top_performer:
                gap_multiplier = round(top_performer['avg_engagement'] / crooks_rank['avg_engagement'])
                insights.append({
                    'priority': 'high',
                    'title': 'Critical Engagement Gap',
                    'description': f"Crooks ranks #{crooks_rank['rank']}/12 with {gap_multiplier}x lower engagement than {top_performer['brand']}",
                    'action': 'Increase posting frequency and engagement strategy'
                })
    
    # Content frequency insight
    if rankings:
        avg_posts = sum(r['posts'] for r in rankings) / len(rankings)
        if crooks_rank and crooks_rank['posts'] < avg_posts * 0.7:
            insights.append({
                'priority': 'medium',
                'title': 'Content Frequency Below Average',
                'description': f"Posting {crooks_rank['posts']} vs industry average of {round(avg_posts)}",
                'action': 'Develop consistent content calendar'
            })
    
    return insights

def generate_hashtag_insights(trending_themes):
    """Generate cultural insights from hashtag analysis"""
    insights = []
    
    if trending_themes:
        top_trend = trending_themes[0]
        insights.append({
            'trend': top_trend['theme'],
            'velocity': top_trend['velocity'],
            'opportunity': f"#{top_trend['theme']} showing +{top_trend['velocity']}% velocity - high engagement potential"
        })
    
    return insights

def generate_tiktok_insights(cultural_insights):
    """Generate strategic insights from TikTok cultural analysis"""
    insights = []
    
    if cultural_insights:
        total_engagement = sum(c['engagement'] for c in cultural_insights)
        avg_engagement = total_engagement / len(cultural_insights)
        
        insights.append({
            'platform': 'TikTok',
            'cultural_moment_count': len(cultural_insights),
            'avg_viral_engagement': round(avg_engagement),
            'recommendation': 'Focus on authentic cultural moments vs manufactured content'
        })
    
    return insights

@app.route('/api/competitive-rankings')
def get_competitive_rankings():
    """API endpoint for competitive rankings data"""
    # Sample data for demo - in production, this would come from processed uploads
    sample_rankings = [
        {'rank': 1, 'brand': 'Supreme', 'avg_engagement': 12500, 'posts': 8},
        {'rank': 2, 'brand': 'Stussy', 'avg_engagement': 8200, 'posts': 12},
        {'rank': 3, 'brand': 'Fear of God Essentials', 'avg_engagement': 7800, 'posts': 6},
        {'rank': 4, 'brand': 'Hellstar', 'avg_engagement': 6500, 'posts': 15},
        {'rank': 5, 'brand': 'Diamond Supply Co.', 'avg_engagement': 4200, 'posts': 10},
        {'rank': 6, 'brand': 'LRG', 'avg_engagement': 3800, 'posts': 9},
        {'rank': 7, 'brand': 'Ed Hardy', 'avg_engagement': 2900, 'posts': 7},
        {'rank': 8, 'brand': 'Von Dutch', 'avg_engagement': 2100, 'posts': 5},
        {'rank': 9, 'brand': 'Crooks & Castles', 'avg_engagement': 1200, 'posts': 3},
        {'rank': 10, 'brand': 'Reason Clothing', 'avg_engagement': 980, 'posts': 4},
        {'rank': 11, 'brand': 'Godspeed', 'avg_engagement': 750, 'posts': 6},
        {'rank': 12, 'brand': 'Smoke Rise', 'avg_engagement': 420, 'posts': 2}
    ]
    
    return jsonify(sample_rankings)

@app.route('/api/cultural-trends')
def get_cultural_trends():
    """API endpoint for cultural trend data"""
    sample_trends = [
        {'theme': 'y2kfashion', 'velocity': 340, 'posts': 156},
        {'theme': 'streetweararchive', 'velocity': 280, 'posts': 89},
        {'theme': 'vintagestreetwear', 'velocity': 220, 'posts': 134},
        {'theme': 'streetweardrop', 'velocity': 180, 'posts': 67},
        {'theme': 'crooksandcastles', 'velocity': 150, 'posts': 23},
        {'theme': 'heritagebrand', 'velocity': 120, 'posts': 45}
    ]
    
    return jsonify(sample_trends)

@app.route('/api/strategic-insights')
def get_strategic_insights():
    """API endpoint for strategic insights"""
    insights = [
        {
            'priority': 'high',
            'title': 'Engagement Gap Critical',
            'description': 'Crooks ranks #9/12 with 10x lower engagement than Supreme',
            'action': 'Implement daily posting schedule and engagement strategy'
        },
        {
            'priority': 'medium', 
            'title': 'Y2K Revival Opportunity',
            'description': 'Y2K fashion hashtag showing +340% velocity this week',
            'action': 'Launch Archive Remastered collection targeting nostalgic millennials'
        },
        {
            'priority': 'medium',
            'title': 'TikTok Platform Gap',
            'description': 'Zero presence on TikTok while competitors gain Gen Z mindshare',
            'action': 'Develop TikTok content strategy focusing on streetwear culture'
        }
    ]
    
    return jsonify(insights)

# Calendar and Asset Management (Crooks & Castles specific)
@app.route('/api/calendar-events')
def get_calendar_events():
    """Get Crooks & Castles business calendar events"""
    events = [
        {
            'title': 'Archive Remastered Drop Planning',
            'date': '2025-09-25',
            'type': 'product_planning',
            'priority': 'high'
        },
        {
            'title': 'Competitive Intelligence Review',
            'date': '2025-09-23',
            'type': 'strategy_meeting',
            'priority': 'medium'
        },
        {
            'title': 'Cultural Radar Analysis',
            'date': '2025-09-24',
            'type': 'trend_analysis',
            'priority': 'medium'
        }
    ]
    
    return jsonify(events)

@app.route('/api/brand-assets')
def get_brand_assets():
    """Get Crooks & Castles brand assets"""
    assets = [
        {
            'name': 'Medusa Logo Collection',
            'type': 'logo',
            'status': 'active',
            'usage': 'primary_branding'
        },
        {
            'name': 'Crown Icon Set',
            'type': 'icon',
            'status': 'active', 
            'usage': 'secondary_branding'
        },
        {
            'name': 'Archive Photography',
            'type': 'photography',
            'status': 'active',
            'usage': 'heritage_content'
        }
    ]
    
    return jsonify(assets)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
