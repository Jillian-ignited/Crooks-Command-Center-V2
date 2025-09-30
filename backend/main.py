from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Error handler for consistent error responses
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'ok': False,
        'error': 'Endpoint not found',
        'message': 'The requested resource was not found on this server.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'ok': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500

# Executive Overview Routes
@app.route('/api/executive/overview', methods=['GET'])
def get_executive_overview():
    """Get executive overview data including brands, competitors, and benchmarks."""
    try:
        # Mock data - replace with actual database queries
        overview_data = {
            'ok': True,
            'brands': {
                'count': 3,
                'list': ['Crooks & Castles', 'Streetwear Co', 'Urban Brand']
            },
            'competitors': {
                'count': 5,
                'list': ['Supreme', 'Off-White', 'Fear of God', 'Stussy', 'BAPE']
            },
            'benchmarks': {
                'count': 12,
                'metrics': [
                    {'metric': 'CTR', 'value': '2.3%', 'trend': 'up'},
                    {'metric': 'Conversion Rate', 'value': '1.8%', 'trend': 'stable'},
                    {'metric': 'AOV', 'value': '$127', 'trend': 'up'},
                    {'metric': 'ROAS', 'value': '4.2x', 'trend': 'up'}
                ]
            },
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("Executive overview data retrieved successfully")
        return jsonify(overview_data)
        
    except Exception as e:
        logger.error(f"Error retrieving executive overview: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to retrieve overview data',
            'message': str(e)
        }), 500

# Intelligence Routes
@app.route('/api/intelligence/upload', methods=['POST'])
def upload_intelligence():
    """Handle file upload for intelligence processing."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'ok': False,
                'error': 'No file provided',
                'message': 'Please select a file to upload.'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'ok': False,
                'error': 'No file selected',
                'message': 'Please select a valid file.'
            }), 400
        
        # Process the file (mock implementation)
        filename = file.filename
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        
        # Mock processing result
        result = {
            'ok': True,
            'message': 'File uploaded and processed successfully',
            'file_info': {
                'filename': filename,
                'size': file_size,
                'processed_at': datetime.now().isoformat()
            },
            'insights': [
                'Identified 15 trending keywords',
                'Found 8 competitor mentions',
                'Extracted 23 cultural moments'
            ]
        }
        
        logger.info(f"Intelligence file uploaded: {filename}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error uploading intelligence file: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': str(e)
        }), 500

# Calendar Routes
@app.route('/api/calendar/status', methods=['GET'])
def get_calendar_status():
    """Get Google Calendar connection status."""
    try:
        # Mock calendar status
        status = {
            'ok': True,
            'connected': True,
            'last_sync': datetime.now().isoformat(),
            'account': 'crooks@example.com',
            'calendars_count': 3
        }
        
        logger.info("Calendar status retrieved")
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting calendar status: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to get calendar status',
            'message': str(e)
        }), 500

@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get calendar events for specified time range."""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Mock events data
        events = []
        base_date = datetime.now()
        
        for i in range(min(days // 7, 5)):  # Generate some sample events
            event_date = base_date + timedelta(days=i*2)
            events.append({
                'title': f'Content Review Meeting #{i+1}',
                'start': event_date.isoformat(),
                'end': (event_date + timedelta(hours=1)).isoformat(),
                'location': 'Conference Room A'
            })
        
        logger.info(f"Retrieved {len(events)} calendar events for {days} days")
        return jsonify(events)
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to get calendar events',
            'message': str(e)
        }), 500

# Content Creation Routes
@app.route('/api/content/brief', methods=['POST'])
def create_content_brief():
    """Create a new content brief."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'ok': False,
                'error': 'No data provided',
                'message': 'Please provide brief data in JSON format.'
            }), 400
        
        # Validate required fields
        required_fields = ['brand', 'objective', 'audience', 'tone', 'channels']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'ok': False,
                'error': 'Missing required fields',
                'message': f'Please provide: {", ".join(missing_fields)}'
            }), 400
        
        # Process the brief (mock implementation)
        brief_result = {
            'ok': True,
            'brief_id': f'brief_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'created_at': datetime.now().isoformat(),
            'input_data': data,
            'generated_brief': {
                'campaign_name': f'{data["brand"]} - {data["objective"]}',
                'target_audience': data['audience'],
                'key_messages': [
                    f'Authentic {data["brand"]} experience',
                    f'Designed for {data["audience"]}',
                    f'Tone: {data["tone"]}'
                ],
                'channels': data['channels'].split(','),
                'deliverables': [
                    '4 social media posts',
                    '2 video assets',
                    '1 email campaign'
                ]
            }
        }
        
        logger.info(f"Content brief created for {data['brand']}")
        return jsonify(brief_result)
        
    except Exception as e:
        logger.error(f"Error creating content brief: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to create brief',
            'message': str(e)
        }), 500

@app.route('/api/content/generate', methods=['POST'])
def generate_content_ideas():
    """Generate content ideas based on theme and brand."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'ok': False,
                'error': 'No data provided',
                'message': 'Please provide generation parameters in JSON format.'
            }), 400
        
        brand = data.get('brand', '')
        theme = data.get('theme', '')
        count = data.get('count', '5')
        
        try:
            count = int(count)
        except ValueError:
            count = 5
        
        # Generate mock content ideas
        ideas = []
        for i in range(min(count, 10)):  # Limit to 10 ideas max
            ideas.append({
                'id': f'idea_{i+1}',
                'title': f'{brand} {theme} Concept #{i+1}',
                'description': f'A compelling {theme.lower()} story that showcases {brand} authenticity',
                'format': ['Instagram Post', 'TikTok Video', 'Story'][i % 3],
                'target_audience': 'Gen Z streetwear enthusiasts',
                'key_elements': [
                    f'{theme} aesthetic',
                    f'{brand} branding',
                    'Street culture references'
                ]
            })
        
        result = {
            'ok': True,
            'generated_at': datetime.now().isoformat(),
            'parameters': {
                'brand': brand,
                'theme': theme,
                'requested_count': count
            },
            'ideas': ideas,
            'total_generated': len(ideas)
        }
        
        logger.info(f"Generated {len(ideas)} content ideas for {brand}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating content ideas: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to generate ideas',
            'message': str(e)
        }), 500

# Media/Asset Library Routes
@app.route('/api/media', methods=['GET'])
def get_media_assets():
    """Get list of media assets."""
    try:
        # Mock media assets
        assets = [
            {
                'id': 'asset_1',
                'name': 'Crooks Logo Primary',
                'type': 'image',
                'format': 'PNG',
                'size': '1080x1080',
                'url': '/assets/crooks_logo_primary.png',
                'created_at': '2025-09-15T10:00:00Z'
            },
            {
                'id': 'asset_2',
                'name': 'Street Culture Video',
                'type': 'video',
                'format': 'MP4',
                'duration': '00:30',
                'url': '/assets/street_culture_video.mp4',
                'created_at': '2025-09-20T14:30:00Z'
            },
            {
                'id': 'asset_3',
                'name': 'Hip-Hop Background Track',
                'type': 'audio',
                'format': 'MP3',
                'duration': '02:15',
                'url': '/assets/hiphop_background.mp3',
                'created_at': '2025-09-25T09:15:00Z'
            }
        ]
        
        result = {
            'ok': True,
            'assets': assets,
            'total_count': len(assets),
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info(f"Retrieved {len(assets)} media assets")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrieving media assets: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to retrieve media assets',
            'message': str(e)
        }), 500

# Summary Routes
@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get application summary data."""
    try:
        summary = {
            'ok': True,
            'period': 'Last 30 days',
            'metrics': {
                'content_created': 47,
                'campaigns_active': 8,
                'assets_generated': 156,
                'compliance_score': 94.5
            },
            'recent_activity': [
                {
                    'action': 'Content Brief Created',
                    'details': 'Hispanic Heritage Campaign',
                    'timestamp': '2025-09-30T10:30:00Z'
                },
                {
                    'action': 'Assets Generated',
                    'details': '12 Instagram posts for BFCM prep',
                    'timestamp': '2025-09-30T09:15:00Z'
                },
                {
                    'action': 'Calendar Updated',
                    'details': 'Q4 campaign milestones added',
                    'timestamp': '2025-09-29T16:45:00Z'
                }
            ],
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info("Summary data retrieved")
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error retrieving summary: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to retrieve summary',
            'message': str(e)
        }), 500

# Agency Routes
@app.route('/api/agency', methods=['GET'])
def get_agency_data():
    """Get agency partnership data."""
    try:
        agency_data = {
            'ok': True,
            'partner': 'High Voltage Digital',
            'contract_phase': 2,
            'monthly_deliverables': {
                'current': 7,
                'target': 10,
                'completion_rate': 70
            },
            'budget_tracking': {
                'current_phase_budget': 7500,
                'spent': 5250,
                'remaining': 2250,
                'efficiency_score': 87.3
            },
            'upcoming_milestones': [
                {
                    'milestone': 'Phase 2 Review',
                    'due_date': '2025-10-15',
                    'status': 'on_track'
                },
                {
                    'milestone': 'BFCM Campaign Launch',
                    'due_date': '2025-11-01',
                    'status': 'planning'
                }
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("Agency data retrieved")
        return jsonify(agency_data)
        
    except Exception as e:
        logger.error(f"Error retrieving agency data: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to retrieve agency data',
            'message': str(e)
        }), 500

# Shopify Routes
@app.route('/api/shopify', methods=['GET'])
def get_shopify_data():
    """Get Shopify integration data."""
    try:
        shopify_data = {
            'ok': True,
            'store_connected': True,
            'store_url': 'crooksandcastles.myshopify.com',
            'products_synced': 247,
            'recent_orders': 156,
            'inventory_status': {
                'in_stock': 198,
                'low_stock': 32,
                'out_of_stock': 17
            },
            'top_products': [
                {
                    'name': 'Crooks Logo Hoodie',
                    'sales': 45,
                    'revenue': 2250
                },
                {
                    'name': 'Castles Graphic Tee',
                    'sales': 38,
                    'revenue': 1140
                },
                {
                    'name': 'Street Culture Cap',
                    'sales': 29,
                    'revenue': 725
                }
            ],
            'last_sync': datetime.now().isoformat()
        }
        
        logger.info("Shopify data retrieved")
        return jsonify(shopify_data)
        
    except Exception as e:
        logger.error(f"Error retrieving Shopify data: {str(e)}")
        return jsonify({
            'ok': False,
            'error': 'Failed to retrieve Shopify data',
            'message': str(e)
        }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'ok': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Crooks Command Center API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
