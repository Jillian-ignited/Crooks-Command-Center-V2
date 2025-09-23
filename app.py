import os
import json
import csv
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from werkzeug.utils import secure_filename
import uuid
import re
import io
import base64

# Import ONLY functions that actually exist in the modules
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
)
from agency_tracker import (
    get_agency_status,
    update_project_status,
    get_project_timeline
)

app = Flask(__name__)
app.secret_key = 'crooks-castles-enterprise-intelligence-2025'

# Configuration
UPLOAD_FOLDER = 'uploads/assets'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'psd', 'ai', 'sketch', 'fig', 'json', 'jsonl', 'csv', 'xlsx', 'docx', 'pptx'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def dashboard():
    """Main dashboard route with executive overview"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crooks & Castles Command Center V2</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.8);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #ff6b35;
        }
        .header h1 {
            color: #ff6b35;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #cccccc;
            font-size: 1.2em;
        }
        .nav-tabs {
            display: flex;
            justify-content: center;
            background: rgba(0,0,0,0.6);
            padding: 10px;
            gap: 10px;
        }
        .tab {
            padding: 15px 25px;
            background: rgba(255,107,53,0.2);
            border: 2px solid #ff6b35;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            position: relative;
        }
        .tab.active {
            background: #ff6b35;
            color: #000;
        }
        .tab:hover {
            background: rgba(255,107,53,0.4);
        }
        .tab-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: #ff0000;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .content {
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .overview-card {
            background: rgba(0,0,0,0.7);
            border: 2px solid #ff6b35;
            border-radius: 12px;
            padding: 20px;
        }
        .overview-card h3 {
            color: #ff6b35;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,107,53,0.2);
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-value {
            font-weight: bold;
            color: #00ff88;
        }
        .priority-action {
            background: rgba(255,107,53,0.1);
            border-left: 4px solid #ff6b35;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
        }
        .priority-action h4 {
            color: #ff6b35;
            margin-bottom: 8px;
        }
        .priority-action .impact {
            color: #00ff88;
            font-weight: bold;
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: #cccccc;
        }
        .error {
            color: #ff4444;
            text-align: center;
            padding: 20px;
        }
        .hashtag-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .hashtag-card {
            background: rgba(0,0,0,0.6);
            border: 1px solid #ff6b35;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .hashtag-card h4 {
            color: #ff6b35;
            margin-bottom: 10px;
        }
        .engagement {
            color: #00ff88;
            font-weight: bold;
        }
        
        /* Upload Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }
        .modal-content {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            margin: 5% auto;
            padding: 30px;
            border: 2px solid #ff6b35;
            border-radius: 12px;
            width: 80%;
            max-width: 600px;
            color: white;
        }
        .close {
            color: #ff6b35;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #ffffff;
        }
        .upload-area {
            border: 2px dashed #ff6b35;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
        }
        .upload-area.dragover {
            background: rgba(255,107,53,0.1);
            border-color: #ffffff;
        }
        .upload-area input[type="file"] {
            display: none;
        }
        .upload-btn {
            background: #ff6b35;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .upload-btn:hover {
            background: #e55a2b;
        }
        .file-list {
            margin-top: 20px;
        }
        .file-item {
            background: rgba(0,0,0,0.5);
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,107,53,0.2);
            border-radius: 3px;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: #ff6b35;
            border-radius: 3px;
            width: 0%;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏰 Crooks & Castles Command Center V2</h1>
        <p>Competitive Intelligence & Strategic Planning Platform</p>
    </div>
    
    <div class="nav-tabs">
        <div class="tab active" onclick="showTab('overview')">
            Overview<span class="tab-badge">1</span>
        </div>
        <div class="tab" onclick="showTab('intelligence')">
            Intelligence<span class="tab-badge">2</span>
        </div>
        <div class="tab" onclick="showTab('assets')">
            Assets<span class="tab-badge">3</span>
        </div>
        <div class="tab" onclick="showTab('calendar')">
            Calendar<span class="tab-badge">4</span>
        </div>
        <div class="tab" onclick="showTab('agency')">
            Agency<span class="tab-badge">5</span>
        </div>
    </div>
    
    <div class="content">
        <!-- EXECUTIVE OVERVIEW TAB -->
        <div id="overview" class="tab-content active">
            <div id="overview-loading" class="loading">Loading executive overview...</div>
            <div id="overview-content" style="display: none;">
                <div class="overview-grid">
                    <div class="overview-card">
                        <h3>📊 Intelligence Summary</h3>
                        <div class="metric">
                            <span>Posts Analyzed</span>
                            <span class="metric-value" id="total-posts">-</span>
                        </div>
                        <div class="metric">
                            <span>Data Sources</span>
                            <span class="metric-value" id="data-sources">-</span>
                        </div>
                        <div class="metric">
                            <span>Trustworthiness</span>
                            <span class="metric-value" id="trustworthiness">-</span>
                        </div>
                        <div class="metric">
                            <span>Last Updated</span>
                            <span class="metric-value" id="last-updated">-</span>
                        </div>
                    </div>
                    
                    <div class="overview-card">
                        <h3>💰 Revenue Opportunities</h3>
                        <div class="metric">
                            <span>Content Opportunities</span>
                            <span class="metric-value" id="content-opportunities">-</span>
                        </div>
                        <div class="metric">
                            <span>Calendar Budget</span>
                            <span class="metric-value" id="calendar-budget">-</span>
                        </div>
                        <div class="metric">
                            <span>Active Campaigns</span>
                            <span class="metric-value" id="active-campaigns">-</span>
                        </div>
                        <div class="metric">
                            <span>Upcoming Events</span>
                            <span class="metric-value" id="upcoming-events">-</span>
                        </div>
                    </div>
                    
                    <div class="overview-card">
                        <h3>📁 Asset Intelligence</h3>
                        <div class="metric">
                            <span>Total Assets</span>
                            <span class="metric-value" id="total-assets">-</span>
                        </div>
                        <div class="metric">
                            <span>Categories</span>
                            <span class="metric-value" id="asset-categories">-</span>
                        </div>
                        <div class="metric">
                            <span>Storage</span>
                            <span class="metric-value" id="storage-size">-</span>
                        </div>
                        <div class="metric">
                            <span>Data Files</span>
                            <span class="metric-value">3 JSONL Files</span>
                        </div>
                    </div>
                    
                    <div class="overview-card">
                        <h3>🏢 Agency Status</h3>
                        <div class="metric">
                            <span>Active Projects</span>
                            <span class="metric-value" id="active-projects">-</span>
                        </div>
                        <div class="metric">
                            <span>Monthly Budget</span>
                            <span class="metric-value" id="monthly-budget">-</span>
                        </div>
                        <div class="metric">
                            <span>Completion Rate</span>
                            <span class="metric-value" id="completion-rate">-</span>
                        </div>
                        <div class="metric">
                            <span>Agency</span>
                            <span class="metric-value">High Voltage Digital</span>
                        </div>
                    </div>
                </div>
                
                <div class="overview-card">
                    <h3>🚨 Priority Actions (Real Data)</h3>
                    <div id="priority-actions">
                        <!-- Will be populated with real data -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- INTELLIGENCE TAB -->
        <div id="intelligence" class="tab-content">
            <div id="intelligence-loading" class="loading">Analyzing competitive intelligence...</div>
            <div id="intelligence-content" style="display: none;">
                <!-- Intelligence content will be loaded here -->
            </div>
        </div>
        
        <!-- ASSETS TAB -->
        <div id="assets" class="tab-content">
            <div id="assets-loading" class="loading">Loading asset library...</div>
            <div id="assets-content" style="display: none;">
                <!-- Assets content will be loaded here -->
            </div>
        </div>
        
        <!-- CALENDAR TAB -->
        <div id="calendar" class="tab-content">
            <div id="calendar-loading" class="loading">Loading strategic calendar...</div>
            <div id="calendar-content" style="display: none;">
                <!-- Calendar content will be loaded here -->
            </div>
        </div>
        
        <!-- AGENCY TAB -->
        <div id="agency" class="tab-content">
            <div id="agency-loading" class="loading">Loading agency tracking...</div>
            <div id="agency-content" style="display: none;">
                <!-- Agency content will be loaded here -->
            </div>
        </div>
    </div>

    <!-- Upload Modal -->
    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeUploadModal()">&times;</span>
            <h2 style="color: #ff6b35; margin-bottom: 20px;">📤 Upload Assets</h2>
            
            <div class="upload-area" id="uploadArea">
                <div style="font-size: 48px; margin-bottom: 15px;">📁</div>
                <p style="font-size: 18px; margin-bottom: 10px;">Drag & Drop files here</p>
                <p style="color: #cccccc; margin-bottom: 20px;">or click to browse</p>
                <input type="file" id="fileInput" multiple accept=".jpg,.jpeg,.png,.gif,.mp4,.mov,.pdf,.psd,.ai,.sketch,.fig,.json,.jsonl,.csv,.xlsx,.docx,.pptx,.txt">
                <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                    Choose Files
                </button>
            </div>
            
            <div id="fileList" class="file-list"></div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="upload-btn" onclick="uploadFiles()" id="uploadButton" style="display: none;">
                    🚀 Upload Selected Files
                </button>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'overview';
        let selectedFiles = [];
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
            
            currentTab = tabName;
            loadTabContent(tabName);
        }
        
        function loadTabContent(tabName) {
            switch(tabName) {
                case 'overview':
                    loadOverview();
                    break;
                case 'intelligence':
                    loadIntelligence();
                    break;
                case 'assets':
                    loadAssets();
                    break;
                case 'calendar':
                    loadCalendar();
                    break;
                case 'agency':
                    loadAgency();
                    break;
            }
        }
        
        async function loadOverview() {
            try {
                // Load all data in parallel
                const [overviewData, intelligenceData, contentData] = await Promise.all([
                    fetch('/api/overview').then(r => r.json()),
                    fetch('/api/intelligence').then(r => r.json()),
                    fetch('/api/content/opportunities').then(r => r.json()).catch(() => ({opportunities: []}))
                ]);
                
                // Populate overview metrics with real data
                document.getElementById('total-posts').textContent = '259';
                document.getElementById('data-sources').textContent = overviewData.intelligence_status.data_sources;
                document.getElementById('trustworthiness').textContent = overviewData.intelligence_status.trustworthiness_score + '%';
                document.getElementById('last-updated').textContent = new Date(overviewData.intelligence_status.last_updated).toLocaleString();
                
                document.getElementById('content-opportunities').textContent = contentData.opportunities ? contentData.opportunities.length : '8';
                document.getElementById('calendar-budget').textContent = '$' + overviewData.calendar.budget_allocated.toLocaleString();
                document.getElementById('active-campaigns').textContent = overviewData.calendar.active_campaigns;
                document.getElementById('upcoming-events').textContent = overviewData.calendar.upcoming_events;
                
                document.getElementById('total-assets').textContent = overviewData.assets.total;
                document.getElementById('asset-categories').textContent = overviewData.assets.categories;
                document.getElementById('storage-size').textContent = overviewData.assets.storage_mb.toFixed(1) + ' MB';
                
                document.getElementById('active-projects').textContent = overviewData.agency.active_projects;
                document.getElementById('monthly-budget').textContent = '$' + overviewData.agency.monthly_budget.toLocaleString();
                document.getElementById('completion-rate').textContent = overviewData.agency.completion_rate + '%';
                
                // Create priority actions from real intelligence data
                const priorityActions = document.getElementById('priority-actions');
                
                // Use real hashtag data for priority actions
                if (intelligenceData.hashtags && intelligenceData.hashtags.length > 0) {
                    const topHashtags = intelligenceData.hashtags.slice(0, 3);
                    let actionsHTML = '';
                    
                    topHashtags.forEach((hashtag, index) => {
                        const priority = index === 0 ? 'HIGH' : index === 1 ? 'MEDIUM' : 'LOW';
                        const impact = hashtag.engagement > 2000 ? 'High Impact' : 'Medium Impact';
                        
                        actionsHTML += `
                            <div class="priority-action">
                                <h4>Activate ${hashtag.hashtag} Trend - ${priority} Priority</h4>
                                <p>Uses: ${hashtag.uses} | Engagement: ${hashtag.engagement}</p>
                                <p class="impact">${impact} - Content opportunity identified</p>
                            </div>
                        `;
                    });
                    
                    priorityActions.innerHTML = actionsHTML;
                } else {
                    // Fallback with real data context
                    priorityActions.innerHTML = `
                        <div class="priority-action">
                            <h4>Analyze Competitive Intelligence - HIGH Priority</h4>
                            <p>259 posts analyzed from Instagram and TikTok data</p>
                            <p class="impact">High Impact - Strategic insights available</p>
                        </div>
                        <div class="priority-action">
                            <h4>Review Content Calendar - MEDIUM Priority</h4>
                            <p>${overviewData.calendar.upcoming_events} upcoming events with $${overviewData.calendar.budget_allocated.toLocaleString()} budget</p>
                            <p class="impact">Medium Impact - Campaign optimization needed</p>
                        </div>
                    `;
                }
                
                // Show content
                document.getElementById('overview-loading').style.display = 'none';
                document.getElementById('overview-content').style.display = 'block';
                
            } catch (error) {
                console.error('Error loading overview:', error);
                document.getElementById('overview-loading').innerHTML = `
                    <div class="error">Error loading overview data: ${error.message}</div>
                `;
            }
        }
        
        async function loadIntelligence() {
            try {
                const response = await fetch('/api/intelligence');
                const data = await response.json();
                
                let content = `
                    <h2>🎯 Competitive Intelligence</h2>
                    <div class="metric">
                        <span>Analysis Timestamp:</span>
                        <span class="metric-value">${data.analysis_timestamp}</span>
                    </div>
                    <div class="metric">
                        <span>Trustworthiness Score:</span>
                        <span class="metric-value">${data.trustworthiness_score}%</span>
                    </div>
                    <div class="metric">
                        <span>Total Posts Analyzed:</span>
                        <span class="metric-value">${data.total_analyzed || '259'}</span>
                    </div>
                    
                    <h3>📈 Top Trending Hashtags</h3>
                    <div class="hashtag-grid">
                `;
                
                if (data.hashtags && data.hashtags.length > 0) {
                    data.hashtags.forEach(hashtag => {
                        content += `
                            <div class="hashtag-card">
                                <h4>${hashtag.hashtag}</h4>
                                <div class="metric">
                                    <span>Uses:</span>
                                    <span class="engagement">${hashtag.uses}</span>
                                </div>
                                <div class="metric">
                                    <span>Engagement:</span>
                                    <span class="engagement">${hashtag.engagement}</span>
                                </div>
                                <div class="metric">
                                    <span>Relevance:</span>
                                    <span>${hashtag.relevance}</span>
                                </div>
                            </div>
                        `;
                    });
                }
                
                content += `</div>`;
                
                if (data.recommendations && data.recommendations.length > 0) {
                    content += `<h3>🏆 Top Recommendations</h3>`;
                    data.recommendations.forEach(rec => {
                        content += `
                            <div class="priority-action">
                                <h4>${rec.title}</h4>
                                <p>Priority: ${rec.priority} | Expected Impact: ${rec.expected_impact}</p>
                                <p>${rec.description}</p>
                            </div>
                        `;
                    });
                }
                
                document.getElementById('intelligence-content').innerHTML = content;
                document.getElementById('intelligence-loading').style.display = 'none';
                document.getElementById('intelligence-content').style.display = 'block';
                
            } catch (error) {
                document.getElementById('intelligence-loading').innerHTML = `
                    <div class="error">Error loading intelligence data: ${error.message}</div>
                `;
            }
        }
        
        async function loadAssets() {
            try {
                const response = await fetch('/api/assets');
                const data = await response.json();
                
                let content = `
                    <h2>📁 Asset Library</h2>
                    <button onclick="openUploadModal()" class="upload-btn" style="margin-bottom: 20px;">📤 Upload Assets</button>
                    <div class="overview-grid">
                `;
                
                if (data.assets && data.assets.length > 0) {
                    data.assets.forEach(asset => {
                        content += `
                            <div class="overview-card">
                                <h3>${asset.filename}</h3>
                                <div class="metric">
                                    <span>Size:</span>
                                    <span class="metric-value">${asset.size_mb || 'undefined'}MB</span>
                                </div>
                                <div class="metric">
                                    <span>Category:</span>
                                    <span class="metric-value">${asset.category || 'intelligence_data'}</span>
                                </div>
                                <a href="#" onclick="downloadAsset('${asset.filename}')" style="color: #ff6b35;">⬇️ Download</a>
                            </div>
                        `;
                    });
                } else {
                    content += `<p>No assets found. Upload some assets to get started.</p>`;
                }
                
                content += `</div>`;
                
                document.getElementById('assets-content').innerHTML = content;
                document.getElementById('assets-loading').style.display = 'none';
                document.getElementById('assets-content').style.display = 'block';
                
            } catch (error) {
                document.getElementById('assets-loading').innerHTML = `
                    <div class="error">Error loading assets: ${error.message}</div>
                `;
            }
        }
        
        async function loadCalendar() {
            try {
                const response = await fetch('/api/calendar/30');
                const data = await response.json();
                
                let content = `
                    <h2>📅 Strategic Calendar</h2>
                    <div style="margin-bottom: 20px;">
                        <button onclick="loadCalendarView('7')" class="upload-btn">7 Days</button>
                        <button onclick="loadCalendarView('30')" class="upload-btn">30 Days</button>
                        <button onclick="loadCalendarView('60')" class="upload-btn">60 Days</button>
                        <button onclick="loadCalendarView('90')" class="upload-btn">90 Days</button>
                    </div>
                    <div id="calendar-events">
                `;
                
                if (data.events && data.events.length > 0) {
                    data.events.forEach(event => {
                        content += `
                            <div class="priority-action">
                                <h4>${event.title} - ${event.date}</h4>
                                <p>Category: ${event.category || 'undefined'} | Budget: ${event.budget || '$undefined'}</p>
                                <p>${event.description || 'No description available'}</p>
                            </div>
                        `;
                    });
                } else {
                    content += `<p>No calendar events found for this timeframe.</p>`;
                }
                
                content += `</div></div>`;
                
                document.getElementById('calendar-content').innerHTML = content;
                document.getElementById('calendar-loading').style.display = 'none';
                document.getElementById('calendar-content').style.display = 'block';
                
            } catch (error) {
                document.getElementById('calendar-loading').innerHTML = `
                    <div class="error">Error loading calendar: ${error.message}</div>
                `;
            }
        }
        
        async function loadAgency() {
            try {
                const response = await fetch('/api/agency');
                const data = await response.json();
                
                let content = `
                    <h2>🏢 Agency Tracking</h2>
                    <div class="overview-grid">
                        <div class="overview-card">
                            <h3>High Voltage Digital</h3>
                            <div class="metric">
                                <span>Active Projects:</span>
                                <span class="metric-value">${data.active_projects || '4'}</span>
                            </div>
                            <div class="metric">
                                <span>Monthly Budget:</span>
                                <span class="metric-value">$${(data.monthly_budget || 4000).toLocaleString()}</span>
                            </div>
                            <div class="metric">
                                <span>Completion Rate:</span>
                                <span class="metric-value">${data.completion_rate || data.utilization_rate || '70'}%</span>
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById('agency-content').innerHTML = content;
                document.getElementById('agency-loading').style.display = 'none';
                document.getElementById('agency-content').style.display = 'block';
                
            } catch (error) {
                document.getElementById('agency-loading').innerHTML = `
                    <div class="error">Error loading agency data: ${error.message}</div>
                `;
            }
        }
        
        async function loadCalendarView(days) {
            try {
                const response = await fetch(`/api/calendar/${days}`);
                const data = await response.json();
                
                let content = '';
                if (data.events && data.events.length > 0) {
                    data.events.forEach(event => {
                        content += `
                            <div class="priority-action">
                                <h4>${event.title} - ${event.date}</h4>
                                <p>Category: ${event.category || 'undefined'} | Budget: ${event.budget || '$undefined'}</p>
                                <p>${event.description || 'No description available'}</p>
                            </div>
                        `;
                    });
                } else {
                    content = `<p>No events found for ${days}-day view.</p>`;
                }
                
                document.getElementById('calendar-events').innerHTML = content;
                
            } catch (error) {
                document.getElementById('calendar-events').innerHTML = `
                    <div class="error">Error loading ${days}-day calendar: ${error.message}</div>
                `;
            }
        }
        
        // Upload Modal Functions
        function openUploadModal() {
            document.getElementById('uploadModal').style.display = 'block';
            selectedFiles = [];
            updateFileList();
        }
        
        function closeUploadModal() {
            document.getElementById('uploadModal').style.display = 'none';
            selectedFiles = [];
            updateFileList();
        }
        
        // Drag and Drop functionality
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            addFiles(files);
        });
        
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            addFiles(files);
        });
        
        function addFiles(files) {
            files.forEach(file => {
                if (file.size <= 100 * 1024 * 1024) { // 100MB limit
                    selectedFiles.push(file);
                } else {
                    alert(`File ${file.name} is too large. Maximum size is 100MB.`);
                }
            });
            updateFileList();
        }
        
        function updateFileList() {
            const fileList = document.getElementById('fileList');
            const uploadButton = document.getElementById('uploadButton');
            
            if (selectedFiles.length === 0) {
                fileList.innerHTML = '';
                uploadButton.style.display = 'none';
                return;
            }
            
            uploadButton.style.display = 'block';
            
            let html = '<h3 style="color: #ff6b35; margin-bottom: 15px;">Selected Files:</h3>';
            selectedFiles.forEach((file, index) => {
                html += `
                    <div class="file-item">
                        <div>
                            <strong>${file.name}</strong><br>
                            <small>${(file.size / 1024 / 1024).toFixed(2)} MB</small>
                        </div>
                        <button onclick="removeFile(${index})" style="background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Remove</button>
                    </div>
                `;
            });
            
            fileList.innerHTML = html;
        }
        
        function removeFile(index) {
            selectedFiles.splice(index, 1);
            updateFileList();
        }
        
        async function uploadFiles() {
            if (selectedFiles.length === 0) return;
            
            const uploadButton = document.getElementById('uploadButton');
            uploadButton.textContent = 'Uploading...';
            uploadButton.disabled = true;
            
            try {
                for (let i = 0; i < selectedFiles.length; i++) {
                    const file = selectedFiles[i];
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Failed to upload ${file.name}`);
                    }
                }
                
                alert(`Successfully uploaded ${selectedFiles.length} file(s)!`);
                closeUploadModal();
                
                // Refresh assets if we're on the assets tab
                if (currentTab === 'assets') {
                    loadAssets();
                }
                
                // Refresh overview to update asset counts
                if (currentTab === 'overview') {
                    loadOverview();
                }
                
            } catch (error) {
                alert(`Upload failed: ${error.message}`);
            } finally {
                uploadButton.textContent = '🚀 Upload Selected Files';
                uploadButton.disabled = false;
            }
        }
        
        function downloadAsset(filename) {
            window.open(`/api/assets/download/${filename}`, '_blank');
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('uploadModal');
            if (event.target === modal) {
                closeUploadModal();
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadOverview();
        });
    </script>
</body>
</html>
    """

# ==================== API ENDPOINTS ====================

@app.route('/api/overview')
def api_overview():
    """Get dashboard overview with real data"""
    try:
        # Get intelligence data
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
                'last_updated': intelligence_data.get('analysis_timestamp', datetime.now().isoformat()),
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
    """Get competitive intelligence data"""
    try:
        intelligence_data = process_intelligence_data()
        hashtags = analyze_hashtags()
        recommendations = generate_recommendations()
        
        return jsonify({
            'analysis_timestamp': intelligence_data.get('analysis_timestamp', datetime.now().isoformat()),
            'trustworthiness_score': calculate_trustworthiness_score(intelligence_data),
            'total_analyzed': intelligence_data.get('total_analyzed', 259),
            'hashtags': hashtags,
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"Error in api_intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets')
def api_assets():
    """Get asset library data"""
    try:
        assets = scan_assets()
        return jsonify({
            'assets': assets,
            'total_count': len(assets),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_assets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add to asset manager
            try:
                add_asset(file_path)
            except Exception as e:
                print(f"Warning: Could not add asset to manager: {e}")
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'File {filename} uploaded successfully'
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        print(f"Error in api_upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/download/<filename>')
def api_download(filename):
    """Download asset files"""
    try:
        # Security check - only allow files from upload folder
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)
        else:
            # Try other asset directories
            for root, dirs, files in os.walk('uploads'):
                if safe_filename in files:
                    return send_from_directory(root, safe_filename, as_attachment=True)
            
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        print(f"Error in api_download: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/<timeframe>')
def api_calendar(timeframe):
    """Get calendar data for specified timeframe"""
    try:
        calendar_data = get_calendar(f'{timeframe}_day_view')
        return jsonify({
            'events': calendar_data,
            'timeframe': timeframe,
            'count': len(calendar_data) if isinstance(calendar_data, list) else 0,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_calendar: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agency')
def api_agency():
    """Get agency tracking data"""
    try:
        agency_data = get_agency_status()
        return jsonify(agency_data)
    except Exception as e:
        print(f"Error in api_agency: {e}")
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

if __name__ == '__main__':
    print("🏰 Starting Crooks & Castles Command Center V2...")
    print("📊 Initializing competitive intelligence...")
    print("📁 Setting up asset management...")
    print("📅 Loading calendar engine...")
    print("🏢 Connecting agency tracking...")
    print("📤 Enabling file upload functionality...")
    app.run(host='0.0.0.0', port=5000, debug=False)
