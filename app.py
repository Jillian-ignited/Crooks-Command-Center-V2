#!/usr/bin/env python3
"""
Crooks & Castles Command Center V2 - Complete Self-Contained Version
All HTML, CSS, JavaScript, and functionality embedded in this single file
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'crooks-castles-command-center-v2'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configuration
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
    'videos': {'mp4', 'mov', 'avi', 'mkv', 'webm'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'md'},
    'data': {'json', 'jsonl', 'csv', 'xlsx'},
    'audio': {'mp3', 'wav', 'aac', 'm4a'}
}

ALL_ALLOWED_EXTENSIONS = set()
for ext_list in ALLOWED_EXTENSIONS.values():
    ALL_ALLOWED_EXTENSIONS.update(ext_list)

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [UPLOAD_FOLDER]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            elif os.path.isfile(directory):
                print(f"⚠️  {directory} exists as file, removing...")
                os.remove(directory)
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Recreated directory: {directory}")
        except Exception as e:
            print(f"⚠️  Directory {directory} handling: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type category"""
    if not filename or '.' not in filename:
        return 'unknown'
    
    ext = filename.rsplit('.', 1)[1].lower()
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'unknown'

def scan_and_catalog_assets():
    """Scan upload folder and catalog all assets"""
    assets = {}
    
    if not os.path.exists(UPLOAD_FOLDER):
        return assets
    
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith('.'):
                continue
                
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            if os.path.isfile(file_path):
                file_type = get_file_type(filename)
                file_size = os.path.getsize(file_path)
                
                # Generate unique asset ID
                asset_id = str(uuid.uuid4())
                
                assets[asset_id] = {
                    'filename': filename,
                    'type': file_type,
                    'size': file_size,
                    'path': file_path,
                    'upload_date': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
    except Exception as e:
        print(f"Asset scanning error: {e}")
    
    return assets

def load_jsonl_data(file_path):
    """Load and parse JSONL data"""
    data = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        print(f"Error loading JSONL data from {file_path}: {e}")
    return data

def analyze_intelligence_data():
    """Analyze competitive intelligence data"""
    instagram_data = []
    tiktok_data = []
    competitive_data = []
    
    # Load data from files
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if filename.endswith('.jsonl'):
                data = load_jsonl_data(file_path)
                
                if 'instagram-hashtag-scraper' in filename:
                    instagram_data.extend(data)
                elif 'tiktok-scraper' in filename:
                    tiktok_data.extend(data)
                elif 'competitive_data' in filename:
                    competitive_data.extend(data)
    
    # Analyze hashtags
    hashtag_counts = {}
    for post in instagram_data:
        hashtags = post.get('hashtags', [])
        for hashtag in hashtags:
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
    
    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Calculate engagement rates
    total_likes = sum(post.get('likesCount', 0) for post in instagram_data)
    total_comments = sum(post.get('commentsCount', 0) for post in instagram_data)
    avg_engagement = (total_likes + total_comments) / len(instagram_data) if instagram_data else 0
    
    return {
        'instagram_posts': len(instagram_data),
        'tiktok_videos': len(tiktok_data),
        'top_hashtags': [{'hashtag': f"#{tag}", 'count': count} for tag, count in top_hashtags],
        'avg_engagement': round(avg_engagement, 2),
        'total_likes': total_likes,
        'total_comments': total_comments,
        'competitive_brands': len(competitive_data),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_calendar_data():
    """Generate enhanced calendar data with asset mapping"""
    base_date = datetime.now()
    
    calendar_data = {
        '7_day_view': [
            {
                'date': (base_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'title': 'Hip-Hop Heritage Story Series Launch',
                'description': 'Launch authentic hip-hop heritage content series with street photography and cultural elements',
                'category': 'cultural',
                'priority': 'high',
                'budget_allocation': 500,
                'deliverables': ['Instagram post', 'Instagram story', 'TikTok video'],
                'kpis': {'engagement_rate': '4.5%', 'reach': '25K', 'saves': '500'}
            },
            {
                'date': (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'title': 'Cultural Fusion Content Drop',
                'description': 'Showcase cultural fusion in streetwear with diverse models and lifestyle context',
                'category': 'cultural',
                'priority': 'high',
                'budget_allocation': 750,
                'deliverables': ['Instagram carousel', 'Story series', 'TikTok trend'],
                'kpis': {'engagement_rate': '5.2%', 'reach': '35K', 'shares': '200'}
            },
            {
                'date': (base_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                'title': 'Weekly Intelligence Recap',
                'description': 'Weekly competitive intelligence and trend analysis report',
                'category': 'intelligence',
                'priority': 'medium',
                'budget_allocation': 300,
                'deliverables': ['Weekly report', 'Dashboard update', 'Trend briefing'],
                'kpis': {'report_views': '150', 'insights_generated': '12', 'actionable_items': '8'}
            }
        ],
        '30_day_view': [
            {
                'date': (base_date + timedelta(days=10)).strftime('%Y-%m-%d'),
                'title': 'Hispanic Heritage Month Celebration',
                'description': 'Authentic celebration of Hispanic heritage in streetwear with community focus',
                'category': 'cultural',
                'priority': 'high',
                'budget_allocation': 2000,
                'deliverables': ['Campaign launch', 'Educational content', 'Community spotlights'],
                'kpis': {'engagement_rate': '6.8%', 'reach': '100K', 'community_mentions': '50'}
            },
            {
                'date': (base_date + timedelta(days=22)).strftime('%Y-%m-%d'),
                'title': 'Hip-Hop Anniversary Tribute',
                'description': 'Tribute to hip-hop anniversary with brand heritage and documentary style',
                'category': 'cultural',
                'priority': 'high',
                'budget_allocation': 1500,
                'deliverables': ['Anniversary post', 'Story timeline', 'Long-form video'],
                'kpis': {'engagement_rate': '7.2%', 'reach': '75K', 'video_completion': '65%'}
            }
        ],
        '60_day_view': [
            {
                'date': (base_date + timedelta(days=47)).strftime('%Y-%m-%d'),
                'title': 'Black Friday Campaign Launch',
                'description': 'Strategic BFCM campaign with cultural authenticity and conversion optimization',
                'category': 'commercial',
                'priority': 'high',
                'budget_allocation': 5000,
                'deliverables': ['Campaign creative suite', 'Email templates', 'Social ads'],
                'kpis': {'conversion_rate': '3.5%', 'roas': '4.2x', 'email_ctr': '8.5%'}
            }
        ],
        '90_day_view': [
            {
                'date': (base_date + timedelta(days=77)).strftime('%Y-%m-%d'),
                'title': 'Q1 2026 Brand Evolution Campaign',
                'description': 'Strategic brand evolution for new year positioning with manifesto content',
                'category': 'brand',
                'priority': 'high',
                'budget_allocation': 8000,
                'deliverables': ['Brand film', 'Manifesto content', 'PR package'],
                'kpis': {'brand_awareness': '+15%', 'sentiment_score': '85%', 'pr_mentions': '100+'}
            }
        ]
    }
    
    return calendar_data

def generate_agency_data():
    """Generate agency tracking data"""
    return {
        'agencies': [
            {
                'name': 'High Voltage Digital',
                'phase': 1,
                'current_deliverables': 4,
                'monthly_budget': 4000,
                'on_time_delivery': 100,
                'quality_score': 95,
                'next_phase_requirements': [
                    'Complete Phase 1 deliverables',
                    'Client approval on creative direction',
                    'Budget allocation for Phase 2 ($6,000)',
                    'Resource allocation (2 additional team members)'
                ],
                'deliverables_breakdown': {
                    'completed': ['Brand audit', 'Competitive analysis'],
                    'in_progress': ['Creative strategy', 'Content calendar'],
                    'pending': ['Asset creation', 'Campaign launch']
                },
                'performance_metrics': {
                    'response_time': '< 2 hours',
                    'revision_rounds': '1.2 avg',
                    'client_satisfaction': '4.8/5'
                }
            }
        ],
        'total_budget': 4000,
        'total_agencies': 1,
        'avg_quality_score': 95
    }

# Complete embedded HTML template with CSS and JavaScript
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crooks & Castles - Command Center V2</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --crooks-primary: #ff6b35;
            --crooks-secondary: #1a1a1a;
            --crooks-accent: #ffd700;
            --crooks-dark: #0d0d0d;
            --crooks-light: #f5f5f5;
            --crooks-gray: #2a2a2a;
            --crooks-success: #28a745;
            --crooks-warning: #ffc107;
            --crooks-danger: #dc3545;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--crooks-dark) 0%, var(--crooks-secondary) 100%);
            color: var(--crooks-light);
            line-height: 1.6;
            min-height: 100vh;
        }

        .header {
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 2px solid var(--crooks-primary);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 8px rgba(255, 107, 53, 0.15);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo h1 {
            color: var(--crooks-primary);
            font-weight: 700;
            font-size: 1.5rem;
            text-shadow: 0 2px 4px rgba(255, 107, 53, 0.3);
        }

        .castle-icon {
            font-size: 2rem;
            color: var(--crooks-accent);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .header-stats {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .stat-item {
            text-align: center;
            padding: 0.5rem;
            border-radius: 8px;
            background: rgba(255, 107, 53, 0.1);
        }

        .stat-number {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--crooks-primary);
            display: block;
        }

        .stat-label {
            font-size: 0.8rem;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .tabs {
            display: flex;
            background: rgba(26, 26, 26, 0.6);
            border-radius: 12px;
            padding: 0.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 8px rgba(255, 107, 53, 0.15);
        }

        .tab {
            flex: 1;
            padding: 1rem 1.5rem;
            text-align: center;
            background: transparent;
            border: none;
            color: #ccc;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 500;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .tab:hover {
            color: var(--crooks-light);
            background: rgba(255, 107, 53, 0.1);
        }

        .tab.active {
            background: linear-gradient(135deg, var(--crooks-primary) 0%, var(--crooks-accent) 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(255, 107, 53, 0.1);
            transform: translateY(-1px);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease-in-out;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .card {
            background: rgba(42, 42, 42, 0.8);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid rgba(255, 107, 53, 0.2);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(135deg, var(--crooks-primary) 0%, var(--crooks-accent) 100%);
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 32px rgba(255, 107, 53, 0.25);
            border-color: rgba(255, 107, 53, 0.4);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 107, 53, 0.1);
        }

        .card-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--crooks-primary);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .card-title i {
            font-size: 1.5rem;
            color: var(--crooks-accent);
        }

        .asset-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1.5rem;
        }

        .asset-item {
            background: rgba(26, 26, 26, 0.6);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255, 107, 53, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .asset-item:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 107, 53, 0.3);
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.2);
        }

        .asset-thumbnail {
            width: 100%;
            height: 140px;
            background: linear-gradient(135deg, var(--crooks-primary) 0%, var(--crooks-accent) 100%);
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .asset-name {
            font-size: 1rem;
            margin-bottom: 0.5rem;
            color: var(--crooks-light);
            font-weight: 500;
            word-break: break-word;
        }

        .asset-type {
            font-size: 0.8rem;
            color: var(--crooks-accent);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }

        .asset-size {
            font-size: 0.7rem;
            color: #999;
            margin-bottom: 1rem;
        }

        .download-btn {
            background: linear-gradient(135deg, var(--crooks-primary) 0%, var(--crooks-accent) 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(255, 107, 53, 0.1);
        }

        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 107, 53, 0.15);
        }

        .upload-area {
            border: 2px dashed var(--crooks-primary);
            border-radius: 16px;
            padding: 3rem 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(255, 107, 53, 0.05);
            margin-bottom: 2rem;
        }

        .upload-area:hover {
            background: rgba(255, 107, 53, 0.1);
            border-color: var(--crooks-accent);
            transform: translateY(-2px);
        }

        .upload-area.dragover {
            background: rgba(255, 107, 53, 0.2);
            border-color: var(--crooks-accent);
            transform: scale(1.02);
        }

        .upload-area h3 {
            color: var(--crooks-light);
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        }

        .upload-area p {
            color: #ccc;
            font-size: 0.95rem;
        }

        .calendar-view {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
        }

        .calendar-event {
            background: rgba(26, 26, 26, 0.6);
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid var(--crooks-primary);
            transition: all 0.3s ease;
        }

        .calendar-event:hover {
            transform: translateX(4px);
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.2);
        }

        .event-date {
            font-size: 0.9rem;
            color: var(--crooks-accent);
            margin-bottom: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .event-title {
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: var(--crooks-light);
            font-size: 1.1rem;
        }

        .event-description {
            font-size: 0.95rem;
            color: #ccc;
            margin-bottom: 1rem;
            line-height: 1.5;
        }

        .event-budget {
            font-size: 0.9rem;
            color: var(--crooks-success);
            font-weight: 600;
            background: rgba(40, 167, 69, 0.1);
            padding: 0.5rem;
            border-radius: 6px;
            display: inline-block;
            margin-bottom: 0.5rem;
        }

        .intelligence-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: rgba(26, 26, 26, 0.6);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255, 107, 53, 0.1);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 107, 53, 0.3);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--crooks-primary);
            margin-bottom: 0.5rem;
        }

        .metric-label {
            font-size: 0.85rem;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .agency-tracking {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }

        .agency-card {
            background: rgba(26, 26, 26, 0.6);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid rgba(255, 107, 53, 0.2);
            transition: all 0.3s ease;
        }

        .agency-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.2);
        }

        .agency-name {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--crooks-primary);
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .agency-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .agency-metric {
            text-align: center;
            padding: 1rem;
            background: rgba(255, 107, 53, 0.1);
            border-radius: 8px;
        }

        .agency-metric-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--crooks-accent);
            margin-bottom: 0.25rem;
        }

        .agency-metric-label {
            font-size: 0.8rem;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .hidden {
            display: none !important;
        }

        #file-input {
            display: none;
        }

        .calendar-tabs {
            display: flex;
            background: rgba(26, 26, 26, 0.6);
            border-radius: 8px;
            padding: 0.25rem;
            margin-bottom: 1rem;
        }

        .calendar-tab {
            flex: 1;
            padding: 0.5rem 1rem;
            text-align: center;
            background: transparent;
            border: none;
            color: #ccc;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.3s ease;
            font-size: 0.8rem;
        }

        .calendar-tab:hover {
            color: var(--crooks-light);
            background: rgba(255, 107, 53, 0.1);
        }

        .calendar-tab.active {
            background: var(--crooks-primary);
            color: white;
        }

        .hashtag-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .hashtag-item {
            background: rgba(255, 107, 53, 0.2);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            color: var(--crooks-light);
        }

        .competitive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .competitive-item {
            background: rgba(26, 26, 26, 0.5);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }

        .competitive-brand {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .competitive-position {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .competitive-category {
            font-size: 0.8rem;
            color: #ccc;
        }

        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .header-stats {
                display: none;
            }
            
            .container {
                padding: 1rem;
            }
            
            .tabs {
                flex-direction: column;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .asset-grid {
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <div class="castle-icon">🏰</div>
                <h1>CROOKS & CASTLES</h1>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <span class="stat-number" id="header-posts">{{ intelligence_data.instagram_posts or 0 }}</span>
                    <span class="stat-label">Posts Analyzed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" id="header-assets">{{ asset_count or 0 }}</span>
                    <span class="stat-label">Assets</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" id="header-events">{{ calendar_events_count or 0 }}</span>
                    <span class="stat-label">Events</span>
                </div>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="tabs">
            <button class="tab active" onclick="showTab('intelligence')">
                <i class="fas fa-chart-line"></i> Intelligence
            </button>
            <button class="tab" onclick="showTab('assets')">
                <i class="fas fa-folder-open"></i> Asset Library
            </button>
            <button class="tab" onclick="showTab('calendar')">
                <i class="fas fa-calendar-alt"></i> Strategic Calendar
            </button>
            <button class="tab" onclick="showTab('agency')">
                <i class="fas fa-handshake"></i> Agency Tracking
            </button>
            <button class="tab" onclick="showTab('upload')">
                <i class="fas fa-upload"></i> Data Upload
            </button>
        </div>

        <!-- Intelligence Dashboard -->
        <div id="intelligence" class="tab-content active">
            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">
                            <i class="fas fa-chart-bar"></i>
                            Intelligence Metrics
                        </h2>
                    </div>
                    <div class="intelligence-metrics">
                        <div class="metric-card">
                            <div class="metric-value">{{ intelligence_data.instagram_posts or 0 }}</div>
                            <div class="metric-label">Instagram Posts</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{{ intelligence_data.tiktok_videos or 0 }}</div>
                            <div class="metric-label">TikTok Videos</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{{ intelligence_data.total_likes or 0 }}</div>
                            <div class="metric-label">Total Likes</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{{ intelligence_data.avg_engagement or 0 }}</div>
                            <div class="metric-label">Avg Engagement</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">
                            <i class="fas fa-hashtag"></i>
                            Top Hashtags
                        </h2>
                    </div>
                    <div class="hashtag-grid">
                        {% for hashtag in intelligence_data.top_hashtags[:8] %}
                        <div class="hashtag-item">{{ hashtag.hashtag }}</div>
                        {% endfor %}
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">
                            <i class="fas fa-trophy"></i>
                            Competitive Rankings
                        </h2>
                    </div>
                    <div class="competitive-grid">
                        <div class="competitive-item">
                            <div class="competitive-brand" style="color: var(--crooks-primary);">Crooks & Castles</div>
                            <div class="competitive-position" style="color: var(--crooks-accent);">#47</div>
                            <div class="competitive-category">Heritage Streetwear</div>
                        </div>
                        <div class="competitive-item">
                            <div class="competitive-brand" style="color: #ccc;">Supreme</div>
                            <div class="competitive-position" style="color: #999;">#1</div>
                            <div class="competitive-category">Streetwear Leader</div>
                        </div>
                        <div class="competitive-item">
                            <div class="competitive-brand" style="color: #ccc;">Off-White</div>
                            <div class="competitive-position" style="color: #999;">#3</div>
                            <div class="competitive-category">Luxury Streetwear</div>
                        </div>
                        <div class="competitive-item">
                            <div class="competitive-brand" style="color: #ccc;">Stussy</div>
                            <div class="competitive-position" style="color: #999;">#12</div>
                            <div class="competitive-category">Classic Streetwear</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Asset Library -->
        <div id="assets" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-folder-open"></i>
                        Asset Library ({{ asset_count or 0 }} items)
                    </h2>
                </div>
                <div class="asset-grid" id="asset-grid">
                    {% for asset_id, asset in assets.items() %}
                    <div class="asset-item">
                        <div class="asset-thumbnail">
                            <i class="fas fa-{{ 'image' if asset.type == 'images' else 'video' if asset.type == 'videos' else 'file-alt' if asset.type == 'documents' else 'chart-bar' if asset.type == 'data' else 'music' if asset.type == 'audio' else 'file' }}"></i>
                        </div>
                        <div class="asset-name">{{ asset.filename }}</div>
                        <div class="asset-type">{{ asset.type.replace('_', ' ') }}</div>
                        <div class="asset-size">{{ "%.2f"|format(asset.size / 1024 / 1024) }} MB</div>
                        <button class="download-btn" onclick="downloadAsset('{{ asset_id }}')">
                            <i class="fas fa-download"></i> Download
                        </button>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Strategic Calendar -->
        <div id="calendar" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-calendar-alt"></i>
                        Strategic Calendar
                    </h2>
                </div>
                <div class="calendar-tabs">
                    <button class="calendar-tab active" onclick="showCalendarView('7day', this)">7 Days</button>
                    <button class="calendar-tab" onclick="showCalendarView('30day', this)">30 Days</button>
                    <button class="calendar-tab" onclick="showCalendarView('60day', this)">60 Days</button>
                    <button class="calendar-tab" onclick="showCalendarView('90day', this)">90 Days</button>
                </div>
                <div id="calendar-content" class="calendar-view">
                    {% for event in calendar_data['7_day_view'] %}
                    <div class="calendar-event">
                        <div class="event-date">
                            <i class="fas fa-calendar-day"></i> {{ event.date }}
                        </div>
                        <div class="event-title">{{ event.title }}</div>
                        <div class="event-description">{{ event.description }}</div>
                        <div class="event-budget">💰 Budget: ${{ "{:,}".format(event.budget_allocation) }}</div>
                        {% if event.deliverables %}
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #ccc;">
                            📋 Deliverables: {{ event.deliverables | length }}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Agency Tracking -->
        <div id="agency" class="tab-content">
            <div class="agency-tracking">
                {% for agency in agency_data.agencies %}
                <div class="agency-card">
                    <div class="agency-name">{{ agency.name }}</div>
                    <div class="agency-metrics">
                        <div class="agency-metric">
                            <div class="agency-metric-value">{{ agency.phase }}</div>
                            <div class="agency-metric-label">Phase</div>
                        </div>
                        <div class="agency-metric">
                            <div class="agency-metric-value">{{ agency.current_deliverables }}</div>
                            <div class="agency-metric-label">Deliverables</div>
                        </div>
                        <div class="agency-metric">
                            <div class="agency-metric-value">${{ "{:,}".format(agency.monthly_budget) }}</div>
                            <div class="agency-metric-label">Budget</div>
                        </div>
                        <div class="agency-metric">
                            <div class="agency-metric-value">{{ agency.on_time_delivery }}%</div>
                            <div class="agency-metric-label">On Time</div>
                        </div>
                        <div class="agency-metric">
                            <div class="agency-metric-value">{{ agency.quality_score }}%</div>
                            <div class="agency-metric-label">Quality</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem;">
                        <h4 style="color: var(--crooks-accent); margin-bottom: 0.5rem;">Next Phase Requirements:</h4>
                        <ul style="color: #ccc; font-size: 0.9rem; padding-left: 1rem;">
                            {% for req in agency.next_phase_requirements %}
                            <li>{{ req }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Data Upload -->
        <div id="upload" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-upload"></i>
                        Upload Intelligence Data
                    </h2>
                </div>
                <div class="upload-area" onclick="document.getElementById('file-input').click()">
                    <h3><i class="fas fa-cloud-upload-alt"></i> Upload Files</h3>
                    <p>Click here or drag and drop JSONL, JSON, images, videos, or documents</p>
                    <p style="font-size: 0.8rem; margin-top: 0.5rem; color: #999;">
                        Supported: .jsonl, .json, .png, .jpg, .mp4, .mov, .pdf, .docx (Max: 100MB)
                    </p>
                </div>
                <input type="file" id="file-input" multiple accept=".jsonl,.json,.png,.jpg,.jpeg,.gif,.webp,.mp4,.mov,.avi,.pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.mp3,.wav">
                
                <div id="upload-status" style="margin-top: 1rem; display: none;">
                    <div style="background: rgba(40, 167, 69, 0.1); border: 1px solid var(--crooks-success); border-radius: 8px; padding: 1rem;">
                        <h4 style="color: var(--crooks-success); margin-bottom: 0.5rem;">Upload Status</h4>
                        <div id="upload-progress"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'intelligence';
        let currentCalendarView = '7day';

        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            currentTab = tabName;
        }

        function showCalendarView(view, element) {
            // Update calendar view tabs
            document.querySelectorAll('.calendar-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            element.classList.add('active');
            
            currentCalendarView = view;
            
            // Load calendar data for the selected view
            loadCalendarData(view);
        }

        function loadCalendarData(view) {
            fetch(`/api/calendar/${view}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCalendarDisplay(data.events);
                    }
                })
                .catch(error => {
                    console.log('Using default calendar data');
                });
        }

        function updateCalendarDisplay(events) {
            const calendarContent = document.getElementById('calendar-content');
            calendarContent.innerHTML = '';
            
            events.forEach(event => {
                const eventElement = document.createElement('div');
                eventElement.className = 'calendar-event';
                eventElement.innerHTML = `
                    <div class="event-date">
                        <i class="fas fa-calendar-day"></i> ${event.date}
                    </div>
                    <div class="event-title">${event.title}</div>
                    <div class="event-description">${event.description}</div>
                    <div class="event-budget">💰 Budget: $${event.budget_allocation.toLocaleString()}</div>
                    ${event.deliverables ? `<div style="margin-top: 0.5rem; font-size: 0.8rem; color: #ccc;">📋 Deliverables: ${event.deliverables.length}</div>` : ''}
                `;
                calendarContent.appendChild(eventElement);
            });
        }

        function downloadAsset(assetId) {
            const button = event.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            button.disabled = true;
            
            // Create download link
            const link = document.createElement('a');
            link.href = `/api/assets/${assetId}/download`;
            link.download = '';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 1000);
        }

        // File upload handling
        document.getElementById('file-input').addEventListener('change', function(e) {
            handleFileUpload(e.target.files);
        });

        // Drag and drop handling
        const uploadArea = document.querySelector('.upload-area');
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            handleFileUpload(e.dataTransfer.files);
        });

        function handleFileUpload(files) {
            const uploadStatus = document.getElementById('upload-status');
            const uploadProgress = document.getElementById('upload-progress');
            
            uploadStatus.style.display = 'block';
            uploadProgress.innerHTML = '';
            
            Array.from(files).forEach(file => {
                const formData = new FormData();
                formData.append('file', file);
                
                const progressDiv = document.createElement('div');
                progressDiv.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Uploading ${file.name}...`;
                uploadProgress.appendChild(progressDiv);
                
                fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        progressDiv.innerHTML = `<i class="fas fa-check" style="color: var(--crooks-success);"></i> ${file.name} uploaded successfully`;
                        // Refresh the page after successful upload
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    } else {
                        progressDiv.innerHTML = `<i class="fas fa-times" style="color: var(--crooks-danger);"></i> ${file.name} upload failed: ${data.error}`;
                    }
                })
                .catch(error => {
                    progressDiv.innerHTML = `<i class="fas fa-times" style="color: var(--crooks-danger);"></i> ${file.name} upload failed`;
                });
            });
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def dashboard():
    """Main dashboard route"""
    # Ensure directories exist
    ensure_directories()
    
    # Scan and catalog assets
    assets = scan_and_catalog_assets()
    asset_count = len(assets)
    
    # Analyze intelligence data
    intelligence_data = analyze_intelligence_data()
    
    # Generate calendar data
    calendar_data = generate_calendar_data()
    calendar_events_count = sum(len(events) for events in calendar_data.values())
    
    # Generate agency data
    agency_data = generate_agency_data()
    
    return render_template_string(DASHBOARD_TEMPLATE,
                                assets=assets,
                                asset_count=asset_count,
                                intelligence_data=intelligence_data,
                                calendar_data=calendar_data,
                                calendar_events_count=calendar_events_count,
                                agency_data=agency_data)

@app.route('/api/assets')
def api_assets():
    """API endpoint for assets"""
    assets = scan_and_catalog_assets()
    return jsonify({
        'success': True,
        'assets': assets,
        'total_count': len(assets),
        'categories': {
            'images': len([a for a in assets.values() if a['type'] == 'images']),
            'videos': len([a for a in assets.values() if a['type'] == 'videos']),
            'documents': len([a for a in assets.values() if a['type'] == 'documents']),
            'data': len([a for a in assets.values() if a['type'] == 'data']),
            'audio': len([a for a in assets.values() if a['type'] == 'audio'])
        }
    })

@app.route('/api/assets/<asset_id>/download')
def download_asset(asset_id):
    """Download asset by ID"""
    assets = scan_and_catalog_assets()
    
    if asset_id not in assets:
        return jsonify({'error': 'Asset not found'}), 404
    
    asset = assets[asset_id]
    file_path = asset['path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=asset['filename'])

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    try:
        # Ensure upload directory exists
        ensure_directories()
        
        # Secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': f'File {filename} uploaded successfully',
            'filename': filename,
            'size': os.path.getsize(file_path)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/intelligence')
def api_intelligence():
    """API endpoint for intelligence data"""
    intelligence_data = analyze_intelligence_data()
    return jsonify({
        'success': True,
        'data': intelligence_data
    })

@app.route('/api/calendar/<view>')
def api_calendar(view):
    """API endpoint for calendar data"""
    calendar_data = generate_calendar_data()
    view_key = f"{view}_view"
    
    if view_key not in calendar_data:
        return jsonify({'success': False, 'error': 'Invalid view'}), 400
    
    return jsonify({
        'success': True,
        'events': calendar_data[view_key]
    })

@app.route('/api/agency')
def api_agency():
    """API endpoint for agency data"""
    agency_data = generate_agency_data()
    return jsonify({
        'success': True,
        'data': agency_data
    })

if __name__ == '__main__':
    # Ensure directories exist on startup
    ensure_directories()
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
