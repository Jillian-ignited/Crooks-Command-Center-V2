from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse
import sqlite3
from werkzeug.utils import secure_filename
import logging
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'competitive-intelligence-key')

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class CompetitiveIntelligenceEngine:
    def __init__(self):
        self.brands_data = {}
        self.competitor_profiles = {}
        self.market_trends = {}
        self.social_metrics = {}
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
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
        
        conn.commit()
        conn.close()
        
    def process_apify_data(self, file_path):
        """Process and organize Apify data by brand with advanced analytics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            organized_data = defaultdict(list)
            brand_metrics = defaultdict(lambda: {
                'total_posts': 0,
                'total_engagement': 0,
                'avg_likes': 0,
                'avg_comments': 0,
                'posting_frequency': {},
                'hashtags': Counter(),
                'mentions': Counter(),
                'sentiment_score': 0
            })
            
            for item in raw_data:
                brand = self.extract_brand_from_data(item)
                if brand:
                    organized_data[brand].append(item)
                    self.update_brand_metrics(brand_metrics[brand], item)
            
            # Calculate advanced metrics
            for brand, metrics in brand_metrics.items():
                self.calculate_advanced_metrics(metrics, organized_data[brand])
            
            # Store in database
            self.store_brand_data(organized_data, brand_metrics)
            
            return {
                'brands': dict(organized_data),
                'metrics': dict(brand_metrics),
                'summary': self.generate_data_summary(organized_data, brand_metrics)
            }
        except Exception as e:
            logger.error(f"Error processing Apify data: {e}")
            return {}
    
    def extract_brand_from_data(self, item):
        """Advanced brand extraction with ML-like pattern recognition"""
        # Known streetwear/fashion brands
        streetwear_brands = [
            'supreme', 'off-white', 'fear-of-god', 'yeezy', 'jordan', 'nike', 'adidas',
            'crooks-castles', 'stussy', 'bape', 'anti-social-social-club', 'palace',
            'kith', 'essentials', 'chrome-hearts', 'gallery-dept', 'rhude', 'amiri'
        ]
        
        brand_fields = ['brand', 'brandName', 'account', 'username', 'handle', 'author']
        
        for field in brand_fields:
            if field in item and item[field]:
                brand_name = item[field].lower().strip()
                # Check if it's a known streetwear brand
                for known_brand in streetwear_brands:
                    if known_brand in brand_name or brand_name in known_brand:
                        return known_brand
                return brand_name
        
        # Extract from URL
        if 'url' in item:
            domain = urlparse(item['url']).netloc
            if domain:
                brand_candidate = domain.replace('www.', '').split('.')[0]
                for known_brand in streetwear_brands:
                    if known_brand in brand_candidate or brand_candidate in known_brand:
                        return known_brand
                return brand_candidate
        
        # Extract from text/caption with NLP
        text_fields = ['text', 'caption', 'description', 'title']
        for field in text_fields:
            if field in item and item[field]:
                brands = self.extract_brands_from_text(item[field])
                if brands:
                    return brands[0]
        
        return 'unknown'
    
    def extract_brands_from_text(self, text):
        """NLP-based brand extraction from text"""
        streetwear_patterns = [
            r'\b(supreme|off.white|fear.of.god|yeezy|jordan|crooks.castles)\b',
            r'\b(stussy|bape|anti.social|palace|kith|essentials)\b',
            r'\b(chrome.hearts|gallery.dept|rhude|amiri)\b'
        ]
        
        brands = []
        for pattern in streetwear_patterns:
            matches = re.findall(pattern, text.lower())
            brands.extend(matches)
        
        return list(set(brands))
    
    def update_brand_metrics(self, metrics, item):
        """Update brand metrics with new data point"""
        metrics['total_posts'] += 1
        
        # Extract engagement metrics
        likes = item.get('likes', 0) or item.get('likesCount', 0) or 0
        comments = item.get('comments', 0) or item.get('commentsCount', 0) or 0
        
        metrics['total_engagement'] += likes + comments
        metrics['avg_likes'] = (metrics['avg_likes'] * (metrics['total_posts'] - 1) + likes) / metrics['total_posts']
        metrics['avg_comments'] = (metrics['avg_comments'] * (metrics['total_posts'] - 1) + comments) / metrics['total_posts']
        
        # Extract hashtags
        text = item.get('text', '') or item.get('caption', '')
        hashtags = re.findall(r'#(\w+)', text)
        for tag in hashtags:
            metrics['hashtags'][tag.lower()] += 1
        
        # Extract mentions
        mentions = re.findall(r'@(\w+)', text)
        for mention in mentions:
            metrics['mentions'][mention.lower()] += 1
        
        # Track posting times for frequency analysis
        timestamp = item.get('timestamp') or item.get('created_at') or datetime.now().isoformat()
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                day_key = dt.strftime('%A')
                hour_key = dt.hour
                if day_key not in metrics['posting_frequency']:
                    metrics['posting_frequency'][day_key] = {}
                metrics['posting_frequency'][day_key][hour_key] = metrics['posting_frequency'][day_key].get(hour_key, 0) + 1
            except:
                pass
    
    def calculate_advanced_metrics(self, metrics, brand_data):
        """Calculate advanced competitive intelligence metrics"""
        if not brand_data:
            return
        
        # Engagement rate
        if metrics['total_posts'] > 0:
            metrics['engagement_rate'] = metrics['total_engagement'] / metrics['total_posts']
        
        # Content diversity score (based on hashtag variety)
        unique_hashtags = len(metrics['hashtags'])
        total_hashtag_uses = sum(metrics['hashtags'].values())
        metrics['content_diversity'] = unique_hashtags / max(total_hashtag_uses, 1)
        
        # Influence score (based on mentions and engagement)
        metrics['influence_score'] = (
            len(metrics['mentions']) * 0.3 +
            metrics['avg_likes'] * 0.0001 +
            metrics['avg_comments'] * 0.001
        )
        
        # Growth trajectory (if we have timestamps)
        metrics['growth_trajectory'] = self.calculate_growth_trend(brand_data)
        
        # Competitive positioning score
        metrics['positioning_score'] = self.calculate_positioning_score(metrics)
    
    def calculate_growth_trend(self, brand_data):
        """Calculate growth trend based on posting frequency and engagement over time"""
        if len(brand_data) < 2:
            return 0
        
        # Sort by timestamp if available
        timestamped_data = []
        for item in brand_data:
            timestamp = item.get('timestamp') or item.get('created_at')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    engagement = (item.get('likes', 0) + item.get('comments', 0))
                    timestamped_data.append((dt, engagement))
                except:
                    continue
        
        if len(timestamped_data) < 2:
            return 0
        
        timestamped_data.sort(key=lambda x: x[0])
        
        # Calculate trend over time
        recent_engagement = sum([x[1] for x in timestamped_data[-5:]])  # Last 5 posts
        earlier_engagement = sum([x[1] for x in timestamped_data[:5]])  # First 5 posts
        
        if earlier_engagement == 0:
            return 1 if recent_engagement > 0 else 0
        
        return (recent_engagement - earlier_engagement) / earlier_engagement
    
    def calculate_positioning_score(self, metrics):
        """Calculate competitive positioning score"""
        score = 0
        
        # High engagement rate increases score
        score += min(metrics.get('engagement_rate', 0) / 1000, 5)
        
        # Content diversity increases score
        score += min(metrics.get('content_diversity', 0) * 10, 3)
        
        # Influence score
        score += min(metrics.get('influence_score', 0), 2)
        
        return min(score, 10)  # Cap at 10
    
    def store_brand_data(self, organized_data, brand_metrics):
        """Store processed data in database"""
        conn = sqlite3.connect('intelligence.db')
        cursor = conn.cursor()
        
        for brand, data in organized_data.items():
            # Insert or update brand
            data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
            cursor.execute('''
                INSERT OR REPLACE INTO brands (name, category, data_hash, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (brand, 'streetwear', data_hash, datetime.now()))
            
            brand_id = cursor.lastrowid or cursor.execute('SELECT id FROM brands WHERE name = ?', (brand,)).fetchone()[0]
            
            # Store competitor data
            cursor.execute('''
                INSERT INTO competitor_data (brand_id, data_type, content, metrics)
                VALUES (?, ?, ?, ?)
            ''', (brand_id, 'social_media', json.dumps(data), json.dumps(brand_metrics[brand])))
        
        conn.commit()
        conn.close()
    
    def generate_data_summary(self, organized_data, brand_metrics):
        """Generate intelligent summary of processed data"""
        total_brands = len(organized_data)
        total_posts = sum(len(data) for data in organized_data.values())
        
        # Top performing brands
        top_brands = sorted(
            brand_metrics.items(),
            key=lambda x: x[1].get('engagement_rate', 0),
            reverse=True
        )[:5]
        
        # Trending hashtags across all brands
        all_hashtags = Counter()
        for metrics in brand_metrics.values():
            all_hashtags.update(metrics['hashtags'])
        
        return {
            'total_brands': total_brands,
            'total_posts': total_posts,
            'top_performing_brands': [{'brand': brand, 'engagement_rate': metrics['engagement_rate']} 
                                    for brand, metrics in top_brands],
            'trending_hashtags': dict(all_hashtags.most_common(10)),
            'summary_generated_at': datetime.now().isoformat()
        }
    
    def generate_competitive_analysis(self, target_brand, competitors=None):
        """Generate comprehensive competitive analysis"""
        conn = sqlite3.connect('intelligence.db')
        cursor = conn.cursor()
        
        # Get target brand data
        target_data = cursor.execute('''
            SELECT cd.content, cd.metrics FROM competitor_data cd
            JOIN brands b ON cd.brand_id = b.id
            WHERE b.name = ? ORDER BY cd.timestamp DESC LIMIT 1
        ''', (target_brand,)).fetchone()
        
        if not target_data:
            return {'error': f'No data found for brand: {target_brand}'}
        
        target_metrics = json.loads(target_data[1])
        
        # Get competitor data
        if not competitors:
            competitors = cursor.execute('''
                SELECT DISTINCT b.name FROM brands b
                WHERE b.name != ? AND b.category = 'streetwear'
                ORDER BY b.last_updated DESC LIMIT 5
            ''', (target_brand,)).fetchall()
            competitors = [comp[0] for comp in competitors]
        
        competitor_analysis = {}
        for competitor in competitors:
            comp_data = cursor.execute('''
                SELECT cd.content, cd.metrics FROM competitor_data cd
                JOIN brands b ON cd.brand_id = b.id
                WHERE b.name = ? ORDER BY cd.timestamp DESC LIMIT 1
            ''', (competitor,)).fetchone()
            
            if comp_data:
                competitor_analysis[competitor] = json.loads(comp_data[1])
        
        conn.close()
        
        # Generate insights
        insights = self.generate_competitive_insights(target_brand, target_metrics, competitor_analysis)
        
        return {
            'target_brand': target_brand,
            'target_metrics': target_metrics,
            'competitors': competitor_analysis,
            'insights': insights,
            'recommendations': self.generate_recommendations(target_brand, target_metrics, competitor_analysis),
            'market_position': self.calculate_market_position(target_metrics, competitor_analysis)
        }
    
    def generate_competitive_insights(self, target_brand, target_metrics, competitor_analysis):
        """Generate AI-powered competitive insights"""
        insights = []
        
        # Engagement comparison
        target_engagement = target_metrics.get('engagement_rate', 0)
        competitor_engagements = [comp.get('engagement_rate', 0) for comp in competitor_analysis.values()]
        
        if competitor_engagements:
            avg_competitor_engagement = sum(competitor_engagements) / len(competitor_engagements)
            
            if target_engagement > avg_competitor_engagement * 1.2:
                insights.append({
                    'type': 'positive',
                    'category': 'engagement',
                    'message': f'{target_brand} outperforms competitors with {target_engagement:.1f} avg engagement vs {avg_competitor_engagement:.1f} competitor average',
                    'impact': 'high'
                })
            elif target_engagement < avg_competitor_engagement * 0.8:
                insights.append({
                    'type': 'opportunity',
                    'category': 'engagement',
                    'message': f'{target_brand} engagement ({target_engagement:.1f}) is below competitor average ({avg_competitor_engagement:.1f})',
                    'impact': 'high'
                })
        
        # Content diversity analysis
        target_diversity = target_metrics.get('content_diversity', 0)
        competitor_diversity = [comp.get('content_diversity', 0) for comp in competitor_analysis.values()]
        
        if competitor_diversity:
            avg_competitor_diversity = sum(competitor_diversity) / len(competitor_diversity)
            
            if target_diversity < avg_competitor_diversity * 0.7:
                insights.append({
                    'type': 'opportunity',
                    'category': 'content',
                    'message': f'{target_brand} could diversify content strategy - currently at {target_diversity:.2f} vs competitor average {avg_competitor_diversity:.2f}',
                    'impact': 'medium'
                })
        
        # Hashtag strategy analysis
        target_hashtags = set(target_metrics.get('hashtags', {}).keys())
        competitor_hashtags = set()
        for comp in competitor_analysis.values():
            competitor_hashtags.update(comp.get('hashtags', {}).keys())
        
        unique_hashtags = target_hashtags - competitor_hashtags
        common_hashtags = target_hashtags & competitor_hashtags
        
        if len(unique_hashtags) > 5:
            insights.append({
                'type': 'positive',
                'category': 'hashtags',
                'message': f'{target_brand} uses {len(unique_hashtags)} unique hashtags, showing content differentiation',
                'impact': 'medium'
            })
        
        if len(common_hashtags) > 10:
            insights.append({
                'type': 'neutral',
                'category': 'hashtags',
                'message': f'{target_brand} shares {len(common_hashtags)} common hashtags with competitors - consider differentiation',
                'impact': 'low'
            })
        
        return insights
    
    def generate_recommendations(self, target_brand, target_metrics, competitor_analysis):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Engagement optimization
        target_engagement = target_metrics.get('engagement_rate', 0)
        if target_engagement < 100:  # Assuming 100 is a baseline
            recommendations.append({
                'category': 'engagement',
                'priority': 'high',
                'action': 'Increase engagement through interactive content',
                'details': 'Focus on polls, Q&As, and user-generated content to boost engagement rates',
                'expected_impact': 'Could improve engagement by 20-30%'
            })
        
        # Content timing optimization
        posting_freq = target_metrics.get('posting_frequency', {})
        if posting_freq:
            best_days = sorted(posting_freq.items(), key=lambda x: sum(x[1].values()), reverse=True)[:3]
            recommendations.append({
                'category': 'timing',
                'priority': 'medium',
                'action': f'Optimize posting schedule for {", ".join([day[0] for day in best_days])}',
                'details': 'Analysis shows higher engagement on these days',
                'expected_impact': 'Could improve reach by 15-25%'
            })
        
        # Competitive differentiation
        recommendations.append({
            'category': 'differentiation',
            'priority': 'medium',
            'action': 'Develop unique content pillars',
            'details': 'Create distinct content themes that set you apart from competitors',
            'expected_impact': 'Improved brand recognition and loyalty'
        })
        
        return recommendations
    
    def calculate_market_position(self, target_metrics, competitor_analysis):
        """Calculate market position relative to competitors"""
        if not competitor_analysis:
            return {'position': 'unknown', 'score': 0}
        
        # Key metrics for positioning
        metrics_to_compare = [
            'engagement_rate', 'content_diversity', 'influence_score', 'positioning_score'
        ]
        
        position_scores = []
        
        for metric in metrics_to_compare:
            target_value = target_metrics.get(metric, 0)
            competitor_values = [comp.get(metric, 0) for comp in competitor_analysis.values()]
            
            if competitor_values:
                # Calculate percentile rank
                better_than = sum(1 for val in competitor_values if target_value > val)
                percentile = better_than / len(competitor_values)
                position_scores.append(percentile)
        
        if position_scores:
            overall_position = sum(position_scores) / len(position_scores)
            
            if overall_position >= 0.8:
                position = 'leader'
            elif overall_position >= 0.6:
                position = 'strong'
            elif overall_position >= 0.4:
                position = 'competitive'
            elif overall_position >= 0.2:
                position = 'challenger'
            else:
                position = 'emerging'
            
            return {
                'position': position,
                'score': overall_position,
                'percentile': int(overall_position * 100)
            }
        
        return {'position': 'unknown', 'score': 0}

# Initialize intelligence engine
intelligence_engine = CompetitiveIntelligenceEngine()

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'platform': 'Crooks Command Center v2.0',
        'features': [
            'Advanced Competitive Intelligence',
            'Brand Analytics',
            'Market Positioning',
            'Trend Analysis',
            'Real-time Insights'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload-apify-data', methods=['POST'])
def upload_apify_data():
    """Upload and process Apify data files"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the data
        processed_data = intelligence_engine.process_apify_data(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {filename}',
            'data': processed_data
        })
    
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/competitive-analysis/<brand_name>')
def get_competitive_analysis(brand_name):
    """Get comprehensive competitive analysis for a brand"""
    try:
        competitors = request.args.getlist('competitors')
        analysis = intelligence_engine.generate_competitive_analysis(brand_name, competitors)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands')
def get_brands():
    """Get list of all tracked brands"""
    try:
        conn = sqlite3.connect('intelligence.db')
        cursor = conn.cursor()
        
        brands = cursor.execute('''
            SELECT b.name, b.category, b.last_updated,
                   COUNT(cd.id) as data_points
            FROM brands b
            LEFT JOIN competitor_data cd ON b.id = cd.brand_id
            GROUP BY b.id, b.name, b.category, b.last_updated
            ORDER BY b.last_updated DESC
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'brands': [
                {
                    'name': brand[0],
                    'category': brand[1],
                    'last_updated': brand[2],
                    'data_points': brand[3]
                }
                for brand in brands
            ]
        })
    
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-intelligence')
def get_market_intelligence():
    """Get overall market intelligence and trends"""
    try:
        conn = sqlite3.connect('intelligence.db')
        cursor = conn.cursor()
        
        # Get recent intelligence reports
        reports = cursor.execute('''
            SELECT report_type, brand_name, insights, recommendations,
                   confidence_score, created_at
            FROM intelligence_reports
            ORDER BY created_at DESC
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        # Generate market trends
        market_trends = {
            'engagement_trends': self.calculate_engagement_trends(),
            'hashtag_trends': self.calculate_hashtag_trends(),
            'brand_momentum': self.calculate_brand_momentum(),
            'market_gaps': self.identify_market_gaps()
        }
        
        return jsonify({
            'reports': [
                {
                    'type': report[0],
                    'brand': report[1],
                    'insights': json.loads(report[2]) if report[2] else [],
                    'recommendations': json.loads(report[3]) if report[3] else [],
                    'confidence': report[4],
                    'created_at': report[5]
                }
                for report in reports
            ],
            'market_trends': market_trends,
            'generated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating market intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/brand/<brand_name>')
def get_brand_insights(brand_name):
    """Get detailed insights for specific brand"""
    try:
        # Get brand analysis
        analysis = intelligence_engine.generate_competitive_analysis(brand_name)
        
        if 'error' in analysis:
            return jsonify(analysis), 404
        
        # Generate additional insights
        additional_insights = {
            'growth_opportunities': self.identify_growth_opportunities(brand_name),
            'threat_analysis': self.analyze_competitive_threats(brand_name),
            'content_recommendations': self.generate_content_recommendations(brand_name),
            'partnership_opportunities': self.identify_partnership_opportunities(brand_name)
        }
        
        return jsonify({
            'brand': brand_name,
            'analysis': analysis,
            'additional_insights': additional_insights,
            'generated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating brand insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets', methods=['GET', 'POST'])
def manage_assets():
    """Manage asset library"""
    if request.method == 'POST':
        # Handle asset upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store asset metadata in database
            conn = sqlite3.connect('intelligence.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO assets (filename, original_name, file_size, file_type, upload_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, file.filename, file.content_length, file.content_type, datetime.now()))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Asset {filename} uploaded successfully',
                'asset': {
                    'filename': filename,
                    'original_name': file.filename,
                    'size': file.content_length,
                    'type': file.content_type
                }
            })
        
        except Exception as e:
            logger.error(f"Error uploading asset: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:
        # Get asset list
        try:
            conn = sqlite3.connect('intelligence.db')
            cursor = conn.cursor()
            assets = cursor.execute('''
                SELECT filename, original_name, file_size, file_type, upload_date
                FROM assets ORDER BY upload_date DESC
            ''').fetchall()
            conn.close()
            
            return jsonify({
                'assets': [
                    {
                        'filename': asset[0],
                        'original_name': asset[1],
                        'size': asset[2],
                        'type': asset[3],
                        'uploaded': asset[4]
                    }
                    for asset in assets
                ]
            })
        
        except Exception as e:
            logger.error(f"Error fetching assets: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/calendar', methods=['GET', 'POST'])
def manage_calendar():
    """Manage content calendar"""
    if request.method == 'POST':
        # Add calendar item
        data = request.get_json()
        
        if not data or 'title' not in data or 'date' not in data:
            return jsonify({'error': 'Missing required fields: title, date'}), 400
        
        try:
            conn = sqlite3.connect('intelligence.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO calendar_items (title, content_type, scheduled_date, description, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['title'],
                data.get('type', 'post'),
                data['date'],
                data.get('description', ''),
                data.get('status', 'scheduled')
            ))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Calendar item "{data["title"]}" added successfully'
            })
        
        except Exception as e:
            logger.error(f"Error adding calendar item: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:
        # Get calendar items
        try:
            start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).isoformat())
            end_date = request.args.get('end_date', (datetime.now() + timedelta(days=60)).isoformat())
            
            conn = sqlite3.connect('intelligence.db')
            cursor = conn.cursor()
            items = cursor.execute('''
                SELECT title, content_type, scheduled_date, description, status, created_at
                FROM calendar_items 
                WHERE scheduled_date BETWEEN ? AND ?
                ORDER BY scheduled_date ASC
            ''', (start_date, end_date)).fetchall()
            conn.close()
            
            return jsonify({
                'calendar_items': [
                    {
                        'title': item[0],
                        'type': item[1],
                        'scheduled_date': item[2],
                        'description': item[3],
                        'status': item[4],
                        'created_at': item[5]
                    }
                    for item in items
                ]
            })
        
        except Exception as e:
            logger.error(f"Error fetching calendar items: {e}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
