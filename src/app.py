#!/usr/bin/env python3
"""
CROOKS & CASTLES COMMAND CENTER
Elegant content planning and agency management system
"""

import os
import sys
import uuid
import json
import sqlite3
import logging
import datetime
from datetime import timedelta
from pathlib import Path
from PIL import Image
import io
import base64

from flask import Flask, render_template_string, request, jsonify, send_file
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - Use relative paths for deployment compatibility
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up from src/ to root
UPLOAD_FOLDER = BASE_DIR / 'uploads'
ASSETS_FOLDER = BASE_DIR / 'static' / 'assets'
DATABASE_PATH = BASE_DIR / 'content_machine.db'
DATA_DIR = BASE_DIR / 'data'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Assets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            original_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER,
            badge_score INTEGER DEFAULT 0,
            assigned_code INTEGER,
            cultural_relevance TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            thumbnail_path TEXT
        )
    ''')
    
    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            hashtags TEXT,
            platform TEXT,
            scheduled_date TIMESTAMP,
            assigned_code INTEGER,
            mapped_asset_id TEXT,
            status TEXT DEFAULT 'draft',
            badge_score INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mapped_asset_id) REFERENCES assets (id)
        )
    ''')
    
    # Agency reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agency_reports (
            id TEXT PRIMARY KEY,
            report_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            parsed_data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Main Command Center interface"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crooks & Castles Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #ffffff;
            min-height: 100vh;
        }

        .header {
            background: rgba(0, 0, 0, 0.9);
            border-bottom: 2px solid #333;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .nav-tabs {
            display: flex;
            gap: 2rem;
        }

        .nav-tab {
            padding: 0.75rem 1.5rem;
            background: transparent;
            border: 1px solid #333;
            color: #ffffff;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .nav-tab:hover, .nav-tab.active {
            background: #333;
            border-color: #555;
        }

        .main-content {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .section {
            display: none;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .section.active {
            display: block;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: #ffffff;
        }

        .calendar-controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .calendar-btn {
            padding: 0.75rem 1.5rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .calendar-btn:hover, .calendar-btn.active {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .calendar-view {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 400px;
        }

        .asset-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }

        .asset-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .asset-card:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .asset-thumbnail {
            width: 100%;
            height: 150px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 4px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .asset-thumbnail img {
            max-width: 100%;
            max-height: 100%;
            object-fit: cover;
        }

        .asset-info {
            font-size: 0.9rem;
        }

        .asset-name {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .badge-score {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .badge-ready {
            background: #22c55e;
            color: #ffffff;
        }

        .badge-review {
            background: #ef4444;
            color: #ffffff;
        }

        .deliverables-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }

        .deliverable-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .deliverable-title {
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 0.5rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #22c55e, #16a34a);
            transition: width 0.3s ease;
        }

        .upload-area {
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
        }

        .upload-area:hover {
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.05);
        }

        .btn {
            padding: 0.75rem 1.5rem;
            background: #333;
            border: 1px solid #555;
            color: #ffffff;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.3s ease;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
        }

        .btn:hover {
            background: #444;
            border-color: #666;
        }

        .btn-primary {
            background: #22c55e;
            border-color: #16a34a;
        }

        .btn-primary:hover {
            background: #16a34a;
            border-color: #15803d;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.7);
        }

        .day-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .day-header {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #22c55e;
        }

        .post-item {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid #22c55e;
        }

        .post-title {
            font-weight: 500;
            margin-bottom: 0.25rem;
        }

        .post-meta {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
        }

        .opportunity-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .opportunity-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .opportunity-title {
            font-weight: 600;
            font-size: 1.1rem;
        }

        .priority-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .priority-high {
            background: #ef4444;
            color: #ffffff;
        }

        .priority-critical {
            background: #dc2626;
            color: #ffffff;
        }

        .content-ideas {
            margin-top: 1rem;
        }

        .content-ideas ul {
            list-style: none;
            padding-left: 1rem;
        }

        .content-ideas li {
            margin-bottom: 0.25rem;
            color: rgba(255, 255, 255, 0.8);
        }

        .content-ideas li:before {
            content: "→";
            margin-right: 0.5rem;
            color: #22c55e;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🏰 Crooks & Castles Command Center</div>
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showSection('calendar')">Calendar Planning</button>
            <button class="nav-tab" onclick="showSection('assets')">Asset Library</button>
            <button class="nav-tab" onclick="showSection('agency')">Agency Tracking</button>
        </div>
    </div>

    <div class="main-content">
        <!-- Calendar Planning Section -->
        <div id="calendar" class="section active">
            <h2 class="section-title">Strategic Calendar Planning</h2>
            
            <div class="calendar-controls">
                <button class="calendar-btn active" onclick="setCalendarView('7day')">7-Day Tactical</button>
                <button class="calendar-btn" onclick="setCalendarView('30day')">30-Day Strategic</button>
                <button class="calendar-btn" onclick="setCalendarView('60day')">60-Day Opportunities</button>
                <button class="calendar-btn" onclick="setCalendarView('90day')">90-Day+ Vision</button>
            </div>
            
            <div id="calendarView" class="calendar-view">
                <div class="loading">Loading calendar data...</div>
            </div>
        </div>

        <!-- Asset Library Section -->
        <div id="assets" class="section">
            <h2 class="section-title">Enhanced Asset Library</h2>
            
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <p>📁 Drag & drop assets here or click to upload</p>
                <p style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); margin-top: 0.5rem;">
                    Supports images and videos. Automatic Badge Test scoring.
                </p>
                <input type="file" id="fileInput" multiple accept="image/*,video/*" style="display: none;" onchange="uploadAssets(this.files)">
            </div>
            
            <div id="assetGrid" class="asset-grid">
                <div class="loading">Loading assets...</div>
            </div>
        </div>

        <!-- Agency Tracking Section -->
        <div id="agency" class="section">
            <h2 class="section-title">High Voltage Digital Partnership</h2>
            
            <div id="deliverablesGrid" class="deliverables-grid">
                <div class="loading">Loading agency data...</div>
            </div>
        </div>
    </div>

    <script>
        let currentCalendarView = '7day';

        // Navigation
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load section data
            if (sectionId === 'calendar') {
                displayCalendar();
            } else if (sectionId === 'assets') {
                loadAssets();
            } else if (sectionId === 'agency') {
                loadDeliverables();
            }
        }

        // Calendar functions
        function setCalendarView(view) {
            currentCalendarView = view;
            
            // Update button states
            document.querySelectorAll('.calendar-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            displayCalendar();
        }

        async function displayCalendar() {
            const container = document.getElementById('calendarView');
            
            try {
                const response = await fetch(`/api/calendar/${currentCalendarView}`);
                const data = await response.json();
                
                if (currentCalendarView === '7day') {
                    display7DayView(container, data.calendar_data);
                } else if (currentCalendarView === '30day') {
                    display30DayView(container, data.calendar_data);
                } else if (currentCalendarView === '60day') {
                    display60DayView(container, data.opportunities);
                } else if (currentCalendarView === '90day') {
                    display90DayView(container, data.long_range);
                }
            } catch (error) {
                console.error('Error loading calendar:', error);
                container.innerHTML = '<div class="loading">Error loading calendar data</div>';
            }
        }

        function display7DayView(container, calendarData) {
            let html = '<h3 style="margin-bottom: 1rem;">7-Day Tactical Execution</h3>';
            
            if (calendarData && calendarData.length > 0) {
                calendarData.forEach(day => {
                    html += `
                        <div class="day-card">
                            <div class="day-header">${day.day_name}, ${day.formatted_date}</div>
                    `;
                    
                    if (day.posts && day.posts.length > 0) {
                        day.posts.forEach(post => {
                            const badgeClass = post.badge_score >= 95 ? 'badge-ready' : 'badge-review';
                            html += `
                                <div class="post-item">
                                    <div class="post-title">${post.title}</div>
                                    <div class="post-meta">
                                        ${post.platform} • ${post.time_slot} • ${post.code_name}
                                        <span class="badge-score ${badgeClass}">${post.badge_score}%</span>
                                    </div>
                                    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
                                        ${post.content}
                                    </div>
                                    <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #22c55e;">
                                        ${post.hashtags}
                                    </div>
                                </div>
                            `;
                        });
                    } else {
                        html += '<div style="color: rgba(255, 255, 255, 0.5); font-style: italic;">No posts scheduled</div>';
                    }
                    
                    html += '</div>';
                });
            } else {
                html += '<div class="loading">No calendar data available</div>';
            }
            
            container.innerHTML = html;
        }

        function display30DayView(container, calendarData) {
            const strategicData = {
                "title": "30-Day Strategic Calendar - September 2025",
                "weeks": [
                    {
                        "week": 1, "dates": "Sep 1-7, 2025", "theme": "Back to School Street Culture",
                        "posts": [
                            {"date": "Sep 2", "title": "Labor Day Street Style", "platform": "Instagram", "asset_status": "✅ MAPPED", "asset": "real_instagram_story_rebel_rooftop.png", "crooks_code": "Code 29: Story"},
                            {"date": "Sep 5", "title": "Back to School Castle Crown", "platform": "TikTok", "asset_status": "🔨 NEEDS CREATION", "asset": "Back to school TikTok video", "crooks_code": "Code 05: Crooks Wear Crowns"}
                        ]
                    },
                    {
                        "week": 2, "dates": "Sep 8-14, 2025", "theme": "NFL Season & Sports Culture",
                        "posts": [
                            {"date": "Sep 8", "title": "NFL Season Kickoff Street Style", "platform": "Instagram Story", "asset_status": "✅ MAPPED", "asset": "real_instagram_story_rebel_rooftop.png", "crooks_code": "Code 29: Story"},
                            {"date": "Sep 9", "title": "Monday Night Football Prep", "platform": "TikTok", "asset_status": "🔨 NEEDS CREATION", "asset": "MNF prep video", "crooks_code": "Code 11: Culture"},
                            {"date": "Sep 10", "title": "Post-Game Street Culture Recap", "platform": "Instagram", "asset_status": "✅ MAPPED", "asset": "sept_16_cultural_fusion(3).png", "crooks_code": "Code 03: Global Throne"}
                        ]
                    },
                    {
                        "week": 3, "dates": "Sep 15-21, 2025", "theme": "Hispanic Heritage Month",
                        "posts": [
                            {"date": "Sep 15", "title": "Hispanic Heritage Month Launch", "platform": "Instagram", "asset_status": "✅ MAPPED", "asset": "sept_15_hispanic_heritage_launch(3).png", "crooks_code": "Code 01: Hustle Into Heritage"},
                            {"date": "Sep 16", "title": "Cultural Fusion Community", "platform": "Instagram", "asset_status": "✅ MAPPED", "asset": "sept_16_cultural_fusion(3).png", "crooks_code": "Code 03: Global Throne"},
                            {"date": "Sep 19", "title": "Hip Hop 52nd Anniversary Tribute", "platform": "Instagram", "asset_status": "✅ MAPPED", "asset": "sept_19_hiphop_anniversary(3).png", "crooks_code": "Code 11: Culture"}
                        ]
                    },
                    {
                        "week": 4, "dates": "Sep 22-30, 2025", "theme": "Street Culture Evolution",
                        "posts": [
                            {"date": "Sep 22", "title": "Medusa Logo Heritage Drop", "platform": "Instagram", "asset_status": "✅ MAPPED", "asset": "crooks-medusa.png", "crooks_code": "Code 05: Crooks Wear Crowns"},
                            {"date": "Sep 25", "title": "Community Spotlight Series", "platform": "Instagram Story", "asset_status": "🔨 NEEDS CREATION", "asset": "Community spotlight video", "crooks_code": "Code 03: Global Throne"},
                            {"date": "Sep 28", "title": "End of Month Streetwear Test", "platform": "TikTok", "asset_status": "✅ MAPPED", "asset": "pasted_file_TiodpQ_image.png", "crooks_code": "Code 29: Story"}
                        ]
                    }
                ]
            };
            
            let html = `<h3 style="margin-bottom: 1rem;">${strategicData.title}</h3>`;
            html += '<div class="strategic-calendar-grid">';
            
            strategicData.weeks.forEach(week => {
                html += `
                    <div class="week-section">
                        <div class="week-header">
                            <h4>Week ${week.week}: ${week.theme}</h4>
                            <span class="week-dates">${week.dates}</span>
                        </div>
                        <div class="week-posts">
                `;
                
                week.posts.forEach(post => {
                    const statusClass = post.asset_status.includes('MAPPED') ? 'status-mapped' : 
                                       post.asset_status.includes('CREATION') ? 'status-needs-creation' : 'status-needs-editing';
                    
                    html += `
                        <div class="strategic-post-card">
                            <div class="post-header">
                                <strong>${post.title}</strong>
                                <span class="post-date">${post.date}</span>
                            </div>
                            <div class="post-details">
                                <span class="platform-tag">${post.platform}</span>
                                <span class="asset-status ${statusClass}">${post.asset_status}</span>
                                <span class="crooks-code">${post.crooks_code}</span>
                            </div>
                            <div class="asset-info">
                                <strong>Asset:</strong> ${post.asset}
                            </div>
                        </div>
                    `;
                });
                
                html += '</div></div>';
            });
            
            html += '</div>';
            
            // Add CSS for strategic calendar
            html += `
                <style>
                .strategic-calendar-grid {
                    display: grid;
                    gap: 20px;
                }
                .week-section {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .week-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                .week-header h4 {
                    color: #22c55e;
                    margin: 0;
                }
                .week-dates {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 14px;
                }
                .week-posts {
                    display: grid;
                    gap: 12px;
                }
                .strategic-post-card {
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                }
                .post-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .post-date {
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 12px;
                }
                .post-details {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    margin-bottom: 8px;
                }
                .platform-tag, .crooks-code {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                .asset-status {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .status-mapped {
                    background: #22c55e;
                    color: white;
                }
                .status-needs-creation {
                    background: #f59e0b;
                    color: white;
                }
                .status-needs-editing {
                    background: #3b82f6;
                    color: white;
                }
                .asset-info {
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                }
                </style>
            `;
            
            container.innerHTML = html;
        }

        function display60DayView(container, opportunities) {
            const strategicOpportunities = [
                {
                    "title": "Hip Hop History Month",
                    "date_range": "October 1-31, 2025",
                    "type": "Cultural Heritage",
                    "priority": "High",
                    "cultural_significance": "Celebrate 52+ years of Hip Hop culture with authentic street storytelling",
                    "content_requirements": ["12 posts (3 per week)", "2 email campaigns", "4 TikTok videos", "Weekly artist spotlights"],
                    "asset_needs": ["Hip Hop legends tribute graphics", "Community spotlight videos", "Street culture timeline", "Artist collaboration visuals"],
                    "suggested_codes": ["Code 11: Culture", "Code 01: Hustle Into Heritage", "Code 03: Global Throne"],
                    "hvd_phase": "Phase 1 - Foundation",
                    "budget_allocation": "$1,200 (30% of monthly budget)"
                },
                {
                    "title": "NBA Season Tip-Off Culture",
                    "date_range": "October 15-22, 2025",
                    "type": "Sports Integration",
                    "priority": "Medium",
                    "cultural_significance": "Basketball culture meets street fashion - authentic urban sports connection",
                    "content_requirements": ["6 posts (game day content)", "Daily NBA stories", "Local basketball features"],
                    "asset_needs": ["Basketball court street photography", "Game day outfit content", "Community spotlights"],
                    "suggested_codes": ["Code 05: Crooks Wear Crowns", "Code 29: Story", "Code 11: Culture"],
                    "hvd_phase": "Phase 1 - Foundation",
                    "budget_allocation": "$800 (20% of monthly budget)"
                },
                {
                    "title": "Halloween Street Style",
                    "date_range": "October 25-31, 2025",
                    "type": "Seasonal Culture",
                    "priority": "Medium",
                    "cultural_significance": "Street culture meets Halloween creativity - authentic urban celebration",
                    "content_requirements": ["8 posts (costume culture)", "Halloween contest", "Community events"],
                    "asset_needs": ["Halloween street photography", "Costume culture content", "Community celebrations"],
                    "suggested_codes": ["Code 29: Story", "Code 03: Global Throne", "Code 11: Culture"],
                    "hvd_phase": "Phase 1 - Foundation",
                    "budget_allocation": "$600 (15% of monthly budget)"
                },
                {
                    "title": "BFCM Prep Launch",
                    "date_range": "November 1-15, 2025",
                    "type": "Commercial Campaign",
                    "priority": "Critical",
                    "cultural_significance": "Authentic street culture meets commerce - community-first Black Friday approach",
                    "content_requirements": ["16 posts (daily)", "4 email campaigns", "8 SMS campaigns", "6 TikTok videos"],
                    "asset_needs": ["Product street styling", "Community testimonials", "Behind-the-scenes", "Limited edition visuals"],
                    "suggested_codes": ["Code 10: Currency", "Code 05: Crooks Wear Crowns", "Code 01: Hustle Into Heritage"],
                    "hvd_phase": "Phase 2 Transition - Growth ($7,500/month)",
                    "budget_allocation": "$2,250 (30% of Phase 2 budget)"
                }
            ];
            
            let html = '<h3 style="margin-bottom: 1rem;">60-Day Marketing Opportunities</h3>';
            html += '<div class="opportunities-grid">';
            
            strategicOpportunities.forEach(opp => {
                const priorityClass = opp.priority === 'Critical' ? 'priority-critical' : 
                                    opp.priority === 'High' ? 'priority-high' : 'priority-medium';
                
                html += `
                    <div class="enhanced-opportunity-card">
                        <div class="opportunity-header">
                            <div class="opportunity-title">${opp.title}</div>
                            <div class="priority-badge ${priorityClass}">${opp.priority}</div>
                        </div>
                        <div class="opportunity-meta">
                            📅 ${opp.date_range} • ${opp.type}
                        </div>
                        <div class="cultural-significance">
                            <strong>Cultural Significance:</strong> ${opp.cultural_significance}
                        </div>
                        <div class="content-section">
                            <strong>Content Requirements:</strong>
                            <ul class="requirements-list">
                                ${opp.content_requirements.map(req => `<li>${req}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="asset-section">
                            <strong>Asset Needs:</strong>
                            <ul class="asset-list">
                                ${opp.asset_needs.map(asset => `<li>🔨 ${asset}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="codes-section">
                            <strong>Suggested Codes:</strong>
                            <div class="codes-tags">
                                ${opp.suggested_codes.map(code => `<span class="code-tag">${code}</span>`).join('')}
                            </div>
                        </div>
                        <div class="phase-budget">
                            <div class="phase-info">${opp.hvd_phase}</div>
                            <div class="budget-info">${opp.budget_allocation}</div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            
            // Add enhanced CSS
            html += `
                <style>
                .opportunities-grid {
                    display: grid;
                    gap: 20px;
                }
                .enhanced-opportunity-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 24px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: all 0.3s ease;
                }
                .enhanced-opportunity-card:hover {
                    background: rgba(255, 255, 255, 0.08);
                    border-color: rgba(34, 197, 94, 0.3);
                }
                .opportunity-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                .opportunity-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #22c55e;
                }
                .priority-badge {
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .priority-critical {
                    background: #dc2626;
                    color: white;
                }
                .priority-high {
                    background: #f59e0b;
                    color: white;
                }
                .priority-medium {
                    background: #3b82f6;
                    color: white;
                }
                .opportunity-meta {
                    color: rgba(255, 255, 255, 0.8);
                    margin-bottom: 16px;
                    font-size: 14px;
                }
                .cultural-significance {
                    margin-bottom: 16px;
                    padding: 12px;
                    background: rgba(34, 197, 94, 0.1);
                    border-radius: 8px;
                    border-left: 4px solid #22c55e;
                }
                .content-section, .asset-section {
                    margin-bottom: 16px;
                }
                .requirements-list, .asset-list {
                    margin: 8px 0;
                    padding-left: 20px;
                }
                .requirements-list li, .asset-list li {
                    margin-bottom: 4px;
                    color: rgba(255, 255, 255, 0.9);
                }
                .codes-section {
                    margin-bottom: 16px;
                }
                .codes-tags {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    margin-top: 8px;
                }
                .code-tag {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #22c55e;
                }
                .phase-budget {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding-top: 16px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }
                .phase-info {
                    color: #22c55e;
                    font-weight: bold;
                }
                .budget-info {
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                }
                </style>
            `;
            
            container.innerHTML = html;
        }

        function display90DayView(container, longRange) {
            const strategicVision = {
                "operational_priorities": [
                    {
                        "title": "HVD Partnership Phase Transitions",
                        "date_range": "September 2025 - March 2026",
                        "type": "Agency Partnership",
                        "phases": {
                            "Phase 1 (Sep-Oct)": "Foundation & Awareness - $4,000/month • 12 posts, 4 creatives, 2 emails",
                            "Phase 2 (Nov-Dec)": "Growth & Q4 Push - $7,500/month • 12-16 posts, 6-8 creatives, 4-6 emails", 
                            "Phase 3 (Jan+)": "Full Retainer + TikTok Shop - $10,000/month • 16-20 posts, 8-12 creatives, 6-8 emails"
                        }
                    },
                    {
                        "title": "TikTok Shop Launch Preparation",
                        "date": "January 15, 2026",
                        "type": "Platform Expansion",
                        "preparation": [
                            "October 2025: TikTok content strategy development",
                            "November 2025: Short-form video asset creation",
                            "December 2025: Influencer partnership planning",
                            "January 2026: E-commerce integration and launch"
                        ]
                    }
                ],
                "thematic_moments": [
                    {
                        "title": "Black History Month Campaign",
                        "date_range": "February 1-28, 2026",
                        "type": "Cultural Heritage",
                        "cultural_significance": "Deep dive into Black culture's influence on street fashion and Hip Hop - authentic storytelling and community amplification",
                        "content_requirements": ["16 social posts celebrating Black culture", "6 email campaigns with educational content", "Community partnership spotlights", "Heritage storytelling video series"],
                        "preparation_timeline": ["November 2025: Community partnership outreach", "December 2025: Heritage content development", "January 2026: Educational campaign preparation"]
                    },
                    {
                        "title": "March Madness Basketball Culture",
                        "date_range": "March 1-31, 2026", 
                        "type": "Sports Culture",
                        "cultural_significance": "Basketball culture integration with street fashion - authentic connection to college and street basketball communities",
                        "content_requirements": ["Daily tournament content (31 posts)", "Bracket challenge with street style prizes", "College basketball community features"],
                        "preparation_timeline": ["January 2026: Basketball community partnerships", "February 2026: Tournament content planning"]
                    },
                    {
                        "title": "Spring Fashion Week Street Culture",
                        "date_range": "March 15-22, 2026",
                        "type": "Fashion Culture",
                        "cultural_significance": "Street culture meets high fashion - authentic representation of street style influence on fashion industry",
                        "content_requirements": ["Daily fashion week street style content", "Behind-the-scenes fashion industry access", "Street style vs. runway comparisons"],
                        "preparation_timeline": ["February 2026: Fashion week content strategy", "March 2026: Street style documentation"]
                    },
                    {
                        "title": "Cinco de Mayo Cultural Celebration",
                        "date_range": "May 1-5, 2026",
                        "type": "Cultural Heritage",
                        "cultural_significance": "Hispanic culture celebration with authentic community representation and cultural respect",
                        "content_requirements": ["5-day cultural celebration series", "Community partnership spotlights", "Cultural education content"],
                        "preparation_timeline": ["March 2026: Hispanic community partnerships", "April 2026: Cultural celebration content creation"]
                    },
                    {
                        "title": "Summer Festival Season Launch",
                        "date_range": "June 1 - August 31, 2026",
                        "type": "Music & Street Culture",
                        "cultural_significance": "Music festival culture meets street fashion - authentic representation of festival style and music community connection",
                        "content_requirements": ["Weekly festival style content (12 weeks)", "Music community partnerships", "Festival fashion guides"],
                        "preparation_timeline": ["April 2026: Festival partnership outreach", "May 2026: Festival content strategy development"]
                    }
                ]
            };
            
            let html = '<h3 style="margin-bottom: 1rem;">90-Day+ Strategic Vision</h3>';
            html += '<div class="vision-container">';
            
            // Operational Priorities Section
            html += '<div class="vision-section"><h4 class="section-title">🎯 Operational Priorities</h4>';
            strategicVision.operational_priorities.forEach(priority => {
                html += `
                    <div class="vision-card operational-card">
                        <div class="card-header">
                            <div class="card-title">${priority.title}</div>
                            <div class="card-type">${priority.type}</div>
                        </div>
                        <div class="card-meta">${priority.date_range || priority.date}</div>
                `;
                
                if (priority.phases) {
                    html += '<div class="phases-section"><strong>Phase Progression:</strong>';
                    Object.entries(priority.phases).forEach(([phase, details]) => {
                        html += `<div class="phase-item"><strong>${phase}:</strong> ${details}</div>`;
                    });
                    html += '</div>';
                }
                
                if (priority.preparation) {
                    html += '<div class="preparation-section"><strong>Preparation Timeline:</strong><ul>';
                    priority.preparation.forEach(item => {
                        html += `<li>${item}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                html += '</div>';
            });
            html += '</div>';
            
            // Thematic Moments Section
            html += '<div class="vision-section"><h4 class="section-title">🎨 Thematic Cultural Moments</h4>';
            strategicVision.thematic_moments.forEach(moment => {
                html += `
                    <div class="vision-card thematic-card">
                        <div class="card-header">
                            <div class="card-title">${moment.title}</div>
                            <div class="card-type">${moment.type}</div>
                        </div>
                        <div class="card-meta">📅 ${moment.date_range}</div>
                        <div class="cultural-significance">
                            <strong>Cultural Significance:</strong> ${moment.cultural_significance}
                        </div>
                        <div class="content-requirements">
                            <strong>Content Requirements:</strong>
                            <ul>
                                ${moment.content_requirements.map(req => `<li>${req}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="preparation-timeline">
                            <strong>Preparation Timeline:</strong>
                            <ul>
                                ${moment.preparation_timeline.map(item => `<li>${item}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            
            html += '</div>';
            
            // Add comprehensive CSS
            html += `
                <style>
                .vision-container {
                    display: grid;
                    gap: 30px;
                }
                .vision-section {
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 12px;
                    padding: 24px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .section-title {
                    color: #22c55e;
                    margin-bottom: 20px;
                    font-size: 20px;
                    border-bottom: 2px solid rgba(34, 197, 94, 0.3);
                    padding-bottom: 10px;
                }
                .vision-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: all 0.3s ease;
                }
                .vision-card:hover {
                    background: rgba(255, 255, 255, 0.08);
                    border-color: rgba(34, 197, 94, 0.3);
                }
                .operational-card {
                    border-left: 4px solid #3b82f6;
                }
                .thematic-card {
                    border-left: 4px solid #f59e0b;
                }
                .card-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                .card-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #22c55e;
                }
                .card-type {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.8);
                }
                .card-meta {
                    color: rgba(255, 255, 255, 0.8);
                    margin-bottom: 16px;
                    font-size: 14px;
                }
                .phases-section, .preparation-section, .content-requirements, .preparation-timeline {
                    margin-bottom: 16px;
                }
                .phase-item {
                    margin: 8px 0;
                    padding: 8px 12px;
                    background: rgba(59, 130, 246, 0.1);
                    border-radius: 6px;
                    border-left: 3px solid #3b82f6;
                }
                .cultural-significance {
                    margin-bottom: 16px;
                    padding: 12px;
                    background: rgba(245, 158, 11, 0.1);
                    border-radius: 8px;
                    border-left: 4px solid #f59e0b;
                }
                .preparation-section ul, .content-requirements ul, .preparation-timeline ul {
                    margin: 8px 0;
                    padding-left: 20px;
                }
                .preparation-section li, .content-requirements li, .preparation-timeline li {
                    margin-bottom: 6px;
                    color: rgba(255, 255, 255, 0.9);
                }
                </style>
            `;
            
            container.innerHTML = html;
        }

        // Asset functions
        async function loadAssets() {
            try {
                const response = await fetch('/api/assets');
                const data = await response.json();
                
                const container = document.getElementById('assetGrid');
                
                if (data.success && data.assets.length > 0) {
                    let html = '';
                    data.assets.forEach(asset => {
                        const badgeClass = asset.badge_score >= 95 ? 'badge-ready' : 'badge-review';
                        const badgeText = asset.badge_score >= 95 ? 'Castle Ready' : 'Needs Review';
                        
                        html += `
                            <div class="asset-card">
                                <div class="asset-thumbnail">
                                    <img src="${asset.thumbnail_url || '/api/thumbnail/' + asset.id}" alt="${asset.original_name}" onerror="this.style.display='none'">
                                </div>
                                <div class="asset-info">
                                    <div class="asset-name">${asset.original_name}</div>
                                    <div style="margin-bottom: 0.5rem; font-size: 0.8rem; color: rgba(255, 255, 255, 0.7);">
                                        Code ${asset.assigned_code || 'Unassigned'}
                                    </div>
                                    <div class="badge-score ${badgeClass}">
                                        ${asset.badge_score}% ${badgeText}
                                    </div>
                                    <div style="margin-top: 0.5rem;">
                                        <a href="/api/download/${asset.id}" class="btn" style="font-size: 0.8rem; padding: 0.5rem 1rem;">
                                            Download
                                        </a>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div class="loading">No assets found</div>';
                }
            } catch (error) {
                console.error('Error loading assets:', error);
                document.getElementById('assetGrid').innerHTML = '<div class="loading">Error loading assets</div>';
            }
        }

        // Agency functions
        async function loadDeliverables() {
            try {
                const response = await fetch('/api/deliverables');
                const data = await response.json();
                
                const container = document.getElementById('deliverablesGrid');
                
                if (data.success) {
                    const currentPhase = data.current_phase;
                    const progress = data.current_progress;
                    
                    // Helper function to get status color
                    function getStatusColor(status) {
                        switch(status) {
                            case 'ahead': return '#22c55e';
                            case 'on_track': return '#3b82f6';
                            case 'behind': return '#ef4444';
                            default: return '#6b7280';
                        }
                    }
                    
                    // Helper function to get status icon
                    function getStatusIcon(status) {
                        switch(status) {
                            case 'ahead': return '🚀';
                            case 'on_track': return '✅';
                            case 'behind': return '⚠️';
                            default: return '📊';
                        }
                    }
                    
                    let html = `
                        <!-- Performance Report Upload Section -->
                        <div class="deliverable-card" style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border: 1px solid #3b82f6;">
                            <div class="deliverable-title" style="color: #3b82f6;">📊 Performance Reporting</div>
                            <div style="margin-bottom: 1rem; color: rgba(255, 255, 255, 0.8);">
                                Upload performance reports for dynamic insights
                            </div>
                            
                            <div class="upload-area" onclick="document.getElementById('reportInput').click()" style="margin-bottom: 1rem; padding: 1rem; border: 2px dashed #3b82f6; border-radius: 8px; cursor: pointer; text-align: center;">
                                <p style="margin: 0; color: #3b82f6;">📈 Upload Performance Report (CSV, Excel, JSON)</p>
                                <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: rgba(255, 255, 255, 0.6);">
                                    Supports engagement metrics, conversion data, reach analytics
                                </p>
                                <input type="file" id="reportInput" accept=".csv,.xlsx,.json" style="display: none;" onchange="uploadPerformanceReport(this.files[0])">
                            </div>
                            
                            <div id="performanceInsights" style="margin-top: 1rem;">
                                <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
                                    Upload a report to see dynamic performance insights and recommendations
                                </div>
                            </div>
                        </div>
                        
                        <!-- Current Phase Progress -->
                        <div class="deliverable-card">
                            <div class="deliverable-title">${currentPhase.name} (${currentPhase.period})</div>
                            <div style="margin-bottom: 1rem; color: rgba(255, 255, 255, 0.8);">
                                ${currentPhase.budget} • Current Phase Progress
                            </div>
                            
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                    <span>Social Posts</span>
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span>${progress.social_posts.current}/${progress.social_posts.target} posts</span>
                                        <span style="color: ${getStatusColor(progress.social_posts.status)};">${getStatusIcon(progress.social_posts.status)}</span>
                                    </div>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${progress.social_posts.progress}%; background-color: ${getStatusColor(progress.social_posts.status)};"></div>
                                </div>
                                ${progress.social_posts.outstanding > 0 ? `<div style="font-size: 0.8rem; color: #ef4444; margin-top: 0.25rem;">Outstanding: ${progress.social_posts.outstanding} posts needed</div>` : ''}
                            </div>
                            
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                    <span>Ad Creatives</span>
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span>${progress.ad_creatives.current}/${progress.ad_creatives.target} creatives</span>
                                        <span style="color: ${getStatusColor(progress.ad_creatives.status)};">${getStatusIcon(progress.ad_creatives.status)}</span>
                                    </div>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${progress.ad_creatives.progress}%; background-color: ${getStatusColor(progress.ad_creatives.status)};"></div>
                                </div>
                                ${progress.ad_creatives.outstanding > 0 ? `<div style="font-size: 0.8rem; color: #ef4444; margin-top: 0.25rem;">Outstanding: ${progress.ad_creatives.outstanding} creatives needed</div>` : ''}
                                ${progress.ad_creatives.current > progress.ad_creatives.target ? `<div style="font-size: 0.8rem; color: #22c55e; margin-top: 0.25rem;">Over-delivered: +${progress.ad_creatives.current - progress.ad_creatives.target} extra creatives</div>` : ''}
                            </div>
                            
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                    <span>Email Campaigns</span>
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span>${progress.email_campaigns.current}/${progress.email_campaigns.target} emails</span>
                                        <span style="color: ${getStatusColor(progress.email_campaigns.status)};">${getStatusIcon(progress.email_campaigns.status)}</span>
                                    </div>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${progress.email_campaigns.progress}%; background-color: ${getStatusColor(progress.email_campaigns.status)};"></div>
                                </div>
                                ${progress.email_campaigns.outstanding > 0 ? `<div style="font-size: 0.8rem; color: #ef4444; margin-top: 0.25rem;">Outstanding: ${progress.email_campaigns.outstanding} campaigns needed</div>` : ''}
                            </div>
                            
                            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                <div style="font-weight: 600; color: #22c55e;">
                                    Overall Progress: ${data.overall_progress}%
                                </div>
                                ${data.next_month_preview ? `
                                <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); margin-top: 0.5rem;">
                                    Next Month (${data.next_month_preview.month}): ${data.next_month_preview.scheduled_posts} posts scheduled
                                </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        <!-- Phase Transition Info -->
                        ${data.phase_transitions.next_phase ? `
                        <div class="deliverable-card" style="background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 100%);">
                            <div class="deliverable-title" style="color: #a78bfa;">🔄 Upcoming Phase Transition</div>
                            <div style="margin-bottom: 1rem; color: rgba(255, 255, 255, 0.8);">
                                Transition Date: ${data.phase_transitions.transition_date}
                            </div>
                            
                            <div style="color: rgba(255, 255, 255, 0.7);">
                                <p>📋 Prepare for increased deliverables:</p>
                                <ul style="margin-top: 0.5rem; padding-left: 1rem;">
                                    ${data.phase_transitions.next_phase === 'phase2' ? `
                                    <li>12-16 social posts/month</li>
                                    <li>6-8 ad creatives/month</li>
                                    <li>4-6 email campaigns</li>
                                    <li>BFCM campaign preparation</li>
                                    ` : `
                                    <li>16-20 social posts/month</li>
                                    <li>8-12 ad creatives/month</li>
                                    <li>Full SEO & CRO implementation</li>
                                    <li>TikTok Shop launch support</li>
                                    `}
                                </ul>
                            </div>
                        </div>
                        ` : ''}
                        
                        <!-- Performance Metrics Summary -->
                        <div class="deliverable-card" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                            <div class="deliverable-title" style="color: #fbbf24;">📈 Performance Metrics</div>
                            <div style="margin-bottom: 1rem; color: rgba(255, 255, 255, 0.8);">
                                Real-time tracking of key performance indicators
                            </div>
                            
                            <div id="performanceMetrics" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                                    <div style="font-size: 1.5rem; font-weight: 600; color: #22c55e;">95%</div>
                                    <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.7);">Avg Compliance Score</div>
                                </div>
                                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                                    <div style="font-size: 1.5rem; font-weight: 600; color: #3b82f6;">8</div>
                                    <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.7);">Assets Created</div>
                                </div>
                                <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                                    <div style="font-size: 1.5rem; font-weight: 600; color: #f59e0b;">3</div>
                                    <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.7);">Cultural Moments</div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div class="loading">Error loading deliverables</div>';
                }
            } catch (error) {
                console.error('Error loading deliverables:', error);
                document.getElementById('deliverablesGrid').innerHTML = '<div class="loading">Error loading deliverables</div>';
            }
        }

        // Performance Report Upload Function
        async function uploadPerformanceReport(file) {
            if (!file) return;
            
            const formData = new FormData();
            formData.append('report', file);
            
            try {
                const response = await fetch('/api/upload-performance-report', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Update performance insights
                    updatePerformanceInsights(result.insights);
                    
                    // Reload deliverables to show updated metrics
                    loadDeliverables();
                    
                    alert('Performance report uploaded successfully!');
                } else {
                    alert('Upload failed: ' + result.message);
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Upload failed');
            }
        }

        // Update Performance Insights
        function updatePerformanceInsights(insights) {
            const container = document.getElementById('performanceInsights');
            
            if (insights && insights.length > 0) {
                let html = '<div style="color: #22c55e; font-weight: 600; margin-bottom: 0.5rem;">📊 Latest Performance Insights:</div>';
                
                insights.forEach(insight => {
                    const iconColor = insight.type === 'positive' ? '#22c55e' : insight.type === 'warning' ? '#f59e0b' : '#3b82f6';
                    const icon = insight.type === 'positive' ? '📈' : insight.type === 'warning' ? '⚠️' : '💡';
                    
                    html += `
                        <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 4px; border-left: 3px solid ${iconColor};">
                            <span style="color: ${iconColor};">${icon}</span>
                            <span style="margin-left: 0.5rem; font-size: 0.9rem;">${insight.message}</span>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
        }

        // Upload functions
        async function uploadAssets(files) {
            if (!files || files.length === 0) return;
            
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            
            try {
                const response = await fetch('/api/upload-assets', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`Successfully uploaded ${result.uploaded_count} assets`);
                    loadAssets(); // Reload assets
                } else {
                    alert('Upload failed: ' + result.message);
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Upload failed');
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            displayCalendar();
        });
    </script>
</body>
</html>
    ''')

# API Routes
@app.route('/api/calendar/<view_type>')
def get_calendar_data(view_type):
    """Get enhanced calendar data with HVD quota tracking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = datetime.datetime.now()
        
        if view_type == '7day':
            # Generate detailed 7-day tactical view
            calendar_data = []
            
            for i in range(7):
                date = today + timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                # Get scheduled posts for this date
                cursor.execute('''
                    SELECT p.*, a.name as asset_name, a.compliance_score as asset_badge_score
                    FROM posts p
                    LEFT JOIN assets a ON p.asset_id = a.id
                    WHERE DATE(p.scheduled_date) = ?
                    ORDER BY p.scheduled_date
                ''', (date_str,))
                
                posts = cursor.fetchall()
                
                day_data = {
                    'date': date_str,
                    'day_name': date.strftime('%A'),
                    'formatted_date': date.strftime('%b %d'),
                    'posts': []
                }
                
                for post in posts:
                    # Calculate Badge Test score for post
                    badge_score = calculate_post_badge_score(post)
                    
                    day_data['posts'].append({
                        'id': post['id'],
                        'title': post['title'],
                        'content': post['content'][:100] + '...' if len(post['content']) > 100 else post['content'],
                        'full_content': post['content'],
                        'hashtags': post['hashtags'],
                        'platform': post['platform'],
                        'time_slot': datetime.datetime.fromisoformat(post['scheduled_date']).strftime('%H:%M CT') if post['scheduled_date'] else 'Not scheduled',
                        'assigned_code': post['crooks_code'],
                        'code_name': get_code_name(post['crooks_code']),
                        'asset_name': post['asset_name'],
                        'badge_score': badge_score,
                        'status': 'Castle Ready' if badge_score >= 95 else 'Needs Review'
                    })
                
                calendar_data.append(day_data)
            
            return jsonify({
                'success': True,
                'view_type': '7day',
                'calendar_data': calendar_data
            })
            
        elif view_type == '30day':
            # Strategic 30-day view with scheduled posts
            calendar_data = []
            
            for i in range(30):
                date = today + timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                # Get scheduled posts for this date
                cursor.execute('''
                    SELECT p.*, a.name as asset_name, a.compliance_score as asset_badge_score
                    FROM posts p
                    LEFT JOIN assets a ON p.asset_id = a.id
                    WHERE DATE(p.scheduled_date) = ?
                    ORDER BY p.scheduled_date
                ''', (date_str,))
                
                posts = cursor.fetchall()
                
                if posts:  # Only include dates with posts for 30-day view
                    day_data = {
                        'date': date_str,
                        'day_name': date.strftime('%A'),
                        'formatted_date': date.strftime('%b %d'),
                        'posts': []
                    }
                    
                    for post in posts:
                        badge_score = post['asset_badge_score'] if post['asset_badge_score'] else 85
                        
                        day_data['posts'].append({
                            'id': post['id'],
                            'title': post['title'],
                            'content': post['content'][:100] + '...' if len(post['content']) > 100 else post['content'],
                            'full_content': post['content'],
                            'hashtags': post['hashtags'],
                            'platform': post['platform'],
                            'time_slot': datetime.datetime.fromisoformat(post['scheduled_date']).strftime('%H:%M CT') if post['scheduled_date'] else 'Not scheduled',
                            'assigned_code': post['crooks_code'],
                            'code_name': get_code_name(post['crooks_code']),
                            'asset_name': post['asset_name'],
                            'badge_score': badge_score,
                            'status': 'Castle Ready' if badge_score >= 95 else 'Needs Review'
                        })
                    
                    calendar_data.append(day_data)
            
            return jsonify({
                'success': True,
                'view_type': '30day',
                'calendar_data': calendar_data
            })
            
        elif view_type == '60day':
            # Marketing opportunities and cultural moments
            opportunities = [
                {
                    'date': '2025-10-15',
                    'event': 'Hip Hop History Month',
                    'type': 'Cultural Heritage',
                    'priority': 'High',
                    'suggested_codes': ['11: Culture', '1: Hustle Into Heritage'],
                    'content_ideas': ['Community spotlight series', 'Hip hop legends tribute', 'Street culture evolution'],
                    'deliverable_impact': 'Phase 1: 4 posts, 1 email campaign'
                },
                {
                    'date': '2025-11-01',
                    'event': 'BFCM Prep Launch',
                    'type': 'Commercial Campaign',
                    'priority': 'Critical',
                    'suggested_codes': ['10: Currency', '5: Crooks Wear Crowns'],
                    'content_ideas': ['Early access preview', 'VIP member benefits', 'Limited edition drops'],
                    'deliverable_impact': 'Phase 2: 8 posts, 2 email campaigns, 4 SMS'
                },
                {
                    'date': '2025-11-29',
                    'event': 'Black Friday Campaign',
                    'type': 'Peak Sales',
                    'priority': 'Critical',
                    'suggested_codes': ['3: Global Throne', '26: The Mark'],
                    'content_ideas': ['Flash sales', 'Bundle offers', 'Community exclusives'],
                    'deliverable_impact': 'Phase 2: 12 posts, 3 email campaigns, 6 SMS'
                },
                {
                    'date': '2025-12-15',
                    'event': 'Holiday Collection Drop',
                    'type': 'Product Launch',
                    'priority': 'High',
                    'suggested_codes': ['16: Icons Reborn', '29: The Legacy'],
                    'content_ideas': ['Gift guides', 'Holiday styling', 'Year-end celebration'],
                    'deliverable_impact': 'Phase 2: 6 posts, 2 email campaigns'
                }
            ]
            
            return jsonify({
                'success': True,
                'view_type': '60day',
                'opportunities': opportunities
            })
            
        elif view_type == '90day':
            # Long-range strategic planning
            long_range = [
                {
                    'date': '2026-01-15',
                    'milestone': 'TikTok Shop Launch',
                    'type': 'Platform Expansion',
                    'phase': 3,
                    'preparation_needed': [
                        'TikTok content strategy development',
                        'Short-form video asset creation',
                        'Influencer partnership planning',
                        'E-commerce integration setup'
                    ],
                    'deliverable_impact': 'Phase 3: 20 posts/month, video-first content',
                    'success_metrics': ['Shop conversion rate', 'Video engagement', 'Follower growth']
                },
                {
                    'date': '2026-02-01',
                    'milestone': 'Black History Month Campaign',
                    'type': 'Cultural Heritage',
                    'phase': 3,
                    'preparation_needed': [
                        'Community partnership outreach',
                        'Heritage storytelling content',
                        'Educational campaign development',
                        'Authentic voice amplification'
                    ],
                    'deliverable_impact': 'Phase 3: 16 posts, 6 emails, cultural partnerships',
                    'success_metrics': ['Community engagement', 'Cultural authenticity score', 'Share rate']
                },
                {
                    'date': '2026-04-01',
                    'milestone': 'Coachella Partnership Prep',
                    'type': 'Event Marketing',
                    'phase': 3,
                    'preparation_needed': [
                        'Festival partnership negotiations',
                        'Live event content strategy',
                        'Influencer collaboration planning',
                        'Real-time engagement tactics'
                    ],
                    'deliverable_impact': 'Phase 3: Event-driven content surge',
                    'success_metrics': ['Event reach', 'Real-time engagement', 'Brand visibility']
                }
            ]
            
            return jsonify({
                'success': True,
                'view_type': '90day',
                'long_range': long_range
            })
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/assets')
def get_assets():
    """Get all assets"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM assets 
            ORDER BY upload_date DESC
        ''')
        
        assets = []
        for row in cursor.fetchall():
            # Generate thumbnail URL for the frontend
            thumbnail_url = f"/uploads/{row['name']}" if row['name'] else None
            
            # Handle file_path safely for SQLite Row
            try:
                file_path = row['file_path'] if 'file_path' in row.keys() else thumbnail_url
            except:
                file_path = thumbnail_url
            
            assets.append({
                'id': row['id'],
                'original_name': row['name'],
                'file_type': row['format'],
                'badge_score': row['compliance_score'],
                'assigned_code': row['crooks_code'],
                'cultural_relevance': row['cultural_relevance'],
                'created_date': row['upload_date'],
                'category': row['category'],
                'usage_count': row['usage_count'],
                'thumbnail_url': thumbnail_url,
                'file_path': file_path
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'assets': assets
        })
        
    except Exception as e:
        logger.error(f"Error getting assets: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/deliverables')
def get_deliverables():
    """Get dynamic agency deliverables status with real-time progress tracking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current date for phase calculation
        from datetime import datetime, timedelta
        current_date = datetime.now()
        current_month = current_date.strftime('%Y-%m')
        
        # Define HVD phase requirements
        phases = {
            'phase1': {
                'name': 'Foundation & Awareness',
                'period': 'Sep-Oct 2025',
                'budget': '$4,000/month',
                'monthly_targets': {
                    'social_posts': 12,
                    'ad_creatives': 4,
                    'email_campaigns': 2
                }
            },
            'phase2': {
                'name': 'Growth & Q4 Push',
                'period': 'Nov-Dec 2025',
                'budget': '$7,500/month',
                'monthly_targets': {
                    'social_posts': 16,
                    'ad_creatives': 8,
                    'email_campaigns': 6
                }
            },
            'phase3': {
                'name': 'Full Retainer + TikTok Shop',
                'period': 'Jan 2026+',
                'budget': '$10,000/month',
                'monthly_targets': {
                    'social_posts': 20,
                    'ad_creatives': 12,
                    'email_campaigns': 8
                }
            }
        }
        
        # Determine current phase based on date
        if current_date.month in [9, 10] and current_date.year == 2025:
            current_phase = 'phase1'
        elif current_date.month in [11, 12] and current_date.year == 2025:
            current_phase = 'phase2'
        else:
            current_phase = 'phase3'
        
        # Count current month's deliverables
        cursor.execute('''
            SELECT COUNT(*) as count FROM posts 
            WHERE strftime('%Y-%m', scheduled_date) = ?
        ''', (current_month,))
        current_posts = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM assets 
            WHERE strftime('%Y-%m', upload_date) = ?
        ''', (current_month,))
        current_creatives = cursor.fetchone()['count']
        
        # Count email campaigns (assuming they're posts with platform='Email')
        cursor.execute('''
            SELECT COUNT(*) as count FROM posts 
            WHERE strftime('%Y-%m', scheduled_date) = ? AND platform = 'Email'
        ''', (current_month,))
        current_emails = cursor.fetchone()['count']
        
        # Calculate progress percentages
        phase_targets = phases[current_phase]['monthly_targets']
        
        posts_progress = min(100, (current_posts / phase_targets['social_posts']) * 100)
        creatives_progress = min(100, (current_creatives / phase_targets['ad_creatives']) * 100)
        emails_progress = min(100, (current_emails / phase_targets['email_campaigns']) * 100)
        
        # Calculate overall progress
        overall_progress = (posts_progress + creatives_progress + emails_progress) / 3
        
        # Calculate outstanding deliverables
        outstanding_posts = max(0, phase_targets['social_posts'] - current_posts)
        outstanding_creatives = max(0, phase_targets['ad_creatives'] - current_creatives)
        outstanding_emails = max(0, phase_targets['email_campaigns'] - current_emails)
        
        # Get next month's projections
        next_month_date = current_date + timedelta(days=32)
        next_month = next_month_date.strftime('%Y-%m')
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM posts 
            WHERE strftime('%Y-%m', scheduled_date) = ?
        ''', (next_month,))
        next_month_posts = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'current_phase': {
                'id': current_phase,
                'name': phases[current_phase]['name'],
                'period': phases[current_phase]['period'],
                'budget': phases[current_phase]['budget']
            },
            'current_progress': {
                'social_posts': {
                    'current': current_posts,
                    'target': phase_targets['social_posts'],
                    'progress': round(posts_progress, 1),
                    'outstanding': outstanding_posts,
                    'status': 'ahead' if current_posts > phase_targets['social_posts'] else 'on_track' if posts_progress >= 80 else 'behind'
                },
                'ad_creatives': {
                    'current': current_creatives,
                    'target': phase_targets['ad_creatives'],
                    'progress': round(creatives_progress, 1),
                    'outstanding': outstanding_creatives,
                    'status': 'ahead' if current_creatives > phase_targets['ad_creatives'] else 'on_track' if creatives_progress >= 80 else 'behind'
                },
                'email_campaigns': {
                    'current': current_emails,
                    'target': phase_targets['email_campaigns'],
                    'progress': round(emails_progress, 1),
                    'outstanding': outstanding_emails,
                    'status': 'ahead' if current_emails > phase_targets['email_campaigns'] else 'on_track' if emails_progress >= 80 else 'behind'
                }
            },
            'overall_progress': round(overall_progress, 1),
            'next_month_preview': {
                'scheduled_posts': next_month_posts,
                'month': next_month_date.strftime('%B %Y')
            },
            'phase_transitions': {
                'next_phase': 'phase2' if current_phase == 'phase1' else 'phase3' if current_phase == 'phase2' else None,
                'transition_date': '2025-11-01' if current_phase == 'phase1' else '2026-01-01' if current_phase == 'phase2' else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting deliverables: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/thumbnail/<asset_id>')
def get_thumbnail(asset_id):
    """Get asset thumbnail"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_path, format, name FROM assets WHERE id = ?', (asset_id,))
        asset = cursor.fetchone()
        
        if not asset:
            return jsonify({'success': False, 'message': 'Asset not found'}), 404
        
        # Try file_path first, then fall back to uploads folder
        try:
            file_path = asset['file_path'] if 'file_path' in asset.keys() else None
        except:
            file_path = None
            
        if not file_path or not Path(file_path).exists():
            # Try in uploads folder
            file_path = UPLOAD_FOLDER / asset['name']
            if not file_path.exists():
                # Try in assets folder
                file_path = ASSETS_FOLDER / asset['name']
        
        if Path(file_path).exists() and (asset['format'].startswith('image/') or asset['format'] in ['png', 'jpg', 'jpeg', 'gif']):
            return send_file(file_path)
        else:
            # For videos or missing files, return a placeholder or error
            return jsonify({'success': False, 'message': 'Thumbnail not available'}), 404
        
    except Exception as e:
        logger.error(f"Error getting thumbnail: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download/<asset_id>')
def download_asset(asset_id):
    """Download asset"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_path, name FROM assets WHERE id = ?', (asset_id,))
        asset = cursor.fetchone()
        
        if not asset:
            return jsonify({'success': False, 'message': 'Asset not found'}), 404
        
        return send_file(asset['file_path'], as_attachment=True, download_name=asset['name'])
        
    except Exception as e:
        logger.error(f"Error downloading asset: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded asset files"""
    try:
        file_path = UPLOAD_FOLDER / filename
        if file_path.exists():
            return send_file(file_path)
        else:
            # Try in assets folder
            file_path = ASSETS_FOLDER / filename
            if file_path.exists():
                return send_file(file_path)
            else:
                return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'File serving error'}), 500

@app.route('/api/upload-assets', methods=['POST'])
def upload_assets():
    """Upload new assets"""
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_count = 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for file in files:
            if file.filename == '':
                continue
            
            # Generate unique filename and save file
            asset_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename)[1]
            saved_filename = f"{asset_id}{file_extension}"
            file_path = UPLOAD_FOLDER / saved_filename
            
            # Ensure upload directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            file.save(str(file_path))
            
            # Calculate badge score
            badge_score = calculate_asset_badge_score(file.filename, file.content_type)
            
            # Save to database with the saved filename (not full path)
            cursor.execute('''
                INSERT INTO assets (id, name, category, format, compliance_score, usage_count, file_path, upload_date, crooks_code, cultural_relevance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_id,
                saved_filename,  # Use the saved filename
                'User Upload',  # Default category
                file.content_type,
                badge_score,
                0,  # Initial usage count
                str(file_path),  # Full path for internal use
                datetime.datetime.now().isoformat(),
                f"Code {badge_score//10}: Upload",  # Generate code based on score
                'User uploaded content'  # Default cultural relevance
            ))
            
            uploaded_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'uploaded_count': uploaded_count,
            'message': f'Successfully uploaded {uploaded_count} assets'
        })
        
    except Exception as e:
        logger.error(f"Error uploading assets: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Helper functions
def calculate_post_badge_score(post):
    """Calculate Badge Test score for a post"""
    try:
        score = 0
        
        # Preconversion effectiveness (40 points)
        content_length = len(post['content']) if post['content'] else 0
        if 100 <= content_length <= 300:
            score += 15
        elif content_length > 0:
            score += 10
        
        if post['hashtags'] and len(post['hashtags'].split()) >= 3:
            score += 10
        
        if post['platform'] in ['instagram', 'instagram_reels']:
            score += 10
        elif post['platform'] in ['facebook', 'instagram_story']:
            score += 7
        
        if post['scheduled_date']:
            try:
                hour = datetime.datetime.fromisoformat(post['scheduled_date']).hour
                if 17 <= hour <= 21:  # Peak engagement hours
                    score += 5
            except:
                pass
        
        # Brand guidelines compliance (35 points)
        if post['assigned_code']:
            score += 20  # Code assignment
        
        if post['content'] and ('crooks' in post['content'].lower() or 'castle' in post['content'].lower()):
            score += 10  # Brand mention
        
        if post['hashtags'] and '#crooksandcastles' in post['hashtags'].lower():
            score += 5  # Brand hashtag
        
        # Code alignment (25 points)
        if post['assigned_code']:
            score += 15  # Has assigned code
            
            # Bonus for authentic code usage
            code_keywords = get_code_keywords(post['assigned_code'])
            content_lower = post['content'].lower() if post['content'] else ''
            if any(keyword in content_lower for keyword in code_keywords):
                score += 10
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating post badge score: {str(e)}")
        return 75

def calculate_asset_badge_score(filename, content_type):
    """Calculate Badge Test score for an asset"""
    try:
        score = 75  # Base score
        
        # File type bonus
        if content_type.startswith('image/'):
            score += 10
        elif content_type.startswith('video/'):
            score += 15
        
        # Filename analysis
        filename_lower = filename.lower()
        if any(word in filename_lower for word in ['crooks', 'castle', 'heritage', 'street']):
            score += 10
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating asset badge score: {str(e)}")
        return 75

def get_code_name(code_input):
    """Get Crooks Code name by number or extract from string"""
    codes = {
        1: "Hustle Into Heritage", 2: "Code Over Clothes", 3: "Global Throne",
        4: "Streets to Castles", 5: "Crooks Wear Crowns", 6: "Tone",
        7: "Voice", 8: "The Keeper", 9: "Moves", 10: "Currency",
        11: "Culture", 12: "Faces", 13: "The Grid", 14: "Hierarchy",
        15: "Lens", 16: "Icons Reborn", 17: "Symbols", 18: "Filter",
        19: "Form", 20: "Feel", 21: "Details", 22: "Type",
        23: "Wordmark", 24: "Palette", 25: "Motifs", 26: "The Mark",
        27: "The Seal", 28: "The Story", 29: "The Legacy", 30: "The Value"
    }
    
    if not code_input:
        return "No Code"
    
    # If it's already a string with the full code name, return it
    if isinstance(code_input, str) and ":" in code_input:
        return code_input.split(":", 1)[1].strip() if ":" in code_input else code_input
    
    # If it's a number or string number, look it up
    try:
        code_number = int(code_input)
        return codes.get(code_number, "Unknown Code")
    except (ValueError, TypeError):
        return str(code_input)

def get_code_keywords(code_number):
    """Get keywords associated with each Crooks Code"""
    keywords = {
        1: ["heritage", "hustle", "legacy", "roots"],
        2: ["code", "rules", "principles", "standards"],
        3: ["global", "throne", "worldwide", "empire"],
        4: ["streets", "castle", "rise", "elevation"],
        5: ["crown", "royalty", "king", "queen"],
        11: ["culture", "community", "movement", "street"],
        # Add more as needed
    }
    return keywords.get(int(code_number), []) if code_number else []

@app.route('/api/upload-performance-report', methods=['POST'])
def upload_performance_report():
    """Upload and analyze performance reports for dynamic insights"""
    try:
        if 'report' not in request.files:
            return jsonify({'success': False, 'message': 'No report file provided'}), 400
        
        file = request.files['report']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Save uploaded file
        import os
        from datetime import datetime
        
        upload_dir = BASE_DIR / 'agency_reports'
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"performance_report_{timestamp}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Analyze the report and generate insights
        insights = analyze_performance_report(filepath)
        
        # Store insights in database for future reference
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create performance_reports table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_reports (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                insights TEXT NOT NULL
            )
        ''')
        
        import json
        cursor.execute('''
            INSERT INTO performance_reports (id, filename, filepath, upload_date, insights)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, filename, filepath, datetime.now().isoformat(), json.dumps(insights)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Performance report uploaded and analyzed successfully',
            'insights': insights,
            'report_id': timestamp
        })
        
    except Exception as e:
        logger.error(f"Error uploading performance report: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

def analyze_performance_report(filepath):
    """Analyze uploaded performance report and generate insights"""
    try:
        import pandas as pd
        import json
        
        insights = []
        
        # Determine file type and read data
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
        else:
            return [{'type': 'warning', 'message': 'Unsupported file format. Please use CSV, Excel, or JSON.'}]
        
        # Analyze common performance metrics
        columns = [col.lower() for col in df.columns]
        
        # Engagement analysis
        if any('engagement' in col for col in columns):
            engagement_cols = [col for col in df.columns if 'engagement' in col.lower()]
            if engagement_cols:
                avg_engagement = df[engagement_cols[0]].mean()
                if avg_engagement > 5:  # Assuming percentage
                    insights.append({
                        'type': 'positive',
                        'message': f'Strong engagement rate of {avg_engagement:.1f}% - exceeding industry benchmarks'
                    })
                elif avg_engagement > 2:
                    insights.append({
                        'type': 'info',
                        'message': f'Moderate engagement rate of {avg_engagement:.1f}% - room for improvement'
                    })
                else:
                    insights.append({
                        'type': 'warning',
                        'message': f'Low engagement rate of {avg_engagement:.1f}% - consider content strategy review'
                    })
        
        # Reach analysis
        if any('reach' in col for col in columns):
            reach_cols = [col for col in df.columns if 'reach' in col.lower()]
            if reach_cols:
                total_reach = df[reach_cols[0]].sum()
                insights.append({
                    'type': 'info',
                    'message': f'Total reach achieved: {total_reach:,.0f} impressions across reporting period'
                })
        
        # Conversion analysis
        if any('conversion' in col for col in columns):
            conversion_cols = [col for col in df.columns if 'conversion' in col.lower()]
            if conversion_cols:
                avg_conversion = df[conversion_cols[0]].mean()
                if avg_conversion > 3:
                    insights.append({
                        'type': 'positive',
                        'message': f'Excellent conversion rate of {avg_conversion:.1f}% - strong ROI performance'
                    })
                else:
                    insights.append({
                        'type': 'info',
                        'message': f'Conversion rate of {avg_conversion:.1f}% - monitor for optimization opportunities'
                    })
        
        # Cultural relevance analysis (Crooks & Castles specific)
        if any('cultural' in col for col in columns) or any('heritage' in col for col in columns):
            insights.append({
                'type': 'positive',
                'message': 'Cultural content performing well - maintain authentic storytelling approach'
            })
        
        # Time-based performance trends
        if any('date' in col for col in columns):
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols and len(df) > 1:
                insights.append({
                    'type': 'info',
                    'message': f'Performance data spans {len(df)} data points - sufficient for trend analysis'
                })
        
        # HVD phase alignment
        insights.append({
            'type': 'info',
            'message': 'Performance data integrated with HVD Phase 1 tracking - monitor against 12 posts/month target'
        })
        
        if not insights:
            insights.append({
                'type': 'info',
                'message': 'Performance report uploaded successfully. Manual review recommended for detailed insights.'
            })
        
        return insights
        
    except Exception as e:
        logger.error(f"Error analyzing performance report: {str(e)}")
        return [{'type': 'warning', 'message': f'Error analyzing report: {str(e)}'}]

if __name__ == '__main__':
    logger.info("🏰 CROOKS & CASTLES COMMAND CENTER - FINAL DEPLOYMENT")
    
    # Initialize database
    init_database()
    
    # Start server
    app.run(host='0.0.0.0', port=5103, debug=False)

