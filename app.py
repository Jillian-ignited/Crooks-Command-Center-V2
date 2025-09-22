import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.utils
from collections import Counter, defaultdict
import re
import zipfile
import io
import hashlib
import uuid
from PIL import Image
import mimetypes

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'crooks-castles-strategic-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ASSETS_FOLDER'] = 'assets'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure directories exist
for directory in ['uploads', 'assets', 'reports', 'team_data', 'content_library', 'calendar_data']:
    os.makedirs(directory, exist_ok=True)

# Asset categories for organization
ASSET_CATEGORIES = [
    'Images', 'Videos', 'Graphics', 'Documents', 'Audio', 
    'Templates', 'Brand Assets', 'Campaign Materials', 'Other'
]

class ContentManager:
    def __init__(self):
        self.content_file = 'content_library/content.json'
        
    def get_all_content(self):
        """Get all content items"""
        if os.path.exists(self.content_file):
            try:
                with open(self.content_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def add_content(self, content_data):
        """Add new content item"""
        content_id = str(uuid.uuid4())[:8]
        content_data['id'] = content_id
        content_data['created_at'] = datetime.now().isoformat()
        content_data['status'] = content_data.get('status', 'draft')
        
        all_content = self.get_all_content()
        all_content.append(content_data)
        
        with open(self.content_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, indent=2, ensure_ascii=False)
        
        return content_id
    
    def update_content(self, content_id, updates):
        """Update existing content"""
        all_content = self.get_all_content()
        for content in all_content:
            if content['id'] == content_id:
                content.update(updates)
                content['updated_at'] = datetime.now().isoformat()
                break
        
        with open(self.content_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, indent=2, ensure_ascii=False)
    
    def delete_content(self, content_id):
        """Delete content item"""
        all_content = self.get_all_content()
        all_content = [c for c in all_content if c['id'] != content_id]
        
        with open(self.content_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, indent=2, ensure_ascii=False)

class CalendarManager:
    def __init__(self):
        self.calendar_file = 'calendar_data/calendar.json'
        
    def get_calendar_events(self, start_date=None, end_date=None):
        """Get calendar events within date range"""
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                
                if start_date and end_date:
                    filtered_events = []
                    for event in events:
                        event_date = datetime.fromisoformat(event['date']).date()
                        if start_date <= event_date <= end_date:
                            filtered_events.append(event)
                    return filtered_events
                
                return events
            except:
                return []
        return []
    
    def add_event(self, event_data):
        """Add calendar event"""
        event_id = str(uuid.uuid4())[:8]
        event_data['id'] = event_id
        event_data['created_at'] = datetime.now().isoformat()
        
        events = self.get_calendar_events()
        events.append(event_data)
        
        # Sort events by date
        events.sort(key=lambda x: x['date'])
        
        with open(self.calendar_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        return event_id
    
    def update_event(self, event_id, updates):
        """Update calendar event"""
        events = self.get_calendar_events()
        for event in events:
            if event['id'] == event_id:
                event.update(updates)
                event['updated_at'] = datetime.now().isoformat()
                break
        
        with open(self.calendar_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
    
    def delete_event(self, event_id):
        """Delete calendar event"""
        events = self.get_calendar_events()
        events = [e for e in events if e['id'] != event_id]
        
        with open(self.calendar_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
    
    def generate_strategic_milestones(self):
        """Generate strategic planning milestones with streetwear cultural moments"""
        today = datetime.now().date()
        current_year = today.year
        milestones = []
        
        # Streetwear Cultural Calendar - Key Dates
        streetwear_moments = [
            # Q4 2024 / Q1 2025
            {'date': '2024-11-29', 'title': 'Black Friday Streetwear Drop', 'type': 'cultural', 'category': 'sales', 
             'description': 'Major streetwear brands release limited Black Friday collections'},
            {'date': '2024-12-02', 'title': 'Cyber Monday Exclusive Releases', 'type': 'cultural', 'category': 'sales',
             'description': 'Online-exclusive streetwear drops and collaborations'},
            {'date': '2024-12-26', 'title': 'Boxing Day Streetwear Sales', 'type': 'cultural', 'category': 'sales',
             'description': 'Post-holiday sales and end-of-year clearance'},
            
            # 2025 Streetwear Cultural Moments
            {'date': '2025-01-01', 'title': 'New Year Fresh Start Campaign', 'type': 'cultural', 'category': 'lifestyle',
             'description': 'New year, new style messaging - fresh beginnings in streetwear'},
            {'date': '2025-02-14', 'title': 'Valentine\'s Day Couples Streetwear', 'type': 'cultural', 'category': 'lifestyle',
             'description': 'Matching streetwear sets and couples fashion campaigns'},
            {'date': '2025-03-20', 'title': 'Spring Streetwear Transition', 'type': 'seasonal', 'category': 'product',
             'description': 'Lighter layers, spring colorways, and transitional pieces'},
            {'date': '2025-04-15', 'title': 'Coachella Streetwear Influence', 'type': 'cultural', 'category': 'events',
             'description': 'Festival fashion, influencer collaborations, and music culture tie-ins'},
            {'date': '2025-05-01', 'title': 'Summer Collection Preview', 'type': 'seasonal', 'category': 'product',
             'description': 'Summer streetwear launch - shorts, tank tops, light jackets'},
            {'date': '2025-06-21', 'title': 'Summer Solstice Street Style', 'type': 'seasonal', 'category': 'lifestyle',
             'description': 'Peak summer streetwear, outdoor culture, and urban exploration'},
            {'date': '2025-07-04', 'title': 'Independence Day Americana', 'type': 'cultural', 'category': 'patriotic',
             'description': 'American streetwear themes, vintage Americana, and patriotic colorways'},
            {'date': '2025-08-15', 'title': 'Back-to-School Streetwear', 'type': 'seasonal', 'category': 'lifestyle',
             'description': 'Student-focused campaigns, campus streetwear, and academic year prep'},
            {'date': '2025-09-22', 'title': 'Fall Fashion Week Influence', 'type': 'cultural', 'category': 'fashion',
             'description': 'Fashion week streetwear trends, runway influence, and seasonal transitions'},
            {'date': '2025-10-15', 'title': 'Fall Streetwear Launch', 'type': 'seasonal', 'category': 'product',
             'description': 'Hoodies, jackets, layering pieces, and autumn colorways'},
            {'date': '2025-10-31', 'title': 'Halloween Street Style', 'type': 'cultural', 'category': 'lifestyle',
             'description': 'Costume-inspired streetwear, dark aesthetics, and Halloween collections'},
            {'date': '2025-11-15', 'title': 'Pre-Holiday Streetwear Push', 'type': 'cultural', 'category': 'sales',
             'description': 'Gift-focused messaging, holiday party outfits, and winter prep'},
            {'date': '2025-12-15', 'title': 'Holiday Streetwear Gifting', 'type': 'cultural', 'category': 'gifting',
             'description': 'Streetwear as gifts, holiday colorways, and end-of-year campaigns'}
        ]
        
        # High Voltage Digital Deliverable Tracking (Based on Agreement)
        hvd_deliverables = []
        
        # Phase 1: Foundation & Awareness (Sep 3 - Oct 31, 2025) - $4,000/month
        if today <= datetime(2025, 10, 31).date():
            hvd_deliverables.extend([
                {'date': '2025-09-10', 'title': 'HVD Phase 1: Ad Creative Batch 1', 'type': 'hvd-phase1', 'category': 'deliverable',
                 'description': 'Deliver 3-4 ad creatives (static + light video/motion) - Week 1'},
                {'date': '2025-09-17', 'title': 'HVD Phase 1: Social Media Content Week 1', 'type': 'hvd-phase1', 'category': 'deliverable',
                 'description': 'Deliver 2-3 social posts for brand reintroduction'},
                {'date': '2025-09-24', 'title': 'HVD Phase 1: Weekly Report #1', 'type': 'hvd-phase1', 'category': 'reporting',
                 'description': 'Weekly performance report (ads + social) with key takeaways'},
                {'date': '2025-10-01', 'title': 'HVD Phase 1: Email Campaign #1', 'type': 'hvd-phase1', 'category': 'deliverable',
                 'description': 'Brand update email for soft re-engagement'},
                {'date': '2025-10-15', 'title': 'HVD Phase 1: Mid-Phase Review', 'type': 'hvd-phase1', 'category': 'strategy',
                 'description': 'Review foundation building progress and adjust strategy'},
                {'date': '2025-10-29', 'title': 'HVD Phase 1: Phase Completion Review', 'type': 'hvd-phase1', 'category': 'analysis',
                 'description': 'Assess Phase 1 results and prepare for Q4 push'}
            ])
        
        # Phase 2: Growth & Q4 Push (Nov 1 - Dec 31, 2025) - $7,500/month  
        hvd_deliverables.extend([
            {'date': '2025-11-01', 'title': 'HVD Phase 2: Q4 Campaign Launch', 'type': 'hvd-phase2', 'category': 'campaign',
             'description': 'Launch full-funnel campaigns for holiday season'},
            {'date': '2025-11-15', 'title': 'HVD Phase 2: BFCM Campaign Prep', 'type': 'hvd-phase2', 'category': 'deliverable',
             'description': 'Deliver 6-8 BFCM creatives and promotional content'},
            {'date': '2025-11-25', 'title': 'HVD Phase 2: Black Friday Activation', 'type': 'hvd-phase2', 'category': 'campaign',
             'description': 'Execute Black Friday campaigns across all channels'},
            {'date': '2025-12-02', 'title': 'HVD Phase 2: Cyber Monday Push', 'type': 'hvd-phase2', 'category': 'campaign',
             'description': 'Cyber Monday campaign execution and optimization'},
            {'date': '2025-12-15', 'title': 'HVD Phase 2: Holiday Final Push', 'type': 'hvd-phase2', 'category': 'campaign',
             'description': 'Final holiday campaigns and gift guide promotions'},
            {'date': '2025-12-31', 'title': 'HVD Phase 2: Q4 Performance Review', 'type': 'hvd-phase2', 'category': 'analysis',
             'description': 'Comprehensive Q4 results analysis and Phase 3 planning'}
        ])
        
        # Phase 3: Full Retainer (Jan 2026 onward) - $10,000/month
        hvd_deliverables.extend([
            {'date': '2026-01-15', 'title': 'HVD Phase 3: SEO Audit Launch', 'type': 'hvd-phase3', 'category': 'seo',
             'description': 'Technical SEO audit of new site and optimization strategy'},
            {'date': '2026-01-30', 'title': 'HVD Phase 3: CRO Testing Begin', 'type': 'hvd-phase3', 'category': 'cro',
             'description': 'Start A/B testing for PDPs, landing pages, and checkout flow'},
            {'date': '2026-02-15', 'title': 'HVD Phase 3: Email Flow Setup', 'type': 'hvd-phase3', 'category': 'email',
             'description': 'Implement welcome, abandoned cart, and post-purchase flows'},
            {'date': '2026-03-01', 'title': 'HVD Phase 3: Quarterly Strategy', 'type': 'hvd-phase3', 'category': 'strategy',
             'description': 'Quarterly strategic roadmap and performance review'}
        ])
        
        # Combine all milestones and filter by date range
        all_milestones = streetwear_moments + hvd_deliverables
        
        # Add current milestones within next 90 days
        end_date = today + timedelta(days=90)
        
        for milestone in all_milestones:
            milestone_date = datetime.strptime(milestone['date'], '%Y-%m-%d').date()
            if today <= milestone_date <= end_date:
                milestone['auto_generated'] = True
                milestones.append(milestone)
        
        # Add daily tactical goals for next 7 days
        for i in range(1, 8):
            date = today + timedelta(days=i)
            milestones.append({
                'id': f'daily_{i}',
                'title': f'Daily Content & Performance Review',
                'date': date.isoformat(),
                'type': '7-day',
                'category': 'daily',
                'description': 'Review content performance, engagement metrics, and optimize posting strategy',
                'auto_generated': True
            })
        
        return sorted(milestones, key=lambda x: x['date'])

class AssetManager:
    def __init__(self):
        self.assets_folder = app.config['ASSETS_FOLDER']
        self.metadata_file = 'assets_metadata.json'
    
    def get_asset_metadata(self):
        """Get all asset metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_asset_metadata(self, metadata):
        """Save asset metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def add_asset(self, filename, category='Other', description='', tags=None, uploader='Unknown'):
        """Add asset with metadata"""
        file_path = os.path.join(self.assets_folder, filename)
        
        if not os.path.exists(file_path):
            return None
        
        # Get file info
        stat_info = os.stat(file_path)
        file_type = self.get_file_type(filename)
        
        # Generate thumbnail for images
        thumbnail_path = None
        if file_type == 'image':
            thumbnail_path = self.generate_thumbnail(filename)
        
        asset_info = {
            'id': str(uuid.uuid4())[:8],
            'filename': filename,
            'original_name': filename,
            'category': category,
            'description': description,
            'tags': tags or [],
            'file_type': file_type,
            'size': stat_info.st_size,
            'created_at': datetime.now().isoformat(),
            'uploader': uploader,
            'thumbnail': thumbnail_path,
            'download_count': 0
        }
        
        # Save metadata
        metadata = self.get_asset_metadata()
        metadata[filename] = asset_info
        self.save_asset_metadata(metadata)
        
        return asset_info
    
    def get_file_type(self, filename):
        """Determine file type category"""
        ext = filename.lower().split('.')[-1]
        
        image_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']
        video_exts = ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm']
        audio_exts = ['mp3', 'wav', 'flac', 'aac', 'ogg']
        doc_exts = ['pdf', 'doc', 'docx', 'txt', 'rtf']
        
        if ext in image_exts:
            return 'image'
        elif ext in video_exts:
            return 'video'
        elif ext in audio_exts:
            return 'audio'
        elif ext in doc_exts:
            return 'document'
        else:
            return 'other'
    
    def generate_thumbnail(self, filename):
        """Generate thumbnail for image files"""
        try:
            file_path = os.path.join(self.assets_folder, filename)
            thumbnail_dir = os.path.join(self.assets_folder, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            
            with Image.open(file_path) as img:
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, optimize=True, quality=85)
            
            return f"thumbnails/{thumbnail_filename}"
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    def search_assets(self, query='', category=None, file_type=None):
        """Search assets by query, category, or file type"""
        metadata = self.get_asset_metadata()
        results = []
        
        for filename, asset_info in metadata.items():
            # Check if file still exists
            if not os.path.exists(os.path.join(self.assets_folder, filename)):
                continue
                
            # Apply filters
            if category and asset_info.get('category') != category:
                continue
                
            if file_type and asset_info.get('file_type') != file_type:
                continue
                
            # Search in filename, description, and tags
            if query:
                search_text = f"{filename} {asset_info.get('description', '')} {' '.join(asset_info.get('tags', []))}"
                if query.lower() not in search_text.lower():
                    continue
            
            results.append(asset_info)
        
        return sorted(results, key=lambda x: x['created_at'], reverse=True)

# Initialize managers
content_manager = ContentManager()
calendar_manager = CalendarManager()
asset_manager = AssetManager()

# Data processor from previous version
class DataProcessor:
    def __init__(self):
        self.instagram_data = []
        self.tiktok_data = []
        
    def load_social_data(self):
        """Load real data from JSONL files"""
        try:
            # Load Instagram data
            if os.path.exists('instagram_data.jsonl'):
                with open('instagram_data.jsonl', 'r', encoding='utf-8') as f:
                    self.instagram_data = []
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                self.instagram_data.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            
            # Load TikTok data
            if os.path.exists('tiktok_data.jsonl'):
                with open('tiktok_data.jsonl', 'r', encoding='utf-8') as f:
                    self.tiktok_data = []
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                self.tiktok_data.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            
            print(f"Loaded {len(self.instagram_data)} Instagram records, {len(self.tiktok_data)} TikTok records")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_engagement_patterns(self):
        """Analyze real engagement patterns from data"""
        all_posts = self.instagram_data + self.tiktok_data
        
        if not all_posts:
            return {
                'total_posts': 0,
                'engagement_metrics': {},
                'temporal_patterns': {},
                'content_analysis': {}
            }
        
        # Engagement metrics
        engagement_data = []
        hashtag_performance = defaultdict(list)
        temporal_data = defaultdict(list)
        
        for post in all_posts:
            # Extract engagement metrics
            likes = self._safe_get_number(post, ['like_count', 'likes', 'likeCount'])
            comments = self._safe_get_number(post, ['comment_count', 'comments', 'commentCount'])
            shares = self._safe_get_number(post, ['share_count', 'shares', 'shareCount'])
            
            total_engagement = likes + comments + shares
            engagement_data.append(total_engagement)
            
            # Temporal analysis
            timestamp = self._extract_timestamp(post)
            if timestamp:
                date_key = timestamp.strftime('%Y-%m-%d')
                temporal_data[date_key].append(total_engagement)
            
            # Hashtag performance
            caption = self._safe_get_text(post, ['caption', 'text', 'description'])
            hashtags = self._extract_hashtags(caption)
            for hashtag in hashtags:
                hashtag_performance[hashtag].append(total_engagement)
        
        # Calculate averages and trends
        avg_engagement = sum(engagement_data) / len(engagement_data) if engagement_data else 0
        
        # Top performing hashtags
        hashtag_avg = {}
        for tag, engagements in hashtag_performance.items():
            if len(engagements) >= 2:
                hashtag_avg[tag] = sum(engagements) / len(engagements)
        
        top_hashtags = sorted(hashtag_avg.items(), key=lambda x: x[1], reverse=True)[:15]
        
        # Temporal trends
        temporal_trends = {}
        for date, engagements in temporal_data.items():
            temporal_trends[date] = sum(engagements) / len(engagements)
        
        return {
            'total_posts': len(all_posts),
            'total_engagement': sum(engagement_data),
            'avg_engagement': avg_engagement,
            'engagement_metrics': {
                'instagram_posts': len(self.instagram_data),
                'tiktok_posts': len(self.tiktok_data),
                'top_hashtags': top_hashtags,
                'temporal_trends': temporal_trends
            }
        }
    
    def _safe_get_number(self, data, keys):
        for key in keys:
            if key in data and data[key] is not None:
                try:
                    return int(data[key])
                except (ValueError, TypeError):
                    continue
        return 0
    
    def _safe_get_text(self, data, keys):
        for key in keys:
            if key in data and data[key]:
                return str(data[key])
        return ""
    
    def _extract_timestamp(self, post):
        timestamp_keys = ['timestamp', 'created_at', 'date', 'published_at']
        for key in timestamp_keys:
            if key in post and post[key]:
                try:
                    ts = post[key]
                    if isinstance(ts, str):
                        for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                            try:
                                return datetime.strptime(ts.replace('Z', '+00:00'), fmt.replace('%z', ''))
                            except ValueError:
                                continue
                    elif isinstance(ts, (int, float)):
                        return datetime.fromtimestamp(ts)
                except Exception:
                    continue
        return None
    
    def _extract_hashtags(self, text):
        if not text:
            return []
        return re.findall(r'#\w+', text.lower())

data_processor = DataProcessor()

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    """Get real analytics data"""
    analysis = data_processor.analyze_engagement_patterns()
    
    if analysis['total_posts'] == 0:
        return jsonify({
            'status': 'no_data',
            'message': 'No data found. Please ensure instagram_data.jsonl and tiktok_data.jsonl are in the root directory.'
        })
    
    # Create charts (same as previous version)
    temporal_trends = analysis['engagement_metrics'].get('temporal_trends', {})
    sorted_dates = sorted(temporal_trends.keys())[-30:]
    
    engagement_chart = {
        'data': [{
            'x': sorted_dates,
            'y': [temporal_trends.get(date, 0) for date in sorted_dates],
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Daily Avg Engagement',
            'line': {'color': '#ff6b35', 'width': 3}
        }],
        'layout': {
            'title': {'text': 'Engagement Timeline', 'font': {'color': 'white'}},
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'}
        }
    }
    
    top_hashtags = analysis['engagement_metrics'].get('top_hashtags', [])[:10]
    hashtag_chart = {
        'data': [{
            'x': [tag for tag, avg_eng in top_hashtags],
            'y': [avg_eng for tag, avg_eng in top_hashtags],
            'type': 'bar',
            'marker': {'color': '#ff6b35'}
        }],
        'layout': {
            'title': {'text': 'Top Hashtags', 'font': {'color': 'white'}},
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'}
        }
    }
    
    return jsonify({
        'status': 'success',
        'metrics': {
            'total_posts': analysis['total_posts'],
            'total_engagement': int(analysis['total_engagement']),
            'avg_engagement': round(analysis['avg_engagement'], 1),
            'instagram_posts': analysis['engagement_metrics']['instagram_posts'],
            'tiktok_posts': analysis['engagement_metrics']['tiktok_posts']
        },
        'charts': {
            'engagement': engagement_chart,
            'hashtags': hashtag_chart
        },
        'data_freshness': datetime.now().isoformat()
    })

# Content Management Routes
@app.route('/api/content', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_content():
    if request.method == 'GET':
        content = content_manager.get_all_content()
        return jsonify({'content': content})
    
    elif request.method == 'POST':
        content_data = request.json
        content_id = content_manager.add_content(content_data)
        return jsonify({'success': True, 'content_id': content_id})
    
    elif request.method == 'PUT':
        content_id = request.json.get('id')
        updates = {k: v for k, v in request.json.items() if k != 'id'}
        content_manager.update_content(content_id, updates)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        content_id = request.json.get('id')
        content_manager.delete_content(content_id)
        return jsonify({'success': True})

# Calendar Management Routes
@app.route('/api/calendar', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_calendar():
    if request.method == 'GET':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
            events = calendar_manager.get_calendar_events(start, end)
        else:
            events = calendar_manager.get_calendar_events()
        
        # Add strategic milestones
        milestones = calendar_manager.generate_strategic_milestones()
        
        return jsonify({
            'events': events,
            'milestones': milestones
        })
    
    elif request.method == 'POST':
        event_data = request.json
        event_id = calendar_manager.add_event(event_data)
        return jsonify({'success': True, 'event_id': event_id})
    
    elif request.method == 'PUT':
        event_id = request.json.get('id')
        updates = {k: v for k, v in request.json.items() if k != 'id'}
        calendar_manager.update_event(event_id, updates)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        event_id = request.json.get('id')
        calendar_manager.delete_event(event_id)
        return jsonify({'success': True})

@app.route('/api/deliverables/update', methods=['POST'])
def update_deliverable_status():
    """Update deliverable completion status"""
    try:
        data = request.json
        deliverable_id = data.get('id')
        status = data.get('status')  # 'pending', 'in_progress', 'completed', 'approved'
        notes = data.get('notes', '')
        
        # Load existing deliverables tracking
        tracking_file = 'calendar_data/deliverables_tracking.json'
        tracking_data = {}
        
        if os.path.exists(tracking_file):
            with open(tracking_file, 'r', encoding='utf-8') as f:
                tracking_data = json.load(f)
        
        # Update deliverable status
        tracking_data[deliverable_id] = {
            'status': status,
            'notes': notes,
            'updated_at': datetime.now().isoformat(),
            'updated_by': data.get('updated_by', 'User')
        }
        
        # Save tracking data
        with open(tracking_file, 'w', encoding='utf-8') as f:
            json.dump(tracking_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deliverables/status')
def get_deliverables_status():
    """Get current deliverables tracking status"""
    try:
        tracking_file = 'calendar_data/deliverables_tracking.json'
        tracking_data = {}
        
        if os.path.exists(tracking_file):
            with open(tracking_file, 'r', encoding='utf-8') as f:
                tracking_data = json.load(f)
        
        return jsonify({'tracking': tracking_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cultural-insights')
def get_cultural_insights():
    """Get streetwear-specific cultural insights"""
    insights = [
        {
            'trend': 'Y2K Streetwear Revival',
            'impact': 'High',
            'description': 'Early 2000s baggy jeans, oversized tees, and tech-wear aesthetics returning',
            'opportunity': 'Launch retro-inspired collection with modern fits',
            'timeline': '2024-2025',
            'cultural_moment': 'Nostalgia cycles driving 20-year fashion returns'
        },
        {
            'trend': 'Sustainable Streetwear Movement',
            'impact': 'Medium',
            'description': 'Gen Z driving demand for eco-conscious streetwear brands',
            'opportunity': 'Highlight sustainable materials and ethical manufacturing',
            'timeline': 'Ongoing',
            'cultural_moment': 'Climate consciousness in fashion consumption'
        },
        {
            'trend': 'Micro-Influencer Streetwear Culture',
            'impact': 'High',
            'description': 'Smaller creators driving authentic streetwear engagement',
            'opportunity': 'Partner with niche streetwear content creators under 100K followers',
            'timeline': '2024-2025',
            'cultural_moment': 'Authenticity over celebrity in streetwear marketing'
        },
        {
            'trend': 'Streetwear x Music Collaborations',
            'impact': 'High',
            'description': 'Hip-hop, trap, and alternative artists driving streetwear trends',
            'opportunity': 'Explore artist collaborations and music festival presence',
            'timeline': 'Year-round',
            'cultural_moment': 'Music and streetwear cultural convergence'
        },
        {
            'trend': 'Gender-Neutral Streetwear',
            'impact': 'Medium',
            'description': 'Unisex sizing and non-binary fashion gaining streetwear market share',
            'opportunity': 'Expand unisex product lines and inclusive marketing',
            'timeline': 'Ongoing',
            'cultural_moment': 'Gender fluidity in fashion expression'
        }
    ]
    
    return jsonify({'cultural_insights': insights})

# Enhanced Asset Management Routes
@app.route('/api/assets', methods=['GET', 'POST'])
def handle_assets():
    if request.method == 'GET':
        query = request.args.get('search', '')
        category = request.args.get('category')
        file_type = request.args.get('type')
        
        assets = asset_manager.search_assets(query, category, file_type)
        categories = ASSET_CATEGORIES
        
        return jsonify({
            'assets': assets,
            'categories': categories
        })
    
    elif request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['ASSETS_FOLDER'], filename)
        file.save(filepath)
        
        # Add asset with metadata
        category = request.form.get('category', 'Other')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        uploader = request.form.get('uploader', 'Unknown')
        
        asset_info = asset_manager.add_asset(filename, category, description, tags, uploader)
        
        if asset_info:
            return jsonify({'success': True, 'asset': asset_info})
        else:
            return jsonify({'error': 'Failed to process asset'}), 500

@app.route('/api/assets/download/<filename>')
def download_asset(filename):
    """Download asset and increment download counter"""
    try:
        filepath = os.path.join(app.config['ASSETS_FOLDER'], filename)
        if not os.path.exists(filepath):
            abort(404)
        
        # Update download counter
        metadata = asset_manager.get_asset_metadata()
        if filename in metadata:
            metadata[filename]['download_count'] = metadata[filename].get('download_count', 0) + 1
            metadata[filename]['last_downloaded'] = datetime.now().isoformat()
            asset_manager.save_asset_metadata(metadata)
        
        return send_file(filepath, as_attachment=True)
    except Exception:
        abort(404)

@app.route('/api/assets/thumbnail/<path:thumbnail_path>')
def get_thumbnail(thumbnail_path):
    """Serve asset thumbnails"""
    try:
        filepath = os.path.join(app.config['ASSETS_FOLDER'], thumbnail_path)
        return send_file(filepath)
    except Exception:
        abort(404)

@app.route('/api/assets/delete/<filename>', methods=['DELETE'])
def delete_asset(filename):
    """Delete asset and its metadata"""
    try:
        filepath = os.path.join(app.config['ASSETS_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remove thumbnail if exists
        metadata = asset_manager.get_asset_metadata()
        if filename in metadata and metadata[filename].get('thumbnail'):
            thumbnail_path = os.path.join(app.config['ASSETS_FOLDER'], metadata[filename]['thumbnail'])
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        
        # Remove metadata
        if filename in metadata:
            del metadata[filename]
            asset_manager.save_asset_metadata(metadata)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/analytics')
def export_analytics():
    """Export analytics data for team reporting"""
    analysis = data_processor.analyze_engagement_patterns()
    
    # Create comprehensive CSV report
    data = []
    temporal_trends = analysis['engagement_metrics'].get('temporal_trends', {})
    
    for date, engagement in temporal_trends.items():
        data.append({
            'Date': date,
            'Average_Engagement': engagement,
            'Total_Posts': analysis['total_posts'],
            'Platform_Mix': f"IG: {analysis['engagement_metrics']['instagram_posts']}, TT: {analysis['engagement_metrics']['tiktok_posts']}"
        })
    
    if data:
        df = pd.DataFrame(data)
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=crooks_analytics_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    else:
        return jsonify({'error': 'No data to export'}), 400

# Initialize data processing
@app.before_first_request
def initialize_app():
    """Initialize the application with real data"""
    success = data_processor.load_social_data()
    if success:
        print("✅ Real data loaded successfully")
    else:
        print("⚠️  No data files found - ensure JSONL files are present")

if __name__ == '__main__':
    # Load data immediately for development
    data_processor.load_social_data()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
