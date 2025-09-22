import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import statistics

INTEL_FOLDER = os.path.join('uploads', 'intel')
PROCESSED_DATA_FILE = os.path.join('data', 'processed_intelligence.json')

# Ensure directories exist
os.makedirs(INTEL_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(PROCESSED_DATA_FILE), exist_ok=True)

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

def competitive_analysis(instagram_data, tiktok_data=None):
    """Perform competitive analysis with actionable insights"""
    competitors = identify_competitors(instagram_data)
    
    analysis = {
        'total_posts_analyzed': len(instagram_data),
        'analysis_date': datetime.now().isoformat(),
        'competitors': {},
        'market_insights': {},
        'opportunities': [],
        'threats': [],
        'recommendations': []
    }
    
    # Analyze each competitor
    for competitor in competitors:
        competitor_posts = [post for post in instagram_data 
                          if post.get('ownerUsername', '').lower() == competitor.lower()]
        
        if competitor_posts:
            competitor_analysis = analyze_competitor(competitor, competitor_posts)
            analysis['competitors'][competitor] = competitor_analysis
    
    # Generate market insights
    analysis['market_insights'] = generate_market_insights(instagram_data, tiktok_data)
    
    # Identify opportunities and threats
    analysis['opportunities'] = identify_opportunities(analysis['competitors'], analysis['market_insights'])
    analysis['threats'] = identify_threats(analysis['competitors'], analysis['market_insights'])
    
    # Generate actionable recommendations
    analysis['recommendations'] = generate_recommendations(analysis)
    
    return analysis

def identify_competitors(data):
    """Identify key competitors from the data"""
    # Known streetwear competitors
    known_competitors = [
        'supremenewyork', 'offwhite', 'fearofgod', 'kith', 'stussy', 
        'bape_us', 'antisocialsocialclub', 'golf_wang', 'braindead',
        'humanmade', 'neighborhoodnyc', 'wtaps', 'visvim'
    ]
    
    # Find competitors present in data
    found_competitors = []
    usernames = set(post.get('ownerUsername', '').lower() for post in data)
    
    for competitor in known_competitors:
        if competitor.lower() in usernames:
            found_competitors.append(competitor)
    
    return found_competitors

def analyze_competitor(competitor_name, posts):
    """Analyze individual competitor performance"""
    if not posts:
        return {}
    
    total_engagement = sum(calculate_engagement(post) for post in posts)
    avg_engagement = total_engagement / len(posts)
    
    # Analyze posting patterns
    posting_frequency = analyze_posting_frequency(posts)
    
    # Analyze content themes
    content_themes = analyze_content_themes(posts)
    
    # Calculate engagement metrics
    engagement_metrics = calculate_detailed_engagement_metrics(posts)
    
    return {
        'total_posts': len(posts),
        'total_engagement': total_engagement,
        'avg_engagement': round(avg_engagement, 2),
        'posting_frequency': posting_frequency,
        'content_themes': content_themes,
        'engagement_metrics': engagement_metrics,
        'performance_score': calculate_performance_score(posts),
        'strengths': identify_competitor_strengths(posts),
        'weaknesses': identify_competitor_weaknesses(posts)
    }

def analyze_posting_frequency(posts):
    """Analyze posting frequency patterns"""
    if not posts:
        return {}
    
    # Group posts by date
    posts_by_date = defaultdict(int)
    for post in posts:
        timestamp = post.get('timestamp', '')
        if timestamp:
            try:
                date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                posts_by_date[date.isoformat()] += 1
            except:
                continue
    
    if not posts_by_date:
        return {}
    
    daily_counts = list(posts_by_date.values())
    
    return {
        'avg_posts_per_day': round(statistics.mean(daily_counts), 2),
        'max_posts_per_day': max(daily_counts),
        'min_posts_per_day': min(daily_counts),
        'total_active_days': len(posts_by_date),
        'consistency_score': calculate_consistency_score(daily_counts)
    }

def analyze_content_themes(posts):
    """Analyze content themes and topics"""
    themes = defaultdict(int)
    
    # Theme keywords
    theme_keywords = {
        'product_showcase': ['new', 'drop', 'release', 'collection', 'available'],
        'lifestyle': ['lifestyle', 'mood', 'vibes', 'aesthetic', 'style'],
        'community': ['community', 'family', 'crew', 'squad', 'team'],
        'culture': ['culture', 'heritage', 'authentic', 'tradition', 'legacy'],
        'collaboration': ['collab', 'collaboration', 'partnership', 'with'],
        'behind_scenes': ['behind', 'bts', 'process', 'making', 'studio']
    }
    
    for post in posts:
        caption = post.get('caption', '').lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in caption for keyword in keywords):
                themes[theme] += 1
    
    # Calculate theme percentages
    total_posts = len(posts)
    theme_percentages = {theme: round((count / total_posts) * 100, 1) 
                        for theme, count in themes.items()}
    
    return theme_percentages

def calculate_detailed_engagement_metrics(posts):
    """Calculate detailed engagement metrics"""
    if not posts:
        return {}
    
    likes = [post.get('likesCount', 0) for post in posts]
    comments = [post.get('commentsCount', 0) for post in posts]
    
    return {
        'avg_likes': round(statistics.mean(likes), 2),
        'avg_comments': round(statistics.mean(comments), 2),
        'engagement_rate': calculate_engagement_rate(posts),
        'top_performing_post': find_top_performing_post(posts),
        'engagement_consistency': calculate_engagement_consistency(posts)
    }

def calculate_engagement_rate(posts):
    """Calculate engagement rate (simplified without follower count)"""
    if not posts:
        return 0
    
    total_engagement = sum(calculate_engagement(post) for post in posts)
    # Estimate engagement rate based on average performance
    avg_engagement = total_engagement / len(posts)
    
    # Rough engagement rate estimation (would need follower count for accuracy)
    estimated_rate = min(avg_engagement / 1000, 10)  # Cap at 10%
    return round(estimated_rate, 2)

def find_top_performing_post(posts):
    """Find the top performing post"""
    if not posts:
        return None
    
    top_post = max(posts, key=calculate_engagement)
    
    return {
        'id': top_post.get('id', ''),
        'caption': top_post.get('caption', '')[:100] + '...' if len(top_post.get('caption', '')) > 100 else top_post.get('caption', ''),
        'engagement_score': calculate_engagement(top_post),
        'likes': top_post.get('likesCount', 0),
        'comments': top_post.get('commentsCount', 0)
    }

def calculate_consistency_score(values):
    """Calculate consistency score based on standard deviation"""
    if len(values) < 2:
        return 1.0
    
    mean_val = statistics.mean(values)
    std_dev = statistics.stdev(values)
    
    # Lower standard deviation relative to mean = higher consistency
    if mean_val == 0:
        return 1.0
    
    coefficient_of_variation = std_dev / mean_val
    consistency_score = max(0, 1 - coefficient_of_variation)
    
    return round(consistency_score, 2)

def calculate_engagement_consistency(posts):
    """Calculate engagement consistency"""
    engagement_scores = [calculate_engagement(post) for post in posts]
    return calculate_consistency_score(engagement_scores)

def calculate_performance_score(posts):
    """Calculate overall performance score for competitor"""
    if not posts:
        return 0
    
    # Factors: engagement, consistency, posting frequency
    avg_engagement = statistics.mean([calculate_engagement(post) for post in posts])
    consistency = calculate_engagement_consistency(posts)
    frequency_score = min(len(posts) / 30, 1)  # Normalize to 30 posts max
    
    # Weighted score
    performance_score = (avg_engagement * 0.5) + (consistency * 0.3) + (frequency_score * 0.2)
    
    return round(performance_score, 2)

def identify_competitor_strengths(posts):
    """Identify competitor strengths"""
    strengths = []
    
    if not posts:
        return strengths
    
    avg_engagement = statistics.mean([calculate_engagement(post) for post in posts])
    consistency = calculate_engagement_consistency(posts)
    posting_frequency = len(posts)
    
    if avg_engagement > 1000:
        strengths.append("High engagement rates")
    
    if consistency > 0.7:
        strengths.append("Consistent performance")
    
    if posting_frequency > 20:
        strengths.append("Active posting schedule")
    
    # Analyze content themes
    themes = analyze_content_themes(posts)
    if themes.get('community', 0) > 20:
        strengths.append("Strong community engagement")
    
    if themes.get('culture', 0) > 15:
        strengths.append("Cultural authenticity focus")
    
    return strengths

def identify_competitor_weaknesses(posts):
    """Identify competitor weaknesses"""
    weaknesses = []
    
    if not posts:
        return ["No data available"]
    
    avg_engagement = statistics.mean([calculate_engagement(post) for post in posts])
    consistency = calculate_engagement_consistency(posts)
    posting_frequency = len(posts)
    
    if avg_engagement < 500:
        weaknesses.append("Low engagement rates")
    
    if consistency < 0.4:
        weaknesses.append("Inconsistent performance")
    
    if posting_frequency < 10:
        weaknesses.append("Infrequent posting")
    
    # Analyze content diversity
    themes = analyze_content_themes(posts)
    if len(themes) < 3:
        weaknesses.append("Limited content diversity")
    
    return weaknesses

def generate_market_insights(instagram_data, tiktok_data=None):
    """Generate market insights from data analysis"""
    insights = {
        'trending_hashtags': analyze_hashtags(instagram_data, min_frequency=3),
        'content_trends': identify_content_trends(instagram_data),
        'engagement_patterns': analyze_engagement_patterns(instagram_data),
        'cultural_moments': identify_cultural_moments(instagram_data),
        'market_gaps': identify_market_gaps(instagram_data)
    }
    
    if tiktok_data:
        insights['tiktok_trends'] = analyze_tiktok_trends(tiktok_data)
    
    return insights

def identify_content_trends(data):
    """Identify trending content types and formats"""
    content_types = defaultdict(lambda: {'count': 0, 'total_engagement': 0})
    
    for post in data:
        # Determine content type from caption or other indicators
        caption = post.get('caption', '').lower()
        
        if any(word in caption for word in ['video', 'watch', 'clip']):
            content_type = 'video'
        elif any(word in caption for word in ['carousel', 'swipe', 'slide']):
            content_type = 'carousel'
        elif any(word in caption for word in ['story', 'behind', 'bts']):
            content_type = 'story'
        else:
            content_type = 'single_image'
        
        content_types[content_type]['count'] += 1
        content_types[content_type]['total_engagement'] += calculate_engagement(post)
    
    # Calculate average engagement per content type
    trends = {}
    for content_type, data in content_types.items():
        if data['count'] > 0:
            trends[content_type] = {
                'count': data['count'],
                'avg_engagement': round(data['total_engagement'] / data['count'], 2),
                'total_engagement': data['total_engagement']
            }
    
    return dict(sorted(trends.items(), key=lambda x: x[1]['avg_engagement'], reverse=True))

def analyze_engagement_patterns(data):
    """Analyze engagement patterns over time"""
    if not data:
        return {}
    
    # Group by hour of day and day of week
    hourly_engagement = defaultdict(list)
    daily_engagement = defaultdict(list)
    
    for post in data:
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
                  for hour, engagements in hourly_engagement.items()}
    daily_avg = {day: round(statistics.mean(engagements), 2) 
                 for day, engagements in daily_engagement.items()}
    
    return {
        'best_posting_hours': dict(sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)[:3]),
        'best_posting_days': dict(sorted(daily_avg.items(), key=lambda x: x[1], reverse=True)[:3]),
        'hourly_patterns': hourly_avg,
        'daily_patterns': daily_avg
    }

def identify_cultural_moments(data):
    """Identify cultural moments and events from content"""
    cultural_keywords = {
        'hispanic_heritage': ['hispanic', 'latino', 'heritage', 'cultura'],
        'black_history': ['black', 'history', 'african', 'heritage'],
        'hip_hop': ['hiphop', 'rap', 'hip-hop', 'anniversary'],
        'pride': ['pride', 'lgbtq', 'rainbow', 'love'],
        'holidays': ['christmas', 'thanksgiving', 'halloween', 'valentine'],
        'fashion_weeks': ['fashion', 'week', 'runway', 'show'],
        'music_events': ['coachella', 'festival', 'concert', 'music']
    }
    
    cultural_moments = defaultdict(lambda: {'count': 0, 'posts': [], 'engagement': 0})
    
    for post in data:
        caption = post.get('caption', '').lower()
        engagement = calculate_engagement(post)
        
        for moment, keywords in cultural_keywords.items():
            if any(keyword in caption for keyword in keywords):
                cultural_moments[moment]['count'] += 1
                cultural_moments[moment]['posts'].append(post.get('id', ''))
                cultural_moments[moment]['engagement'] += engagement
    
    # Calculate averages and sort by relevance
    moments = {}
    for moment, data in cultural_moments.items():
        if data['count'] > 0:
            moments[moment] = {
                'count': data['count'],
                'avg_engagement': round(data['engagement'] / data['count'], 2),
                'total_engagement': data['engagement'],
                'relevance_score': data['count'] * (data['engagement'] / data['count'])
            }
    
    return dict(sorted(moments.items(), key=lambda x: x[1]['relevance_score'], reverse=True))

def identify_market_gaps(data):
    """Identify potential market gaps and opportunities"""
    gaps = []
    
    # Analyze content themes to find underrepresented areas
    all_themes = analyze_content_themes(data)
    
    # Define important themes for streetwear
    important_themes = ['sustainability', 'diversity', 'community', 'culture', 'collaboration']
    
    for theme in important_themes:
        if theme not in all_themes or all_themes[theme] < 10:
            gaps.append({
                'gap': theme,
                'opportunity': f"Underrepresented {theme} content",
                'current_coverage': all_themes.get(theme, 0),
                'recommendation': f"Increase {theme}-focused content"
            })
    
    return gaps

def analyze_tiktok_trends(tiktok_data):
    """Analyze TikTok specific trends"""
    if not tiktok_data:
        return {}
    
    return {
        'total_videos': len(tiktok_data),
        'avg_views': round(statistics.mean([post.get('viewsCount', 0) for post in tiktok_data]), 2),
        'trending_sounds': extract_trending_sounds(tiktok_data),
        'video_lengths': analyze_video_lengths(tiktok_data)
    }

def extract_trending_sounds(tiktok_data):
    """Extract trending sounds from TikTok data"""
    sounds = defaultdict(int)
    
    for video in tiktok_data:
        sound = video.get('musicMeta', {}).get('musicName', '')
        if sound:
            sounds[sound] += 1
    
    return dict(sorted(sounds.items(), key=lambda x: x[1], reverse=True)[:10])

def analyze_video_lengths(tiktok_data):
    """Analyze video length patterns"""
    lengths = []
    
    for video in tiktok_data:
        duration = video.get('videoMeta', {}).get('duration', 0)
        if duration:
            lengths.append(duration)
    
    if not lengths:
        return {}
    
    return {
        'avg_length': round(statistics.mean(lengths), 2),
        'median_length': statistics.median(lengths),
        'most_common_range': categorize_video_lengths(lengths)
    }

def categorize_video_lengths(lengths):
    """Categorize video lengths into ranges"""
    ranges = {'short (0-15s)': 0, 'medium (16-30s)': 0, 'long (31s+)': 0}
    
    for length in lengths:
        if length <= 15:
            ranges['short (0-15s)'] += 1
        elif length <= 30:
            ranges['medium (16-30s)'] += 1
        else:
            ranges['long (31s+)'] += 1
    
    return max(ranges, key=ranges.get)

def identify_opportunities(competitors_analysis, market_insights):
    """Identify strategic opportunities based on analysis"""
    opportunities = []
    
    # Content opportunities
    trending_hashtags = market_insights.get('trending_hashtags', {})
    top_hashtags = list(trending_hashtags.keys())[:5]
    
    if top_hashtags:
        opportunities.append({
            'type': 'content',
            'opportunity': 'Leverage trending hashtags',
            'details': f"Top trending: {', '.join(top_hashtags)}",
            'priority': 'high',
            'estimated_impact': 'Increase reach by 25-40%'
        })
    
    # Cultural moments
    cultural_moments = market_insights.get('cultural_moments', {})
    if cultural_moments:
        top_moment = list(cultural_moments.keys())[0]
        opportunities.append({
            'type': 'cultural',
            'opportunity': f'Capitalize on {top_moment} trend',
            'details': f"High engagement potential: {cultural_moments[top_moment]['avg_engagement']} avg engagement",
            'priority': 'high',
            'estimated_impact': 'Strengthen cultural positioning'
        })
    
    # Competitor gaps
    for competitor, analysis in competitors_analysis.items():
        weaknesses = analysis.get('weaknesses', [])
        if 'Limited content diversity' in weaknesses:
            opportunities.append({
                'type': 'competitive',
                'opportunity': f'Outperform {competitor} with diverse content',
                'details': 'Competitor has limited content variety',
                'priority': 'medium',
                'estimated_impact': 'Gain market share through better content strategy'
            })
    
    return opportunities

def identify_threats(competitors_analysis, market_insights):
    """Identify potential threats from competitive analysis"""
    threats = []
    
    # High-performing competitors
    for competitor, analysis in competitors_analysis.items():
        performance_score = analysis.get('performance_score', 0)
        if performance_score > 1000:
            threats.append({
                'type': 'competitive',
                'threat': f'{competitor} high performance',
                'details': f'Performance score: {performance_score}, Strong engagement',
                'severity': 'medium',
                'mitigation': 'Improve content quality and consistency'
            })
    
    # Market saturation
    total_competitors = len(competitors_analysis)
    if total_competitors > 5:
        threats.append({
            'type': 'market',
            'threat': 'High market competition',
            'details': f'{total_competitors} active competitors identified',
            'severity': 'high',
            'mitigation': 'Focus on unique brand positioning and cultural authenticity'
        })
    
    return threats

def generate_recommendations(analysis):
    """Generate actionable recommendations based on complete analysis"""
    recommendations = []
    
    # Content recommendations
    market_insights = analysis.get('market_insights', {})
    trending_hashtags = market_insights.get('trending_hashtags', {})
    
    if trending_hashtags:
        top_hashtag = list(trending_hashtags.keys())[0]
        recommendations.append({
            'category': 'content_strategy',
            'recommendation': f'Incorporate trending hashtag {top_hashtag}',
            'rationale': f'High trend score: {trending_hashtags[top_hashtag]["trend_score"]}',
            'implementation': 'Include in next 3-5 posts with relevant content',
            'expected_outcome': 'Increased reach and engagement',
            'priority': 'high'
        })
    
    # Posting optimization
    engagement_patterns = market_insights.get('engagement_patterns', {})
    if engagement_patterns.get('best_posting_hours'):
        best_hour = list(engagement_patterns['best_posting_hours'].keys())[0]
        recommendations.append({
            'category': 'posting_optimization',
            'recommendation': f'Post during peak engagement hour: {best_hour}:00',
            'rationale': f'Highest average engagement: {engagement_patterns["best_posting_hours"][str(best_hour)]}',
            'implementation': 'Schedule posts for this time zone',
            'expected_outcome': 'Improved organic reach and engagement',
            'priority': 'medium'
        })
    
    # Cultural opportunities
    cultural_moments = market_insights.get('cultural_moments', {})
    if cultural_moments:
        top_moment = list(cultural_moments.keys())[0]
        recommendations.append({
            'category': 'cultural_marketing',
            'recommendation': f'Create content around {top_moment}',
            'rationale': f'High cultural relevance and engagement potential',
            'implementation': 'Develop authentic content series celebrating this cultural moment',
            'expected_outcome': 'Strengthened brand cultural positioning',
            'priority': 'high'
        })
    
    # Competitive positioning
    competitors = analysis.get('competitors', {})
    if competitors:
        # Find competitor with highest performance
        top_competitor = max(competitors.items(), key=lambda x: x[1].get('performance_score', 0))
        recommendations.append({
            'category': 'competitive_strategy',
            'recommendation': f'Study and differentiate from {top_competitor[0]} strategy',
            'rationale': f'Top performing competitor with score: {top_competitor[1]["performance_score"]}',
            'implementation': 'Analyze their content themes and develop unique positioning',
            'expected_outcome': 'Improved competitive positioning',
            'priority': 'medium'
        })
    
    return recommendations

def generate_intelligence_report(instagram_file=None, tiktok_file=None, competitive_file=None):
    """Generate comprehensive intelligence report from uploaded data files"""
    report = {
        'report_id': str(uuid.uuid4()),
        'generated_at': datetime.now().isoformat(),
        'data_sources': [],
        'executive_summary': {},
        'detailed_analysis': {},
        'recommendations': [],
        'data_quality': {},
        'trustworthiness_score': 0
    }
    
    # Load and validate data
    instagram_data = []
    tiktok_data = []
    competitive_data = []
    
    if instagram_file and os.path.exists(instagram_file):
        ig_result = load_jsonl_data(instagram_file)
        if ig_result['status'] == 'success':
            instagram_data = ig_result['data']
            report['data_sources'].append({
                'source': 'Instagram',
                'file': os.path.basename(instagram_file),
                'records': len(instagram_data),
                'errors': len(ig_result['errors']),
                'quality_score': calculate_data_quality_score(ig_result)
            })
    
    if tiktok_file and os.path.exists(tiktok_file):
        tt_result = load_jsonl_data(tiktok_file)
        if tt_result['status'] == 'success':
            tiktok_data = tt_result['data']
            report['data_sources'].append({
                'source': 'TikTok',
                'file': os.path.basename(tiktok_file),
                'records': len(tiktok_data),
                'errors': len(tt_result['errors']),
                'quality_score': calculate_data_quality_score(tt_result)
            })
    
    if competitive_file and os.path.exists(competitive_file):
        comp_result = load_jsonl_data(competitive_file)
        if comp_result['status'] == 'success':
            competitive_data = comp_result['data']
            report['data_sources'].append({
                'source': 'Competitive Intelligence',
                'file': os.path.basename(competitive_file),
                'records': len(competitive_data),
                'errors': len(comp_result['errors']),
                'quality_score': calculate_data_quality_score(comp_result)
            })
    
    # Perform analysis if data is available
    if instagram_data or competitive_data:
        all_data = instagram_data + competitive_data
        
        # Competitive analysis
        competitive_analysis = competitive_analysis(all_data, tiktok_data)
        
        # Generate executive summary
        report['executive_summary'] = generate_executive_summary(
            len(all_data), competitive_analysis, len(tiktok_data)
        )
        
        # Detailed analysis
        report['detailed_analysis'] = {
            'hashtag_analysis': analyze_hashtags(all_data),
            'competitive_landscape': competitive_analysis,
            'market_insights': competitive_analysis['market_insights'],
            'cultural_intelligence': identify_cultural_moments(all_data)
        }
        
        # Recommendations
        report['recommendations'] = competitive_analysis['recommendations']
        
        # Calculate trustworthiness score
        report['trustworthiness_score'] = calculate_trustworthiness_score(report)
    
    # Save processed report
    save_processed_intelligence(report)
    
    return report

def calculate_data_quality_score(data_result):
    """Calculate data quality score based on errors and completeness"""
    total_records = data_result.get('total_records', 0)
    error_count = data_result.get('error_count', 0)
    
    if total_records == 0:
        return 0
    
    error_rate = error_count / total_records
    quality_score = max(0, 1 - error_rate) * 100
    
    return round(quality_score, 1)

def calculate_trustworthiness_score(report):
    """Calculate overall trustworthiness score for the intelligence report"""
    factors = []
    
    # Data quality factor
    data_sources = report.get('data_sources', [])
    if data_sources:
        avg_quality = statistics.mean([source['quality_score'] for source in data_sources])
        factors.append(avg_quality / 100)
    
    # Data volume factor
    total_records = sum(source['records'] for source in data_sources)
    volume_score = min(total_records / 1000, 1)  # Normalize to 1000 records
    factors.append(volume_score)
    
    # Analysis completeness factor
    detailed_analysis = report.get('detailed_analysis', {})
    completeness_score = len(detailed_analysis) / 4  # 4 expected analysis types
    factors.append(completeness_score)
    
    # Recommendation quality factor
    recommendations = report.get('recommendations', [])
    rec_score = min(len(recommendations) / 5, 1)  # Normalize to 5 recommendations
    factors.append(rec_score)
    
    # Calculate weighted average
    if factors:
        trustworthiness = statistics.mean(factors) * 100
        return round(trustworthiness, 1)
    
    return 0

def generate_executive_summary(total_posts, competitive_analysis, tiktok_count):
    """Generate executive summary for the intelligence report"""
    return {
        'total_posts_analyzed': total_posts,
        'tiktok_videos_analyzed': tiktok_count,
        'competitors_identified': len(competitive_analysis.get('competitors', {})),
        'key_opportunities': len(competitive_analysis.get('opportunities', [])),
        'market_threats': len(competitive_analysis.get('threats', [])),
        'actionable_recommendations': len(competitive_analysis.get('recommendations', [])),
        'analysis_confidence': 'High' if total_posts > 100 else 'Medium' if total_posts > 50 else 'Low'
    }

def save_processed_intelligence(report_data):
    """Save processed intelligence report"""
    try:
        with open(PROCESSED_DATA_FILE, 'w') as f:
            json.dump(report_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving processed intelligence: {e}")
        return False

def load_processed_intelligence():
    """Load processed intelligence report"""
    try:
        if os.path.exists(PROCESSED_DATA_FILE):
            with open(PROCESSED_DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading processed intelligence: {e}")
        return {}

# Auto-scan for data files on import
def auto_scan_intel_files():
    """Automatically scan for intelligence files in uploads/intel directory"""
    intel_files = {
        'instagram': None,
        'tiktok': None,
        'competitive': None
    }
    
    if os.path.exists(INTEL_FOLDER):
        for filename in os.listdir(INTEL_FOLDER):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(INTEL_FOLDER, filename)
                
                if 'instagram' in filename.lower():
                    intel_files['instagram'] = filepath
                elif 'tiktok' in filename.lower():
                    intel_files['tiktok'] = filepath
                elif 'competitive' in filename.lower():
                    intel_files['competitive'] = filepath
    
    return intel_files

# Import required modules
import uuid

# Initialize on import
auto_scan_intel_files()
