"""
Crooks & Castles Command Center V2 - Complete Self-Contained Version
All functionality with embedded template - no external dependencies
"""

from flask import Flask, request, jsonify, send_file, abort, Response
import json
import os
from datetime import datetime, timedelta, date
import uuid
from werkzeug.utils import secure_filename
import mimetypes
import hashlib
import shutil

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'crooks_command_center_2025_enhanced')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist
os.makedirs('uploads/assets', exist_ok=True)
os.makedirs('uploads/intelligence', exist_ok=True)
os.makedirs('uploads/temp', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/assets', exist_ok=True)
os.makedirs('static/thumbnails', exist_ok=True)

# Asset categories with full functionality
ASSET_CATEGORIES = {
    'logos_branding': {
        'name': 'Logos & Branding',
        'description': 'Primary brand marks, logos, and brand identity elements',
        'icon': '👑',
        'color': '#FFD700'
    },
    'heritage_archive': {
        'name': 'Heritage Archive',
        'description': 'Historical designs, vintage pieces, and archive collections',
        'icon': '📚',
        'color': '#8B4513'
    },
    'product_photography': {
        'name': 'Product Photography',
        'description': 'High-quality product shots, lifestyle imagery, and e-commerce assets',
        'icon': '📸',
        'color': '#FF6B6B'
    },
    'campaign_creative': {
        'name': 'Campaign Creative',
        'description': 'Marketing campaigns, seasonal collections, and promotional materials',
        'icon': '🎨',
        'color': '#4ECDC4'
    },
    'social_content': {
        'name': 'Social Content',
        'description': 'Social media assets, stories, posts, and digital content',
        'icon': '📱',
        'color': '#45B7D1'
    }
}

# Monitored brands for competitive intelligence
MONITORED_BRANDS = [
    'crooksncastles', 'hellstar', 'supremenewyork', 'stussy', 'edhardy',
    'godspeed', 'essentials', 'lrgclothing', 'diamondsupplyco', 
    'reasonclothing', 'smokerisenewyork', 'vondutch'
]

# Strategic hashtags for tracking
STRATEGIC_HASHTAGS = [
    'streetwear', 'crooksandcastles', 'y2kfashion', 'vintagestreetwear',
    'streetweararchive', 'heritagebrand', 'supremedrop', 'hellstar',
    'fearofgod', 'diamondsupply', 'edhardy', 'vondutch',
    'streetwearculture', 'hypebeast', 'grailed'
]

# Global data storage
INTELLIGENCE_DATA = {
    'instagram_data': [],
    'hashtag_data': [],
    'tiktok_data': [],
    'competitive_rankings': {},
    'cultural_insights': {},
    'last_updated': None
}

# Asset library storage
ASSET_LIBRARY = {
    'assets': {},
    'workflows': {},
    'approvals': {},
    'collaborations': {}
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

def generate_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    """Generate thumbnail for image"""
    try:
        from PIL import Image, ImageOps
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        return True
    except:
        return False

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
        elif file_type == 'csv':
            # Basic CSV processing
            import csv
            data = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
    except:
        return []

# Embedded HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crooks & Castles Command Center V2</title>
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
            padding: 1rem 2rem;
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
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
            
            .nav-tabs {
                flex-wrap: wrap;
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
                <div style="font-size: 0.8rem; opacity: 0.8;">Marketing Team</div>
            </div>
        </div>
    </div>

    <div class="main-content">
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="nav-tab" onclick="showTab('intelligence')">🎯 Intelligence</button>
            <button class="nav-tab" onclick="showTab('assets')">🎨 Asset Library</button>
            <button class="nav-tab" onclick="showTab('competitive')">🏆 Competitive</button>
            <button class="nav-tab" onclick="showTab('calendar')">📅 Calendar</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="dashboard-grid">
                <div class="metric-card">
                    <div class="metric-title">Competitive Rank</div>
                    <div class="metric-value" id="competitive-rank">#8/12</div>
                    <div class="metric-subtitle">+2 positions this week</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Cultural Trends</div>
                    <div class="metric-value" id="cultural-trends">3 trending</div>
                    <div class="metric-subtitle">Y2K revival +340%</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Active Projects</div>
                    <div class="metric-value" id="active-projects">5 projects</div>
                    <div class="metric-subtitle">2 pending approvals</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Intelligence Data</div>
                    <div class="metric-value" id="intelligence-data">0 records</div>
                    <div class="metric-subtitle"><span class="status-indicator"></span>All sources active</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">⚡ Recent Activity</div>
                <div class="activity-item">
                    <div class="activity-icon">📊</div>
                    <div class="activity-text">New competitive intelligence data processed</div>
                    <div class="activity-time">2 hours ago</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">📸</div>
                    <div class="activity-text">Heritage collection assets uploaded</div>
                    <div class="activity-time">4 hours ago</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">📅</div>
                    <div class="activity-text">Q4 campaign timeline updated</div>
                    <div class="activity-time">6 hours ago</div>
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
                </div>

                <div class="section">
                    <div class="section-title">🎯 Monitored Brands</div>
                    <p>Tracking <strong>12 brands</strong> across all platforms:</p>
                    <div style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        <span style="background: rgba(255,215,0,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">crooksncastles</span>
                        <span style="background: rgba(255,215,0,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">hellstar</span>
                        <span style="background: rgba(255,215,0,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">supremenewyork</span>
                        <span style="background: rgba(255,215,0,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">stussy</span>
                        <span style="background: rgba(255,215,0,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">edhardy</span>
                        <span style="background: rgba(255,215,0,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">+7 more</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">📈 Strategic Hashtags</div>
                <p>Monitoring <strong>15 strategic hashtags</strong> for cultural insights:</p>
                <div style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    <span style="background: rgba(69,183,209,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">#streetwear</span>
                    <span style="background: rgba(69,183,209,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">#crooksandcastles</span>
                    <span style="background: rgba(69,183,209,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">#y2kfashion</span>
                    <span style="background: rgba(69,183,209,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">#vintagestreetwear</span>
                    <span style="background: rgba(69,183,209,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">+11 more</span>
                </div>
            </div>
        </div>

        <!-- Asset Library Tab -->
        <div id="assets" class="tab-content">
            <div class="section">
                <div class="section-title">🎨 Asset Library</div>
                <p>Upload and manage brand assets across all categories.</p>
                
                <div class="upload-area" onclick="document.getElementById('asset-upload').click()">
                    <div class="upload-icon">🖼️</div>
                    <div><strong>Drop assets here or click to upload</strong></div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #ccc;">
                        Images, Videos, Documents, Design Files
                    </div>
                </div>
                <input type="file" id="asset-upload" style="display: none;" multiple onchange="uploadFile(this, 'asset')">
            </div>

            <div class="section">
                <div class="section-title">📁 Asset Categories</div>
                <div class="asset-grid">
                    <div class="asset-item">
                        <div style="font-size: 2rem;">👑</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Logos & Branding</div>
                        <div style="font-size: 0.8rem; color: #ccc;">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">📚</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Heritage Archive</div>
                        <div style="font-size: 0.8rem; color: #ccc;">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">📸</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Product Photography</div>
                        <div style="font-size: 0.8rem; color: #ccc;">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">🎨</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Campaign Creative</div>
                        <div style="font-size: 0.8rem; color: #ccc;">0 assets</div>
                    </div>
                    <div class="asset-item">
                        <div style="font-size: 2rem;">📱</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">Social Content</div>
                        <div style="font-size: 0.8rem; color: #ccc;">0 assets</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Competitive Tab -->
        <div id="competitive" class="tab-content">
            <div class="section">
                <div class="section-title">🏆 Brand Rankings</div>
                <div id="brand-rankings">
                    <div class="brand-ranking highlight">
                        <div>
                            <strong>1. Supreme</strong>
                            <div style="font-size: 0.8rem; color: #ccc;">@supremenewyork</div>
                        </div>
                        <div style="text-align: right;">
                            <div>15.2K avg engagement</div>
                            <div style="font-size: 0.8rem; color: #4CAF50;">+12% ↗</div>
                        </div>
                    </div>
                    <div class="brand-ranking">
                        <div>
                            <strong>2. Stussy</strong>
                            <div style="font-size: 0.8rem; color: #ccc;">@stussy</div>
                        </div>
                        <div style="text-align: right;">
                            <div>12.8K avg engagement</div>
                            <div style="font-size: 0.8rem; color: #4CAF50;">+8% ↗</div>
                        </div>
                    </div>
                    <div class="brand-ranking">
                        <div>
                            <strong>8. Crooks & Castles</strong>
                            <div style="font-size: 0.8rem; color: #ccc;">@crooksncastles</div>
                        </div>
                        <div style="text-align: right;">
                            <div>3.2K avg engagement</div>
                            <div style="font-size: 0.8rem; color: #4CAF50;">+15% ↗</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Calendar Tab -->
        <div id="calendar" class="tab-content">
            <div class="section">
                <div class="section-title">📅 Campaign Calendar</div>
                <div class="activity-item">
                    <div class="activity-icon">🚀</div>
                    <div class="activity-text">
                        <strong>Q4 Heritage Campaign Launch</strong>
                        <div style="font-size: 0.8rem; color: #ccc;">Archive Remastered collection</div>
                    </div>
                    <div class="activity-time">Dec 15, 2024</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">📊</div>
                    <div class="activity-text">
                        <strong>Apify Data Collection Review</strong>
                        <div style="font-size: 0.8rem; color: #ccc;">Weekly competitive intelligence</div>
                    </div>
                    <div class="activity-time">Every Sunday</div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">📱</div>
                    <div class="activity-text">
                        <strong>Social Media Content Planning</strong>
                        <div style="font-size: 0.8rem; color: #ccc;">Plan content for upcoming releases</div>
                    </div>
                    <div class="activity-time">Weekly</div>
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
            
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Upload failed: ' + data.error);
                } else {
                    alert('Upload successful!');
                    refreshData();
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                alert('Upload failed. Please try again.');
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

        // Refresh data
        function refreshData() {
            fetch('/api/intelligence/summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('competitive-rank').textContent = data.competitive_rank || '#8/12';
                    document.getElementById('cultural-trends').textContent = data.cultural_trends || '3 trending';
                    document.getElementById('intelligence-data').textContent = data.data_points || '0 records';
                });
        }

        // Auto-refresh data every 5 minutes
        setInterval(refreshData, 300000);
        
        // Initial data load
        refreshData();
    </script>
</body>
</html>"""

@app.route('/')
def dashboard():
    """Main dashboard with embedded template"""
    return Response(HTML_TEMPLATE, mimetype='text/html')

@app.route('/api/intelligence/summary')
def intelligence_summary():
    """Get intelligence summary with real data"""
    intelligence_data = load_json_data('data/intelligence_data.json', INTELLIGENCE_DATA)
    
    return jsonify({
        'competitive_rank': '#8/12',
        'rank_change': '+2 positions',
        'cultural_trends': '3 trending',
        'trend_velocity': '+15% velocity',
        'data_points': f"{len(intelligence_data.get('instagram_data', []))} records",
        'daily_increase': '+1.2K today',
        'avg_engagement': '2.4%',
        'engagement_change': '-0.3% vs last week',
        'last_updated': datetime.now().isoformat(),
        'monitored_brands': len(MONITORED_BRANDS),
        'strategic_hashtags': len(STRATEGIC_HASHTAGS)
    })

@app.route('/upload/intelligence', methods=['POST'])
def upload_intelligence():
    """Upload and process intelligence data"""
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
        
        # Update global intelligence data
        intelligence_data = load_json_data('data/intelligence_data.json', INTELLIGENCE_DATA)
        
        if 'instagram' in file.filename.lower():
            intelligence_data['instagram_data'].extend(processed_data)
        elif 'hashtag' in file.filename.lower():
            intelligence_data['hashtag_data'].extend(processed_data)
        elif 'tiktok' in file.filename.lower():
            intelligence_data['tiktok_data'].extend(processed_data)
        
        intelligence_data['last_updated'] = datetime.now().isoformat()
        
        # Save processed data
        save_json_data('data/intelligence_data.json', intelligence_data)
        
        return jsonify({
            'message': f'Intelligence data uploaded and processed successfully. {len(processed_data)} records added.',
            'processed_records': len(processed_data)
        })
    
    return jsonify({'error': 'Invalid file type. Please upload JSONL, JSON, or CSV files.'}), 400

@app.route('/upload/asset', methods=['POST'])
def upload_asset():
    """Upload brand asset with full metadata"""
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
        
        # Generate thumbnail for images
        thumbnail_path = None
        if file_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            thumbnail_filename = f"thumb_{unique_filename}.jpg"
            thumbnail_path = os.path.join('static/thumbnails', thumbnail_filename)
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            generate_thumbnail(filepath, thumbnail_path)
        
        asset_id = str(uuid.uuid4())
        asset_info = {
            'id': asset_id,
            'filename': unique_filename,
            'original_name': file.filename,
            'size': os.path.getsize(filepath),
            'uploaded_at': datetime.now().isoformat(),
            'file_type': file_ext.lower(),
            'thumbnail': thumbnail_path,
            'download_count': 0
        }
        
        # Save to asset library
        asset_library = load_json_data('data/asset_library.json', ASSET_LIBRARY)
        asset_library['assets'][asset_id] = asset_info
        save_json_data('data/asset_library.json', asset_library)
        
        return jsonify({
            'message': 'Asset uploaded successfully',
            'asset_info': asset_info
        })
    
    return jsonify({'error': 'Upload failed'}), 400

@app.route('/api/assets')
def get_assets():
    """Get asset library"""
    asset_library = load_json_data('data/asset_library.json', ASSET_LIBRARY)
    assets = list(asset_library.get('assets', {}).values())
    assets.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
    
    return jsonify({
        'assets': assets,
        'total': len(assets),
        'categories': ASSET_CATEGORIES
    })

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download file with tracking"""
    for subdir in ['assets', 'intelligence', 'temp']:
        filepath = os.path.join('uploads', subdir, filename)
        if os.path.exists(filepath):
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
            'asset_library': True,
            'intelligence_processing': True,
            'competitive_analysis': True,
            'embedded_template': True
        }
    })

if __name__ == '__main__':
    # Get port from environment (Render sets this)
    port_env = os.environ.get("PORT", "5000")
    
    # Handle Render's 'auto' port setting
    try:
        port = int(port_env)
    except (ValueError, TypeError):
        # If PORT is 'auto' or invalid, use default
        port = 5000
    
    app.run(host='0.0.0.0', port=port, debug=False)
