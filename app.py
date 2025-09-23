import os
import json
import sqlite3
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import uuid
import json
import os
from datetime import datetime

# Define a function to load the calendar data from the JSON file
def load_calendar_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'content_calendar.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get("events", [])
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not valid JSON.")
        return []

# Example of how to use this data to filter by date range
def get_events_for_range(days):
    events = load_calendar_data()
    today = datetime.strptime("2025-09-23", "%Y-%m-%d").date() # Use datetime.now().date() in production
    
    end_date = today + timedelta(days=days)
    
    filtered_events = []
    for event in events:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        if today <= event_date < end_date:
            filtered_events.append(event)
    
    return filtered_events

# Example Usage in a Flask route
# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def home():
#     seven_day_events = get_events_for_range(7)
#     thirty_day_events = get_events_for_range(30)
#     # And so on for 60 and 90+ days
    
#     return render_template('your_template.html', 
#                            seven_day=seven_day_events, 
#                            thirty_day=thirty_day_events)

# if __name__ == '__main__':
#     app.run(debug=True)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'crooks-castles-command-center-2025')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ASSETS_FOLDER'] = 'assets'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure directories exist
for directory in ['uploads', 'assets', 'reports', 'data']:
    os.makedirs(directory, exist_ok=True)

# Database setup
DATABASE = 'command_center.db'

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            priority TEXT DEFAULT 'medium',
            deadline DATE,
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Assets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            description TEXT,
            tags TEXT,
            uploaded_by TEXT,
            project_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # Calendar events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT DEFAULT 'general',
            start_date DATE NOT NULL,
            end_date DATE,
            created_by TEXT,
            project_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # Agency deliverables table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agency_deliverables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deliverable_name TEXT NOT NULL,
            phase INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending',
            due_date DATE,
            assigned_to TEXT,
            notes TEXT,
            project_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Competitor Intelligence Database
COMPETITORS = {
    'supreme': {
        'name': 'Supreme',
        'tier': 'luxury',
        'detection_keywords': ['supreme', 'supremenewyork', '@supremenewyork', '#supreme'],
        'usernames': ['supremenewyork', 'supreme'],
        'target_audience': 'hype-collectors',
        'price_range': 'premium'
    },
    'stussy': {
        'name': 'Stussy', 
        'tier': 'heritage',
        'detection_keywords': ['stussy', '@stussy', '#stussy', 'stüssy'],
        'usernames': ['stussy'],
        'target_audience': 'streetwear-og',
        'price_range': 'mid-premium'
    },
    'hellstar': {
        'name': 'Hellstar',
        'tier': 'emerging',
        'detection_keywords': ['hellstar', '@hellstar', '#hellstar'],
        'usernames': ['hellstar'],
        'target_audience': 'gen-z-alt',
        'price_range': 'mid-tier'
    },
    'godspeed': {
        'name': 'Godspeed',
        'tier': 'emerging',
        'detection_keywords': ['godspeed', '@godspeed', '#godspeed'],
        'usernames': ['godspeed'],
        'target_audience': 'streetwear-purist',
        'price_range': 'mid-tier'
    },
    'fog_essentials': {
        'name': 'Fear of God Essentials',
        'tier': 'luxury',
        'detection_keywords': ['fearofgod', 'essentials', '@fearofgodessentials', '#fearofgod', '#essentials'],
        'usernames': ['fearofgodessentials', 'fearofgod'],
        'target_audience': 'minimalist-luxury',
        'price_range': 'premium'
    },
    'smoke_rise': {
        'name': 'Smoke Rise',
        'tier': 'established',
        'detection_keywords': ['smokerise', '@smokerise', '#smokerise'],
        'usernames': ['smokerise'],
        'target_audience': 'urban-contemporary',
        'price_range': 'mid-tier'
    },
    'reason_clothing': {
        'name': 'Reason Clothing',
        'tier': 'established',
        'detection_keywords': ['reasonclothing', 'reason', '@reasonclothing', '#reasonclothing'],
        'usernames': ['reasonclothing'],
        'target_audience': 'urban-lifestyle',
        'price_range': 'accessible'
    },
    'lrg': {
        'name': 'LRG',
        'tier': 'heritage',
        'detection_keywords': ['lrg', 'lrgclothing', '@lrgclothing', '#lrg'],
        'usernames': ['lrgclothing', 'lrg'],
        'target_audience': 'skatewear-culture',
        'price_range': 'accessible'
    },
    'diamond_supply': {
        'name': 'Diamond Supply Co.',
        'tier': 'established',
        'detection_keywords': ['diamond', 'diamondsupplyco', '@diamondsupplyco', '#diamondsupply'],
        'usernames': ['diamondsupplyco', 'diamondsupply'],
        'target_audience': 'skate-culture',
        'price_range': 'mid-tier'
    },
    'ed_hardy': {
        'name': 'Ed Hardy',
        'tier': 'legacy',
        'detection_keywords': ['edhardy', '@edhardyofficial', '#edhardy'],
        'usernames': ['edhardyofficial', 'edhardy'],
        'target_audience': 'nostalgic-revival',
        'price_range': 'mid-tier'
    },
    'von_dutch': {
        'name': 'Von Dutch',
        'tier': 'legacy',
        'detection_keywords': ['vondutch', '@vondutchoriginals', '#vondutch'],
        'usernames': ['vondutchoriginals', 'vondutch'],
        'target_audience': 'y2k-revival',
        'price_range': 'premium'
    },
    'crooks_castles': {
        'name': 'Crooks & Castles',
        'tier': 'established',
        'detection_keywords': ['crooks', 'castles', 'crooksandcastles', '@crooksandcastles', '#crooksandcastles'],
        'usernames': ['crooksandcastles', 'crookscastles'],
        'target_audience': 'streetwear-luxury',
        'price_range': 'premium'
    }
}

# Initialize database on startup
init_database()

# MAIN ROUTES
@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('index.html')

# PROJECT MANAGEMENT ROUTES
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM projects 
        ORDER BY created_at DESC
    ''')
    
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create new project"""
    data = request.json
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO projects (name, description, status, priority, deadline, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('description'),
        data.get('status', 'active'),
        data.get('priority', 'medium'),
        data.get('deadline'),
        data.get('assigned_to')
    ))
    
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': project_id, 'status': 'created'})

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update project"""
    data = request.json
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE projects 
        SET name=?, description=?, status=?, priority=?, deadline=?, assigned_to=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    ''', (
        data.get('name'),
        data.get('description'),
        data.get('status'),
        data.get('priority'),
        data.get('deadline'),
        data.get('assigned_to'),
        project_id
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'updated'})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'deleted'})

# ASSET MANAGEMENT ROUTES
@app.route('/api/assets', methods=['GET'])
def get_assets():
    """Get all assets"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, p.name as project_name 
        FROM assets a
        LEFT JOIN projects p ON a.project_id = p.id
        ORDER BY a.created_at DESC
    ''')
    
    assets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(assets)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Save to database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO assets (filename, original_filename, file_type, file_size, description, tags, uploaded_by, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            file.filename,
            file.content_type,
            os.path.getsize(filepath),
            request.form.get('description', ''),
            request.form.get('tags', ''),
            request.form.get('uploaded_by', ''),
            request.form.get('project_id', None)
        ))
        
        asset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': asset_id,
            'filename': filename,
            'original_filename': file.filename,
            'status': 'uploaded'
        })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# CALENDAR ROUTES
@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get calendar events"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT e.*, p.name as project_name 
        FROM calendar_events e
        LEFT JOIN projects p ON e.project_id = p.id
        ORDER BY e.start_date ASC
    ''')
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(events)

@app.route('/api/calendar/events', methods=['POST'])
def create_calendar_event():
    """Create calendar event"""
    data = request.json
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO calendar_events (title, description, event_type, start_date, end_date, created_by, project_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('title'),
        data.get('description'),
        data.get('event_type', 'general'),
        data.get('start_date'),
        data.get('end_date'),
        data.get('created_by'),
        data.get('project_id')
    ))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': event_id, 'status': 'created'})

# AGENCY ROUTES
@app.route('/api/agency/deliverables', methods=['GET'])
def get_agency_deliverables():
    """Get agency deliverables"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.*, p.name as project_name 
        FROM agency_deliverables d
        LEFT JOIN projects p ON d.project_id = p.id
        ORDER BY d.due_date ASC, d.phase ASC
    ''')
    
    deliverables = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(deliverables)

@app.route('/api/agency/deliverables', methods=['POST'])
def create_agency_deliverable():
    """Create agency deliverable"""
    data = request.json
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO agency_deliverables (deliverable_name, phase, status, due_date, assigned_to, notes, project_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('deliverable_name'),
        data.get('phase', 1),
        data.get('status', 'pending'),
        data.get('due_date'),
        data.get('assigned_to'),
        data.get('notes'),
        data.get('project_id')
    ))
    
    deliverable_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': deliverable_id, 'status': 'created'})

@app.route('/api/agency/deliverables/<int:deliverable_id>', methods=['PUT'])
def update_agency_deliverable(deliverable_id):
    """Update agency deliverable"""
    data = request.json
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE agency_deliverables 
        SET deliverable_name=?, phase=?, status=?, due_date=?, assigned_to=?, notes=?, project_id=?
        WHERE id=?
    ''', (
        data.get('deliverable_name'),
        data.get('phase'),
        data.get('status'),
        data.get('due_date'),
        data.get('assigned_to'),
        data.get('notes'),
        data.get('project_id'),
        deliverable_id
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'updated'})

# COMPETITIVE INTELLIGENCE ROUTES
@app.route('/api/competitors')
def get_competitors():
    """Get all competitor data"""
    return jsonify(COMPETITORS)

@app.route('/api/competitive-analysis')
def competitive_analysis():
    """Generate competitive analysis by auto-detecting competitors in JSONL files"""
    try:
        analysis_data = auto_detect_and_analyze_competitors()
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({'error': 'Unable to process data', 'details': str(e)}), 500

@app.route('/api/brand-comparison/<competitor_key>')
def brand_comparison(competitor_key):
    """Head-to-head comparison with specific competitor"""
    if competitor_key not in COMPETITORS:
        return jsonify({'error': 'Competitor not found'}), 404
    
    try:
        comparison_data = generate_brand_comparison(competitor_key)
        return jsonify(comparison_data)
    except Exception as e:
        return jsonify({'error': 'Unable to generate comparison', 'details': str(e)}), 500

@app.route('/api/competitive-insights')
def competitive_insights():
    """Get strategic insights based on competitive analysis"""
    try:
        insights = generate_competitive_insights()
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': 'Unable to generate insights', 'details': str(e)}), 500

# COMPETITIVE INTELLIGENCE HELPER FUNCTIONS
def auto_detect_and_analyze_competitors():
    """Read all JSONL files and auto-detect which competitor each post belongs to"""
    upload_dir = app.config['UPLOAD_FOLDER']
    
    if not os.path.exists(upload_dir):
        return {}
    
    # Storage for posts by competitor
    competitor_posts = {key: [] for key in COMPETITORS.keys()}
    
    # Process all JSONL files
    for filename in os.listdir(upload_dir):
        if filename.endswith('.jsonl'):
            file_path = os.path.join(upload_dir, filename)
            posts = read_jsonl_file(file_path)
            
            # Classify each post by competitor
            for post in posts:
                detected_competitor = detect_competitor_from_post(post)
                if detected_competitor:
                    competitor_posts[detected_competitor].append(post)
    
    # Analyze each competitor's data
    competitor_analysis = {}
    for comp_key, posts in competitor_posts.items():
        if posts:
            metrics = analyze_posts_for_competitor(posts)
            competitor_analysis[comp_key] = {
                'name': COMPETITORS[comp_key]['name'],
                'tier': COMPETITORS[comp_key]['tier'],
                'target_audience': COMPETITORS[comp_key]['target_audience'],
                'price_range': COMPETITORS[comp_key]['price_range'],
                'posts_found': len(posts),
                'metrics': metrics,
                'competitive_position': assess_competitive_position(metrics, COMPETITORS[comp_key]['tier']),
                'content_strategy': analyze_content_strategy(metrics)
            }
    
    return competitor_analysis

def read_jsonl_file(file_path):
    """Read JSONL file and return list of posts"""
    posts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        post = json.loads(line)
                        posts.append(post)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return posts

def detect_competitor_from_post(post):
    """Detect which competitor a post belongs to based on content analysis"""
    searchable_text = []
    
    # Common text fields in social media posts
    text_fields = ['text', 'caption', 'description', 'username', 'displayname', 
                   'ownerUsername', 'author', 'user', 'profile_name']
    
    for field in text_fields:
        if field in post and post[field]:
            searchable_text.append(str(post[field]).lower())
    
    # Check hashtags
    if 'hashtags' in post and post['hashtags']:
        for hashtag in post['hashtags']:
            searchable_text.append(f"#{hashtag.lower()}")
    
    # Look for hashtags in text content
    combined_text = ' '.join(searchable_text)
    hashtag_matches = re.findall(r'#\w+', combined_text)
    searchable_text.extend(hashtag_matches)
    
    # Check mentions
    mention_matches = re.findall(r'@\w+', combined_text)
    searchable_text.extend(mention_matches)
    
    combined_search_text = ' '.join(searchable_text)
    
    # Score each competitor
    competitor_scores = {}
    
    for comp_key, comp_data in COMPETITORS.items():
        score = 0
        
        for keyword in comp_data['detection_keywords']:
            keyword_lower = keyword.lower()
            if keyword_lower in combined_search_text:
                if keyword.startswith('@'):
                    score += 10
                elif keyword.startswith('#'):
                    score += 8
                else:
                    score += 5
        
        for username in comp_data['usernames']:
            if username.lower() in combined_search_text:
                score += 15
        
        if score > 0:
            competitor_scores[comp_key] = score
    
    if competitor_scores:
        best_match = max(competitor_scores.items(), key=lambda x: x[1])
        if best_match[1] >= 5:
            return best_match[0]
    
    return None

def analyze_posts_for_competitor(posts):
    """Analyze posts for competitive metrics"""
    total_posts = len(posts)
    total_engagement = 0
    hashtags = []
    content_types = {'image': 0, 'video': 0, 'carousel': 0, 'text': 0}
    
    for post in posts:
        # Engagement metrics
        engagement_fields = [
            ['likesCount', 'likes', 'like_count'],
            ['commentsCount', 'comments', 'comment_count'], 
            ['sharesCount', 'shares', 'share_count']
        ]
        
        post_engagement = 0
        for field_group in engagement_fields:
            for field in field_group:
                if field in post and post[field]:
                    try:
                        post_engagement += int(post[field])
                        break
                    except (ValueError, TypeError):
                        continue
        
        total_engagement += post_engagement
        
        # Hashtags
        post_hashtags = []
        if 'hashtags' in post and post['hashtags']:
            post_hashtags.extend(post['hashtags'])
        
        text_content = post.get('text', '') or post.get('caption', '')
        if text_content:
            text_hashtags = re.findall(r'#\w+', str(text_content))
            post_hashtags.extend([tag[1:] for tag in text_hashtags])
        
        hashtags.extend(post_hashtags)
        
        # Content type
        if (post.get('videoUrl') or post.get('video') or 
            post.get('type') == 'video'):
            content_types['video'] += 1
        elif (post.get('images') and len(post.get('images', [])) > 1):
            content_types['carousel'] += 1
        elif (post.get('images') or post.get('imageUrl')):
            content_types['image'] += 1
        else:
            content_types['text'] += 1
    
    avg_engagement = total_engagement / max(total_posts, 1)
    hashtag_counter = Counter(hashtags)
    top_hashtags = [f"#{tag}" for tag, count in hashtag_counter.most_common(10)]
    
    return {
        'total_posts': total_posts,
        'avg_engagement_per_post': round(avg_engagement, 2),
        'total_engagement': total_engagement,
        'top_hashtags': top_hashtags,
        'content_distribution': content_types
    }

def assess_competitive_position(metrics, tier):
    """Assess competitive position"""
    if not metrics or metrics.get('total_posts', 0) == 0:
        return 'insufficient_data'
    
    engagement_score = metrics.get('avg_engagement_per_post', 0)
    
    tier_benchmarks = {
        'luxury': {'strong': 8000, 'moderate': 3000},
        'heritage': {'strong': 5000, 'moderate': 2000},
        'established': {'strong': 3000, 'moderate': 1000},
        'emerging': {'strong': 2000, 'moderate': 500},
        'legacy': {'strong': 1500, 'moderate': 600}
    }
    
    benchmark = tier_benchmarks.get(tier, {'strong': 1000, 'moderate': 500})
    
    if engagement_score >= benchmark['strong']:
        return 'strong'
    elif engagement_score >= benchmark['moderate']:
        return 'moderate'
    else:
        return 'developing'

def analyze_content_strategy(metrics):
    """Analyze content strategy"""
    if not metrics or not metrics.get('content_distribution'):
        return 'insufficient_data'
    
    content_dist = metrics['content_distribution']
    total_content = sum(content_dist.values())
    
    if total_content == 0:
        return 'no_data'
    
    video_ratio = content_dist.get('video', 0) / total_content
    carousel_ratio = content_dist.get('carousel', 0) / total_content
    
    if video_ratio > 0.6:
        return 'video_dominant'
    elif video_ratio > 0.4:
        return 'video_focused'
    elif carousel_ratio > 0.4:
        return 'carousel_focused'
    elif video_ratio > 0.2 and carousel_ratio > 0.2:
        return 'mixed_media'
    else:
        return 'image_focused'

def generate_brand_comparison(competitor_key):
    """Generate brand comparison"""
    competitor_info = COMPETITORS[competitor_key]
    all_data = auto_detect_and_analyze_competitors()
    
    competitor_data = all_data.get(competitor_key, {})
    crooks_data = all_data.get('crooks_castles', {})
    
    if not competitor_data or not competitor_data.get('metrics'):
        return {
            'competitor': competitor_info,
            'comparison': 'no_data',
            'message': f'No posts detected for {competitor_info["name"]} in your data files'
        }
    
    return {
        'competitor': competitor_info,
        'competitor_posts_detected': competitor_data.get('posts_found', 0),
        'crooks_posts_detected': crooks_data.get('posts_found', 0),
        'metrics_comparison': {
            'crooks_castles': crooks_data.get('metrics', {}),
            'competitor': competitor_data.get('metrics', {})
        }
    }

def generate_competitive_insights():
    """Generate competitive insights"""
    all_competitor_data = auto_detect_and_analyze_competitors()
    
    insights = {
        'competitors_detected': len([k for k, v in all_competitor_data.items() if v.get('posts_found', 0) > 0]),
        'market_leaders': [],
        'strategic_recommendations': []
    }
    
    if not all_competitor_data:
        insights['strategic_recommendations'] = [
            'Upload JSONL files containing competitor social media data'
        ]
        return insights
    
    # Engagement rankings
    engagement_rankings = []
    for comp_key, data in all_competitor_data.items():
        if data.get('posts_found', 0) > 0:
            metrics = data.get('metrics', {})
            engagement = metrics.get('avg_engagement_per_post', 0)
            engagement_rankings.append((comp_key, data['name'], engagement, data['tier']))
    
    engagement_rankings.sort(key=lambda x: x[2], reverse=True)
    
    insights['market_leaders'] = [
        {'name': name, 'engagement': eng, 'tier': tier} 
        for _, name, eng, tier in engagement_rankings[:3]
    ]
    
    if len(all_competitor_data) > 0:
        insights['strategic_recommendations'] = [
            f"Successfully detected {insights['competitors_detected']} competitors in your data",
            "Monitor top performers for content strategy insights"
        ]
    
    return insights

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
