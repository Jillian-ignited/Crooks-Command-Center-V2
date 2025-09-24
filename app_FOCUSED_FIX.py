from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse
import hashlib
import logging
from werkzeug.utils import secure_filename
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
upload_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

@app.route('/')
def index():
    return render_template('index.html')

# FIXED: Data deduplication and asset management
def load_and_deduplicate_data():
    """Load data from JSONL files with proper deduplication"""
    all_data = []
    seen_posts = set()  # Track unique posts to prevent duplication
    
    # Get all JSONL files from uploads directory
    upload_path = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(upload_path):
        return []
    
    for root, dirs, files in os.walk(upload_path):
        for file in files:
            if file.endswith('.jsonl'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line:
                                try:
                                    data = json.loads(line)
                                    
                                    # Create unique identifier for deduplication
                                    unique_id = None
                                    if 'url' in data:
                                        unique_id = data['url']
                                    elif 'id' in data:
                                        unique_id = str(data['id'])
                                    elif 'text' in data and 'username' in data:
                                        unique_id = f"{data['username']}_{hashlib.md5(data['text'].encode()).hexdigest()[:8]}"
                                    
                                    # Only add if we haven't seen this post before
                                    if unique_id and unique_id not in seen_posts:
                                        seen_posts.add(unique_id)
                                        data['_source_file'] = file
                                        data['_unique_id'] = unique_id
                                        all_data.append(data)
                                        
                                except json.JSONDecodeError as e:
                                    logger.warning(f"JSON decode error in {file} line {line_num}: {e}")
                                    continue
                                    
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue
    
    logger.info(f"Loaded {len(all_data)} unique posts from {len(files)} files")
    return all_data

def get_asset_files():
    """Get list of asset files with metadata - NO DUPLICATION"""
    assets = []
    upload_path = os.path.join(os.getcwd(), 'uploads')
    
    if not os.path.exists(upload_path):
        return assets
    
    seen_files = set()  # Prevent file duplication
    
    for root, dirs, files in os.walk(upload_path):
        for file in files:
            if file.endswith('.jsonl') and file not in seen_files:
                seen_files.add(file)
                file_path = os.path.join(root, file)
                
                try:
                    # Get file stats
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    last_modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                    
                    # Count records in file
                    record_count = 0
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip():
                                    record_count += 1
                    except:
                        record_count = 0
                    
                    assets.append({
                        'name': file,
                        'path': file_path,
                        'type': 'JSONL Data',
                        'size': f"{file_size//1024}KB" if file_size > 1024 else f"{file_size}B",
                        'records': record_count,
                        'last_modified': last_modified
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing file {file}: {e}")
                    continue
    
    return assets

# COMPETITIVE INTELLIGENCE FUNCTIONS (PRESERVED)
def extract_competitors_from_data(data):
    """Extract competitor mentions and engagement data"""
    competitors = defaultdict(lambda: {
        'posts': 0,
        'total_engagement': 0,
        'mentions': [],
        'hashtags': [],
        'avg_engagement': 0,
        'sentiment_scores': []
    })
    
    # Expanded competitor keywords
    competitor_keywords = {
        'supreme': ['supreme', '@supreme', '#supreme'],
        'offwhite': ['off-white', 'off white', '@off___white', '#offwhite'],
        'bape': ['bape', 'a bathing ape', '@bape_us', '#bape'],
        'stussy': ['stussy', '@stussy', '#stussy'],
        'kith': ['kith', '@kith', '#kith'],
        'fear_of_god': ['fear of god', 'fog', '@fearofgod', '#fearofgod'],
        'essentials': ['essentials', '@essentials', '#essentials'],
        'palm_angels': ['palm angels', '@palmangels', '#palmangels'],
        'stone_island': ['stone island', '@stoneisland', '#stoneisland'],
        'cdg': ['comme des garcons', 'cdg', '@commedesgarcons', '#cdg'],
        'vetements': ['vetements', '@vetements_official', '#vetements'],
        'balenciaga': ['balenciaga', '@balenciaga', '#balenciaga'],
        'yeezy': ['yeezy', '@yeezy', '#yeezy'],
        'jordan': ['jordan', 'air jordan', '@jumpman23', '#jordan'],
        'nike': ['nike', '@nike', '#nike'],
        'adidas': ['adidas', '@adidas', '#adidas'],
        'crooks_castles': ['crooks', 'castles', 'crooks & castles', 'crooks and castles', '@crooksandcastles', '#crooksandcastles']
    }
    
    for post in data:
        text = str(post.get('text', '')).lower()
        username = str(post.get('username', '')).lower()
        hashtags = post.get('hashtags', [])
        
        # Get engagement metrics
        engagement = 0
        if 'likesCount' in post:
            engagement += int(post.get('likesCount', 0))
        if 'commentsCount' in post:
            engagement += int(post.get('commentsCount', 0))
        if 'sharesCount' in post:
            engagement += int(post.get('sharesCount', 0))
        if 'viewsCount' in post:
            engagement += int(post.get('viewsCount', 0)) // 10  # Weight views less
        
        # Check for competitor mentions
        for competitor, keywords in competitor_keywords.items():
            mentioned = False
            for keyword in keywords:
                if keyword in text or keyword in username:
                    mentioned = True
                    break
            
            if mentioned:
                competitors[competitor]['posts'] += 1
                competitors[competitor]['total_engagement'] += engagement
                competitors[competitor]['mentions'].append(text[:100])
                competitors[competitor]['hashtags'].extend(hashtags)
                
                # Simple sentiment analysis
                positive_words = ['great', 'amazing', 'love', 'best', 'awesome', 'fire', 'dope', 'clean']
                negative_words = ['bad', 'hate', 'worst', 'terrible', 'ugly', 'trash']
                
                sentiment_score = 0.5  # neutral
                for word in positive_words:
                    if word in text:
                        sentiment_score += 0.1
                for word in negative_words:
                    if word in text:
                        sentiment_score -= 0.1
                
                sentiment_score = max(0, min(1, sentiment_score))
                competitors[competitor]['sentiment_scores'].append(sentiment_score)
    
    # Calculate averages
    for competitor in competitors:
        if competitors[competitor]['posts'] > 0:
            competitors[competitor]['avg_engagement'] = competitors[competitor]['total_engagement'] / competitors[competitor]['posts']
            competitors[competitor]['avg_sentiment'] = sum(competitors[competitor]['sentiment_scores']) / len(competitors[competitor]['sentiment_scores'])
        else:
            competitors[competitor]['avg_sentiment'] = 0.5
    
    return dict(competitors)

def get_trending_hashtags(data, limit=20):
    """Extract trending hashtags from data"""
    hashtag_counts = Counter()
    
    for post in data:
        hashtags = post.get('hashtags', [])
        if isinstance(hashtags, list):
            for tag in hashtags:
                if isinstance(tag, str) and len(tag) > 1:
                    hashtag_counts[tag.lower()] += 1
        
        # Also extract hashtags from text
        text = str(post.get('text', ''))
        hashtag_pattern = r'#(\w+)'
        found_hashtags = re.findall(hashtag_pattern, text.lower())
        for tag in found_hashtags:
            hashtag_counts[tag] += 1
    
    return hashtag_counts.most_common(limit)

# API ENDPOINTS
@app.route('/api/overview')
def api_overview():
    """Executive overview with real competitive intelligence"""
    try:
        data = load_and_deduplicate_data()
        competitors = extract_competitors_from_data(data)
        
        # Calculate metrics
        total_posts = len(data)
        total_engagement = sum(int(post.get('likesCount', 0)) + int(post.get('commentsCount', 0)) for post in data)
        avg_engagement = total_engagement / total_posts if total_posts > 0 else 0
        
        # Crooks & Castles specific analysis
        crooks_data = competitors.get('crooks_castles', {})
        crooks_posts = crooks_data.get('posts', 0)
        crooks_engagement = crooks_data.get('total_engagement', 0)
        crooks_avg_engagement = crooks_data.get('avg_engagement', 0)
        
        # Competitive ranking
        competitor_rankings = sorted(
            [(name, data['avg_engagement']) for name, data in competitors.items() if data['posts'] > 0],
            key=lambda x: x[1], reverse=True
        )
        
        crooks_ranking = "#N/A"
        for i, (name, _) in enumerate(competitor_rankings, 1):
            if name == 'crooks_castles':
                crooks_ranking = f"#{i}"
                break
        
        # Sentiment analysis
        all_sentiment_scores = []
        for comp_data in competitors.values():
            all_sentiment_scores.extend(comp_data.get('sentiment_scores', []))
        
        avg_sentiment = sum(all_sentiment_scores) / len(all_sentiment_scores) if all_sentiment_scores else 0.5
        positive_sentiment = (avg_sentiment * 100)
        
        return jsonify({
            'data_sources': len(get_asset_files()),
            'trust_score': int(positive_sentiment),
            'total_assets': len(get_asset_files()),
            'crooks_ranking': crooks_ranking,
            'crooks_performance': {
                'posts': crooks_posts,
                'total_engagement': crooks_engagement,
                'avg_engagement': round(crooks_avg_engagement, 2),
                'market_position': f"{crooks_ranking} out of {len(competitor_rankings)} tracked brands",
                'sentiment': round(crooks_data.get('avg_sentiment', 0.5), 3)
            },
            'executive_summary': {
                'summary': f"Analysis of {total_posts} posts from {datetime.now().strftime('%Y-%m-%d')} shows Crooks & Castles holding a strong position in the streetwear market.",
                'key_takeaways': [
                    f"Engagement is healthy, with an average of {avg_engagement:.2f} interactions per post.",
                    f"Sentiment is largely positive at {positive_sentiment:.1f}%, indicating strong brand reception.",
                    f"Crooks & Castles is ranked {crooks_ranking} for engagement against {len(competitor_rankings)} competitors."
                ],
                'recommendations': [
                    "Leverage top hashtags to increase reach.",
                    "Analyze competitor strategies to identify new opportunities.",
                    "Focus on video content, as it drives higher engagement."
                ]
            },
            'priority_actions': [
                {
                    'title': 'Hashtag Optimization',
                    'description': 'Implement trending hashtags in upcoming campaigns to increase visibility.'
                },
                {
                    'title': 'Competitor Analysis',
                    'description': 'Deep dive into top-performing competitor content strategies.'
                },
                {
                    'title': 'Content Diversification',
                    'description': 'Expand content types based on engagement performance data.'
                }
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in overview API: {e}")
        return jsonify({'error': 'Failed to load overview data'}), 500

@app.route('/api/intelligence')
def api_intelligence():
    """Intelligence data with competitive analysis"""
    try:
        data = load_and_deduplicate_data()
        competitors = extract_competitors_from_data(data)
        trending_hashtags = get_trending_hashtags(data)
        
        # Calculate sentiment
        all_sentiment_scores = []
        for comp_data in competitors.values():
            all_sentiment_scores.extend(comp_data.get('sentiment_scores', []))
        
        avg_sentiment = sum(all_sentiment_scores) / len(all_sentiment_scores) if all_sentiment_scores else 0.5
        positive_sentiment = (avg_sentiment * 100)
        
        return jsonify({
            'posts_analyzed': len(data),
            'sentiment_analyzed': len(all_sentiment_scores),
            'positive_sentiment': round(positive_sentiment, 1),
            'trends_tracked': len(trending_hashtags),
            'trending_hashtags': [{'hashtag': f"#{tag}", 'count': count} for tag, count in trending_hashtags[:10]],
            'strategic_recommendations': [
                {
                    'title': 'Market Positioning',
                    'description': 'Leverage competitive intelligence to identify market gaps and opportunities.'
                },
                {
                    'title': 'Content Strategy',
                    'description': 'Focus on high-engagement content types based on competitor analysis.'
                },
                {
                    'title': 'Trend Adoption',
                    'description': 'Incorporate trending hashtags and themes into content calendar.'
                }
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in intelligence API: {e}")
        return jsonify({'error': 'Failed to load intelligence data'}), 500

@app.route('/api/intelligence/competitors')
def api_competitors():
    """Detailed competitor analysis"""
    try:
        data = load_and_deduplicate_data()
        competitors = extract_competitors_from_data(data)
        
        # Format competitor data
        competitor_list = []
        for name, comp_data in competitors.items():
            if comp_data['posts'] > 0:  # Only include competitors with data
                # Determine tier based on engagement
                avg_eng = comp_data['avg_engagement']
                if avg_eng > 1000:
                    tier = "Premium"
                elif avg_eng > 500:
                    tier = "Mid-tier"
                else:
                    tier = "Emerging"
                
                competitor_list.append({
                    'name': name.replace('_', ' ').title(),
                    'posts': comp_data['posts'],
                    'avg_engagement': round(comp_data['avg_engagement'], 2),
                    'avg_sentiment': round(comp_data.get('avg_sentiment', 0.5), 3),
                    'tier': tier
                })
        
        # Sort by engagement
        competitor_list.sort(key=lambda x: x['avg_engagement'], reverse=True)
        
        return jsonify({
            'competitors': competitor_list
        })
        
    except Exception as e:
        logger.error(f"Error in competitors API: {e}")
        return jsonify({'error': 'Failed to load competitor data'}), 500

@app.route('/api/assets')
def api_assets():
    """Asset management with deduplication"""
    try:
        assets = get_asset_files()
        total_records = sum(asset['records'] for asset in assets)
        
        # Calculate storage
        total_size = 0
        for asset in assets:
            try:
                size_str = asset['size']
                if 'KB' in size_str:
                    total_size += int(size_str.replace('KB', '')) * 1024
                elif 'B' in size_str:
                    total_size += int(size_str.replace('B', ''))
            except:
                continue
        
        storage_used = f"{total_size//1024}KB" if total_size > 1024 else f"{total_size}B"
        
        return jsonify({
            'data_assets': assets,
            'total_records': total_records,
            'media_assets': [],  # No media assets currently
            'storage_used': storage_used
        })
        
    except Exception as e:
        logger.error(f"Error in assets API: {e}")
        return jsonify({'error': 'Failed to load assets'}), 500

# NEW: Asset removal functionality
@app.route('/api/assets/delete/<filename>', methods=['DELETE'])
def delete_asset(filename):
    """Delete an asset file"""
    try:
        # Security check - only allow deletion of files in uploads directory
        safe_filename = secure_filename(filename)
        if not safe_filename.endswith('.jsonl'):
            return jsonify({'error': 'Only JSONL files can be deleted'}), 400
        
        # Find and delete the file
        upload_path = os.path.join(os.getcwd(), 'uploads')
        deleted = False
        
        for root, dirs, files in os.walk(upload_path):
            if safe_filename in files:
                file_path = os.path.join(root, safe_filename)
                try:
                    os.remove(file_path)
                    deleted = True
                    logger.info(f"Deleted asset: {safe_filename}")
                    break
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
                    return jsonify({'error': f'Failed to delete file: {e}'}), 500
        
        if deleted:
            return jsonify({'message': f'Successfully deleted {safe_filename}'})
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in delete asset API: {e}")
        return jsonify({'error': 'Failed to delete asset'}), 500

@app.route('/api/calendar/<timeframe>')
def api_calendar(timeframe):
    """Calendar planning data"""
    try:
        # Generate strategic campaigns based on timeframe
        campaigns = []
        
        if timeframe == '7':
            campaigns = [
                {
                    'title': 'Weekly Streetwear Drop',
                    'start_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'target': 'Core streetwear audience',
                    'goal': 'Drive immediate sales',
                    'content': 'Product showcase, lifestyle imagery',
                    'assets': 'High-res product photos, video content',
                    'budget': 2500
                }
            ]
        elif timeframe == '30':
            campaigns = [
                {
                    'title': 'Monthly Brand Campaign',
                    'start_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                    'target': 'Broader streetwear community',
                    'goal': 'Brand awareness and engagement',
                    'content': 'Brand story, community features',
                    'assets': 'Video series, user-generated content',
                    'budget': 7500
                }
            ]
        
        return jsonify({
            'campaigns': campaigns,
            'active_campaigns': len(campaigns),
            'total_budget': sum(c.get('budget', 0) for c in campaigns),
            'cultural_moments': [
                'Hispanic Heritage Month',
                'Hip-Hop Anniversary',
                'Black Friday/Cyber Monday'
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in calendar API: {e}")
        return jsonify({'error': 'Failed to load calendar data'}), 500

@app.route('/api/agency')
def api_agency():
    """Agency partnership data"""
    try:
        return jsonify({
            'deliverables': [
                {
                    'title': 'Q4 Campaign Creative Package',
                    'status': 'In Progress',
                    'due_date': '2025-10-15',
                    'assignee': 'HVD Creative Team'
                },
                {
                    'title': 'Brand Compliance Review',
                    'status': 'Completed',
                    'due_date': '2025-09-20',
                    'assignee': 'Brand Manager'
                },
                {
                    'title': 'Performance Analytics Report',
                    'status': 'Planning',
                    'due_date': '2025-10-01',
                    'assignee': 'Analytics Team'
                }
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in agency API: {e}")
        return jsonify({'error': 'Failed to load agency data'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
