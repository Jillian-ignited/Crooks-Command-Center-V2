#!/usr/bin/env python3
"""
Crooks & Castles Command Center V2
A comprehensive brand management and competitive intelligence platform
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'crooks-command-center-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['THUMBNAILS_FOLDER'] = 'uploads/thumbnails'
app.config['METADATA_FOLDER'] = 'uploads/metadata'
app.config['CALENDAR_DATA'] = 'data'
app.config['COMPETITIVE_DATA'] = 'data/competitive'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp4', 'mov', 'jsonl', 'csv', 'xlsx'}

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['THUMBNAILS_FOLDER'], 
               app.config['METADATA_FOLDER'], app.config['CALENDAR_DATA'], 
               app.config['COMPETITIVE_DATA']]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_string(size_bytes):
    """Convert bytes to human readable string"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_asset_type(filename):
    """Determine asset type based on file extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext in ['png', 'jpg', 'jpeg', 'gif']:
        return 'image'
    elif ext in ['pdf']:
        return 'document'
    elif ext in ['mp4', 'mov']:
        return 'video'
    elif ext in ['doc', 'docx']:
        return 'document'
    elif ext in ['txt']:
        return 'document'
    elif ext in ['jsonl', 'csv', 'xlsx']:
        return 'data'
    else:
        return 'general'

# Competitive Intelligence Class
class CompetitiveIntelligence:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def process_apify_jsonl(self, file_path):
        """Process Apify JSONL data"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data.append(json.loads(line.strip()))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping malformed JSON on line {line_num}: {e}")
                        continue
            
            df = pd.DataFrame(data)
            logger.info(f"Processed {len(df)} Instagram posts from {df['ownerUsername'].nunique()} brands")
            return df
        except Exception as e:
            logger.error(f"Error processing JSONL: {e}")
            return None
    
    def generate_brand_metrics(self, df):
        """Generate competitive metrics from Instagram data"""
        metrics = {}
        cultural_moments = []
        
        for brand in df['ownerUsername'].unique():
            brand_data = df[df['ownerUsername'] == brand]
            
            # Calculate key metrics
            total_likes = brand_data['likesCount'].sum()
            total_comments = brand_data['commentsCount'].sum()
            avg_engagement = (brand_data['likesCount'] + brand_data['commentsCount']).mean()
            post_count = len(brand_data)
            
            # Handle follower data if available
            if 'followersCount' in brand_data.columns and not brand_data['followersCount'].isna().all():
                avg_followers = brand_data['followersCount'].mean()
                engagement_rate = (avg_engagement / avg_followers * 100) if avg_followers > 0 else 0
            else:
                engagement_rate = 0
                avg_followers = 0
            
            metrics[brand] = {
                'posts_count': post_count,
                'total_likes': int(total_likes),
                'total_comments': int(total_comments),
                'avg_engagement': round(avg_engagement, 2),
                'max_likes': int(brand_data['likesCount'].max()),
                'posting_frequency': round(post_count / 30, 2),  # posts per day
                'engagement_rate': round(engagement_rate, 3),
                'avg_followers': int(avg_followers),
                'last_updated': datetime.now().isoformat()
            }
            
            # Identify viral content (top 10% for this brand)
            if len(brand_data) > 0:
                viral_threshold = brand_data['likesCount'].quantile(0.9)
                viral_posts = brand_data[brand_data['likesCount'] >= viral_threshold]
                
                for _, post in viral_posts.head(3).iterrows():  # Top 3 per brand
                    cultural_moments.append({
                        'brand': brand,
                        'content_preview': str(post.get('caption', ''))[:100] + '...',
                        'likes': int(post['likesCount']),
                        'comments': int(post['commentsCount']),
                        'total_engagement': int(post['likesCount'] + post['commentsCount']),
                        'date': post.get('timestamp', ''),
                        'viral_score': round(post['likesCount'] / brand_data['likesCount'].mean(), 2) if brand_data['likesCount'].mean() > 0 else 0
                    })
        
        return metrics, cultural_moments
    
    def save_competitive_data(self, metrics, cultural_moments):
        """Save competitive intelligence data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save metrics
        metrics_file = os.path.join(self.data_dir, f'brand_metrics_{timestamp}.json')
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        # Save cultural moments
        cultural_file = os.path.join(self.data_dir, f'cultural_moments_{timestamp}.json')
        with open(cultural_file, 'w') as f:
            json.dump(cultural_moments, f, indent=2, default=str)
        
        # Save latest (for quick access)
        latest_metrics = os.path.join(self.data_dir, 'latest_metrics.json')
        latest_cultural = os.path.join(self.data_dir, 'latest_cultural_moments.json')
        
        with open(latest_metrics, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        with open(latest_cultural, 'w') as f:
            json.dump(cultural_moments, f, indent=2, default=str)
        
        return metrics_file, cultural_file
    
    def get_latest_metrics(self):
        """Get latest competitive metrics"""
        try:
            latest_file = os.path.join(self.data_dir, 'latest_metrics.json')
            if os.path.exists(latest_file):
                with open(latest_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading latest metrics: {e}")
        return {}
    
    def get_latest_cultural_moments(self):
        """Get latest cultural moments"""
        try:
            latest_file = os.path.join(self.data_dir, 'latest_cultural_moments.json')
            if os.path.exists(latest_file):
                with open(latest_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cultural moments: {e}")
        return []

# Initialize competitive intelligence
ci = CompetitiveIntelligence(app.config['COMPETITIVE_DATA'])

# Sample data for demonstration
def get_sample_calendar_data():
    """Sample calendar data for Crooks & Castles"""
    return {
        "events": [
            {
                "id": "1",
                "title": "Archive Collection Launch",
                "description": "Launch heritage Medusa collection with social media campaign",
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "type": "product_launch",
                "status": "planning",
                "progress": 65
            },
            {
                "id": "2", 
                "title": "Sean Paul Collaboration Content",
                "description": "Create content for ongoing Sean Paul partnership",
                "start_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=10)).isoformat(),
                "type": "collaboration",
                "status": "in_progress",
                "progress": 80
            },
            {
                "id": "3",
                "title": "TikTok Platform Launch",
                "description": "Strategic launch on TikTok to capture Gen Z audience",
                "start_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "type": "platform_expansion",
                "status": "planning",
                "progress": 25
            }
        ]
    }

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/calendar')
def get_calendar():
    """Get calendar events"""
    return jsonify(get_sample_calendar_data())

@app.route('/api/calendar/events', methods=['POST'])
def create_event():
    """Create new calendar event"""
    data = request.get_json()
    # In a real app, save to database
    event_id = str(uuid.uuid4())
    data['id'] = event_id
    return jsonify({"status": "success", "event": data})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        asset_type = get_asset_type(filename)
        
        # Save metadata
        metadata = {
            'filename': filename,
            'original_name': file.filename,
            'size': file_size,
            'size_string': get_file_size_string(file_size),
            'type': asset_type,
            'upload_date': datetime.now().isoformat(),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else []
        }
        
        metadata_file = os.path.join(app.config['METADATA_FOLDER'], filename + '.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'metadata': metadata
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/competitive-intelligence/upload', methods=['POST'])
def upload_competitive_data():
    """Handle Apify competitive intelligence data upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.jsonl'):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        file_path = os.path.join(app.config['COMPETITIVE_DATA'], filename)
        file.save(file_path)
        
        # Process the JSONL data
        df = ci.process_apify_jsonl(file_path)
        if df is not None:
            metrics, cultural_moments = ci.generate_brand_metrics(df)
            metrics_file, cultural_file = ci.save_competitive_data(metrics, cultural_moments)
            
            return jsonify({
                'status': 'success',
                'message': f'Processed {len(df)} posts from {df["ownerUsername"].nunique()} brands',
                'brands_analyzed': list(df['ownerUsername'].unique()),
                'metrics_file': os.path.basename(metrics_file),
                'cultural_file': os.path.basename(cultural_file)
            })
        else:
            return jsonify({'error': 'Failed to process JSONL data'}), 500
    
    return jsonify({'error': 'Please upload a .jsonl file from Apify'}), 400

@app.route('/api/competitive-intelligence/metrics')
def get_competitive_metrics():
    """Get latest competitive metrics"""
    metrics = ci.get_latest_metrics()
    if metrics:
        # Create rankings
        rankings = sorted(metrics.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
        
        return jsonify({
            'metrics': metrics,
            'rankings': [{'brand': brand, **data} for brand, data in rankings],
            'total_brands': len(metrics),
            'last_updated': rankings[0][1].get('last_updated') if rankings else None
        })
    
    return jsonify({'metrics': {}, 'rankings': [], 'total_brands': 0})

@app.route('/api/competitive-intelligence/cultural-moments')
def get_cultural_moments():
    """Get latest cultural moments"""
    moments = ci.get_latest_cultural_moments()
    # Sort by engagement
    moments.sort(key=lambda x: x.get('total_engagement', 0), reverse=True)
    
    return jsonify({
        'cultural_moments': moments[:20],  # Top 20
        'total_moments': len(moments)
    })

@app.route('/api/assets')
def get_assets():
    """Get all uploaded assets"""
    assets = []
    
    if os.path.exists(app.config['METADATA_FOLDER']):
        for metadata_file in os.listdir(app.config['METADATA_FOLDER']):
            if metadata_file.endswith('.json'):
                try:
                    with open(os.path.join(app.config['METADATA_FOLDER'], metadata_file), 'r') as f:
                        metadata = json.load(f)
                        assets.append(metadata)
                except Exception as e:
                    logger.error(f"Error loading metadata {metadata_file}: {e}")
    
    return jsonify({'assets': assets})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/performance-metrics')
def get_performance_metrics():
    """Get performance metrics for dashboard"""
    # Get competitive metrics
    competitive_metrics = ci.get_latest_metrics()
    cultural_moments = ci.get_latest_cultural_moments()
    
    # Calculate Crooks performance
    crooks_data = competitive_metrics.get('crooksncastles', {})
    
    # Get asset count
    asset_count = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    
    # Calculate competitive position
    if competitive_metrics:
        rankings = sorted(competitive_metrics.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
        crooks_rank = next((i for i, (brand, _) in enumerate(rankings, 1) if brand == 'crooksncastles'), None)
        total_competitors = len(rankings)
    else:
        crooks_rank = None
        total_competitors = 0
    
    return jsonify({
        'assets_created': asset_count,
        'cultural_moments': len(cultural_moments),
        'competitive_rank': f"#{crooks_rank}/{total_competitors}" if crooks_rank else "No data",
        'avg_engagement': crooks_data.get('avg_engagement', 0),
        'posts_this_period': crooks_data.get('posts_count', 0),
        'engagement_rate': crooks_data.get('engagement_rate', 0),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/healthz')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
