import os
import json
import csv
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import uuid
from PIL import Image
import io
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'assets'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'psd', 'ai', 'sketch', 'fig'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'assets',
        'team_data',
        'content_library', 
        'calendar_data'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Initialize directories when app starts
ensure_directories()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_thumbnail(filepath):
    """Generate thumbnail for image files"""
    try:
        if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            with Image.open(filepath) as img:
                img.thumbnail((200, 200))
                thumb_path = filepath.rsplit('.', 1)[0] + '_thumb.' + filepath.rsplit('.', 1)[1]
                img.save(thumb_path)
                return thumb_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
    return None

def load_social_data():
    """Load and process social media data from JSONL files"""
    instagram_data = []
    tiktok_data = []
    
    # Load Instagram data
    try:
        with open('instagram_data.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        instagram_data.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
    except FileNotFoundError:
        pass
    
    # Load TikTok data  
    try:
        with open('tiktok_data.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        tiktok_data.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
    except FileNotFoundError:
        pass
    
    return instagram_data, tiktok_data

def get_cultural_moments():
    """Return streetwear cultural moments and seasonal events"""
    cultural_moments = [
        {
            'date': '2025-01-01',
            'event': 'New Year Collections Launch',
            'category': 'seasonal',
            'description': 'Fresh starts, new year drops, resolution-themed content',
            'opportunity': 'Launch limited edition "New Year, New Fit" collection'
        },
        {
            'date': '2025-02-14',
            'event': 'Valentine\'s Day',
            'category': 'seasonal',
            'description': 'Couple streetwear, gift-worthy accessories',
            'opportunity': 'Partner pieces, gift guides for streetwear couples'
        },
        {
            'date': '2025-03-20',
            'event': 'Spring Equinox',
            'category': 'seasonal',
            'description': 'Layering transition, lighter colors',
            'opportunity': 'Spring transition collection, lighter fabrics'
        },
        {
            'date': '2025-04-11',
            'event': 'Coachella Weekend 1',
            'category': 'cultural',
            'description': 'Peak festival fashion, influencer collabs, desert aesthetics',
            'opportunity': 'Festival capsule collection, influencer partnerships'
        },
        {
            'date': '2025-04-18',
            'event': 'Coachella Weekend 2',
            'category': 'cultural', 
            'description': 'Extended festival content, FOMO marketing',
            'opportunity': 'Weekend 2 exclusive drops, social content push'
        },
        {
            'date': '2025-05-15',
            'event': 'High School Graduation Season',
            'category': 'demographic',
            'description': 'Gen Z milestone moments, celebratory fits',
            'opportunity': 'Graduation collection, milestone marketing'
        },
        {
            'date': '2025-06-21',
            'event': 'Summer Solstice',
            'category': 'seasonal',
            'description': 'Peak summer vibes, vacation fits',
            'opportunity': 'Summer essentials, vacation-ready streetwear'
        },
        {
            'date': '2025-07-04',
            'event': 'Independence Day',
            'category': 'cultural',
            'description': 'American streetwear pride, patriotic aesthetics',
            'opportunity': 'USA-themed limited drops, patriotic colorways'
        },
        {
            'date': '2025-08-15',
            'event': 'Back-to-School Season',
            'category': 'demographic',
            'description': 'Student streetwear, campus culture, fresh semester energy',
            'opportunity': 'Student discounts, campus ambassador program'
        },
        {
            'date': '2025-09-10',
            'event': 'New York Fashion Week',
            'category': 'cultural',
            'description': 'High fashion meets street, trend forecasting',
            'opportunity': 'NYFW influence pieces, runway-to-street translations'
        },
        {
            'date': '2025-10-31',
            'event': 'Halloween',
            'category': 'seasonal',
            'description': 'Costume streetwear, spooky aesthetics',
            'opportunity': 'Halloween-themed drops, costume-ready pieces'
        },
        {
            'date': '2025-11-28',
            'event': 'Black Friday',
            'category': 'commercial',
            'description': 'Biggest streetwear shopping day, limited drops',
            'opportunity': 'Major discounts, exclusive BFCM releases'
        },
        {
            'date': '2025-11-30',
            'event': 'Cyber Monday',
            'category': 'commercial',
            'description': 'Online streetwear sales peak',
            'opportunity': 'Digital-exclusive drops, online-only colorways'
        },
        {
            'date': '2025-12-25',
            'event': 'Holiday Season',
            'category': 'seasonal',
            'description': 'Gift-giving, holiday parties, winter layering',
            'opportunity': 'Holiday gift guides, winter essentials, party fits'
        }
    ]
    
    return cultural_moments

def get_hvd_deliverables():
    """Return High Voltage Digital deliverables structure from agreement"""
    deliverables = {
        'phase1': {
            'budget': 4000,
            'duration': 'Months 1-3',
            'focus': 'Foundation & Awareness',
            'deliverables': [
                {
                    'item': 'Social Media Content',
                    'quantity': '3-4 creatives per month',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'Email Marketing Setup',
                    'quantity': '2 campaigns per month',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'SMS Marketing Setup',
                    'quantity': '1 campaign per month', 
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'Brand Strategy Development',
                    'quantity': '1 comprehensive strategy',
                    'status': 'pending',
                    'notes': ''
                }
            ]
        },
        'phase2': {
            'budget': 7500,
            'duration': 'Months 4-6 (Q4 Push)',
            'focus': 'BFCM Campaign & Growth',
            'deliverables': [
                {
                    'item': 'BFCM Campaign Development',
                    'quantity': 'Complete campaign package',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'Increased Social Content',
                    'quantity': '5-6 creatives per month',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'Email Automation Flows',
                    'quantity': '3-4 flows per month',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'SMS Campaign Scale',
                    'quantity': '2 campaigns per month',
                    'status': 'pending', 
                    'notes': ''
                }
            ]
        },
        'phase3': {
            'budget': 10000,
            'duration': 'Months 7+ (Full Retainer)',
            'focus': 'Full Service Marketing',
            'deliverables': [
                {
                    'item': 'SEO Optimization',
                    'quantity': 'Ongoing optimization',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'CRO Implementation', 
                    'quantity': 'Conversion rate optimization',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'Advanced Email Flows',
                    'quantity': '4-5 complex flows per month',
                    'status': 'pending',
                    'notes': ''
                },
                {
                    'item': 'Premium Social Content',
                    'quantity': '6-8 creatives per month',
                    'status': 'pending',
                    'notes': ''
                }
            ]
        }
    }
    
    return deliverables

def save_hvd_deliverables(deliverables_data):
    """Save updated HVD deliverables to file"""
    try:
        with open('team_data/hvd_deliverables.json', 'w') as f:
            json.dump(deliverables_data, f, indent=2)
    except Exception as e:
        print(f"Error saving deliverables: {e}")

def load_hvd_deliverables():
    """Load HVD deliverables from file or return defaults"""
    try:
        with open('team_data/hvd_deliverables.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return get_hvd_deliverables()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/api/analytics')
def get_analytics():
    """API endpoint for analytics data"""
    instagram_data, tiktok_data = load_social_data()
    
    analytics = {
        'instagram': {
            'total_posts': len(instagram_data),
            'avg_engagement': 0,
            'top_hashtags': [],
            'recent_performance': []
        },
        'tiktok': {
            'total_posts': len(tiktok_data),
            'avg_engagement': 0,
            'top_hashtags': [],
            'recent_performance': []
        },
        'combined': {
            'total_posts': len(instagram_data) + len(tiktok_data),
            'platforms': 2 if (instagram_data and tiktok_data) else 1 if (instagram_data or tiktok_data) else 0
        }
    }
    
    # Process Instagram data
    if instagram_data:
        total_engagement = 0
        hashtag_counts = {}
        
        for post in instagram_data:
            # Calculate engagement if available
            if 'likes' in post and 'comments' in post:
                engagement = int(post.get('likes', 0)) + int(post.get('comments', 0))
                total_engagement += engagement
            
            # Count hashtags
            if 'hashtags' in post:
                for hashtag in post['hashtags']:
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        analytics['instagram']['avg_engagement'] = round(total_engagement / len(instagram_data), 2) if instagram_data else 0
        analytics['instagram']['top_hashtags'] = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Process TikTok data
    if tiktok_data:
        total_engagement = 0
        hashtag_counts = {}
        
        for post in tiktok_data:
            # Calculate engagement if available  
            if 'likes' in post and 'comments' in post:
                engagement = int(post.get('likes', 0)) + int(post.get('comments', 0))
                total_engagement += engagement
            
            # Count hashtags
            if 'hashtags' in post:
                for hashtag in post['hashtags']:
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        analytics['tiktok']['avg_engagement'] = round(total_engagement / len(tiktok_data), 2) if tiktok_data else 0
        analytics['tiktok']['top_hashtags'] = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify(analytics)

@app.route('/api/assets')
def get_assets():
    """API endpoint for asset library"""
    assets = []
    
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file_stat = os.stat(filepath)
                
                asset = {
                    'id': str(uuid.uuid4()),
                    'name': filename,
                    'type': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown',
                    'size': file_stat.st_size,
                    'uploaded': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'uploader': 'Team',
                    'downloads': 0,
                    'thumbnail': None
                }
                
                # Check for thumbnail
                thumb_path = filepath.rsplit('.', 1)[0] + '_thumb.' + filepath.rsplit('.', 1)[1]
                if os.path.exists(thumb_path):
                    asset['thumbnail'] = thumb_path
                
                assets.append(asset)
    
    return jsonify(assets)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Handle filename conflicts
        counter = 1
        while os.path.exists(filepath):
            name, ext = filename.rsplit('.', 1)
            new_filename = f"{name}_{counter}.{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, new_filename)
            filename = new_filename
            counter += 1
        
        file.save(filepath)
        
        # Generate thumbnail for images
        thumbnail = generate_thumbnail(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File uploaded successfully'
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/download/<filename>')
def download_file(filename):
    """Handle file downloads"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/content')
def get_content():
    """API endpoint for content library"""
    content = []
    
    try:
        if os.path.exists('content_library/content.json'):
            with open('content_library/content.json', 'r') as f:
                content = json.load(f)
    except Exception as e:
        print(f"Error loading content: {e}")
    
    return jsonify(content)

@app.route('/api/content', methods=['POST'])
def create_content():
    """Create new content piece"""
    try:
        data = request.json
        content_piece = {
            'id': str(uuid.uuid4()),
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'platform': data.get('platform', 'instagram'),
            'status': data.get('status', 'draft'),
            'scheduled_date': data.get('scheduled_date', ''),
            'hashtags': data.get('hashtags', []),
            'created': datetime.now().isoformat(),
            'creator': 'Team'
        }
        
        # Load existing content
        content = []
        if os.path.exists('content_library/content.json'):
            with open('content_library/content.json', 'r') as f:
                content = json.load(f)
        
        content.append(content_piece)
        
        # Save updated content
        with open('content_library/content.json', 'w') as f:
            json.dump(content, f, indent=2)
        
        return jsonify({'success': True, 'content': content_piece})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar')
def get_calendar():
    """API endpoint for calendar events"""
    events = []
    
    # Load cultural moments
    cultural_moments = get_cultural_moments()
    for moment in cultural_moments:
        events.append({
            'id': str(uuid.uuid4()),
            'title': moment['event'],
            'date': moment['date'],
            'category': moment['category'],
            'description': moment['description'],
            'type': 'cultural',
            'editable': False
        })
    
    # Load custom events
    try:
        if os.path.exists('calendar_data/events.json'):
            with open('calendar_data/events.json', 'r') as f:
                custom_events = json.load(f)
                events.extend(custom_events)
    except Exception as e:
        print(f"Error loading custom events: {e}")
    
    return jsonify(events)

@app.route('/api/calendar', methods=['POST'])
def create_event():
    """Create calendar event"""
    try:
        data = request.json
        event = {
            'id': str(uuid.uuid4()),
            'title': data.get('title', ''),
            'date': data.get('date', ''),
            'category': data.get('category', 'campaign'),
            'description': data.get('description', ''),
            'assignee': data.get('assignee', ''),
            'type': 'custom',
            'editable': True,
            'created': datetime.now().isoformat()
        }
        
        # Load existing events
        events = []
        if os.path.exists('calendar_data/events.json'):
            with open('calendar_data/events.json', 'r') as f:
                events = json.load(f)
        
        events.append(event)
        
        # Save updated events
        with open('calendar_data/events.json', 'w') as f:
            json.dump(events, f, indent=2)
        
        return jsonify({'success': True, 'event': event})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deliverables')
def get_deliverables():
    """API endpoint for HVD deliverables"""
    deliverables = load_hvd_deliverables()
    return jsonify(deliverables)

@app.route('/api/deliverables', methods=['POST'])
def update_deliverables():
    """Update deliverable status"""
    try:
        data = request.json
        deliverables = load_hvd_deliverables()
        
        phase = data.get('phase')
        item_index = data.get('item_index')
        status = data.get('status')
        notes = data.get('notes', '')
        
        if phase in deliverables and 0 <= item_index < len(deliverables[phase]['deliverables']):
            deliverables[phase]['deliverables'][item_index]['status'] = status
            deliverables[phase]['deliverables'][item_index]['notes'] = notes
            deliverables[phase]['deliverables'][item_index]['updated'] = datetime.now().isoformat()
            
            save_hvd_deliverables(deliverables)
            return jsonify({'success': True})
        
        return jsonify({'error': 'Invalid deliverable reference'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cultural-insights')
def get_cultural_insights():
    """API endpoint for cultural intelligence insights"""
    insights = {
        'current_trends': [
            {
                'trend': 'Y2K Streetwear Revival',
                'description': 'Baggy jeans, oversized fits, and tech-wear aesthetics returning strongly',
                'opportunity': 'Launch Y2K-inspired capsule collection with authentic early 2000s silhouettes',
                'timeframe': 'Q1-Q2 2025',
                'confidence': 'High'
            },
            {
                'trend': 'Sustainable Streetwear Movement',
                'description': 'Gen Z driving demand for eco-conscious materials and ethical production',
                'opportunity': 'Develop sustainable line using recycled materials and transparent supply chain',
                'timeframe': 'Ongoing',
                'confidence': 'Very High'
            },
            {
                'trend': 'Gender-Neutral Fashion',
                'description': 'Increasing demand for unisex sizing and inclusive marketing approaches',
                'opportunity': 'Create gender-neutral core collection with inclusive sizing and marketing',
                'timeframe': 'Q2 2025',
                'confidence': 'High'
            }
        ],
        'cultural_moments': get_cultural_moments()[:5],  # Next 5 cultural moments
        'consumer_behavior': [
            {
                'behavior': 'Micro-Influencer Trust',
                'insight': 'Consumers trust smaller creators (10K-100K followers) more than mega-influencers',
                'action': 'Partner with streetwear micro-influencers for authentic product showcases'
            },
            {
                'behavior': 'Music x Fashion Connection',
                'insight': 'Hip-hop and alternative music artists heavily influence streetwear purchasing decisions',
                'action': 'Identify rising artists for collaboration opportunities and playlist partnerships'
            },
            {
                'behavior': 'Limited Drop FOMO',
                'insight': 'Scarcity marketing drives immediate purchase decisions in streetwear community',
                'action': 'Implement limited edition drops with clear quantity limits and countdown timers'
            }
        ]
    }
    
    return jsonify(insights)

@app.route('/api/export/analytics')
def export_analytics():
    """Export analytics data as CSV"""
    try:
        instagram_data, tiktok_data = load_social_data()
        
        # Create CSV data
        csv_data = []
        csv_data.append(['Platform', 'Total Posts', 'Avg Engagement', 'Date Exported'])
        csv_data.append(['Instagram', len(instagram_data), 'N/A', datetime.now().strftime('%Y-%m-%d')])
        csv_data.append(['TikTok', len(tiktok_data), 'N/A', datetime.now().strftime('%Y-%m-%d')])
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        
        return jsonify({
            'success': True,
            'filename': f'analytics_export_{datetime.now().strftime("%Y%m%d")}.csv',
            'data': output.getvalue()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
