from flask import Flask, render_template, request, jsonify, send_from_directory
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

# Initialize managers only if modules are available
try:
    from asset_manager import AssetManager
    asset_manager = AssetManager(
        app.config['UPLOAD_FOLDER'],
        app.config['THUMBNAILS_FOLDER'], 
        app.config['METADATA_FOLDER']
    )
    ASSET_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Asset manager not available: {e}")
    ASSET_MANAGER_AVAILABLE = False

try:
    from calendar_manager import CalendarManager
    calendar_manager = CalendarManager(app.config['CALENDAR_DATA'])
    CALENDAR_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Calendar manager not available: {e}")
    CALENDAR_MANAGER_AVAILABLE = False

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Sample data for fallback when managers aren't available
sample_calendar_data = {
    "events": [
        {
            "id": "1",
            "title": "Gratitude Collection Launch",
            "description": "Launch new gratitude-themed apparel collection",
            "start_date": (datetime.now() + timedelta(days=6)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=6)).isoformat(),
            "type": "product_launch",
            "status": "scheduled",
            "priority": "high"
        },
        {
            "id": "2",
            "title": "Frequency Collective Recruitment",
            "description": "Campus ambassador program recruitment campaign",
            "start_date": (datetime.now() + timedelta(days=11)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=25)).isoformat(),
            "type": "marketing",
            "status": "planning",
            "priority": "medium"
        }
    ]
}

sample_assets = [
    {
        "id": "1",
        "name": "Peacock Color Palette Guide",
        "type": "brand_guide",
        "url": "/static/assets/peacock-palette.jpg",
        "created_date": "2025-09-09",
        "file_size": "2.1 MB",
        "is_uploaded": False
    },
    {
        "id": "2", 
        "name": "Kynd Vibes Script Logo",
        "type": "logo",
        "url": "/static/assets/kynd-vibes-script.svg",
        "created_date": "2025-09-09",
        "file_size": "45 KB",
        "is_uploaded": False
    },
    {
        "id": "3",
        "name": "Energy Rays Element",
        "type": "brand_element", 
        "url": "/static/assets/energy-rays.svg",
        "created_date": "2025-09-09",
        "file_size": "12 KB",
        "is_uploaded": False
    }
]

sample_deliverables = [
    {
        "id": "1",
        "title": "Homepage Mockup - BOHO Theme",
        "description": "Sophisticated homepage design with peacock palette",
        "status": "completed",
        "due_date": "2025-09-10",
        "priority": "high"
    },
    {
        "id": "2",
        "title": "Frequency Collective Page Design",
        "description": "Ambassador program page with UGC integration",
        "status": "in_progress",
        "due_date": "2025-09-12",
        "priority": "medium"
    },
    {
        "id": "3",
        "title": "Brand Guide Implementation",
        "description": "Complete brand guide with peacock palette and usage guidelines",
        "status": "pending",
        "due_date": "2025-09-15",
        "priority": "high"
    }
]

def get_all_assets():
    """Get all assets - use asset manager if available, otherwise fallback to sample data"""
    if ASSET_MANAGER_AVAILABLE:
        try:
            # Static sample assets
            static_assets = sample_assets.copy()
            
            # Add uploaded assets
            uploaded_assets = []
            uploads_dir = app.config['UPLOAD_FOLDER']
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    file_path = os.path.join(uploads_dir, filename)
                    if os.path.isfile(file_path):
                        # Extract original filename from unique filename
                        original_name = filename.split('_', 1)[1] if '_' in filename else filename
                        file_ext = original_name.split('.')[-1].lower()
                        
                        # Determine asset type based on extension
                        if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                            asset_type = 'image'
                        elif file_ext in ['pdf']:
                            asset_type = 'document'
                        elif file_ext in ['mp4', 'mov']:
                            asset_type = 'video'
                        else:
                            asset_type = 'file'
                        
                        uploaded_assets.append({
                            "id": f"uploaded_{filename}",
                            "name": original_name,
                            "type": asset_type,
                            "url": f"/uploads/{filename}",
                            "created_date": datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d"),
                            "file_size": f"{os.path.getsize(file_path) / 1024:.1f} KB",
                            "is_uploaded": True
                        })
            
            return static_assets + uploaded_assets
        except Exception as e:
            logger.error(f"Error getting assets: {e}")
            return sample_assets
    else:
        return sample_assets

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/healthz')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "KyndVibes Command Center"
    })

@app.route('/api/calendar')
def get_calendar():
    try:
        if CALENDAR_MANAGER_AVAILABLE:
            # Get query parameters
            period = request.args.get('period', 'next_30_days')
            days_back = int(request.args.get('days_back', 7))
            days_forward = int(request.args.get('days_forward', 60))
            
            if period == 'rolling':
                calendar_data = calendar_manager.get_rolling_calendar(days_back, days_forward)
            else:
                # Handle legacy period requests
                period_map = {
                    'next_7_days': 7,
                    'next_30_days': 30,
                    'next_60_days': 60,
                    'next_90_days': 90
                }
                days = period_map.get(period, 30)
                start_date = datetime.now()
                end_date = start_date + timedelta(days=days)
                events = calendar_manager.get_events_in_range(start_date, end_date)
                
                calendar_data = {
                    'events': events,
                    'total_events': len(events),
                    'period': period,
                    'range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }
            
            return jsonify(calendar_data)
        else:
            # Fallback to sample data
            period = request.args.get('period', 'next_30_days')
            today = datetime.now()
            
            period_map = {
                'next_7_days': 7,
                'next_30_days': 30,
                'next_60_days': 60,
                'next_90_days': 90
            }
            days = period_map.get(period, 30)
            end_date = today + timedelta(days=days)
            
            # Filter events based on period
            filtered_events = []
            for event in sample_calendar_data['events']:
                event_date = datetime.fromisoformat(event['start_date'])
                if today <= event_date <= end_date:
                    filtered_events.append(event)
            
            return jsonify({
                "events": filtered_events,
                "total_events": len(filtered_events),
                "period": period
            })
        
    except Exception as e:
        logger.error(f"Calendar error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calendar/events', methods=['POST'])
def create_event():
    try:
        if CALENDAR_MANAGER_AVAILABLE:
            event_data = request.get_json()
            new_event = calendar_manager.create_event(event_data)
            return jsonify(new_event), 201
        else:
            return jsonify({"error": "Calendar manager not available"}), 503
        
    except Exception as e:
        logger.error(f"Create event error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/assets')
def get_assets():
    try:
        all_assets = get_all_assets()
        return jsonify({
            "assets": all_assets,
            "total_assets": len(all_assets)
        })
    except Exception as e:
        logger.error(f"Assets error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/deliverables')
def get_deliverables():
    try:
        return jsonify({
            "deliverables": sample_deliverables,
            "total_deliverables": len(sample_deliverables)
        })
    except Exception as e:
        logger.error(f"Deliverables error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            if ASSET_MANAGER_AVAILABLE:
                # Get additional metadata from form
                campaign_tags = request.form.get('campaign_tags', '').split(',') if request.form.get('campaign_tags') else []
                asset_type = request.form.get('asset_type', 'general')
                
                # Process asset with full pipeline
                metadata = asset_manager.process_uploaded_asset(
                    file_path, filename, campaign_tags, asset_type
                )
                
                # Copy thumbnail to static folder for web access
                if metadata.get('thumbnail_url'):
                    thumbnail_filename = os.path.basename(metadata['thumbnail_url'])
                    src_path = os.path.join(app.config['THUMBNAILS_FOLDER'], thumbnail_filename)
                    dst_path = os.path.join(app.config['STATIC_THUMBNAILS'], thumbnail_filename)
                    if os.path.exists(src_path):
                        import shutil
                        shutil.copy2(src_path, dst_path)
                
                return jsonify({
                    "success": True,
                    "filename": unique_filename,
                    "original_filename": filename,
                    "metadata": metadata
                })
            else:
                # Basic upload without processing
                return jsonify({
                    "success": True,
                    "filename": unique_filename,
                    "original_filename": filename,
                    "upload_date": datetime.now().isoformat(),
                    "file_size": os.path.getsize(file_path)
                })
        else:
            return jsonify({"error": "File type not allowed"}), 400
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Additional endpoints for when managers are available
@app.route('/api/content-planning/campaign-requirements/<campaign_type>')
def get_campaign_requirements(campaign_type):
    try:
        if ASSET_MANAGER_AVAILABLE:
            deliverable_date_str = request.args.get('deliverable_date')
            if deliverable_date_str:
                deliverable_date = datetime.fromisoformat(deliverable_date_str)
            else:
                deliverable_date = datetime.now() + timedelta(days=30)
            
            requirements = asset_manager.get_campaign_requirements(campaign_type, deliverable_date)
            if requirements:
                return jsonify(requirements)
            else:
                return jsonify({"error": "Campaign type not found"}), 404
        else:
            return jsonify({"error": "Asset manager not available"}), 503
            
    except Exception as e:
        logger.error(f"Campaign requirements error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

