#!/usr/bin/env python3
"""
Database initialization script for Crooks Command Center v2.0
Run this script to set up the SQLite database with sample data
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def create_database():
    """Create and initialize the SQLite database"""
    conn = sqlite3.connect('intelligence.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            data_hash TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER,
            data_type TEXT,
            content TEXT,
            metrics TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (brand_id) REFERENCES brands (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intelligence_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT,
            brand_name TEXT,
            insights TEXT,
            recommendations TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_size INTEGER,
            file_type TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tags TEXT,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content_type TEXT DEFAULT 'post',
            scheduled_date DATE NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Database tables created successfully")
    
    # Insert sample brands
    sample_brands = [
        ('supreme', 'streetwear'),
        ('off-white', 'streetwear'),
        ('fear-of-god', 'streetwear'),
        ('yeezy', 'streetwear'),
        ('jordan', 'streetwear'),
        ('crooks-castles', 'streetwear'),
        ('stussy', 'streetwear'),
        ('bape', 'streetwear'),
        ('palace', 'streetwear'),
        ('kith', 'streetwear')
    ]
    
    for brand_name, category in sample_brands:
        cursor.execute('''
            INSERT OR IGNORE INTO brands (name, category, data_hash, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (brand_name, category, f"sample_{brand_name}", datetime.now()))
    
    print("✅ Sample brands inserted")
    
    # Insert sample metrics for each brand
    for i, (brand_name, category) in enumerate(sample_brands):
        # Get brand ID
        brand_id = cursor.execute('SELECT id FROM brands WHERE name = ?', (brand_name,)).fetchone()[0]
        
        # Generate sample metrics
        sample_metrics = {
            'total_posts': random.randint(50, 500),
            'total_engagement': random.randint(1000, 50000),
            'avg_likes': random.randint(100, 5000),
            'avg_comments': random.randint(10, 500),
            'engagement_rate': random.uniform(50, 500),
            'content_diversity': random.uniform(0.1, 0.8),
            'influence_score': random.uniform(1, 10),
            'positioning_score': random.uniform(3, 10),
            'growth_trajectory': random.uniform(-0.5, 1.5),
            'hashtags': {
                'streetwear': random.randint(10, 100),
                'fashion': random.randint(5, 50),
                'style': random.randint(15, 80),
                'hypebeast': random.randint(8, 60),
                'ootd': random.randint(20, 120)
            },
            'mentions': {
                'influencer1': random.randint(1, 10),
                'influencer2': random.randint(1, 5)
            },
            'posting_frequency': {
                'Monday': {12: 5, 18: 8, 20: 12},
                'Tuesday': {14: 3, 19: 6, 21: 9},
                'Wednesday': {13: 4, 17: 7, 22: 5}
            }
        }
        
        # Sample content data
        sample_content = [
            {
                'text': f'New {brand_name} drop is fire 🔥 #streetwear #fashion',
                'likes': random.randint(100, 5000),
                'comments': random.randint(10, 500),
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
        ]
        
        cursor.execute('''
            INSERT INTO competitor_data (brand_id, data_type, content, metrics)
            VALUES (?, ?, ?, ?)
        ''', (brand_id, 'social_media', json.dumps(sample_content), json.dumps(sample_metrics)))
    
    print("✅ Sample competitor data inserted")
    
    # Insert sample intelligence reports
    sample_insights = [
        {
            'type': 'positive',
            'category': 'engagement',
            'message': 'Brand shows strong engagement growth this quarter',
            'impact': 'high'
        },
        {
            'type': 'opportunity',
            'category': 'content',
            'message': 'Content diversity could be improved for better reach',
            'impact': 'medium'
        }
    ]
    
    sample_recommendations = [
        {
            'category': 'engagement',
            'priority': 'high',
            'action': 'Increase user-generated content campaigns',
            'expected_impact': '25% engagement boost'
        }
    ]
    
    for brand_name, _ in sample_brands[:3]:  # Add reports for first 3 brands
        cursor.execute('''
            INSERT INTO intelligence_reports 
            (report_type, brand_name, insights, recommendations, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        ''', ('competitive_analysis', brand_name, json.dumps(sample_insights), 
              json.dumps(sample_recommendations), random.uniform(0.7, 0.95)))
    
    print("✅ Sample intelligence reports inserted")
    
    # Insert sample calendar items
    sample_calendar_items = [
        ('Supreme Drop Announcement', 'post', (datetime.now() + timedelta(days=1)).date(), 'Announce new Supreme collection drop', 'scheduled'),
        ('Streetwear Trend Analysis', 'story', (datetime.now() + timedelta(days=3)).date(), 'Share insights on current streetwear trends', 'scheduled'),
        ('Collaboration Reveal', 'campaign', (datetime.now() + timedelta(days=7)).date(), 'Major brand collaboration announcement', 'scheduled'),
        ('Community Engagement', 'post', (datetime.now() + timedelta(days=5)).date(), 'User-generated content feature', 'scheduled'),
        ('Behind the Scenes', 'story', (datetime.now() + timedelta(days=2)).date(), 'Show design process', 'draft')
    ]
    
    for title, content_type, scheduled_date, description, status in sample_calendar_items:
        cursor.execute('''
            INSERT INTO calendar_items (title, content_type, scheduled_date, description, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content_type, scheduled_date, description, status))
    
    print("✅ Sample calendar items inserted")
    
    # Insert sample assets metadata
    sample_assets = [
        ('sample_logo.png', 'Brand Logo.png', 25600, 'image/png', datetime.now(), 'branding,logo', 'Main brand logo file'),
        ('campaign_video.mp4', 'Campaign Video.mp4', 15728640, 'video/mp4', datetime.now() - timedelta(days=1), 'campaign,video', 'Latest campaign video'),
        ('style_guide.pdf', 'Brand Style Guide.pdf', 2048000, 'application/pdf', datetime.now() - timedelta(days=2), 'branding,guidelines', 'Brand style guidelines document')
    ]
    
    for filename, original_name, file_size, file_type, upload_date, tags, description in sample_assets:
        cursor.execute('''
            INSERT INTO assets (filename, original_name, file_size, file_type, upload_date, tags, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filename, original_name, file_size, file_type, upload_date, tags, description))
    
    print("✅ Sample assets inserted")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Database initialization complete!")
    print("Your Crooks Command Center v2.0 is ready for deployment!")

if __name__ == '__main__':
    create_database()
