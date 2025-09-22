import os
import json
import csv
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import uuid
import re
from collections import defaultdict, Counter
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import io
import base64

# Import enhanced modules
from data_processor import (
    generate_competitive_analysis, 
    process_intelligence_data,
    analyze_hashtags,
    identify_cultural_moments,
    generate_recommendations,
    calculate_trustworthiness_score
)
from enhanced_data_processor import process_enhanced_intelligence_data
from content_planning_engine import get_content_opportunities, get_content_calendar, export_content_plan
from asset_manager import (
    scan_assets,
    add_asset,
    remove_asset,
    get_assets_by_category,
    get_asset_categories,
    search_assets,
    get_asset_stats,
    generate_thumbnail
)
from calendar_engine import (
    get_calendar,
    add_calendar_event,
    remove_calendar_event
    #get_cultural_intelligence,
    #get_budget_allocation
)

from agency_tracker import (
    get_agency_status,
    update_project_status,
    get_deliverables,
    track_budget_usage
)

app = Flask(__name__)
app.secret_key = 'crooks-castles-secret-key-2025'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'psd', 'ai', 'sketch', 'fig', 'json', 'jsonl'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Competitive Intelligence Configuration
COMPETITORS = {
    'stussy': {'name': 'Stussy', 'tier': 'premium', 'founded': 1980},
    'supreme': {'name': 'Supreme', 'tier': 'luxury', 'founded': 1994},
    'hellstar': {'name': 'Hellstar', 'tier': 'emerging', 'founded': 2020},
    'godspeed': {'name': 'Godspeed', 'tier': 'emerging', 'founded': 2019},
    'fear_of_god_essentials': {'name': 'Fear of God Essentials', 'tier': 'luxury', 'founded': 2018},
    'smoke_rise': {'name': 'Smoke Rise', 'tier': 'mid-tier', 'founded': 2012},
    'reason_clothing': {'name': 'Reason Clothing', 'tier': 'mid-tier', 'founded': 2006},
    'lrg': {'name': 'LRG', 'tier': 'established', 'founded': 1999},
    'diamond_supply': {'name': 'Diamond Supply Co.', 'tier': 'established', 'founded': 1998},
    'ed_hardy': {'name': 'Ed Hardy', 'tier': 'legacy', 'founded': 2004},
    'von_dutch': {'name': 'Von Dutch', 'tier': 'legacy', 'founded': 1999}
}

def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'uploads', 'static/thumbnails', 'data', 'content_library', 'calendar_data',
        'competitive_data', 'competitive_data/social_scrapes',
        'competitive_data/price_monitoring', 'competitive_data/seo_data',
        'competitive_data/brand_mentions', 'competitive_data/product_launches'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Error creating directory {directory}: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize directories on startup
ensure_directories()

# ==================== MAIN ROUTES ====================

@app.route('/')
def dashboard():
    """Main dashboard route - Using embedded HTML for reliability"""
    # Use the embedded HTML template for consistent rendering
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crooks & Castles Command Center V2</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
                .header { text-align: center; margin-bottom: 30px; }
                .tabs { display: flex; justify-content: center; margin-bottom: 20px; }
                .tab { padding: 10px 20px; margin: 0 5px; background: #333; color: #fff; cursor: pointer; border-radius: 5px; }
                .tab.active { background: #ff6b35; }
                .content { max-width: 1200px; margin: 0 auto; }
                .loading { text-align: center; padding: 50px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏰 Crooks & Castles Command Center V2</h1>
                <p>Competitive Intelligence & Strategic Planning Platform</p>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('overview')">Overview</div>
                <div class="tab" onclick="showTab('intelligence')">Intelligence</div>
                <div class="tab" onclick="showTab('assets')">Assets</div>
                <div class="tab" onclick="showTab('calendar')">Calendar</div>
                <div class="tab" onclick="showTab('agency')">Agency</div>
            </div>
            
            <div class="content">
                <div id="overview" class="tab-content">
                    <div class="loading">Loading dashboard data...</div>
                </div>
                <div id="intelligence" class="tab-content" style="display:none;">
                    <div class="loading">Loading intelligence data...</div>
                </div>
                <div id="assets" class="tab-content" style="display:none;">
                    <div class="loading">Loading asset library...</div>
                </div>
                <div id="calendar" class="tab-content" style="display:none;">
                    <div class="loading">Loading calendar...</div>
                </div>
                <div id="agency" class="tab-content" style="display:none;">
                    <div class="loading">Loading agency tracking...</div>
                </div>
            </div>
            
            <script>
                function showTab(tabName) {
                    // Hide all tabs
                    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
                    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                    
                    // Show selected tab
                    document.getElementById(tabName).style.display = 'block';
                    event.target.classList.add('active');
                    
                    // Load data for the tab
                    loadTabData(tabName);
                }
                
                function loadTabData(tabName) {
                    const content = document.getElementById(tabName);
                    
                    switch(tabName) {
                        case 'overview':
                            loadOverview(content);
                            break;
                        case 'intelligence':
                            loadIntelligence(content);
                            break;
                        case 'assets':
                            loadAssets(content);
                            break;
                        case 'calendar':
                            loadCalendar(content);
                            break;
                        case 'agency':
                            loadAgency(content);
                            break;
                    }
                }
                
                function loadOverview(container) {
                    fetch('/api/overview')
                        .then(response => response.json())
                        .then(data => {
                            container.innerHTML = `
                                <h2>📊 Dashboard Overview</h2>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                                    <div style="background: #333; padding: 20px; border-radius: 8px;">
                                        <h3>Intelligence Status</h3>
                                        <p>Data Sources: ${data.intelligence.sources}</p>
                                        <p>Last Updated: ${data.intelligence.last_updated}</p>
                                        <p>Trustworthiness: ${data.intelligence.trustworthiness_score}%</p>
                                    </div>
                                    <div style="background: #333; padding: 20px; border-radius: 8px;">
                                        <h3>Asset Library</h3>
                                        <p>Total Assets: ${data.assets.total}</p>
                                        <p>Categories: ${data.assets.categories}</p>
                                        <p>Storage Used: ${data.assets.storage_mb}MB</p>
                                    </div>
                                    <div style="background: #333; padding: 20px; border-radius: 8px;">
                                        <h3>Calendar Planning</h3>
                                        <p>Upcoming Events: ${data.calendar.upcoming_events}</p>
                                        <p>Active Campaigns: ${data.calendar.active_campaigns}</p>
                                        <p>Budget Allocated: $${data.calendar.budget_allocated}</p>
                                    </div>
                                    <div style="background: #333; padding: 20px; border-radius: 8px;">
                                        <h3>Agency Status</h3>
                                        <p>Active Projects: ${data.agency.active_projects}</p>
                                        <p>Monthly Budget: $${data.agency.monthly_budget}</p>
                                        <p>Completion Rate: ${data.agency.completion_rate}%</p>
                                    </div>
                                </div>
                            `;
                        })
                        .catch(error => {
                            container.innerHTML = '<p>Error loading overview data</p>';
                        });
                }
                
                function loadIntelligence(container) {
                    fetch('/api/intelligence')
                        .then(response => response.json())
                        .then(data => {
                            container.innerHTML = `
                                <h2>🎯 Competitive Intelligence</h2>
                                <div style="margin-bottom: 20px;">
                                    <strong>Analysis Timestamp:</strong> ${data.analysis_timestamp}<br>
                                    <strong>Trustworthiness Score:</strong> ${data.trustworthiness_score}%<br>
                                    <strong>Total Posts Analyzed:</strong> ${data.data_summary.total_analyzed}
                                </div>
                                
                                <h3>📈 Top Trending Hashtags</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                                    ${Object.entries(data.hashtag_analysis).slice(0, 6).map(([hashtag, info]) => `
                                        <div style="background: #333; padding: 15px; border-radius: 5px;">
                                            <strong>${hashtag}</strong><br>
                                            <small>Uses: ${info.count} | Engagement: ${info.avg_engagement}</small><br>
                                            <small>Relevance: ${info.relevance}</small>
                                        </div>
                                    `).join('')}
                                </div>
                                
                                <h3>🏆 Top Recommendations</h3>
                                <div>
                                    ${data.recommendations.slice(0, 3).map(rec => `
                                        <div style="background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff6b35;">
                                            <strong>${rec.recommendation}</strong><br>
                                            <small>Priority: ${rec.priority} | Expected Impact: ${rec.expected_impact}</small><br>
                                            <p style="margin: 10px 0 0 0; font-size: 0.9em;">${rec.rationale}</p>
                                        </div>
                                    `).join('')}
                                </div>
                            `;
                        })
                        .catch(error => {
                            container.innerHTML = '<p>Error loading intelligence data</p>';
                        });
                }
                
                function loadAssets(container) {
                    fetch('/api/assets')
                        .then(response => response.json())
                        .then(data => {
                            container.innerHTML = `
                                <h2>📁 Asset Library</h2>
                                <div style="margin-bottom: 20px;">
                                    <button onclick="document.getElementById('fileInput').click()" style="background: #ff6b35; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                                        📤 Upload Assets
                                    </button>
                                    <input type="file" id="fileInput" multiple style="display: none;" onchange="uploadFiles(this.files)">
                                </div>
                                
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                    ${data.assets.map(asset => `
                                        <div style="background: #333; padding: 15px; border-radius: 8px; text-align: center;">
                                            ${asset.thumbnail_path ? 
                                                `<img src="${asset.thumbnail_path}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 5px; margin-bottom: 10px;">` :
                                                `<div style="width: 100%; height: 120px; background: #555; border-radius: 5px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center;">📄</div>`
                                            }
                                            <strong>${asset.filename}</strong><br>
                                            <small>${asset.file_size_mb}MB | ${asset.category}</small><br>
                                            <a href="${asset.download_url}" style="color: #ff6b35; text-decoration: none; font-size: 0.9em;">⬇️ Download</a>
                                        </div>
                                    `).join('')}
                                </div>
                            `;
                        })
                        .catch(error => {
                            container.innerHTML = '<p>Error loading asset data</p>';
                        });
                }
                
                function loadCalendar(container) {
                    fetch('/api/calendar/30')
                        .then(response => response.json())
                        .then(data => {
                            container.innerHTML = `
                                <h2>📅 Strategic Calendar</h2>
                                <div style="margin-bottom: 20px;">
                                    <button onclick="loadCalendarView('7')" style="background: #333; color: white; padding: 8px 16px; border: none; border-radius: 3px; margin: 0 5px; cursor: pointer;">7 Days</button>
                                    <button onclick="loadCalendarView('30')" style="background: #ff6b35; color: white; padding: 8px 16px; border: none; border-radius: 3px; margin: 0 5px; cursor: pointer;">30 Days</button>
                                    <button onclick="loadCalendarView('60')" style="background: #333; color: white; padding: 8px 16px; border: none; border-radius: 3px; margin: 0 5px; cursor: pointer;">60 Days</button>
                                    <button onclick="loadCalendarView('90')" style="background: #333; color: white; padding: 8px 16px; border: none; border-radius: 3px; margin: 0 5px; cursor: pointer;">90 Days</button>
                                </div>
                                
                                <div id="calendar-events">
                                    ${data.events.map(event => `
                                        <div style="background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff6b35;">
                                            <strong>${event.title}</strong> - ${event.date}<br>
                                            <small>Category: ${event.category} | Budget: $${event.budget}</small><br>
                                            <p style="margin: 10px 0 0 0; font-size: 0.9em;">${event.description}</p>
                                            ${event.assets ? `<small>Assets: ${event.assets.join(', ')}</small>` : ''}
                                        </div>
                                    `).join('')}
                                </div>
                            `;
                        })
                        .catch(error => {
                            container.innerHTML = '<p>Error loading calendar data</p>';
                        });
                }
                
                function loadAgency(container) {
                    fetch('/api/agency')
                        .then(response => response.json())
                        .then(data => {
                            container.innerHTML = `
                                <h2>🏢 Agency Tracking</h2>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                                    <div style="background: #333; padding: 20px; border-radius: 8px;">
                                        <h3>High Voltage Digital</h3>
                                        <p><strong>Current Phase:</strong> ${data.current_phase}</p>
                                        <p><strong>Monthly Budget:</strong> $${data.monthly_budget}</p>
                                        <p><strong>Completion Rate:</strong> ${data.completion_rate}%</p>
                                        <p><strong>Next Milestone:</strong> ${data.next_milestone}</p>
                                    </div>
                                    <div style="background: #333; padding: 20px; border-radius: 8px;">
                                        <h3>Recent Deliverables</h3>
                                        ${data.recent_deliverables.map(deliverable => `
                                            <div style="margin: 10px 0; padding: 10px; background: #444; border-radius: 5px;">
                                                <strong>${deliverable.title}</strong><br>
                                                <small>Due: ${deliverable.due_date} | Status: ${deliverable.status}</small>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            `;
                        })
                        .catch(error => {
                            container.innerHTML = '<p>Error loading agency data</p>';
                        });
                }
                
                function loadCalendarView(days) {
                    fetch(`/api/calendar/${days}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('calendar-events').innerHTML = data.events.map(event => `
                                <div style="background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff6b35;">
                                    <strong>${event.title}</strong> - ${event.date}<br>
                                    <small>Category: ${event.category} | Budget: $${event.budget}</small><br>
                                    <p style="margin: 10px 0 0 0; font-size: 0.9em;">${event.description}</p>
                                    ${event.assets ? `<small>Assets: ${event.assets.join(', ')}</small>` : ''}
                                </div>
                            `).join('');
                            
                            // Update button styles
                            document.querySelectorAll('button').forEach(btn => btn.style.background = '#333');
                            event.target.style.background = '#ff6b35';
                        });
                }
                
                function uploadFiles(files) {
                    const formData = new FormData();
                    for (let file of files) {
                        formData.append('files', file);
                    }
                    
                    fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert('Files uploaded successfully!');
                        loadAssets(document.getElementById('assets'));
                    })
                    .catch(error => {
                        alert('Upload failed: ' + error);
                    });
                }
                
                // Load overview on page load
                loadOverview(document.getElementById('overview'));
            </script>
        </body>
        </html>
        """

# ==================== API ENDPOINTS ====================

@app.route('/api/overview')
def api_overview():
    """Dashboard overview data"""
    try:
        # Get intelligence status
        intelligence_data = process_intelligence_data()
        trustworthiness = calculate_trustworthiness_score(intelligence_data)
        
        # Get asset stats
        asset_stats = get_asset_stats()
        
        # Get calendar data
        calendar_data = get_calendar('30_day_view')
        
        # Get agency status
        agency_data = get_agency_status()
        
        overview_data = {
            'intelligence_status': {
                'data_sources': intelligence_data.get('total_data_sources', 3),
                'last_updated': intelligence_data.get('analysis_timestamp', 'Unknown'),
                'trustworthiness_score': trustworthiness
            },
            'assets': {
                'total': asset_stats.get('total_assets', 0),
                'categories': len(asset_stats.get('categories', {})),
                'storage_mb': asset_stats.get('total_size_mb', 0)
            },
            'calendar': {
                'upcoming_events': len(calendar_data) if isinstance(calendar_data, list) else 0,
                'active_campaigns': len([e for e in calendar_data if isinstance(e, dict) and e.get('status') == 'active']) if isinstance(calendar_data, list) else 0,
                'budget_allocated': sum(e.get('budget_allocation', 0) for e in calendar_data if isinstance(e, dict)) if isinstance(calendar_data, list) else 0
            },
            'agency': {
                'active_projects': agency_data.get('active_projects', 0),
                'monthly_budget': agency_data.get('monthly_budget', 0),
                'completion_rate': agency_data.get('utilization_rate', 0)
            }
        }
        
        return jsonify(overview_data)
    except Exception as e:
        print(f"Error in api_overview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence')
def api_intelligence():
    """Competitive intelligence analysis"""
    try:
        analysis = generate_competitive_analysis()
        return jsonify(analysis)
    except Exception as e:
        print(f"Error in api_intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets')
def api_assets():
    """Asset library data"""
    try:
        assets = scan_assets()
        categories = get_asset_categories()
        
        return jsonify({
            'assets': assets,
            'categories': categories,
            'total_assets': len(assets),
            'total_size_mb': sum(asset.get('file_size_mb', 0) for asset in assets)
        })
    except Exception as e:
        print(f"Error in api_assets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/download/<filename>')
def download_asset(filename):
    """Download asset file"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/calendar/<view>')
def api_calendar(view):
    """Calendar data for different views"""
    try:
        # Map view parameter to calendar view names
        view_mapping = {
            '7': '7_day_view',
            '30': '30_day_view', 
            '60': '60_day_view',
            '90': '90_day_view',
            '120': '120_day_view'
        }
        
        calendar_view = view_mapping.get(view, f'{view}_day_view')
        calendar_data = get_calendar(calendar_view)
        
        return jsonify({
            'view': view,
            'events': calendar_data,
            'total_events': len(calendar_data),
            'total_budget': sum(event.get('budget_allocation', 0) for event in calendar_data)
        })
    except Exception as e:
        print(f"Error in api_calendar: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agency')
def api_agency():
    """Agency tracking data"""
    try:
        agency_data = get_agency_status()
        return jsonify(agency_data)
    except Exception as e:
        print(f"Error in api_agency: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/weekly')
def api_weekly_report():
    """Weekly intelligence report"""
    try:
        analysis = generate_competitive_analysis()
        
        report = {
            'report_type': 'weekly',
            'generated_at': datetime.now().isoformat(),
            'period': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            'executive_summary': {
                'total_posts_analyzed': analysis.get('data_summary', {}).get('total_analyzed', 0),
                'trending_hashtags': len(analysis.get('hashtag_analysis', {})),
                'cultural_moments': len(analysis.get('cultural_moments', {})),
                'recommendations': len(analysis.get('recommendations', [])),
                'trustworthiness_score': analysis.get('trustworthiness_score', 0)
            },
            'key_insights': analysis.get('recommendations', [])[:5],
            'competitive_landscape': analysis.get('competitor_insights', {}),
            'cultural_intelligence': analysis.get('cultural_moments', {}),
            'next_actions': [rec.get('implementation', '') for rec in analysis.get('recommendations', [])[:3]]
        }
        
        return jsonify(report)
    except Exception as e:
        print(f"Error in api_weekly_report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/competitive')
def api_competitive_report():
    """Competitive analysis report"""
    try:
        analysis = generate_competitive_analysis()
        
        report = {
            'report_type': 'competitive',
            'generated_at': datetime.now().isoformat(),
            'competitor_analysis': analysis.get('competitor_insights', {}),
            'market_positioning': {
                'strengths': ['Authentic streetwear heritage', 'Strong cultural connections', 'Established brand recognition'],
                'opportunities': ['Digital engagement growth', 'Cultural moment activation', 'Community building'],
                'threats': ['Emerging brand competition', 'Fast fashion imitation', 'Cultural appropriation risks']
            },
            'recommendations': analysis.get('recommendations', [])
        }
        
        return jsonify(report)
    except Exception as e:
        print(f"Error in api_competitive_report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/export')
def api_export_report():
    """Export report data"""
    try:
        analysis = generate_competitive_analysis()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'data_summary': analysis.get('data_summary', {}),
            'hashtag_analysis': analysis.get('hashtag_analysis', {}),
            'competitor_insights': analysis.get('competitor_insights', {}),
            'cultural_moments': analysis.get('cultural_moments', {}),
            'recommendations': analysis.get('recommendations', []),
            'trustworthiness_score': analysis.get('trustworthiness_score', 0)
        }
        
        return jsonify(export_data)
    except Exception as e:
        print(f"Error in api_export_report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Add timestamp to avoid conflicts
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{name}_{timestamp}{ext}"
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Add to asset management system
                result = add_asset(filepath, filename, category="uploaded", metadata={
                    'upload_timestamp': datetime.now().isoformat(),
                    'original_filename': file.filename
                })
                
                if result.get('success'):
                    uploaded_files.append(result.get('asset'))
                else:
                    print(f"Error adding asset {filename}: {result.get('error')}")
        
        return jsonify({
            'success': True,
            'uploaded_files': uploaded_files,
            'count': len(uploaded_files)
        })
        
    except Exception as e:
        print(f"Error in api_upload: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== CONTENT PLANNING API ENDPOINTS ====================

@app.route('/api/content/opportunities')
def api_content_opportunities():
    """Get content opportunities based on competitive intelligence"""
    try:
        opportunities = get_content_opportunities()
        return jsonify({
            'success': True,
            'opportunities': opportunities,
            'count': len(opportunities),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_content_opportunities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/calendar')
@app.route('/api/content/calendar/<timeframe>')
def api_content_calendar(timeframe='30_day'):
    """Get comprehensive content calendar with asset mapping"""
    try:
        calendar = get_content_calendar(timeframe)
        return jsonify({
            'success': True,
            'calendar': calendar,
            'timeframe': timeframe,
            'count': len(calendar),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_content_calendar: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/export')
@app.route('/api/content/export/<format>')
def api_content_export(format='json'):
    """Export content plan in various formats"""
    try:
        if format not in ['json', 'csv']:
            return jsonify({'error': 'Invalid format. Use json or csv'}), 400
        
        content_plan = export_content_plan(format)
        
        if format == 'csv':
            response = make_response(content_plan)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=content_plan_{datetime.now().strftime("%Y%m%d")}.csv'
            return response
        else:
            return jsonify({
                'success': True,
                'content_plan': json.loads(content_plan),
                'format': format,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        print(f"Error in api_content_export: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence/enhanced')
def api_enhanced_intelligence():
    """Get enhanced competitive intelligence with Cultural Radar and Competitive Playbook insights"""
    try:
        intelligence = process_enhanced_intelligence_data()
        return jsonify({
            'success': True,
            'intelligence': intelligence,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_enhanced_intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence/cultural-radar')
def api_cultural_radar():
    """Get Cultural Radar v3.0 style report"""
    try:
        intelligence = process_enhanced_intelligence_data()
        cultural_radar = intelligence.get('cultural_radar', {})
        return jsonify({
            'success': True,
            'cultural_radar': cultural_radar,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_cultural_radar: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence/competitive-playbook')
def api_competitive_playbook():
    """Get Competitive Playbook v3.2 style analysis"""
    try:
        intelligence = process_enhanced_intelligence_data()
        competitive_playbook = intelligence.get('competitive_playbook', {})
        return jsonify({
            'success': True,
            'competitive_playbook': competitive_playbook,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_competitive_playbook: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ENHANCED CALENDAR API ENDPOINTS ====================

@app.route('/api/calendar/add', methods=['POST'])
def api_add_calendar_event():
    """Add calendar event"""
    try:
        data = request.get_json()
        result = add_calendar_event(
            title=data.get('title'),
            date=data.get('date'),
            category=data.get('category'),
            description=data.get('description'),
            budget=data.get('budget', 0),
            assets=data.get('assets', [])
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error in api_add_calendar_event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/remove/<event_id>', methods=['DELETE'])
def api_remove_calendar_event(event_id):
    """Remove calendar event"""
    try:
        result = remove_calendar_event(event_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error in api_remove_calendar_event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/remove/<asset_id>', methods=['DELETE'])
def api_remove_asset(asset_id):
    """Remove asset"""
    try:
        result = remove_asset(asset_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error in api_remove_asset: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large'}), 413

# ==================== STARTUP ====================

if __name__ == '__main__':
    print("🏰 Starting Crooks & Castles Command Center V2...")
    print("📊 Initializing competitive intelligence...")
    print("📁 Setting up asset management...")
    print("📅 Loading calendar engine...")
    print("🏢 Connecting agency tracking...")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
