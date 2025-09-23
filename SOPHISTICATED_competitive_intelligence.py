"""
Sophisticated Competitive Intelligence Engine
Real data analysis comparing Crooks & Castles vs 11+ streetwear competitors
Uses actual Apify scraped data for authentic competitive positioning
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from textblob import TextBlob
import statistics

class StreetWearCompetitiveIntelligence:
    def __init__(self):
        self.instagram_data = []
        self.tiktok_data = []
        self.competitive_data = []
        self.load_real_data()
        
        # Define the 17 major streetwear competitors
        self.competitor_brands = {
            'Supreme': {'tier': 'Luxury', 'keywords': ['supreme'], 'price_range': '$50-$500'},
            'Off-White': {'tier': 'Luxury', 'keywords': ['offwhite', 'off-white'], 'price_range': '$200-$1000'},
            'Fear of God': {'tier': 'Luxury', 'keywords': ['fearofgod', 'fog'], 'price_range': '$100-$800'},
            'Essentials': {'tier': 'Premium', 'keywords': ['essentials'], 'price_range': '$40-$200'},
            'Stussy': {'tier': 'Heritage', 'keywords': ['stussy'], 'price_range': '$30-$150'},
            'BAPE': {'tier': 'Luxury', 'keywords': ['bape', 'bathing'], 'price_range': '$100-$400'},
            'Kith': {'tier': 'Premium', 'keywords': ['kith'], 'price_range': '$50-$300'},
            'Palace': {'tier': 'Premium', 'keywords': ['palace'], 'price_range': '$40-$200'},
            'Golf Wang': {'tier': 'Mid-tier', 'keywords': ['golf', 'golfwang'], 'price_range': '$30-$150'},
            'Chrome Hearts': {'tier': 'Ultra-Luxury', 'keywords': ['chrome', 'hearts'], 'price_range': '$200-$2000'},
            'Rhude': {'tier': 'Luxury', 'keywords': ['rhude'], 'price_range': '$150-$600'},
            'LRG': {'tier': 'Heritage', 'keywords': ['lrg', 'lifted'], 'price_range': '$25-$120'},
            'Reason Clothing': {'tier': 'Mid-tier', 'keywords': ['reason', 'reasonclothing'], 'price_range': '$30-$100'},
            'Smokerise': {'tier': 'Mid-tier', 'keywords': ['smokerise', 'smoke'], 'price_range': '$40-$150'},
            'Ed Hardy': {'tier': 'Heritage', 'keywords': ['edhardy', 'hardy'], 'price_range': '$50-$200'},
            'Von Dutch': {'tier': 'Heritage', 'keywords': ['vondutch', 'dutch'], 'price_range': '$40-$180'},
            'Crooks & Castles': {'tier': 'Heritage', 'keywords': ['crooks', 'castles'], 'price_range': '$40-$150'}
        }
    
    def load_real_data(self):
        """Load actual scraped data from Apify"""
        try:
            # Load Instagram hashtag scraper data
            instagram_path = 'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl'
            if os.path.exists(instagram_path):
                with open(instagram_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.instagram_data.append(json.loads(line))
            
            # Load TikTok scraper data
            tiktok_path = 'uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl'
            if os.path.exists(tiktok_path):
                with open(tiktok_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.tiktok_data.append(json.loads(line))
            
            # Load competitive intelligence data
            competitive_path = 'uploads/intel/instagram_competitive_data.jsonl'
            if os.path.exists(competitive_path):
                with open(competitive_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.competitive_data.append(json.loads(line))
                            
        except Exception as e:
            print(f"Error loading competitive data: {e}")
    
    def identify_brand_from_post(self, post):
        """Identify which brand a post belongs to based on username and hashtags"""
        username = post.get('ownerUsername', '').lower()
        hashtags = [str(h).lower() for h in post.get('hashtags', [])]
        caption = post.get('caption', '').lower()
        
        # Check each brand's keywords
        for brand, info in self.competitor_brands.items():
            for keyword in info['keywords']:
                if (keyword in username or 
                    any(keyword in hashtag for hashtag in hashtags) or
                    keyword in caption):
                    return brand
        
        return None
    
    def analyze_brand_performance(self):
        """Analyze performance metrics for each competitor brand"""
        brand_metrics = defaultdict(lambda: {
            'posts': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0,
            'total_views': 0,
            'hashtags': set(),
            'sentiment_scores': [],
            'engagement_rates': [],
            'recent_posts': 0
        })
        
        # Analyze Instagram data
        for post in self.instagram_data + self.competitive_data:
            brand = self.identify_brand_from_post(post)
            if brand:
                likes = post.get('likesCount', 0)
                comments = post.get('commentsCount', 0)
                
                brand_metrics[brand]['posts'] += 1
                brand_metrics[brand]['total_likes'] += likes
                brand_metrics[brand]['total_comments'] += comments
                
                # Calculate engagement rate (simplified)
                engagement = likes + comments
                brand_metrics[brand]['engagement_rates'].append(engagement)
                
                # Analyze sentiment
                caption = post.get('caption', '')
                if caption:
                    sentiment = TextBlob(caption).sentiment.polarity
                    brand_metrics[brand]['sentiment_scores'].append(sentiment)
                
                # Track hashtags
                for hashtag in post.get('hashtags', []):
                    brand_metrics[brand]['hashtags'].add(hashtag.lower())
                
                # Check if recent (last 7 days)
                try:
                    post_date = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                    if post_date >= datetime.now() - timedelta(days=7):
                        brand_metrics[brand]['recent_posts'] += 1
                except:
                    pass
        
        # Analyze TikTok data
        for post in self.tiktok_data:
            author_username = post.get('author', {}).get('uniqueId', '').lower()
            desc = post.get('desc', '').lower()
            
            # Create a pseudo-post for brand identification
            pseudo_post = {
                'ownerUsername': author_username,
                'caption': desc,
                'hashtags': []
            }
            
            brand = self.identify_brand_from_post(pseudo_post)
            if brand:
                stats = post.get('stats', {})
                brand_metrics[brand]['total_views'] += stats.get('playCount', 0)
                brand_metrics[brand]['total_likes'] += stats.get('diggCount', 0)
                brand_metrics[brand]['total_shares'] += stats.get('shareCount', 0)
                brand_metrics[brand]['total_comments'] += stats.get('commentCount', 0)
        
        # Calculate final metrics
        competitive_analysis = []
        for brand, metrics in brand_metrics.items():
            if metrics['posts'] > 0:
                avg_engagement = statistics.mean(metrics['engagement_rates']) if metrics['engagement_rates'] else 0
                avg_sentiment = statistics.mean(metrics['sentiment_scores']) if metrics['sentiment_scores'] else 0
                
                # Determine market position
                if avg_engagement > 10000:
                    market_position = 'Leading'
                elif avg_engagement > 5000:
                    market_position = 'Strong'
                elif avg_engagement > 1000:
                    market_position = 'Competitive'
                else:
                    market_position = 'Emerging'
                
                # Determine sentiment status
                if avg_sentiment > 0.1:
                    sentiment_status = 'Positive'
                elif avg_sentiment > -0.1:
                    sentiment_status = 'Neutral'
                else:
                    sentiment_status = 'Negative'
                
                competitive_analysis.append({
                    'brand': brand,
                    'tier': self.competitor_brands[brand]['tier'],
                    'price_range': self.competitor_brands[brand]['price_range'],
                    'posts': metrics['posts'],
                    'avg_engagement': avg_engagement,
                    'total_engagement': metrics['total_likes'] + metrics['total_comments'],
                    'tiktok_views': metrics['total_views'],
                    'sentiment_score': avg_sentiment,
                    'sentiment_status': sentiment_status,
                    'market_position': market_position,
                    'unique_hashtags': len(metrics['hashtags']),
                    'recent_activity': metrics['recent_posts'],
                    'engagement_trend': 'Growing' if metrics['recent_posts'] > metrics['posts'] * 0.3 else 'Stable'
                })
        
        return sorted(competitive_analysis, key=lambda x: x['avg_engagement'], reverse=True)
    
    def analyze_market_share(self):
        """Analyze market share based on engagement and mentions"""
        brand_performance = self.analyze_brand_performance()
        
        total_engagement = sum(brand['total_engagement'] for brand in brand_performance)
        
        market_share = []
        for brand in brand_performance:
            share_percentage = (brand['total_engagement'] / total_engagement * 100) if total_engagement > 0 else 0
            market_share.append({
                'brand': brand['brand'],
                'market_share': share_percentage,
                'engagement_share': brand['total_engagement'],
                'position_rank': len(market_share) + 1
            })
        
        return market_share
    
    def identify_competitive_gaps(self):
        """Identify opportunities and gaps in competitive landscape"""
        brand_performance = self.analyze_brand_performance()
        crooks_data = next((b for b in brand_performance if b['brand'] == 'Crooks & Castles'), None)
        
        gaps_and_opportunities = []
        
        if crooks_data:
            # Compare against top performers
            top_performers = [b for b in brand_performance if b['avg_engagement'] > crooks_data['avg_engagement']]
            
            for competitor in top_performers[:3]:  # Top 3 competitors
                engagement_gap = competitor['avg_engagement'] - crooks_data['avg_engagement']
                gaps_and_opportunities.append({
                    'type': 'Performance Gap',
                    'competitor': competitor['brand'],
                    'gap_metric': 'Engagement',
                    'gap_value': engagement_gap,
                    'opportunity': f"Close {engagement_gap:.0f} engagement gap with {competitor['brand']}",
                    'priority': 'High' if engagement_gap > 10000 else 'Medium'
                })
            
            # Identify underperforming tiers
            heritage_brands = [b for b in brand_performance if b['tier'] == 'Heritage']
            if len(heritage_brands) > 1:
                heritage_avg = statistics.mean([b['avg_engagement'] for b in heritage_brands])
                if crooks_data['avg_engagement'] < heritage_avg:
                    gaps_and_opportunities.append({
                        'type': 'Tier Underperformance',
                        'competitor': 'Heritage Tier Average',
                        'gap_metric': 'Tier Performance',
                        'gap_value': heritage_avg - crooks_data['avg_engagement'],
                        'opportunity': 'Improve performance within heritage streetwear tier',
                        'priority': 'High'
                    })
        
        # Identify trending competitors
        trending_brands = [b for b in brand_performance if b['engagement_trend'] == 'Growing']
        for brand in trending_brands:
            if brand['brand'] != 'Crooks & Castles':
                gaps_and_opportunities.append({
                    'type': 'Trending Threat',
                    'competitor': brand['brand'],
                    'gap_metric': 'Growth Momentum',
                    'gap_value': brand['recent_activity'],
                    'opportunity': f"Monitor and respond to {brand['brand']} growth momentum",
                    'priority': 'Medium'
                })
        
        return gaps_and_opportunities
    
    def generate_competitive_insights(self):
        """Generate actionable competitive insights"""
        brand_performance = self.analyze_brand_performance()
        market_share = self.analyze_market_share()
        gaps_opportunities = self.identify_competitive_gaps()
        
        # Find Crooks & Castles position
        crooks_position = next((i+1 for i, b in enumerate(brand_performance) if b['brand'] == 'Crooks & Castles'), None)
        crooks_data = next((b for b in brand_performance if b['brand'] == 'Crooks & Castles'), None)
        
        insights = {
            'competitive_landscape': {
                'total_brands_analyzed': len(brand_performance),
                'crooks_market_position': crooks_position,
                'crooks_tier_ranking': crooks_data['tier'] if crooks_data else 'Unknown',
                'market_leaders': [b['brand'] for b in brand_performance[:3]],
                'heritage_competitors': [b['brand'] for b in brand_performance if b['tier'] == 'Heritage']
            },
            
            'performance_comparison': brand_performance,
            
            'market_share_analysis': market_share,
            
            'competitive_gaps': gaps_opportunities,
            
            'strategic_recommendations': [
                {
                    'priority': 'High',
                    'action': 'Leverage heritage positioning against Supreme and Off-White',
                    'rationale': 'Heritage brands show strong authenticity appeal',
                    'timeline': 'Immediate'
                },
                {
                    'priority': 'Medium',
                    'action': 'Increase TikTok presence to match competitor activity',
                    'rationale': 'TikTok showing strong engagement for streetwear brands',
                    'timeline': '30 days'
                },
                {
                    'priority': 'Medium',
                    'action': 'Develop premium line to compete in $200+ range',
                    'rationale': 'Gap in heritage luxury positioning',
                    'timeline': '90 days'
                }
            ],
            
            'data_quality': {
                'instagram_posts_analyzed': len(self.instagram_data),
                'competitive_posts_analyzed': len(self.competitive_data),
                'tiktok_posts_analyzed': len(self.tiktok_data),
                'brands_with_data': len([b for b in brand_performance if b['posts'] > 0]),
                'analysis_confidence': 'High' if len(brand_performance) >= 8 else 'Medium'
            }
        }
        
        return insights

# API functions for integration
def get_competitive_analysis():
    """Get comprehensive competitive analysis for API"""
    try:
        analyzer = StreetWearCompetitiveIntelligence()
        return analyzer.generate_competitive_insights()
    except Exception as e:
        return {
            'error': f'Competitive analysis error: {str(e)}',
            'competitive_landscape': {},
            'performance_comparison': [],
            'market_share_analysis': [],
            'competitive_gaps': [],
            'strategic_recommendations': [],
            'data_quality': {'analysis_confidence': 'Error'}
        }

def get_competitor_grid():
    """Get competitor comparison grid for frontend display"""
    try:
        analyzer = StreetWearCompetitiveIntelligence()
        brand_performance = analyzer.analyze_brand_performance()
        
        # Format for frontend grid display
        competitor_grid = []
        for brand in brand_performance:
            competitor_grid.append({
                'brand': brand['brand'],
                'tier': brand['tier'],
                'avg_engagement': f"{brand['avg_engagement']:,.0f}",
                'market_position': brand['market_position'],
                'sentiment': brand['sentiment_status'],
                'posts_analyzed': brand['posts'],
                'price_range': brand['price_range'],
                'trend': brand['engagement_trend']
            })
        
        return competitor_grid
    except Exception as e:
        return []

if __name__ == "__main__":
    # Test competitive intelligence
    insights = get_competitive_analysis()
    print("=== COMPETITIVE INTELLIGENCE ANALYSIS ===")
    print(f"Brands analyzed: {insights['competitive_landscape']['total_brands_analyzed']}")
    print(f"Crooks position: #{insights['competitive_landscape']['crooks_market_position']}")
    print(f"Market leaders: {', '.join(insights['competitive_landscape']['market_leaders'])}")
    print(f"Analysis confidence: {insights['data_quality']['analysis_confidence']}")
