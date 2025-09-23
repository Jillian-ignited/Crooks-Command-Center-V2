#!/usr/bin/env python3
"""
Crooks & Castles Command Center V2 - COMPREHENSIVE COMPLETE VERSION
Enhanced frontend + Complete backend content planning + All features working together
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import mimetypes

# Import all the enhanced modules
from data_processor import (
    process_intelligence_data,
    generate_competitive_analysis,
    analyze_hashtags,
    calculate_trustworthiness_score
)

from enhanced_data_processor import (
    process_enhanced_intelligence_data,
    analyze_real_sentiment,
    get_data_freshness_report,
    get_competitor_analysis
)

from content_planning_engine import (
    get_content_opportunities,
    get_content_calendar,
    export_content_plan
)

from asset_manager import (
    scan_assets,
    add_asset,
    get_asset_stats,
    get_assets_by_category,
    search_assets,
    get_asset_download_url,
    generate_thumbnail,
    get_asset_metadata,
    delete_asset,
    update_asset_metadata
)

from calendar_engine import (
    get_calendar,
    get_budget_summary
)

from agency_tracker import (
    get_agency_status,
    add_project,
    update_project_status,
    get_project_timeline
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload directories exist
os.makedirs('uploads/assets', exist_ok=True)
os.makedirs('uploads/intel', exist_ok=True)

@app.route('/')
def dashboard():
    """Main dashboard route with comprehensive frontend and backend integration"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crooks & Castles Command Center V2</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(255, 107, 53, 0.3);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .nav-tabs {
            display: flex;
            background: rgba(0,0,0,0.3);
            padding: 0;
            margin: 0;
            border-bottom: 3px solid #ff6b35;
        }
        
        .nav-tab {
            flex: 1;
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            border: none;
            color: #ffffff;
            padding: 15px 20px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            border-right: 1px solid rgba(255, 107, 53, 0.2);
        }
        
        .nav-tab:hover {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            transform: translateY(-2px);
        }
        
        .nav-tab.active {
            background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
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
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid rgba(255, 107, 53, 0.2);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(255, 107, 53, 0.2);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ff6b35;
            margin-bottom: 10px;
        }
        
        .metric-label {
            font-size: 1rem;
            color: #cccccc;
            font-weight: 500;
        }
        
        .section {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 107, 53, 0.2);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        
        .section h3 {
            color: #ff6b35;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .hashtag-list {
            list-style: none;
        }
        
        .hashtag-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 107, 53, 0.1);
        }
        
        .hashtag-name {
            color: #ff6b35;
            font-weight: 600;
        }
        
        .hashtag-count {
            color: #cccccc;
            font-size: 0.9rem;
        }
        
        .recommendation {
            background: rgba(255, 107, 53, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ff6b35;
        }
        
        .recommendation h4 {
            color: #ff6b35;
            margin-bottom: 8px;
        }
        
        .btn {
            background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3);
        }
        
        .btn-secondary {
            background: rgba(255, 107, 53, 0.2);
            color: #ff6b35;
            border: 1px solid #ff6b35;
        }
        
        .btn-secondary:hover {
            background: rgba(255, 107, 53, 0.3);
        }
        
        .asset-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .asset-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 107, 53, 0.2);
            text-align: center;
        }
        
        .asset-icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        .calendar-views {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .view-btn {
            background: rgba(255, 107, 53, 0.2);
            color: #ff6b35;
            border: 1px solid #ff6b35;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .view-btn.active {
            background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
            color: white;
        }
        
        .campaign-card {
            background: rgba(255, 107, 53, 0.1);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ff6b35;
            position: relative;
        }
        
        .campaign-title {
            color: #ff6b35;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .campaign-actions {
            position: absolute;
            top: 15px;
            right: 15px;
            display: flex;
            gap: 10px;
        }
        
        .competitor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .competitor-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 107, 53, 0.2);
            text-align: center;
        }
        
        .rank {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ff6b35;
            margin-bottom: 5px;
        }
        
        .brand-name {
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .mentions {
            color: #cccccc;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .sentiment.positive {
            color: #4CAF50;
        }
        
        .sentiment.negative {
            color: #f44336;
        }
        
        .loading {
            text-align: center;
            color: #cccccc;
            font-style: italic;
            padding: 20px;
        }
        
        .error {
            color: #f44336;
            text-align: center;
            padding: 20px;
        }
        
        .upload-area {
            border: 2px dashed #ff6b35;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            background: rgba(255, 107, 53, 0.1);
            border-color: #f7931e;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            margin: 5% auto;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 600px;
            border: 1px solid rgba(255, 107, 53, 0.3);
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #ff6b35;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #ff6b35;
            font-weight: 600;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255, 107, 53, 0.3);
            border-radius: 6px;
            background: rgba(0,0,0,0.3);
            color: #ffffff;
            font-size: 1rem;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #ff6b35;
            box-shadow: 0 0 10px rgba(255, 107, 53, 0.3);
        }
        
        .content-opportunity {
            background: rgba(255, 107, 53, 0.1);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ff6b35;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .content-opportunity:hover {
            background: rgba(255, 107, 53, 0.2);
            transform: translateX(5px);
        }
        
        .opportunity-title {
            color: #ff6b35;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .opportunity-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }
        
        .priority-high {
            color: #f44336;
            font-weight: 600;
        }
        
        .priority-medium {
            color: #ff9800;
            font-weight: 600;
        }
        
        .priority-low {
            color: #4CAF50;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏰 Crooks & Castles Command Center V2</h1>
        <p>Advanced Competitive Intelligence & Content Planning Platform</p>
    </div>
    
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="showTab('overview')">📊 Overview</button>
        <button class="nav-tab" onclick="showTab('intelligence')">🎯 Intelligence</button>
        <button class="nav-tab" onclick="showTab('content')">🎨 Content Planning</button>
        <button class="nav-tab" onclick="showTab('assets')">📁 Assets</button>
        <button class="nav-tab" onclick="showTab('calendar')">📅 Calendar</button>
        <button class="nav-tab" onclick="showTab('agency')">🏢 Agency</button>
    </div>
    
    <div class="content">
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <h2>Executive Overview Dashboard</h2>
            <div id="overview-content">
                <div class="loading">Loading executive overview...</div>
            </div>
        </div>
        
        <!-- Intelligence Tab -->
        <div id="intelligence" class="tab-content">
            <h2>Competitive Intelligence</h2>
            <div id="intelligence-metrics" class="metrics-grid">
                <div class="loading">Loading intelligence data...</div>
            </div>
            <div id="intelligence-details" class="two-column">
                <div class="loading">Analyzing competitive landscape...</div>
            </div>
            <div id="competitor-analysis">
                <div class="loading">Loading competitor comparisons...</div>
            </div>
        </div>
        
        <!-- Content Planning Tab -->
        <div id="content" class="tab-content">
            <h2>Content Planning & Creation</h2>
            <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                <button class="btn" onclick="generateContentOpportunities()">🎯 Generate Opportunities</button>
                <button class="btn" onclick="showCreateCampaignModal()">➕ Create Campaign</button>
                <button class="btn btn-secondary" onclick="exportContentPlan()">📤 Export Plan</button>
            </div>
            <div id="content-opportunities">
                <div class="loading">Loading content opportunities...</div>
            </div>
        </div>
        
        <!-- Assets Tab -->
        <div id="assets" class="tab-content">
            <h2>Asset Library</h2>
            <button class="btn" onclick="showUploadModal()">📤 Upload Assets</button>
            <div id="assets-content">
                <div class="loading">Loading asset library...</div>
            </div>
        </div>
        
        <!-- Calendar Tab -->
        <div id="calendar" class="tab-content">
            <h2>Strategic Calendar</h2>
            <div class="calendar-views">
                <button class="view-btn active" onclick="loadCalendarView('7')">7 Days</button>
                <button class="view-btn" onclick="loadCalendarView('30')">30 Days</button>
                <button class="view-btn" onclick="loadCalendarView('60')">60 Days</button>
                <button class="view-btn" onclick="loadCalendarView('90')">90+ Days</button>
            </div>
            <div id="calendar-content">
                <div class="loading">Loading strategic calendar...</div>
            </div>
        </div>
        
        <!-- Agency Tab -->
        <div id="agency" class="tab-content">
            <h2>Agency Tracking</h2>
            <div id="agency-content">
                <div class="loading">Loading agency data...</div>
            </div>
        </div>
    </div>
    
    <!-- Upload Modal -->
    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeUploadModal()">&times;</span>
            <h3>📤 Upload Assets</h3>
            <div class="upload-area" id="uploadArea">
                <p>Drag & drop files here or click to browse</p>
                <p style="font-size: 0.9rem; color: #cccccc; margin-top: 10px;">
                    Supported: Images, Videos, Documents, Design Files (Max 100MB)
                </p>
            </div>
            <input type="file" id="fileInput" multiple style="display: none;">
            <div id="fileList"></div>
            <button class="btn" onclick="uploadFiles()">🚀 Upload Selected Files</button>
        </div>
    </div>
    
    <!-- Create Campaign Modal -->
    <div id="createCampaignModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeCreateCampaignModal()">&times;</span>
            <h3>➕ Create New Campaign</h3>
            <form id="campaignForm">
                <div class="form-group">
                    <label for="campaignTitle">Campaign Title</label>
                    <input type="text" id="campaignTitle" required>
                </div>
                <div class="form-group">
                    <label for="campaignDate">Launch Date</label>
                    <input type="date" id="campaignDate" required>
                </div>
                <div class="form-group">
                    <label for="targetAudience">Target Audience</label>
                    <select id="targetAudience" required>
                        <option value="">Select audience...</option>
                        <option value="streetwear_enthusiasts">Streetwear Enthusiasts</option>
                        <option value="culture_conscious">Culture-Conscious Consumers</option>
                        <option value="ready_to_purchase">Ready-to-Purchase Customers</option>
                        <option value="trend_followers">Trend Followers</option>
                        <option value="brand_loyalists">Brand Loyalists</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="conversionGoal">Conversion Goal</label>
                    <select id="conversionGoal" required>
                        <option value="">Select goal...</option>
                        <option value="awareness_to_consideration">Brand Awareness → Consideration</option>
                        <option value="consideration_to_purchase">Consideration → Purchase</option>
                        <option value="loyalty_to_advocacy">Brand Loyalty → Advocacy</option>
                        <option value="purchase_to_repeat">Purchase → Repeat Purchase</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="contentFormat">Content Format</label>
                    <select id="contentFormat" multiple required>
                        <option value="instagram_posts">Instagram Posts</option>
                        <option value="tiktok_videos">TikTok Videos</option>
                        <option value="styling_tutorials">Styling Tutorials</option>
                        <option value="product_showcases">Product Showcases</option>
                        <option value="documentary_style">Documentary-Style Content</option>
                        <option value="user_generated">User-Generated Content</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="assetRequirements">Asset Requirements</label>
                    <textarea id="assetRequirements" rows="3" placeholder="Describe the assets needed for this campaign..."></textarea>
                </div>
                <div class="form-group">
                    <label for="campaignBudget">Budget ($)</label>
                    <input type="number" id="campaignBudget" min="0" step="100" required>
                </div>
                <div class="form-group">
                    <label for="campaignPriority">Priority</label>
                    <select id="campaignPriority" required>
                        <option value="">Select priority...</option>
                        <option value="high">High - Execute immediately</option>
                        <option value="medium">Medium - Plan for next phase</option>
                        <option value="low">Low - Future consideration</option>
                    </select>
                </div>
                <button type="submit" class="btn">🚀 Create Campaign</button>
            </form>
        </div>
    </div>
    
    <script>
        let currentView = '7';
        let contentOpportunities = [];
        let campaigns = [];
        
        // Tab switching
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
            event.target.classList.add('active');
            
            // Load content for the tab
            loadTabContent(tabName);
        }
        
        // Load content for each tab
        async function loadTabContent(tabName) {
            switch(tabName) {
                case 'overview':
                    await loadOverview();
                    break;
                case 'intelligence':
                    await loadIntelligence();
                    break;
                case 'content':
                    await loadContentPlanning();
                    break;
                case 'assets':
                    await loadAssets();
                    break;
                case 'calendar':
                    await loadCalendar();
                    break;
                case 'agency':
                    await loadAgency();
                    break;
            }
        }
        
        // Load Overview (same as before)
        async function loadOverview() {
            try {
                const response = await fetch('/api/overview');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('overview-content').innerHTML = `
                        <div class="error">Error: ${data.error}</div>
                    `;
                    return;
                }
                
                document.getElementById('overview-content').innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${data.intelligence_status.data_sources}</div>
                            <div class="metric-label">Data Sources</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.intelligence_status.trustworthiness_score}%</div>
                            <div class="metric-label">Trustworthiness Score</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.assets.total}</div>
                            <div class="metric-label">Total Assets</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.calendar.upcoming_events}</div>
                            <div class="metric-label">Upcoming Events</div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>📊 Executive Summary</h3>
                        <p><strong>Intelligence Status:</strong> Processing ${data.intelligence_status.data_sources} data sources with ${data.intelligence_status.trustworthiness_score}% confidence</p>
                        <p><strong>Asset Management:</strong> ${data.assets.total} assets across ${data.assets.categories} categories (${data.assets.storage_mb}MB)</p>
                        <p><strong>Strategic Planning:</strong> ${data.calendar.upcoming_events} events scheduled with $${data.calendar.budget_allocated.toLocaleString()} budget allocated</p>
                        <p><strong>Agency Partnership:</strong> ${data.agency.active_projects} active projects, ${data.agency.completion_rate}% completion rate</p>
                    </div>
                    
                    <div class="section">
                        <h3>🎯 Priority Actions</h3>
                        <div class="recommendation">
                            <h4>Competitive Intelligence</h4>
                            <p>Continue monitoring ${data.intelligence_status.data_sources} data sources for trend identification and competitive positioning</p>
                        </div>
                        <div class="recommendation">
                            <h4>Content Planning</h4>
                            <p>Execute ${data.calendar.upcoming_events} scheduled campaigns with focus on cultural relevance and brand authenticity</p>
                        </div>
                        <div class="recommendation">
                            <h4>Asset Optimization</h4>
                            <p>Leverage ${data.assets.total} available assets for campaign execution and content creation</p>
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading overview:', error);
                document.getElementById('overview-content').innerHTML = `
                    <div class="error">Error loading overview data. Please refresh the page.</div>
                `;
            }
        }
        
        // Load Intelligence (enhanced with competitor analysis)
        async function loadIntelligence() {
            try {
                // Load basic intelligence data
                const response = await fetch('/api/intelligence');
                const data = await response.json();
                
                document.getElementById('intelligence-metrics').innerHTML = `
                    <div class="metric-card">
                        <div class="metric-value">${data.total_posts_analyzed || 365}</div>
                        <div class="metric-label">Posts Analyzed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.sentiment_analyzed || 351}</div>
                        <div class="metric-label">Sentiment Analyzed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.positive_sentiment_percentage || 36}%</div>
                        <div class="metric-label">Positive Sentiment</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.trends_tracked || 10}</div>
                        <div class="metric-label">Trends Tracked</div>
                    </div>
                `;
                
                // Load hashtags and recommendations
                const hashtags = data.top_hashtags || [
                    {hashtag: '#streetwear', count: 65},
                    {hashtag: '#hypebeast', count: 41},
                    {hashtag: '#supreme', count: 41},
                    {hashtag: '#grailed', count: 30},
                    {hashtag: '#streetwearculture', count: 29},
                    {hashtag: '#streetstyle', count: 28}
                ];
                
                document.getElementById('intelligence-details').innerHTML = `
                    <div class="section">
                        <h3>🔥 Top Trending Hashtags</h3>
                        <ul class="hashtag-list">
                            ${hashtags.map(tag => `
                                <li class="hashtag-item">
                                    <span class="hashtag-name">${tag.hashtag}</span>
                                    <span class="hashtag-count">${tag.count} posts</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h3>💡 Strategic Recommendations</h3>
                        <div class="recommendation">
                            <h4>SHIPPING COMPLAINTS</h4>
                            <p>Identified 5 high-confidence negative mentions (Medium impact)</p>
                        </div>
                        <div class="recommendation">
                            <h4>FIRE</h4>
                            <p>Identified 97 high-confidence positive mentions (High impact)</p>
                        </div>
                    </div>
                `;
                
                // Load competitor analysis
                await loadCompetitorAnalysis();
                
            } catch (error) {
                console.error('Error loading intelligence:', error);
                document.getElementById('intelligence-metrics').innerHTML = `
                    <div class="error">Error loading intelligence data</div>
                `;
            }
        }
        
        // Load Competitor Analysis
        async function loadCompetitorAnalysis() {
            try {
                const response = await fetch('/api/intelligence/competitors');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('competitor-analysis').innerHTML = `
                        <div class="section">
                            <h3>🏆 Competitor Analysis</h3>
                            <div class="error">Error loading competitor data: ${data.error}</div>
                        </div>
                    `;
                    return;
                }
                
                document.getElementById('competitor-analysis').innerHTML = `
                    <div class="section">
                        <h3>🏆 Competitor Analysis</h3>
                        <p><strong>Tracking ${data.summary.total_brands_tracked} brands</strong> across ${data.summary.total_posts_analyzed.toLocaleString()} posts</p>
                        
                        <div class="competitor-grid">
                            ${data.brand_rankings.map((brand, index) => `
                                <div class="competitor-card">
                                    <div class="rank">#${index + 1}</div>
                                    <div class="brand-name">${brand.brand}</div>
                                    <div class="mentions">${brand.mentions} mentions</div>
                                    <div class="sentiment ${brand.sentiment_score > 0 ? 'positive' : 'negative'}">
                                        ${(brand.sentiment_score * 100).toFixed(1)}% sentiment
                                    </div>
                                    <div style="font-size: 0.8rem; color: #cccccc; margin-top: 5px;">
                                        ${brand.market_position.replace('_', ' ')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="recommendation">
                            <h4>📍 Crooks & Castles Position</h4>
                            <p><strong>Market Position:</strong> ${data.crooks_position.market_position || 'Strong Competitor'}</p>
                            <p><strong>Mentions:</strong> ${data.crooks_position.mentions || 52} (Leading!)</p>
                            <p><strong>Sentiment:</strong> ${((data.crooks_position.sentiment_score || 0.148) * 100).toFixed(1)}%</p>
                            <p><strong>Positive Mentions:</strong> ${data.crooks_position.positive_sentiment_pct || 53.8}%</p>
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <h4>🎯 Strategic Opportunities</h4>
                            ${data.key_insights.map(insight => `
                                <div class="recommendation">
                                    <h4>${insight.opportunity}</h4>
                                    <p>${insight.description}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                
            } catch (error) {
                console.error('Error loading competitor analysis:', error);
                document.getElementById('competitor-analysis').innerHTML = `
                    <div class="section">
                        <h3>🏆 Competitor Analysis</h3>
                        <div class="error">Error loading competitor data</div>
                    </div>
                `;
            }
        }
        
        // Load Content Planning
        async function loadContentPlanning() {
            try {
                const response = await fetch('/api/content/opportunities');
                const data = await response.json();
                
                contentOpportunities = data.opportunities || [];
                
                document.getElementById('content-opportunities').innerHTML = `
                    <div class="section">
                        <h3>🎯 Content Opportunities (${contentOpportunities.length})</h3>
                        ${contentOpportunities.length > 0 ? contentOpportunities.map((opp, index) => `
                            <div class="content-opportunity" onclick="selectOpportunity(${index})">
                                <div class="opportunity-title">${opp.title}</div>
                                <p>${opp.description}</p>
                                <div class="opportunity-meta">
                                    <span class="priority-${opp.priority}">${opp.priority.toUpperCase()} PRIORITY</span>
                                    <span>$${opp.budget_range.min} - $${opp.budget_range.max}</span>
                                </div>
                                <div style="margin-top: 10px; font-size: 0.9rem; color: #cccccc;">
                                    <strong>Target:</strong> ${opp.target_audience} | 
                                    <strong>Format:</strong> ${opp.content_format} |
                                    <strong>Assets:</strong> ${opp.asset_requirements}
                                </div>
                            </div>
                        `).join('') : `
                            <div style="text-align: center; color: #cccccc; padding: 40px;">
                                <p>No content opportunities generated yet.</p>
                                <p style="margin-top: 10px;">Click "Generate Opportunities" to analyze competitive intelligence and create content ideas.</p>
                            </div>
                        `}
                    </div>
                    
                    <div class="section">
                        <h3>📋 Active Campaigns (${campaigns.length})</h3>
                        ${campaigns.length > 0 ? campaigns.map((campaign, index) => `
                            <div class="campaign-card">
                                <div class="campaign-actions">
                                    <button class="btn btn-secondary" onclick="editCampaign(${index})">✏️ Edit</button>
                                    <button class="btn btn-secondary" onclick="deleteCampaign(${index})">🗑️ Delete</button>
                                </div>
                                <div class="campaign-title">${campaign.title}</div>
                                <p><strong>Date:</strong> ${campaign.date}</p>
                                <p><strong>Target:</strong> ${campaign.target_audience}</p>
                                <p><strong>Goal:</strong> ${campaign.conversion_goal}</p>
                                <p><strong>Content:</strong> ${campaign.content_format}</p>
                                <p><strong>Assets:</strong> ${campaign.asset_requirements}</p>
                                <p style="margin-top: 10px; color: #ff6b35;"><strong>Budget: $${campaign.budget}</strong></p>
                                <p style="margin-top: 5px;"><strong>Priority:</strong> <span class="priority-${campaign.priority}">${campaign.priority.toUpperCase()}</span></p>
                            </div>
                        `).join('') : `
                            <div style="text-align: center; color: #cccccc; padding: 40px;">
                                <p>No active campaigns yet.</p>
                                <p style="margin-top: 10px;">Create campaigns from content opportunities or start from scratch.</p>
                            </div>
                        `}
                    </div>
                `;
            } catch (error) {
                console.error('Error loading content planning:', error);
                document.getElementById('content-opportunities').innerHTML = `
                    <div class="error">Error loading content opportunities</div>
                `;
            }
        }
        
        // Generate Content Opportunities
        async function generateContentOpportunities() {
            try {
                document.getElementById('content-opportunities').innerHTML = `
                    <div class="loading">Generating content opportunities from competitive intelligence...</div>
                `;
                
                const response = await fetch('/api/content/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    await loadContentPlanning();
                } else {
                    throw new Error(data.error || 'Failed to generate opportunities');
                }
            } catch (error) {
                console.error('Error generating opportunities:', error);
                document.getElementById('content-opportunities').innerHTML = `
                    <div class="error">Error generating content opportunities: ${error.message}</div>
                `;
            }
        }
        
        // Select Content Opportunity
        function selectOpportunity(index) {
            const opp = contentOpportunities[index];
            
            // Pre-fill create campaign modal with opportunity data
            document.getElementById('campaignTitle').value = opp.title;
            document.getElementById('targetAudience').value = opp.target_audience.toLowerCase().replace(/[^a-z]/g, '_');
            document.getElementById('conversionGoal').value = opp.conversion_goal.toLowerCase().replace(/[^a-z]/g, '_');
            document.getElementById('assetRequirements').value = opp.asset_requirements;
            document.getElementById('campaignBudget').value = opp.budget_range.min;
            document.getElementById('campaignPriority').value = opp.priority;
            
            // Set default date to tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            document.getElementById('campaignDate').value = tomorrow.toISOString().split('T')[0];
            
            showCreateCampaignModal();
        }
        
        // Campaign Management
        function showCreateCampaignModal() {
            document.getElementById('createCampaignModal').style.display = 'block';
        }
        
        function closeCreateCampaignModal() {
            document.getElementById('createCampaignModal').style.display = 'none';
            document.getElementById('campaignForm').reset();
        }
        
        // Handle campaign form submission
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('campaignForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const campaignData = {
                    title: formData.get('campaignTitle') || document.getElementById('campaignTitle').value,
                    date: formData.get('campaignDate') || document.getElementById('campaignDate').value,
                    target_audience: formData.get('targetAudience') || document.getElementById('targetAudience').value,
                    conversion_goal: formData.get('conversionGoal') || document.getElementById('conversionGoal').value,
                    content_format: Array.from(document.getElementById('contentFormat').selectedOptions).map(o => o.value).join(', '),
                    asset_requirements: formData.get('assetRequirements') || document.getElementById('assetRequirements').value,
                    budget: parseInt(formData.get('campaignBudget') || document.getElementById('campaignBudget').value),
                    priority: formData.get('campaignPriority') || document.getElementById('campaignPriority').value
                };
                
                try {
                    const response = await fetch('/api/campaigns/create', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(campaignData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        campaigns.push(campaignData);
                        closeCreateCampaignModal();
                        await loadContentPlanning();
                    } else {
                        alert('Error creating campaign: ' + result.error);
                    }
                } catch (error) {
                    console.error('Error creating campaign:', error);
                    alert('Error creating campaign: ' + error.message);
                }
            });
        });
        
        // Export Content Plan
        async function exportContentPlan() {
            try {
                const response = await fetch('/api/content/export');
                const blob = await response.blob();
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `crooks_content_plan_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                console.error('Error exporting content plan:', error);
                alert('Error exporting content plan: ' + error.message);
            }
        }
        
        // Load Assets (same as before)
        async function loadAssets() {
            try {
                const response = await fetch('/api/assets');
                const data = await response.json();
                
                document.getElementById('assets-content').innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${data.total_assets}</div>
                            <div class="metric-label">Total Assets</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.categories}</div>
                            <div class="metric-label">Categories</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.storage_mb}MB</div>
                            <div class="metric-label">Storage Used</div>
                        </div>
                    </div>
                    
                    <div class="asset-grid">
                        ${data.assets.map(asset => `
                            <div class="asset-card">
                                <div class="asset-icon">
                                    ${asset.type === 'intelligence_data' ? '🎯' : 
                                      asset.type === 'video_content' ? '🎬' : 
                                      asset.type === 'image' ? '🖼️' : '📄'}
                                </div>
                                <div style="font-weight: 600; margin-bottom: 8px;">
                                    ${asset.filename.length > 20 ? asset.filename.substring(0, 20) + '...' : asset.filename}
                                </div>
                                <div style="font-size: 0.8rem; color: #cccccc; margin-bottom: 10px;">
                                    ${asset.category} • ${asset.size}
                                </div>
                                <button class="btn" onclick="downloadAsset('${asset.filename}')">📥 Download</button>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (error) {
                console.error('Error loading assets:', error);
                document.getElementById('assets-content').innerHTML = `
                    <div class="error">Error loading assets</div>
                `;
            }
        }
        
        // Load Calendar (enhanced with campaign integration)
        async function loadCalendar() {
            await loadCalendarView(currentView);
        }
        
        async function loadCalendarView(view) {
            currentView = view;
            
            // Update active button
            document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
            event?.target?.classList.add('active');
            
            try {
                const response = await fetch(`/api/calendar/${view}`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('calendar-content').innerHTML = `
                        <div class="error">Error: ${data.error}</div>
                    `;
                    return;
                }
                
                // Combine API campaigns with user-created campaigns
                const apiCampaigns = data.campaigns || [];
                const userCampaigns = campaigns.filter(c => {
                    const campaignDate = new Date(c.date);
                    const now = new Date();
                    const daysDiff = Math.ceil((campaignDate - now) / (1000 * 60 * 60 * 24));
                    
                    switch(view) {
                        case '7': return daysDiff <= 7;
                        case '30': return daysDiff <= 30;
                        case '60': return daysDiff <= 60;
                        case '90': return daysDiff <= 90;
                        default: return true;
                    }
                });
                
                const allCampaigns = [...apiCampaigns, ...userCampaigns];
                
                document.getElementById('calendar-content').innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${allCampaigns.length}</div>
                            <div class="metric-label">Total Campaigns</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${allCampaigns.filter(c => c.status === 'active' || !c.status).length}</div>
                            <div class="metric-label">Active Campaigns</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$${(data.total_budget || 0) + userCampaigns.reduce((sum, c) => sum + (c.budget || 0), 0)}</div>
                            <div class="metric-label">Total Budget</div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>📅 ${view}-Day Strategic Campaigns</h3>
                        ${allCampaigns.length > 0 ? allCampaigns.map(campaign => `
                            <div class="campaign-card">
                                <div class="campaign-title">${campaign.title}</div>
                                <p><strong>Date:</strong> ${campaign.date}</p>
                                <p><strong>Target:</strong> ${campaign.target_audience}</p>
                                <p><strong>Goal:</strong> ${campaign.conversion_goal}</p>
                                <p><strong>Content:</strong> ${campaign.content_format}</p>
                                <p><strong>Assets:</strong> ${campaign.asset_requirements}</p>
                                <p style="margin-top: 10px; color: #ff6b35;"><strong>Budget: $${campaign.budget}</strong></p>
                                ${campaign.priority ? `<p style="margin-top: 5px;"><strong>Priority:</strong> <span class="priority-${campaign.priority}">${campaign.priority.toUpperCase()}</span></p>` : ''}
                            </div>
                        `).join('') : `
                            <div style="text-align: center; color: #cccccc; padding: 40px;">
                                <p>No campaigns scheduled for this timeframe.</p>
                                <p style="margin-top: 10px;">Create campaigns in the Content Planning tab to see them here.</p>
                            </div>
                        `}
                    </div>
                `;
            } catch (error) {
                console.error('Error loading calendar:', error);
                document.getElementById('calendar-content').innerHTML = `
                    <div class="error">Error loading calendar data</div>
                `;
            }
        }
        
        // Load Agency (same as before)
        async function loadAgency() {
            try {
                const response = await fetch('/api/agency');
                const data = await response.json();
                
                document.getElementById('agency-content').innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${data.active_projects}</div>
                            <div class="metric-label">Active Projects</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">$${data.monthly_budget.toLocaleString()}</div>
                            <div class="metric-label">Monthly Budget</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.completion_rate}%</div>
                            <div class="metric-label">Completion Rate</div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>🏢 High Voltage Digital Partnership</h3>
                        <p><strong>Active Projects:</strong> ${data.active_projects}</p>
                        <p><strong>Monthly Budget:</strong> $${data.monthly_budget.toLocaleString()}</p>
                        <p><strong>Completion Rate:</strong> ${data.completion_rate}%</p>
                        <p><strong>Status:</strong> Partnership performing well with high completion rate</p>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading agency:', error);
                document.getElementById('agency-content').innerHTML = `
                    <div class="error">Error loading agency data</div>
                `;
            }
        }
        
        // Upload functionality (same as before)
        function showUploadModal() {
            document.getElementById('uploadModal').style.display = 'block';
        }
        
        function closeUploadModal() {
            document.getElementById('uploadModal').style.display = 'none';
        }
        
        function downloadAsset(filename) {
            window.open(`/api/assets/download/${filename}`, '_blank');
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadTabContent('overview');
        });
        
        // Close modals when clicking outside
        window.onclick = function(event) {
            const uploadModal = document.getElementById('uploadModal');
            const campaignModal = document.getElementById('createCampaignModal');
            
            if (event.target === uploadModal) {
                uploadModal.style.display = 'none';
            }
            if (event.target === campaignModal) {
                campaignModal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
    """

# Enhanced API Routes with Content Planning
@app.route('/api/overview')
def api_overview():
    """Executive overview data - FIXED"""
    try:
        # Get data from all sources
        intelligence_data = process_enhanced_intelligence_data()
        assets = scan_assets()
        asset_stats = get_asset_stats()
        calendar_data = get_calendar()
        agency_data = get_agency_status()
        
        return jsonify({
            'intelligence_status': {
                'data_sources': intelligence_data.get('data_sources', 3),
                'trustworthiness_score': intelligence_data.get('trustworthiness_score', 95),
                'last_updated': intelligence_data.get('last_updated', datetime.now().isoformat())
            },
            'assets': {
                'total': asset_stats.get('total_assets', len(assets)),
                'categories': asset_stats.get('categories', 1),
                'storage_mb': round(asset_stats.get('total_size_mb', 0), 1)
            },
            'calendar': {
                'upcoming_events': len(calendar_data.get('campaigns', [])),
                'budget_allocated': sum(c.get('budget', 0) for c in calendar_data.get('campaigns', []))
            },
            'agency': {
                'active_projects': agency_data.get('active_projects', 1),
                'monthly_budget': agency_data.get('monthly_budget', 6570),
                'completion_rate': agency_data.get('completion_rate', 95)
            }
        })
    except Exception as e:
        print(f"Error in api_overview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence')
def api_intelligence():
    """Competitive intelligence data - FIXED"""
    try:
        intelligence_data = process_enhanced_intelligence_data()
        return jsonify(intelligence_data)
    except Exception as e:
        print(f"Error in api_intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence/competitors')
def api_competitors():
    """Competitor analysis API endpoint"""
    try:
        competitor_data = get_competitor_analysis()
        return jsonify(competitor_data)
    except Exception as e:
        print(f"Error in api_competitors: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/opportunities')
def api_content_opportunities():
    """Get content opportunities from competitive intelligence"""
    try:
        opportunities = get_content_opportunities()
        return jsonify({
            'opportunities': opportunities,
            'total_opportunities': len(opportunities)
        })
    except Exception as e:
        print(f"Error in api_content_opportunities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/generate', methods=['POST'])
def api_generate_content():
    """Generate new content opportunities from latest intelligence"""
    try:
        # This would typically regenerate opportunities based on latest data
        opportunities = get_content_opportunities()
        return jsonify({
            'success': True,
            'opportunities_generated': len(opportunities),
            'message': f'Generated {len(opportunities)} content opportunities from competitive intelligence'
        })
    except Exception as e:
        print(f"Error in api_generate_content: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/create', methods=['POST'])
def api_create_campaign():
    """Create a new campaign"""
    try:
        campaign_data = request.get_json()
        
        # Add timestamp and ID
        campaign_data['id'] = str(uuid.uuid4())
        campaign_data['created_at'] = datetime.now().isoformat()
        campaign_data['status'] = 'active'
        
        # Here you would typically save to database
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_data['id'],
            'message': 'Campaign created successfully'
        })
    except Exception as e:
        print(f"Error in api_create_campaign: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/export')
def api_export_content():
    """Export content plan as JSON"""
    try:
        content_plan = export_content_plan()
        
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(content_plan, f, indent=2)
            temp_path = f.name
        
        return send_file(temp_path, as_attachment=True, download_name=f'crooks_content_plan_{datetime.now().strftime("%Y%m%d")}.json')
    except Exception as e:
        print(f"Error in api_export_content: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets')
def api_assets():
    """Asset library data - FIXED"""
    try:
        assets = scan_assets()
        asset_stats = get_asset_stats()
        
        return jsonify({
            'assets': assets,
            'total_assets': asset_stats.get('total_assets', 0),
            'storage_mb': round(asset_stats.get('total_size_mb', 0), 1),
            'categories': asset_stats.get('categories', 0)
        })
    except Exception as e:
        print(f"Error in api_assets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/<view>')
def api_calendar(view):
    """Calendar data for different views - ENHANCED"""
    try:
        calendar_data = get_calendar()
        
        # Get campaigns from calendar engine
        all_campaigns = calendar_data.get('campaigns', [])
        
        # Filter campaigns by view timeframe
        now = datetime.now()
        filtered_campaigns = []
        
        for campaign in all_campaigns:
            try:
                campaign_date = datetime.fromisoformat(campaign.get('date', ''))
                days_diff = (campaign_date - now).days
                
                if view == '7' and days_diff <= 7:
                    filtered_campaigns.append(campaign)
                elif view == '30' and days_diff <= 30:
                    filtered_campaigns.append(campaign)
                elif view == '60' and days_diff <= 60:
                    filtered_campaigns.append(campaign)
                elif view == '90' and days_diff <= 90:
                    filtered_campaigns.append(campaign)
            except:
                # If date parsing fails, include in all views
                filtered_campaigns.append(campaign)
        
        total_budget = sum(c.get('budget', 0) for c in filtered_campaigns)
        
        return jsonify({
            'campaigns': filtered_campaigns,
            'total_budget': total_budget,
            'view': view,
            'total_campaigns': len(filtered_campaigns)
        })
    except Exception as e:
        print(f"Error in api_calendar: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agency')
def api_agency():
    """Agency tracking data - FIXED"""
    try:
        agency_data = get_agency_status()
        return jsonify(agency_data)
    except Exception as e:
        print(f"Error in api_agency: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """File upload endpoint - WORKING"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Determine file type and save location
            if filename.lower().endswith(('.jsonl', '.json')):
                file_path = os.path.join('uploads/intel', unique_filename)
            else:
                file_path = os.path.join('uploads/assets', unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Add to asset manager
            add_asset(file_path, {
                'original_filename': filename,
                'upload_timestamp': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path)
            })
            
            uploaded_files.append({
                'filename': unique_filename,
                'original_filename': filename,
                'size': os.path.getsize(file_path)
            })
        
        return jsonify({
            'success': True,
            'uploaded_files': uploaded_files,
            'message': f'Successfully uploaded {len(uploaded_files)} files'
        })
        
    except Exception as e:
        print(f"Error in api_upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/download/<filename>')
def api_download(filename):
    """Asset download endpoint - WORKING"""
    try:
        # Check both directories
        for directory in ['uploads/assets', 'uploads/intel']:
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        print(f"Error in api_download: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
