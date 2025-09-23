from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
from collections import Counter
import re
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Import your existing database connection
# Replace this with your actual database setup
from your_database import db  # Replace with your actual DB connection

def extract_text_for_sentiment(post):
    """Extract text from both Instagram and TikTok post structures"""
    # Instagram posts use 'caption', TikTok posts use 'desc'
    text = post.get('caption') or post.get('desc')
    
    if text:
        # Clean text for sentiment analysis
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return None

def extract_hashtags(post):
    """Extract hashtags from both Instagram and TikTok structures"""
    hashtags = []
    
    # Instagram: hashtags are in 'hashtags' array
    if 'hashtags' in post and isinstance(post['hashtags'], list):
        hashtags.extend(post['hashtags'])
    
    # TikTok: hashtags are in 'textExtra' array with type=1
    if 'textExtra' in post:
        for item in post['textExtra']:
            if item.get('type') == 1 and item.get('hashtag_name'):
                hashtags.append(item['hashtag_name'])
    
    # Backup: extract from text content
    text = extract_text_for_sentiment(post)
    if text:
        text_hashtags = re.findall(r'#(\w+)', text)
        hashtags.extend(text_hashtags)
    
    return list(set(hashtags))

def get_unique_post_id(post):
    """Generate unique ID that works for both platforms"""
    # Instagram posts have 'url' field
    if 'url' in post:
        return post['url']
    # TikTok posts have 'id' field  
    if 'id' in post:
        return post['id']
    # Fallback
    return str(hash(str(post)))

def analyze_sentiment(text):
    """Analyze sentiment using VADER (optimized for social media)"""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        
        return {
            'compound': scores['compound'],
            'positive': scores['pos'], 
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    except ImportError:
        print("VADER not installed. Run: pip install vaderSentiment")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/intelligence')
def get_intelligence():
    try:
        # Get all posts from database
        posts = list(db.posts.find())
        
        # Deduplicate posts using unique IDs
        unique_posts = {}
        for post in posts:
            unique_id = get_unique_post_id(post)
            unique_posts[unique_id] = post
        
        posts = list(unique_posts.values())
        total_posts = len(posts)
        
        # Process sentiment analysis
        sentiment_results = []
        for post in posts:
            text = extract_text_for_sentiment(post)
            if text and len(text.strip()) > 0:
                sentiment = analyze_sentiment(text)
                if sentiment:
                    sentiment_results.append(sentiment)
        
        # Calculate sentiment metrics
        sentiment_analyzed = len(sentiment_results)
        positive_sentiment = 0
        
        if sentiment_analyzed > 0:
            positive_count = sum(1 for s in sentiment_results if s.get('compound', 0) > 0.1)
            positive_sentiment = round((positive_count / sentiment_analyzed) * 100, 1)
        
        # Process hashtags from both platforms
        all_hashtags = []
        for post in posts:
            hashtags = extract_hashtags(post)
            all_hashtags.extend(hashtags)
        
        hashtag_counts = Counter(all_hashtags)
        trending_hashtags = [
            {'hashtag': tag, 'count': count}
            for tag, count in hashtag_counts.most_common(20)
        ]
        
        # Generate strategic recommendations based on actual data
        recommendations = []
        if hashtag_counts:
            top_hashtag = hashtag_counts.most_common(1)[0]
            recommendations.append({
                'title': 'TOP HASHTAG OPPORTUNITY',
                'description': f"#{top_hashtag[0]} showing {top_hashtag[1]} mentions - amplify this trend"
            })
        
        if sentiment_analyzed > 0:
            recommendations.append({
                'title': 'SENTIMENT INSIGHTS',
                'description': f"{positive_sentiment}% positive sentiment across {sentiment_analyzed} analyzed posts"
            })
            
        if len(trending_hashtags) > 5:
            recommendations.append({
                'title': 'HASHTAG DIVERSITY',
                'description': f"Tracking {len(trending_hashtags)} trending hashtags across competitor analysis"
            })
        
        return jsonify({
            'posts_analyzed': total_posts,
            'sentiment_analyzed': sentiment_analyzed, 
            'positive_sentiment': positive_sentiment,
            'trending_hashtags': trending_hashtags,
            'trends_tracked': len(trending_hashtags),
            'strategic_recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence/competitors')
def get_competitors():
    try:
        # Get competitor analysis data
        # Replace this with your actual competitor analysis logic
        posts = list(db.posts.find())
        
        # Group posts by brand/account
        brands = {}
        for post in posts:
            # Instagram: ownerUsername, TikTok: author.uniqueId
            brand_name = post.get('ownerUsername') or post.get('author', {}).get('uniqueId', 'Unknown')
            
            if brand_name not in brands:
                brands[brand_name] = {
                    'posts': [],
                    'total_engagement': 0,
                    'total_views': 0
                }
            
            brands[brand_name]['posts'].append(post)
            
            # Calculate engagement
            if 'likesCount' in post:  # Instagram
                brands[brand_name]['total_engagement'] += post.get('likesCount', 0) + post.get('commentsCount', 0)
            elif 'stats' in post:  # TikTok
                stats = post['stats']
                brands[brand_name]['total_engagement'] += stats.get('diggCount', 0) + stats.get('commentCount', 0)
                brands[brand_name]['total_views'] += stats.get('playCount', 0)
        
        # Calculate share of voice
        total_posts = sum(len(brand['posts']) for brand in brands.values())
        share_of_voice = []
        brand_engagement = []
        
        for brand_name, data in brands.items():
            post_count = len(data['posts'])
            share_pct = round((post_count / total_posts) * 100, 1) if total_posts > 0 else 0
            avg_engagement = round(data['total_engagement'] / post_count) if post_count > 0 else 0
            avg_views = round(data['total_views'] / post_count) if post_count > 0 else 0
            
            share_of_voice.append({
                'brand': brand_name,
                'mentions': post_count,
                'share_pct': share_pct
            })
            
            brand_engagement.append({
                'brand': brand_name,
                'avg_engagement': avg_engagement,
                'avg_views': avg_views,
                'posts': post_count
            })
        
        # Sort by share percentage and engagement
        share_of_voice.sort(key=lambda x: x['share_pct'], reverse=True)
        brand_engagement.sort(key=lambda x: x['avg_engagement'], reverse=True)
        
        return jsonify({
            'share_of_voice': share_of_voice[:10],  # Top 10
            'brand_engagement': brand_engagement[:10]  # Top 10
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets')
def get_assets():
    # Replace with your actual assets logic
    return jsonify({
        'assets': []
    })

@app.route('/api/calendar/<view>')
def get_calendar(view):
    # Replace with your actual calendar logic
    return jsonify({
        'events': []
    })

@app.route('/api/agency')
def get_agency():
    # Replace with your actual agency workflow logic
    return jsonify({
        'phase': 'Phase 2',
        'monthly_budget': 50000,
        'budget_used': 35000,
        'on_time_delivery': 85,
        'quality_score': '9.2/10',
        'response_time': '< 2 hours',
        'current_projects': [
            {'name': 'Heritage Campaign', 'status': 'In Progress', 'due_date': '2024-12-15'},
            {'name': 'Holiday Collection', 'status': 'Planning', 'due_date': '2024-12-30'}
        ],
        'deliverables_breakdown': {
            'completed': ['Brand Guidelines', 'Logo Variations'],
            'in_progress': ['Campaign Assets', 'Social Templates'],
            'pending': ['Video Content', 'Print Materials']
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_files():
    # Replace with your actual file upload logic
    return jsonify({
        'status': 'success',
        'assets': []
    })

if __name__ == '__main__':
    app.run(debug=True)
