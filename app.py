from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from datetime import datetime, timedelta
import os
import json
from werkzeug.utils import secure_filename
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['THUMBNAILS_FOLDER'] = 'uploads/thumbnails'
app.config['METADATA_FOLDER'] = 'uploads/metadata'
app.config['STATIC_THUMBNAILS'] = 'static/thumbnails'
app.config['CALENDAR_DATA'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['THUMBNAILS_FOLDER'], 
               app.config['METADATA_FOLDER'], app.config['STATIC_THUMBNAILS'],
               app.config['CALENDAR_DATA']]:
    os.makedirs(folder, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp4', 'mov'}

def allowed_file(filename):
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
    else:
        return 'general'

# Sample data for demonstration
def get_sample_calendar_data():
    return {
        "events": [
            # 7-day events
            {
                "id": "1",
                "title": "Gratitude Collection Launch",
                "description": "Launch new gratitude-themed apparel collection with social media campaign",
                "start_date": (datetime.now() + timedelta(days=6)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=6)).isoformat(),
                "type": "product_launch",
                "status": "scheduled",
                "priority": "high"
            },
            {
                "id": "2",
                "title": "Instagram Content Batch",
                "description": "Create and schedule week's worth of Instagram posts",
                "start_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "type": "content_creation",
                "status": "in_progress",
                "priority": "medium"
            },
            # 30-day events
            {
                "id": "3",
                "title": "Frequency Collective Recruitment",
                "description": "Campus ambassador program recruitment campaign across target universities",
                "start_date": (datetime.now() + timedelta(days=15)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=25)).isoformat(),
                "type": "marketing",
                "status": "planning",
                "priority": "medium"
            },
            {
                "id": "4",
                "title": "Brand Photoshoot",
                "description": "Lifestyle photoshoot for new seasonal collection",
                "start_date": (datetime.now() + timedelta(days=18)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=18)).isoformat(),
                "type": "content_creation",
                "status": "scheduled",
                "priority": "high"
            },
            {
                "id": "5",
                "title": "Website Launch",
                "description": "Launch updated e-commerce website with new BOHO theme",
                "start_date": (datetime.now() + timedelta(days=28)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=28)).isoformat(),
                "type": "website",
                "status": "in_progress",
                "priority": "high"
            },
            # 60-day events
            {
                "id": "6",
                "title": "Fall Collection Design",
                "description": "Design and develop fall apparel collection with new affirmations",
                "start_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=55)).isoformat(),
                "type": "product_development",
                "status": "planning",
                "priority": "high"
            },
            {
                "id": "7",
                "title": "Campus Pop-Up Events",
                "description": "Organize pop-up events at target universities",
                "start_date": (datetime.now() + timedelta(days=50)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=52)).isoformat(),
                "type": "events",
                "status": "planning",
                "priority": "medium"
            },
            # 90-day events
            {
                "id": "8",
                "title": "Holiday Collection Launch",
                "description": "Launch limited edition holiday collection with special packaging",
                "start_date": (datetime.now() + timedelta(days=75)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=75)).isoformat(),
                "type": "product_launch",
                "status": "planning",
                "priority": "high"
            },
            {
                "id": "9",
                "title": "Brand Partnership Campaign",
                "description": "Collaborate with wellness brands for cross-promotion",
                "start_date": (datetime.now() + timedelta(days=80)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=85)).isoformat(),
                "type": "partnerships",
                "status": "planning",
                "priority": "medium"
            }
        ]
    }

def get_sample_assets():
    return [
        {
            "id": "1",
            "name": "Peacock Color Palette Guide",
            "type": "brand_guide",
            "url": "#",
            "created_date": "2025-09-09",
            "file_size": "2.1 MB",
            "is_uploaded": False,
            "description": "Complete color palette with hex codes"
        },
        {
            "id": "2", 
            "name": "Kynd Vibes Script Logo",
            "type": "logo",
            "url": "#",
            "created_date": "2025-09-09",
            "file_size": "45 KB",
            "is_uploaded": False,
            "description": "Primary script logo for garments"
        },
        {
            "id": "3",
            "name": "Energy Rays Brand Element",
            "type": "brand_element",
            "url": "#",
            "created_date": "2025-09-09",
            "file_size": "12 KB",
            "is_uploaded": False,
            "description": "Refined energy rays for brand applications"
        },
        {
            "id": "4",
            "name": "Talisman Symbol (44)",
            "type": "brand_element",
            "url": "#",
            "created_date": "2025-09-09",
            "file_size": "8 KB",
            "is_uploaded": False,
            "description": "Feather, flame, and 44 mystique symbol"
        }
    ]

def get_sample_deliverables():
    return [
        {
            "id": "1",
            "title": "Homepage Mockup",
            "description": "Sophisticated homepage design with peacock palette",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "status": "completed",
            "priority": "high",
            "assignee": "Design Team"
        },
        {
            "id": "2",
            "title": "Frequency Collective Landing Page",
            "description": "Ambassador program recruitment page design and copy",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "in_progress",
            "priority": "medium",
            "assignee": "Marketing Team"
        },
        {
            "id": "3",
            "title": "Brand Guidelines Document",
            "description": "Complete brand guidelines with color usage, typography, and logo applications",
            "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "status": "pending",
            "priority": "high",
            "assignee": "Brand Team"
        }
    ]

def load_uploaded_assets():
    """Load assets from uploads directory"""
    uploaded_assets = []
    upload_folder = app.config['UPLOAD_FOLDER']
    
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            if allowed_file(filename):
                file_path = os.path.join(upload_folder, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    uploaded_assets.append({
                        "id": str(uuid.uuid4()),
                        "name": filename,
                        "type": get_asset_type(filename),
                        "url": f"/uploads/{filename}",
                        "created_date": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d'),
                        "file_size": get_file_size_string(stat.st_size),
                        "is_uploaded": True,
                        "description": f"Uploaded {get_asset_type(filename)} file"
                    })
    
    return uploaded_assets

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/healthz')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "brand_frequency": "high"
    })

@app.route('/api/calendar')
def get_calendar():
    try:
        period = request.args.get('period', 'next_30_days')
        logger.info(f"Calendar request for period: {period}")
        
        # Get sample data
        calendar_data = get_sample_calendar_data()
        all_events = calendar_data['events'].copy()
        
        # Load custom events (from deliverables)
        calendar_file = os.path.join(app.config['CALENDAR_DATA'], 'custom_events.json')
        if os.path.exists(calendar_file):
            try:
                with open(calendar_file, 'r') as f:
                    custom_events = json.load(f)
                    all_events.extend(custom_events)
            except Exception as e:
                logger.warning(f"Could not load custom events: {e}")
        
        # Filter events based on period
        now = datetime.now()
        if period == 'next_7_days' or period == '7day':
            end_date = now + timedelta(days=7)
        elif period == 'next_60_days' or period == '60day':
            end_date = now + timedelta(days=60)
        elif period == 'next_90_days' or period == '90day':
            end_date = now + timedelta(days=90)
        else:  # next_30_days or 30day
            end_date = now + timedelta(days=30)
        
        # Filter events within the period
        filtered_events = []
        for event in all_events:
            try:
                event_date = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00').replace('+00:00', ''))
                if now <= event_date <= end_date:
                    filtered_events.append(event)
            except Exception as e:
                logger.warning(f"Could not parse event date: {event.get('start_date', 'unknown')} - {e}")
        
        return jsonify({
            "success": True,
            "events": filtered_events,
            "period": period,
            "total_events": len(filtered_events)
        })
        
    except Exception as e:
        logger.error(f"Calendar error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "events": []
        }), 500

@app.route('/api/assets')
def get_assets():
    try:
        logger.info("Assets request received")
        
        # Combine sample assets with uploaded assets
        sample_assets = get_sample_assets()
        uploaded_assets = load_uploaded_assets()
        
        all_assets = sample_assets + uploaded_assets
        
        return jsonify({
            "success": True,
            "assets": all_assets,
            "total_assets": len(all_assets)
        })
        
    except Exception as e:
        logger.error(f"Assets error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "assets": []
        }), 500

@app.route('/api/deliverables', methods=['GET', 'POST'])
def handle_deliverables():
    if request.method == 'GET':
        try:
            logger.info("Deliverables request received")
            
            # Get sample deliverables
            deliverables = get_sample_deliverables()
            
            # Load custom deliverables from file
            deliverables_file = os.path.join(app.config['CALENDAR_DATA'], 'deliverables.json')
            if os.path.exists(deliverables_file):
                try:
                    with open(deliverables_file, 'r') as f:
                        custom_deliverables = json.load(f)
                        deliverables.extend(custom_deliverables)
                except Exception as e:
                    logger.warning(f"Could not load custom deliverables: {e}")
            
            # Sort by due date
            deliverables.sort(key=lambda x: x.get('due_date', '9999-12-31'))
            
            return jsonify({
                "success": True,
                "deliverables": deliverables,
                "total_deliverables": len(deliverables)
            })
            
        except Exception as e:
            logger.error(f"Deliverables error: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "deliverables": []
            }), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['title', 'description', 'due_date', 'priority']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Create new deliverable
            new_deliverable = {
                "id": str(uuid.uuid4()),
                "title": data['title'],
                "description": data['description'],
                "due_date": data['due_date'],
                "status": data.get('status', 'pending'),
                "priority": data['priority'],
                "assignee": data.get('assignee', 'Team'),
                "created_date": datetime.now().isoformat()
            }
            
            # Save to file (in production, you'd save to database)
            deliverables_file = os.path.join(app.config['CALENDAR_DATA'], 'deliverables.json')
            
            # Load existing deliverables
            existing_deliverables = []
            if os.path.exists(deliverables_file):
                try:
                    with open(deliverables_file, 'r') as f:
                        existing_deliverables = json.load(f)
                except:
                    existing_deliverables = []
            
            # Add new deliverable
            existing_deliverables.append(new_deliverable)
            
            # Save back to file
            with open(deliverables_file, 'w') as f:
                json.dump(existing_deliverables, f, indent=2)
            
            # Also create corresponding calendar event
            calendar_event = {
                "id": f"deliverable_{new_deliverable['id']}",
                "title": f"📋 {new_deliverable['title']}",
                "description": new_deliverable['description'],
                "start_date": new_deliverable['due_date'],
                "end_date": new_deliverable['due_date'],
                "type": "deliverable",
                "status": new_deliverable['status'],
                "priority": new_deliverable['priority'],
                "deliverable_id": new_deliverable['id']
            }
            
            # Save calendar event
            calendar_file = os.path.join(app.config['CALENDAR_DATA'], 'custom_events.json')
            existing_events = []
            if os.path.exists(calendar_file):
                try:
                    with open(calendar_file, 'r') as f:
                        existing_events = json.load(f)
                except:
                    existing_events = []
            
            existing_events.append(calendar_event)
            
            with open(calendar_file, 'w') as f:
                json.dump(existing_events, f, indent=2)
            
            logger.info(f"New deliverable created: {new_deliverable['title']}")
            
            return jsonify({
                "success": True,
                "message": "Deliverable created successfully",
                "deliverable": new_deliverable,
                "calendar_event": calendar_event
            })
            
        except Exception as e:
            logger.error(f"Create deliverable error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "File type not allowed"}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        logger.info(f"File uploaded successfully: {filename}")
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "filename": filename,
            "file_size": get_file_size_string(file_size),
            "asset_type": get_asset_type(filename),
            "url": f"/uploads/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"File serve error: {e}")
        return jsonify({"error": "File not found"}), 404

@app.route('/api/export')
def export_data():
    try:
        # Combine all data for export
        export_data = {
            "calendar": get_sample_calendar_data(),
            "assets": get_sample_assets() + load_uploaded_assets(),
            "deliverables": get_sample_deliverables(),
            "export_date": datetime.now().isoformat(),
            "brand": "KyndVibes"
        }
        
        return jsonify({
            "success": True,
            "data": export_data
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/brand-guide')
def brand_guide():
    return jsonify({
        "success": True,
        "message": "Brand guide accessed",
        "url": "/brand-guide"
    })

@app.route('/api/frequency-collective')
def frequency_collective():
    return jsonify({
        "success": True,
        "message": "Frequency Collective accessed",
        "url": "/frequency-collective"
    })

# Error handlers
@app.route('/api/view-palette')
def view_palette():
    """Serve the brand palette guide"""
    try:
        # Return the palette data as JSON for viewing
        palette_data = {
            "name": "KyndVibes Peacock-Inspired Brand Palette",
            "primary_colors": {
                "deep_teal": "#008B8B",
                "vibrant_turquoise": "#00CED1", 
                "midnight_navy": "#1B2951",
                "bright_pink": "#FF1493"
            },
            "secondary_colors": {
                "lime_green": "#32CD32",
                "rich_purple": "#8A2BE2",
                "lavender": "#D5BDE4",
                "premium_white": "#FFFFFF",
                "sophisticated_charcoal": "#2C2C2C"
            },
            "usage_guidelines": {
                "primary_use": "Headers, buttons, key brand elements",
                "secondary_use": "Accents, backgrounds, supporting elements",
                "accessibility": "All color combinations meet WCAG AA standards"
            }
        }
        return jsonify(palette_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory('uploads', filename)
    except Exception as e:
        return jsonify({"error": "File not found"}), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

