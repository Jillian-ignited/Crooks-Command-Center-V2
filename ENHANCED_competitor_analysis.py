#!/usr/bin/env python3
"""
Enhanced Competitor Analysis for Crooks & Castles Command Center V2
Analyzes competitor brand mentions, sentiment, and positioning from real data
"""

import json
import glob
import os
from collections import defaultdict, Counter
from datetime import datetime
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_competitor_landscape():
    """
    Analyze competitor brands from real JSONL data
    Returns comprehensive competitive intelligence
    """
    
    # Define competitor brands to track
    competitor_brands = {
        'Supreme': ['supreme', '#supreme'],
        'Off-White': ['offwhite', 'off-white', '#offwhite'],
        'BAPE': ['bape', 'bathing ape', '#bape'],
        'Stussy': ['stussy', '#stussy'],
        'Kith': ['kith', '#kith'],
        'Fear of God': ['fear of god', 'fog', 'essentials', '#fearofgod'],
        'Nike': ['nike', '#nike'],
        'Adidas': ['adidas', '#adidas'],
        'Jordan': ['jordan', 'air jordan', '#jordan'],
        'Yeezy': ['yeezy', '#yeezy'],
        'Palace': ['palace', '#palace'],
        'Stone Island': ['stone island', '#stoneisland'],
        'Crooks & Castles': ['crooks', 'castles', 'crooks and castles', 'crooksandcastles', '#crooksandcastles']
    }
    
    # Initialize analysis data
    brand_analysis = {}
    total_posts_analyzed = 0
    vader_analyzer = SentimentIntensityAnalyzer()
    
    # Scan all JSONL files
    data_files = glob.glob('uploads/intel/*.jsonl')
    
    for brand_name, keywords in competitor_brands.items():
        brand_data = {
            'mentions': 0,
            'positive_sentiment': 0,
            'negative_sentiment': 0,
            'neutral_sentiment': 0,
            'avg_sentiment_score': 0,
            'engagement_metrics': {
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0,
                'avg_engagement': 0
            },
            'trending_hashtags': [],
            'sample_posts': [],
            'market_position': 'emerging'
        }
        
        sentiment_scores = []
        engagement_scores = []
        
        # Analyze each data file
        for file_path in data_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                post_data = json.loads(line)
                                total_posts_analyzed += 1
                                
                                # Extract text content
                                text_content = ''
                                if 'caption' in post_data:
                                    text_content += post_data.get('caption', '') + ' '
                                if 'text' in post_data:
                                    text_content += post_data.get('text', '') + ' '
                                if 'description' in post_data:
                                    text_content += post_data.get('description', '') + ' '
                                
                                # Check for brand mentions
                                text_lower = text_content.lower()
                                brand_mentioned = any(keyword.lower() in text_lower for keyword in keywords)
                                
                                if brand_mentioned:
                                    brand_data['mentions'] += 1
                                    
                                    # Sentiment analysis
                                    if text_content.strip():
                                        # TextBlob sentiment
                                        blob = TextBlob(text_content)
                                        textblob_sentiment = blob.sentiment.polarity
                                        
                                        # VADER sentiment
                                        vader_scores = vader_analyzer.polarity_scores(text_content)
                                        vader_compound = vader_scores['compound']
                                        
                                        # Combined sentiment score
                                        combined_sentiment = (textblob_sentiment + vader_compound) / 2
                                        sentiment_scores.append(combined_sentiment)
                                        
                                        # Categorize sentiment
                                        if combined_sentiment > 0.1:
                                            brand_data['positive_sentiment'] += 1
                                        elif combined_sentiment < -0.1:
                                            brand_data['negative_sentiment'] += 1
                                        else:
                                            brand_data['neutral_sentiment'] += 1
                                    
                                    # Engagement metrics
                                    likes = post_data.get('likesCount', post_data.get('likes', 0))
                                    comments = post_data.get('commentsCount', post_data.get('comments', 0))
                                    shares = post_data.get('sharesCount', post_data.get('shares', 0))
                                    
                                    if isinstance(likes, (int, float)):
                                        brand_data['engagement_metrics']['total_likes'] += likes
                                    if isinstance(comments, (int, float)):
                                        brand_data['engagement_metrics']['total_comments'] += comments
                                    if isinstance(shares, (int, float)):
                                        brand_data['engagement_metrics']['total_shares'] += shares
                                    
                                    # Calculate engagement score
                                    engagement_score = likes + (comments * 2) + (shares * 3)
                                    engagement_scores.append(engagement_score)
                                    
                                    # Sample posts for analysis
                                    if len(brand_data['sample_posts']) < 3:
                                        brand_data['sample_posts'].append({
                                            'text': text_content[:200] + '...' if len(text_content) > 200 else text_content,
                                            'sentiment': combined_sentiment,
                                            'engagement': engagement_score,
                                            'source': os.path.basename(file_path)
                                        })
                                
                            except json.JSONDecodeError:
                                continue
                                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Calculate averages
        if sentiment_scores:
            brand_data['avg_sentiment_score'] = sum(sentiment_scores) / len(sentiment_scores)
        
        if engagement_scores:
            brand_data['engagement_metrics']['avg_engagement'] = sum(engagement_scores) / len(engagement_scores)
        
        # Determine market position based on mentions and sentiment
        if brand_data['mentions'] >= 10:
            if brand_data['avg_sentiment_score'] > 0.3:
                brand_data['market_position'] = 'market_leader'
            elif brand_data['avg_sentiment_score'] > 0:
                brand_data['market_position'] = 'strong_competitor'
            else:
                brand_data['market_position'] = 'challenged'
        elif brand_data['mentions'] >= 5:
            brand_data['market_position'] = 'emerging'
        else:
            brand_data['market_position'] = 'niche'
        
        brand_analysis[brand_name] = brand_data
    
    # Generate competitive insights
    competitive_insights = generate_competitive_insights(brand_analysis)
    
    return {
        'total_posts_analyzed': total_posts_analyzed,
        'brands_analyzed': len(competitor_brands),
        'brand_analysis': brand_analysis,
        'competitive_insights': competitive_insights,
        'last_updated': datetime.now().isoformat()
    }

def generate_competitive_insights(brand_analysis):
    """Generate strategic insights from competitor analysis"""
    
    insights = {
        'market_leaders': [],
        'emerging_threats': [],
        'sentiment_winners': [],
        'engagement_leaders': [],
        'opportunities': [],
        'crooks_position': {}
    }
    
    # Sort brands by different metrics
    brands_by_mentions = sorted(brand_analysis.items(), key=lambda x: x[1]['mentions'], reverse=True)
    brands_by_sentiment = sorted(brand_analysis.items(), key=lambda x: x[1]['avg_sentiment_score'], reverse=True)
    brands_by_engagement = sorted(brand_analysis.items(), key=lambda x: x[1]['engagement_metrics']['avg_engagement'], reverse=True)
    
    # Market leaders (top 3 by mentions)
    insights['market_leaders'] = [
        {
            'brand': brand,
            'mentions': data['mentions'],
            'sentiment': round(data['avg_sentiment_score'], 3),
            'position': data['market_position']
        }
        for brand, data in brands_by_mentions[:3] if data['mentions'] > 0
    ]
    
    # Sentiment winners (top 3 by sentiment)
    insights['sentiment_winners'] = [
        {
            'brand': brand,
            'sentiment_score': round(data['avg_sentiment_score'], 3),
            'positive_mentions': data['positive_sentiment'],
            'total_mentions': data['mentions']
        }
        for brand, data in brands_by_sentiment[:3] if data['mentions'] > 0
    ]
    
    # Engagement leaders (top 3 by engagement)
    insights['engagement_leaders'] = [
        {
            'brand': brand,
            'avg_engagement': round(data['engagement_metrics']['avg_engagement'], 1),
            'total_likes': data['engagement_metrics']['total_likes'],
            'mentions': data['mentions']
        }
        for brand, data in brands_by_engagement[:3] if data['mentions'] > 0
    ]
    
    # Crooks & Castles position analysis
    crooks_data = brand_analysis.get('Crooks & Castles', {})
    if crooks_data:
        insights['crooks_position'] = {
            'mentions': crooks_data['mentions'],
            'sentiment_score': round(crooks_data['avg_sentiment_score'], 3),
            'market_position': crooks_data['market_position'],
            'positive_sentiment_pct': round((crooks_data['positive_sentiment'] / max(crooks_data['mentions'], 1)) * 100, 1),
            'avg_engagement': round(crooks_data['engagement_metrics']['avg_engagement'], 1)
        }
        
        # Calculate competitive gaps
        if insights['market_leaders']:
            top_competitor = insights['market_leaders'][0]
            insights['crooks_position']['mention_gap'] = top_competitor['mentions'] - crooks_data['mentions']
            insights['crooks_position']['sentiment_gap'] = round(top_competitor['sentiment'] - crooks_data['avg_sentiment_score'], 3)
    
    # Identify opportunities
    insights['opportunities'] = [
        {
            'opportunity': 'Sentiment Leadership',
            'description': f"Crooks & Castles has {insights['crooks_position'].get('sentiment_score', 0):.3f} sentiment vs top competitor {insights['sentiment_winners'][0]['sentiment_score']:.3f}",
            'priority': 'high' if insights['crooks_position'].get('sentiment_score', 0) < 0 else 'medium'
        },
        {
            'opportunity': 'Mention Volume',
            'description': f"Increase brand mentions from {insights['crooks_position'].get('mentions', 0)} to compete with leaders",
            'priority': 'high' if insights['crooks_position'].get('mentions', 0) < 10 else 'medium'
        },
        {
            'opportunity': 'Engagement Optimization',
            'description': f"Current avg engagement: {insights['crooks_position'].get('avg_engagement', 0):.1f}, top performer: {insights['engagement_leaders'][0]['avg_engagement']:.1f}",
            'priority': 'medium'
        }
    ]
    
    return insights

def get_competitor_comparison_data():
    """Get formatted competitor comparison data for the dashboard"""
    try:
        analysis = analyze_competitor_landscape()
        
        # Format for dashboard display
        comparison_data = {
            'summary': {
                'total_brands_tracked': analysis['brands_analyzed'],
                'total_posts_analyzed': analysis['total_posts_analyzed'],
                'last_updated': analysis['last_updated']
            },
            'brand_rankings': [],
            'crooks_position': analysis['competitive_insights']['crooks_position'],
            'key_insights': analysis['competitive_insights']['opportunities'][:3]
        }
        
        # Create brand rankings
        for brand, data in analysis['brand_analysis'].items():
            if data['mentions'] > 0:  # Only include brands with mentions
                comparison_data['brand_rankings'].append({
                    'brand': brand,
                    'mentions': data['mentions'],
                    'sentiment_score': round(data['avg_sentiment_score'], 3),
                    'positive_pct': round((data['positive_sentiment'] / max(data['mentions'], 1)) * 100, 1),
                    'avg_engagement': round(data['engagement_metrics']['avg_engagement'], 1),
                    'market_position': data['market_position']
                })
        
        # Sort by mentions (descending)
        comparison_data['brand_rankings'].sort(key=lambda x: x['mentions'], reverse=True)
        
        return comparison_data
        
    except Exception as e:
        print(f"Error in competitor analysis: {e}")
        return {
            'summary': {
                'total_brands_tracked': 13,
                'total_posts_analyzed': 0,
                'last_updated': datetime.now().isoformat()
            },
            'brand_rankings': [],
            'crooks_position': {},
            'key_insights': []
        }

if __name__ == "__main__":
    # Test the competitor analysis
    result = get_competitor_comparison_data()
    print(json.dumps(result, indent=2))
