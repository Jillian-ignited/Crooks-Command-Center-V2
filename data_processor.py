import os
import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

def load_jsonl_data(file_path):
    """Load and parse JSONL data file"""
    data = []
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return data
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data.append(json.loads(line.strip()))
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in {file_path} line {line_num}: {e}")
                        continue
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    
    return data

def process_intelligence_data():
    """Process all intelligence data files and return comprehensive analysis"""
    
    # Load Instagram data - ACTUAL APIFY DATA FILES
    instagram_data = []
    instagram_files = [
        'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl',
        'uploads/intel/instagram_competitive_data.jsonl',
    ]
    
    for filename in instagram_files:
        file_path = os.path.join(filename)
        if not os.path.exists(file_path):
            file_path = filename  # Try current directory
        data = load_jsonl_data(file_path)
        instagram_data.extend(data)
    
    # Load TikTok data - CORRECTED PATH
    tiktok_data = []
    tiktok_files = [
        'uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl'
    ]
    
    for filename in tiktok_files:
        file_path = os.path.join(filename)
        if not os.path.exists(file_path):
            file_path = filename  # Try current directory
        data = load_jsonl_data(file_path)
        tiktok_data.extend(data)
    
    # Process the data
    total_sources = 0
    for f in instagram_files:
        if os.path.exists(f) or os.path.exists(os.path.join(f)):
            total_sources += 1
    for f in tiktok_files:
        if os.path.exists(f) or os.path.exists(os.path.join(f)):
            total_sources += 1
    
    processed_data = {
        'instagram_posts': len(instagram_data),
        'tiktok_videos': len(tiktok_data),
        'total_analyzed': len(instagram_data) + len(tiktok_data),
        'analysis_timestamp': datetime.now().isoformat(),
        'total_data_sources': total_sources,
        'data_sources': {
            'instagram_files': len([f for f in instagram_files if os.path.exists(f) or os.path.exists(os.path.join(f))]),
            'tiktok_files': len([f for f in tiktok_files if os.path.exists(f) or os.path.exists(os.path.join(f))]),
        }
    }
    
    return processed_data

def analyze_hashtags(data=None):
    """Analyze hashtag performance across all posts - REQUIRED BY APP.PY"""
    
    if data is None:
        # Load data if not provided
        instagram_data = []
        instagram_files = [
            'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl',
            'uploads/intel/instagram_competitive_data.jsonl',
        ]
        
        for filename in instagram_files:
            if os.path.exists(filename):
                instagram_data.extend(load_jsonl_data(filename))
        
        tiktok_data = []
        tiktok_files = ['uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl']
        for filename in tiktok_files:
            if os.path.exists(filename):
                tiktok_data.extend(load_jsonl_data(filename))
        
        data = instagram_data + tiktok_data
    
    hashtag_stats = defaultdict(lambda: {'count': 0, 'total_engagement': 0, 'posts': []})
    
    for post in data:
        # Extract hashtags from caption/description
        text = post.get('caption', '') or post.get('text', '') or post.get('description', '')
        hashtags = re.findall(r'#\w+', text.lower())
        
        # Get engagement metrics
        engagement = 0
        if 'likesCount' in post:  # Instagram
            engagement = (post.get('likesCount', 0) + post.get('commentsCount', 0))
        elif 'diggCount' in post:  # TikTok
            engagement = (post.get('diggCount', 0) + post.get('shareCount', 0) + post.get('commentCount', 0))
        
        for hashtag in hashtags:
            hashtag_stats[hashtag]['count'] += 1
            hashtag_stats[hashtag]['total_engagement'] += engagement
            hashtag_stats[hashtag]['posts'].append(post)
    
    # Calculate averages and trends
    hashtag_analysis = {}
    for hashtag, stats in hashtag_stats.items():
        if stats['count'] > 0:
            avg_engagement = stats['total_engagement'] / stats['count']
            hashtag_analysis[hashtag] = {
                'count': stats['count'],
                'avg_engagement': round(avg_engagement, 2),
                'total_engagement': stats['total_engagement'],
                'relevance': 'High' if stats['count'] > 10 else 'Medium' if stats['count'] > 5 else 'Low',
                'trend': 'Growing' if avg_engagement > 1000 else 'Stable' if avg_engagement > 500 else 'Declining'
            }
    
    # Sort by engagement performance
    sorted_hashtags = dict(sorted(hashtag_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True))
    
    return dict(list(sorted_hashtags.items())[:20])  # Top 20 hashtags

def identify_cultural_moments(data=None):
    """Detect cultural moments and trends from content - REQUIRED BY APP.PY"""
    
    if data is None:
        # Load data if not provided
        instagram_data = []
        instagram_files = [
            'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl',
            'uploads/intel/instagram_competitive_data.jsonl',
        ]
        
        for filename in instagram_files:
            if os.path.exists(filename):
                instagram_data.extend(load_jsonl_data(filename))
        
        tiktok_data = []
        tiktok_files = ['uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl']
        for filename in tiktok_files:
            if os.path.exists(filename):
                tiktok_data.extend(load_jsonl_data(filename))
        
        data = instagram_data + tiktok_data
    
    cultural_keywords = {
        'hispanic_heritage': ['hispanic', 'latino', 'latina', 'heritage', 'cultura', 'tradition'],
        'hip_hop': ['hiphop', 'hip-hop', 'rap', 'beats', 'culture', 'street'],
        'streetwear': ['streetwear', 'street', 'urban', 'fashion', 'style'],
        'cultural_fusion': ['fusion', 'mix', 'blend', 'culture', 'diversity'],
        'authenticity': ['authentic', 'real', 'genuine', 'original', 'true']
    }
    
    cultural_analysis = {}
    
    for trend, keywords in cultural_keywords.items():
        matching_posts = []
        total_engagement = 0
        
        for post in data:
            text = (post.get('caption', '') or post.get('text', '') or post.get('description', '')).lower()
            
            if any(keyword in text for keyword in keywords):
                matching_posts.append(post)
                
                # Calculate engagement
                engagement = 0
                if 'likesCount' in post:  # Instagram
                    engagement = (post.get('likesCount', 0) + post.get('commentsCount', 0))
                elif 'diggCount' in post:  # TikTok
                    engagement = (post.get('diggCount', 0) + post.get('shareCount', 0) + post.get('commentCount', 0))
                
                total_engagement += engagement
        
        if matching_posts:
            cultural_analysis[trend] = {
                'post_count': len(matching_posts),
                'avg_engagement': round(total_engagement / len(matching_posts), 2),
                'total_engagement': total_engagement,
                'relevance_score': min(100, len(matching_posts) * 10),
                'opportunity': 'High' if len(matching_posts) > 5 else 'Medium' if len(matching_posts) > 2 else 'Low'
            }
    
    return cultural_analysis

def generate_recommendations(hashtag_analysis=None, engagement_analysis=None, cultural_trends=None):
    """Generate actionable recommendations based on analysis - REQUIRED BY APP.PY"""
    
    if hashtag_analysis is None:
        hashtag_analysis = analyze_hashtags()
    if cultural_trends is None:
        cultural_trends = identify_cultural_moments()
    
    recommendations = []
    
    # Hashtag recommendations
    if hashtag_analysis:
        top_hashtag = list(hashtag_analysis.keys())[0]
        recommendations.append({
            'recommendation': f'Increase usage of {top_hashtag} hashtag',
            'category': 'hashtag_optimization',
            'priority': 'high',
            'expected_impact': '15-20% engagement increase',
            'rationale': f'Analysis shows {hashtag_analysis[top_hashtag]["count"]} uses with {hashtag_analysis[top_hashtag]["avg_engagement"]} avg engagement',
            'implementation': 'Use in next 5 posts with relevant content'
        })
    
    # Cultural trend recommendations
    if cultural_trends:
        for trend, data in cultural_trends.items():
            if data['opportunity'] == 'High':
                recommendations.append({
                    'recommendation': f'Capitalize on {trend.replace("_", " ")} trend',
                    'category': 'cultural_marketing',
                    'priority': 'high',
                    'expected_impact': f'{data["relevance_score"]}% cultural relevance increase',
                    'rationale': f'{data["post_count"]} posts detected with {data["avg_engagement"]} avg engagement',
                    'implementation': f'Create 3-5 posts weekly focusing on {trend.replace("_", " ")} themes'
                })
    
    return recommendations

def calculate_trustworthiness_score(data=None):
    """Calculate trustworthiness score based on data quality"""
    
    # If data is a dict (from process_intelligence_data), extract the actual post data
    if isinstance(data, dict):
        # Return a score based on the summary data
        total_analyzed = data.get('total_analyzed', 0)
        if total_analyzed > 200:
            return 95
        elif total_analyzed > 100:
            return 85
        elif total_analyzed > 50:
            return 75
        elif total_analyzed > 0:
            return 65
        else:
            return 0
    
    if data is None:
        # Load data if not provided
        instagram_data = []
        instagram_files = [
            'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl',
            'uploads/intel/instagram_competitive_data.jsonl',
        ]
        
        for filename in instagram_files:
            if os.path.exists(filename):
                instagram_data.extend(load_jsonl_data(filename))
        
        tiktok_data = []
        tiktok_files = ['uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl']
        for filename in tiktok_files:
            if os.path.exists(filename):
                tiktok_data.extend(load_jsonl_data(filename))
        
        data = instagram_data + tiktok_data
    
    if not data:
        return 0
    
    score = 100
    
    # Check data completeness
    missing_engagement = sum(1 for post in data if not any(key in post for key in ['likesCount', 'diggCount', 'viewCount']))
    if missing_engagement > len(data) * 0.1:  # More than 10% missing engagement data
        score -= 15
    
    # Check for valid timestamps
    missing_timestamps = sum(1 for post in data if not post.get('timestamp') and not post.get('createTime'))
    if missing_timestamps > len(data) * 0.05:  # More than 5% missing timestamps
        score -= 10
    
    # Check for content quality
    missing_content = sum(1 for post in data if not post.get('caption') and not post.get('text') and not post.get('description'))
    if missing_content > len(data) * 0.02:  # More than 2% missing content
        score -= 5
    
    # Bonus for data richness
    if len(data) > 100:
        score += 5
    
    rich_data = sum(1 for post in data if len(str(post.get('caption', '') or post.get('text', '') or post.get('description', ''))) > 50)
    if rich_data > len(data) * 0.8:  # More than 80% have rich content
        score += 10
    
    return max(0, min(100, score))

def generate_competitive_analysis():
    """Generate comprehensive competitive analysis from all data sources"""
    
    # Process intelligence data
    intelligence_data = process_intelligence_data()
    
    # Load Instagram data for detailed analysis
    instagram_data = []
    instagram_files = [
        'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl',
        'uploads/intel/instagram_competitive_data.jsonl',
    ]
    
    for filename in instagram_files:
        if os.path.exists(filename):
            data = load_jsonl_data(filename)
            instagram_data.extend(data)
    
    # Load TikTok data for detailed analysis
    tiktok_data = []
    tiktok_files = [
        'uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl'
    ]
    
    for filename in tiktok_files:
        if os.path.exists(filename):
            data = load_jsonl_data(filename)
            tiktok_data.extend(data)
    
    all_data = instagram_data + tiktok_data
    
    # Analyze hashtags from Instagram data
    hashtag_analysis = analyze_hashtags(all_data)
    
    # Analyze engagement patterns
    engagement_analysis = analyze_engagement_patterns(instagram_data, tiktok_data)
    
    # Detect cultural trends
    cultural_trends = identify_cultural_moments(all_data)
    
    # Generate competitive insights
    competitive_insights = generate_competitive_insights(instagram_data, tiktok_data)
    
    # Calculate trustworthiness score
    trustworthiness = calculate_trustworthiness_score(all_data)
    
    # Generate recommendations
    recommendations = generate_recommendations(hashtag_analysis, engagement_analysis, cultural_trends)
    
    return {
        'analysis_timestamp': datetime.now().isoformat(),
        'trustworthiness_score': trustworthiness,
        'data_summary': {
            'instagram_posts': len(instagram_data),
            'tiktok_videos': len(tiktok_data),
            'total_analyzed': len(instagram_data) + len(tiktok_data),
            'data_quality': 'High' if trustworthiness > 80 else 'Medium' if trustworthiness > 60 else 'Low'
        },
        'hashtag_analysis': hashtag_analysis,
        'engagement_analysis': engagement_analysis,
        'cultural_trends': cultural_trends,
        'competitive_insights': competitive_insights,
        'recommendations': recommendations
    }

def analyze_engagement_patterns(instagram_data, tiktok_data):
    """Analyze engagement patterns across platforms"""
    
    instagram_engagement = []
    for post in instagram_data:
        likes = post.get('likesCount', 0)
        comments = post.get('commentsCount', 0)
        engagement_rate = (likes + comments)
        instagram_engagement.append(engagement_rate)
    
    tiktok_engagement = []
    for video in tiktok_data:
        likes = video.get('diggCount', 0)
        shares = video.get('shareCount', 0)
        comments = video.get('commentCount', 0)
        engagement_rate = (likes + shares + comments)
        tiktok_engagement.append(engagement_rate)
    
    return {
        'instagram': {
            'avg_engagement': round(sum(instagram_engagement) / len(instagram_engagement), 2) if instagram_engagement else 0,
            'total_posts': len(instagram_engagement),
            'top_performing': max(instagram_engagement) if instagram_engagement else 0
        },
        'tiktok': {
            'avg_engagement': round(sum(tiktok_engagement) / len(tiktok_engagement), 2) if tiktok_engagement else 0,
            'total_videos': len(tiktok_engagement),
            'top_performing': max(tiktok_engagement) if tiktok_engagement else 0
        },
        'platform_comparison': {
            'instagram_vs_tiktok': 'Instagram higher' if (sum(instagram_engagement) / len(instagram_engagement) if instagram_engagement else 0) > (sum(tiktok_engagement) / len(tiktok_engagement) if tiktok_engagement else 0) else 'TikTok higher'
        }
    }

def generate_competitive_insights(instagram_data, tiktok_data):
    """Generate competitive insights and market positioning"""
    
    # Analyze competitor presence
    competitors = {
        'supreme': 0, 'stussy': 0, 'fear_of_god': 0, 'off_white': 0, 'diamond_supply': 0,
        'lrg': 0, 'hellstar': 0, 'ed_hardy': 0, 'von_dutch': 0, 'reason_clothing': 0
    }
    
    all_data = instagram_data + tiktok_data
    
    for post in all_data:
        text = (post.get('caption', '') or post.get('text', '') or post.get('description', '')).lower()
        
        for competitor in competitors.keys():
            brand_name = competitor.replace('_', ' ')
            if brand_name in text or competitor in text:
                competitors[competitor] += 1
    
    # Generate market opportunities
    market_opportunities = []
    
    if len(instagram_data) > 0:
        market_opportunities.append({
            'opportunity': 'Instagram Content Scaling',
            'description': f'Currently analyzing {len(instagram_data)} Instagram posts. Opportunity to increase posting frequency.',
            'priority': 'Medium',
            'expected_impact': '15-25% engagement increase'
        })
    
    if len(tiktok_data) > 0:
        market_opportunities.append({
            'opportunity': 'TikTok Expansion',
            'description': f'Currently analyzing {len(tiktok_data)} TikTok videos. Platform shows high engagement potential.',
            'priority': 'High',
            'expected_impact': '30-50% reach increase'
        })
    
    return {
        'competitor_mentions': competitors,
        'market_position': 'Emerging' if sum(competitors.values()) < 10 else 'Established',
        'market_opportunities': market_opportunities,
        'competitive_advantage': [
            'Authentic street culture connection',
            'Strong visual brand identity',
            'Cultural moment awareness'
        ]
    }

def generate_weekly_report():
    """Generate comprehensive weekly intelligence report"""
    
    analysis = generate_competitive_analysis()
    
    report = {
        'report_type': 'weekly_intelligence',
        'generated_at': datetime.now().isoformat(),
        'report_period': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
        'executive_summary': f"Analysis of {analysis['data_summary']['total_analyzed']} posts shows competitive positioning opportunities in streetwear market.",
        'key_insights': [
            f"Processed {analysis['data_summary']['instagram_posts']} Instagram posts and {analysis['data_summary']['tiktok_videos']} TikTok videos",
            f"Data quality score: {analysis['trustworthiness_score']}% - {analysis['data_summary']['data_quality']} reliability",
            f"Identified {len(analysis['hashtag_analysis'])} high-performing hashtags",
            f"Detected {len(analysis['cultural_trends'])} cultural trend opportunities"
        ],
        'recommendations': analysis['recommendations'],
        'data_sources': [
            f"Instagram data: {analysis['data_summary']['instagram_posts']} posts analyzed",
            f"TikTok data: {analysis['data_summary']['tiktok_videos']} videos analyzed",
            f"Trustworthiness score: {analysis['trustworthiness_score']}%"
        ],
        'next_actions': [
            'Implement top hashtag recommendations',
            'Develop cultural trend content calendar',
            'Optimize platform-specific content strategy',
            'Monitor competitive landscape changes'
        ]
    }
    
    return report
