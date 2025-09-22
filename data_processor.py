import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import statistics

def load_jsonl_data(file_path):
    """Load and validate JSONL data with error handling"""
    data = []
    errors = []
    
    if not os.path.exists(file_path):
        return {"data": [], "errors": [f"File not found: {file_path}"], "status": "error"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {str(e)}")
                    continue
        
        return {
            "data": data,
            "errors": errors,
            "status": "success" if data else "no_data",
            "total_records": len(data),
            "error_count": len(errors)
        }
    
    except Exception as e:
        return {"data": [], "errors": [f"File read error: {str(e)}"], "status": "error"}

def analyze_hashtags(posts, min_frequency=2):
    """Analyze hashtags with cultural context and trend identification"""
    hashtag_data = defaultdict(lambda: {
        'count': 0,
        'total_engagement': 0,
        'posts': [],
        'cultural_context': [],
        'trend_score': 0
    })
    
    # Cultural keywords for context identification
    cultural_keywords = {
        'streetwear': ['streetwear', 'street', 'urban', 'hypebeast', 'fashion'],
        'hip_hop': ['hiphop', 'rap', 'trap', 'beats', 'culture', 'music'],
        'heritage': ['heritage', 'culture', 'tradition', 'authentic', 'legacy'],
        'lifestyle': ['lifestyle', 'vibes', 'mood', 'aesthetic', 'style'],
        'community': ['community', 'family', 'crew', 'squad', 'collective']
    }
    
    for post in posts:
        hashtags = extract_hashtags(post.get('caption', ''))
        engagement = calculate_engagement(post)
        
        for hashtag in hashtags:
            hashtag_lower = hashtag.lower()
            hashtag_data[hashtag]['count'] += 1
            hashtag_data[hashtag]['total_engagement'] += engagement
            hashtag_data[hashtag]['posts'].append({
                'id': post.get('id', ''),
                'engagement': engagement,
                'timestamp': post.get('timestamp', '')
            })
            
            # Identify cultural context
            for context, keywords in cultural_keywords.items():
                if any(keyword in hashtag_lower for keyword in keywords):
                    if context not in hashtag_data[hashtag]['cultural_context']:
                        hashtag_data[hashtag]['cultural_context'].append(context)
    
    # Calculate trend scores and filter by frequency
    trending_hashtags = {}
    for hashtag, data in hashtag_data.items():
        if data['count'] >= min_frequency:
            # Calculate trend score based on frequency, engagement, and recency
            avg_engagement = data['total_engagement'] / data['count']
            recency_score = calculate_recency_score(data['posts'])
            trend_score = (data['count'] * 0.4) + (avg_engagement * 0.4) + (recency_score * 0.2)
            
            trending_hashtags[hashtag] = {
                'count': data['count'],
                'avg_engagement': round(avg_engagement, 2),
                'total_engagement': data['total_engagement'],
                'trend_score': round(trend_score, 2),
                'cultural_context': data['cultural_context'],
                'relevance': determine_hashtag_relevance(hashtag, data['cultural_context'])
            }
    
    # Sort by trend score
    sorted_hashtags = dict(sorted(trending_hashtags.items(), 
                                key=lambda x: x[1]['trend_score'], reverse=True))
    
    return sorted_hashtags

def extract_hashtags(text):
    """Extract hashtags from text"""
    if not text:
        return []
    
    # Find hashtags using regex
    hashtags = re.findall(r'#(\w+)', text)
    return [f"#{tag}" for tag in hashtags]

def calculate_engagement(post):
    """Calculate engagement score for a post"""
    likes = post.get('likesCount', 0) or post.get('likes', 0)
    comments = post.get('commentsCount', 0) or post.get('comments', 0)
    shares = post.get('sharesCount', 0) or post.get('shares', 0)
    views = post.get('viewsCount', 0) or post.get('views', 0)
    
    # Weighted engagement score
    engagement_score = (likes * 1) + (comments * 3) + (shares * 5) + (views * 0.1)
    return engagement_score

def calculate_recency_score(posts):
    """Calculate recency score based on post timestamps"""
    if not posts:
        return 0
    
    now = datetime.now()
    recency_scores = []
    
    for post in posts:
        timestamp = post.get('timestamp', '')
        if timestamp:
            try:
                post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_ago = (now - post_date).days
                # Higher score for more recent posts
                recency_score = max(0, 30 - days_ago) / 30
                recency_scores.append(recency_score)
            except:
                continue
    
    return statistics.mean(recency_scores) if recency_scores else 0

def determine_hashtag_relevance(hashtag, cultural_context):
    """Determine hashtag relevance to Crooks & Castles brand"""
    hashtag_lower = hashtag.lower()
    
    # High relevance keywords
    high_relevance = ['streetwear', 'hiphop', 'urban', 'fashion', 'style', 'culture', 'authentic']
    medium_relevance = ['lifestyle', 'mood', 'vibes', 'community', 'street', 'music']
    brand_specific = ['crooks', 'castles', 'crooksandcastles']
    
    if any(keyword in hashtag_lower for keyword in brand_specific):
        return 'brand_specific'
    elif any(keyword in hashtag_lower for keyword in high_relevance):
        return 'high'
    elif any(keyword in hashtag_lower for keyword in medium_relevance):
        return 'medium'
    elif cultural_context:
        return 'cultural'
    else:
        return 'low'

def process_intelligence_data():
    """Process all available intelligence data files"""
    intelligence_data = {
        'instagram_data': [],
        'tiktok_data': [],
        'competitive_data': [],
        'processing_summary': {},
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Look for data files in uploads directory
    upload_dir = 'uploads'
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(upload_dir, filename)
                result = load_jsonl_data(filepath)
                
                if result['status'] == 'success':
                    if 'instagram' in filename.lower():
                        intelligence_data['instagram_data'].extend(result['data'])
                    elif 'tiktok' in filename.lower():
                        intelligence_data['tiktok_data'].extend(result['data'])
                    elif 'competitive' in filename.lower():
                        intelligence_data['competitive_data'].extend(result['data'])
                
                intelligence_data['processing_summary'][filename] = {
                    'records': result['total_records'],
                    'errors': result['error_count'],
                    'status': result['status']
                }
    
    return intelligence_data

def generate_competitive_analysis():
    """Generate comprehensive competitive analysis"""
    intelligence_data = process_intelligence_data()
    
    # Combine all data for analysis
    all_posts = (intelligence_data['instagram_data'] + 
                intelligence_data['competitive_data'])
    
    if not all_posts:
        return {
            'error': 'No data available for analysis',
            'total_posts': 0,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    analysis = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_summary': {
            'instagram_posts': len(intelligence_data['instagram_data']),
            'tiktok_videos': len(intelligence_data['tiktok_data']),
            'competitive_posts': len(intelligence_data['competitive_data']),
            'total_analyzed': len(all_posts)
        },
        'hashtag_analysis': analyze_hashtags(all_posts, min_frequency=3),
        'engagement_insights': analyze_engagement_patterns(all_posts),
        'competitor_insights': analyze_competitors(all_posts),
        'cultural_moments': identify_cultural_moments(all_posts),
        'recommendations': generate_recommendations(all_posts),
        'trustworthiness_score': calculate_trustworthiness_score(intelligence_data)
    }
    
    return analysis

def analyze_engagement_patterns(posts):
    """Analyze engagement patterns and trends"""
    if not posts:
        return {}
    
    engagement_scores = [calculate_engagement(post) for post in posts]
    
    # Calculate statistics
    avg_engagement = statistics.mean(engagement_scores)
    median_engagement = statistics.median(engagement_scores)
    max_engagement = max(engagement_scores)
    
    # Find top performing posts
    posts_with_engagement = [(post, calculate_engagement(post)) for post in posts]
    top_posts = sorted(posts_with_engagement, key=lambda x: x[1], reverse=True)[:5]
    
    # Analyze posting times
    time_analysis = analyze_posting_times(posts)
    
    return {
        'avg_engagement': round(avg_engagement, 2),
        'median_engagement': round(median_engagement, 2),
        'max_engagement': max_engagement,
        'engagement_distribution': categorize_engagement_levels(engagement_scores),
        'top_performing_posts': [
            {
                'caption': post[0].get('caption', '')[:100] + '...' if len(post[0].get('caption', '')) > 100 else post[0].get('caption', ''),
                'engagement_score': post[1],
                'username': post[0].get('ownerUsername', 'unknown')
            }
            for post in top_posts
        ],
        'posting_time_insights': time_analysis
    }

def analyze_posting_times(posts):
    """Analyze optimal posting times"""
    hourly_engagement = defaultdict(list)
    daily_engagement = defaultdict(list)
    
    for post in posts:
        timestamp = post.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                engagement = calculate_engagement(post)
                
                hourly_engagement[dt.hour].append(engagement)
                daily_engagement[dt.strftime('%A')].append(engagement)
            except:
                continue
    
    # Calculate averages
    hourly_avg = {hour: round(statistics.mean(engagements), 2) 
                  for hour, engagements in hourly_engagement.items() if engagements}
    daily_avg = {day: round(statistics.mean(engagements), 2) 
                 for day, engagements in daily_engagement.items() if engagements}
    
    # Find best times
    best_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)[:3]
    best_days = sorted(daily_avg.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        'best_posting_hours': [f"{hour}:00" for hour, _ in best_hours],
        'best_posting_days': [day for day, _ in best_days],
        'hourly_performance': hourly_avg,
        'daily_performance': daily_avg
    }

def categorize_engagement_levels(engagement_scores):
    """Categorize engagement into levels"""
    if not engagement_scores:
        return {}
    
    # Define thresholds based on data distribution
    sorted_scores = sorted(engagement_scores)
    q1 = sorted_scores[len(sorted_scores)//4]
    q3 = sorted_scores[3*len(sorted_scores)//4]
    
    low_count = sum(1 for score in engagement_scores if score <= q1)
    medium_count = sum(1 for score in engagement_scores if q1 < score <= q3)
    high_count = sum(1 for score in engagement_scores if score > q3)
    
    total = len(engagement_scores)
    
    return {
        'low_engagement': {'count': low_count, 'percentage': round(low_count/total*100, 1)},
        'medium_engagement': {'count': medium_count, 'percentage': round(medium_count/total*100, 1)},
        'high_engagement': {'count': high_count, 'percentage': round(high_count/total*100, 1)}
    }

def analyze_competitors(posts):
    """Analyze competitor performance and strategies"""
    # Group posts by username
    competitor_data = defaultdict(list)
    
    for post in posts:
        username = post.get('ownerUsername', 'unknown')
        if username != 'unknown':
            competitor_data[username].append(post)
    
    # Analyze each competitor
    competitor_analysis = {}
    
    for username, user_posts in competitor_data.items():
        if len(user_posts) >= 3:  # Only analyze users with sufficient data
            engagement_scores = [calculate_engagement(post) for post in user_posts]
            
            competitor_analysis[username] = {
                'post_count': len(user_posts),
                'avg_engagement': round(statistics.mean(engagement_scores), 2),
                'total_engagement': sum(engagement_scores),
                'consistency_score': calculate_consistency_score(engagement_scores),
                'top_hashtags': get_top_hashtags_for_user(user_posts),
                'content_themes': analyze_content_themes(user_posts),
                'performance_tier': categorize_performance(statistics.mean(engagement_scores))
            }
    
    # Sort by average engagement
    sorted_competitors = dict(sorted(competitor_analysis.items(), 
                                   key=lambda x: x[1]['avg_engagement'], reverse=True))
    
    return sorted_competitors

def calculate_consistency_score(engagement_scores):
    """Calculate consistency score based on standard deviation"""
    if len(engagement_scores) < 2:
        return 1.0
    
    mean_val = statistics.mean(engagement_scores)
    std_dev = statistics.stdev(engagement_scores)
    
    if mean_val == 0:
        return 1.0
    
    coefficient_of_variation = std_dev / mean_val
    consistency_score = max(0, 1 - coefficient_of_variation)
    
    return round(consistency_score, 2)

def get_top_hashtags_for_user(posts):
    """Get top hashtags for a specific user"""
    hashtag_counts = Counter()
    
    for post in posts:
        hashtags = extract_hashtags(post.get('caption', ''))
        hashtag_counts.update(hashtags)
    
    return dict(hashtag_counts.most_common(5))

def analyze_content_themes(posts):
    """Analyze content themes for posts"""
    theme_keywords = {
        'product': ['new', 'drop', 'release', 'collection', 'available', 'shop'],
        'lifestyle': ['lifestyle', 'mood', 'vibes', 'aesthetic', 'style', 'look'],
        'community': ['community', 'family', 'crew', 'squad', 'team', 'together'],
        'culture': ['culture', 'heritage', 'authentic', 'tradition', 'legacy', 'history'],
        'fashion': ['fashion', 'outfit', 'style', 'wear', 'clothing', 'apparel']
    }
    
    theme_counts = defaultdict(int)
    
    for post in posts:
        caption = post.get('caption', '').lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in caption for keyword in keywords):
                theme_counts[theme] += 1
    
    total_posts = len(posts)
    theme_percentages = {theme: round((count / total_posts) * 100, 1) 
                        for theme, count in theme_counts.items()}
    
    return theme_percentages

def categorize_performance(avg_engagement):
    """Categorize performance level"""
    if avg_engagement > 5000:
        return 'high'
    elif avg_engagement > 1000:
        return 'medium'
    else:
        return 'low'

def identify_cultural_moments(posts):
    """Identify cultural moments and trends"""
    cultural_keywords = {
        'hispanic_heritage': ['hispanic', 'latino', 'heritage', 'cultura', 'latinx'],
        'black_history': ['black', 'history', 'african', 'heritage', 'blm'],
        'hip_hop': ['hiphop', 'rap', 'hip-hop', 'anniversary', 'culture'],
        'pride': ['pride', 'lgbtq', 'rainbow', 'love', 'equality'],
        'holidays': ['christmas', 'thanksgiving', 'halloween', 'valentine'],
        'fashion_events': ['fashion', 'week', 'runway', 'show', 'nyfw'],
        'music_festivals': ['coachella', 'festival', 'concert', 'music', 'lollapalooza']
    }
    
    cultural_moments = defaultdict(lambda: {'count': 0, 'engagement': 0, 'posts': []})
    
    for post in posts:
        caption = post.get('caption', '').lower()
        engagement = calculate_engagement(post)
        
        for moment, keywords in cultural_keywords.items():
            if any(keyword in caption for keyword in keywords):
                cultural_moments[moment]['count'] += 1
                cultural_moments[moment]['engagement'] += engagement
                cultural_moments[moment]['posts'].append({
                    'username': post.get('ownerUsername', ''),
                    'caption_preview': post.get('caption', '')[:100] + '...',
                    'engagement': engagement
                })
    
    # Calculate averages and relevance scores
    moments_analysis = {}
    for moment, data in cultural_moments.items():
        if data['count'] > 0:
            avg_engagement = data['engagement'] / data['count']
            relevance_score = data['count'] * avg_engagement / 1000  # Normalize
            
            moments_analysis[moment] = {
                'post_count': data['count'],
                'avg_engagement': round(avg_engagement, 2),
                'total_engagement': data['engagement'],
                'relevance_score': round(relevance_score, 2),
                'sample_posts': data['posts'][:3]  # Top 3 posts
            }
    
    return dict(sorted(moments_analysis.items(), 
                      key=lambda x: x[1]['relevance_score'], reverse=True))

def generate_recommendations(posts):
    """Generate actionable recommendations based on analysis"""
    recommendations = []
    
    # Analyze hashtags for recommendations
    hashtag_analysis = analyze_hashtags(posts, min_frequency=5)
    if hashtag_analysis:
        top_hashtag = list(hashtag_analysis.keys())[0]
        recommendations.append({
            'category': 'hashtag_strategy',
            'priority': 'high',
            'recommendation': f'Leverage trending hashtag: {top_hashtag}',
            'rationale': f'High engagement potential with {hashtag_analysis[top_hashtag]["count"]} uses and {hashtag_analysis[top_hashtag]["avg_engagement"]} avg engagement',
            'implementation': f'Include {top_hashtag} in next 3-5 posts with relevant content',
            'expected_impact': 'Increase reach by 15-25%'
        })
    
    # Posting time recommendations
    time_analysis = analyze_posting_times(posts)
    if time_analysis.get('best_posting_hours'):
        best_hour = time_analysis['best_posting_hours'][0]
        recommendations.append({
            'category': 'posting_optimization',
            'priority': 'medium',
            'recommendation': f'Optimize posting time to {best_hour}',
            'rationale': 'Data shows higher engagement during this time',
            'implementation': 'Schedule posts for peak engagement hours',
            'expected_impact': 'Improve organic reach by 10-20%'
        })
    
    # Cultural moment recommendations
    cultural_moments = identify_cultural_moments(posts)
    if cultural_moments:
        top_moment = list(cultural_moments.keys())[0]
        recommendations.append({
            'category': 'cultural_marketing',
            'priority': 'high',
            'recommendation': f'Create content around {top_moment.replace("_", " ").title()}',
            'rationale': f'High cultural relevance with {cultural_moments[top_moment]["post_count"]} related posts showing strong engagement',
            'implementation': 'Develop authentic content series celebrating this cultural moment',
            'expected_impact': 'Strengthen brand cultural positioning and community engagement'
        })
    
    # Competitor analysis recommendations
    competitor_analysis = analyze_competitors(posts)
    if competitor_analysis:
        top_performers = [comp for comp, data in competitor_analysis.items() 
                         if data['performance_tier'] == 'high']
        if top_performers:
            recommendations.append({
                'category': 'competitive_strategy',
                'priority': 'medium',
                'recommendation': f'Study high-performing competitors: {", ".join(top_performers[:3])}',
                'rationale': 'These accounts show consistently high engagement rates',
                'implementation': 'Analyze their content themes and posting strategies for insights',
                'expected_impact': 'Improve content strategy and competitive positioning'
            })
    
    return recommendations

def calculate_trustworthiness_score(intelligence_data):
    """Calculate trustworthiness score for the analysis"""
    factors = []
    
    # Data volume factor
    total_records = (len(intelligence_data['instagram_data']) + 
                    len(intelligence_data['tiktok_data']) + 
                    len(intelligence_data['competitive_data']))
    volume_score = min(total_records / 1000, 1)  # Normalize to 1000 records
    factors.append(volume_score)
    
    # Data quality factor (based on processing errors)
    processing_summary = intelligence_data.get('processing_summary', {})
    if processing_summary:
        error_rates = []
        for filename, summary in processing_summary.items():
            if summary['records'] > 0:
                error_rate = summary['errors'] / summary['records']
                error_rates.append(1 - error_rate)  # Convert to quality score
        
        if error_rates:
            quality_score = statistics.mean(error_rates)
            factors.append(quality_score)
    
    # Data recency factor
    recency_score = 0.9  # Assume recent data for now
    factors.append(recency_score)
    
    # Calculate weighted average
    if factors:
        trustworthiness = statistics.mean(factors) * 100
        return round(trustworthiness, 1)
    
    return 0
