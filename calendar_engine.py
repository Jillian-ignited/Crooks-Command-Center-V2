"""
Content-Focused Calendar Engine for Streetwear Campaign Planning
Uses real competitive intelligence to plan content that converts streetwear customers
FIXED: Returns proper dictionary structure to prevent 'list' object errors
"""

import os
import json
from datetime import datetime, timedelta
from enhanced_data_processor import process_enhanced_intelligence_data, analyze_real_sentiment

class StreetWearContentCalendar:
    def __init__(self):
        self.intelligence_data = None
        self.base_date = datetime.now()
        self.load_real_data()
    
    def load_real_data(self):
        """Load real competitive intelligence data"""
        try:
            self.intelligence_data = process_enhanced_intelligence_data()
        except Exception as e:
            print(f"Error loading intelligence data: {e}")
            self.intelligence_data = None
    
    def extract_streetwear_trends(self):
        """Extract streetwear-specific trends from real data that drive conversions"""
        if not self.intelligence_data:
            return []
        
        cultural_radar = self.intelligence_data.get('cultural_radar', {})
        trends = cultural_radar.get('trend_momentum', {}).get('top_trends', [])
        
        # Filter for streetwear-relevant trends
        streetwear_keywords = [
            'street', 'urban', 'authentic', 'culture', 'heritage', 'crooks', 'castles',
            'hip-hop', 'fashion', 'style', 'fit', 'drop', 'collection', 'collab'
        ]
        
        streetwear_trends = []
        for trend in trends:
            trend_name = trend.get('trend', '').lower()
            if any(keyword in trend_name for keyword in streetwear_keywords):
                streetwear_trends.append(trend)
        
        return streetwear_trends[:5]  # Top 5 streetwear trends
    
    def identify_conversion_opportunities(self):
        """Identify content opportunities that drive streetwear sales"""
        if not self.intelligence_data:
            return []
        
        cultural_radar = self.intelligence_data.get('cultural_radar', {})
        consumer_signals = cultural_radar.get('consumer_signals', {})
        
        # Look for purchase intent signals
        opportunities = consumer_signals.get('top_opportunities', [])
        conversion_signals = []
        
        purchase_keywords = ['cop', 'buy', 'need', 'want', 'fire', 'clean', 'fresh', 'dope']
        
        for opp in opportunities:
            keyword = opp.get('keyword', '').lower()
            context = opp.get('context', '').lower()
            
            if keyword in purchase_keywords or any(pk in context for pk in purchase_keywords):
                conversion_signals.append({
                    'signal': keyword,
                    'context': opp.get('context', ''),
                    'sentiment': opp.get('sentiment', 0),
                    'conversion_potential': 'high' if keyword in ['cop', 'buy', 'need'] else 'medium'
                })
        
        return conversion_signals[:3]  # Top 3 conversion opportunities
    
    def get_cultural_moments(self):
        """Get cultural moments relevant to streetwear audience"""
        cultural_calendar = {
            'hip_hop_culture': {
                'keywords': ['hip-hop', 'rap', 'culture', 'authentic', 'street'],
                'content_types': ['heritage storytelling', 'artist collaborations', 'culture documentation'],
                'conversion_angle': 'authenticity and cultural credibility'
            },
            'streetwear_drops': {
                'keywords': ['drop', 'release', 'collection', 'limited', 'exclusive'],
                'content_types': ['product reveals', 'behind-the-scenes', 'styling content'],
                'conversion_angle': 'exclusivity and FOMO'
            },
            'community_culture': {
                'keywords': ['community', 'real', 'represent', 'crew', 'family'],
                'content_types': ['customer spotlights', 'community features', 'user-generated content'],
                'conversion_angle': 'belonging and community'
            }
        }
        
        return cultural_calendar
    
    def generate_content_campaigns(self, timeframe_days):
        """Generate streetwear content campaigns based on real data"""
        campaigns = []
        
        # Get real trends and opportunities
        streetwear_trends = self.extract_streetwear_trends()
        conversion_opportunities = self.identify_conversion_opportunities()
        cultural_moments = self.get_cultural_moments()
        
        # Campaign 1: Heritage & Authenticity (always relevant for streetwear)
        heritage_campaign = {
            'date': (self.base_date + timedelta(days=7)).strftime('%Y-%m-%d'),
            'title': 'Streetwear Heritage & Authenticity Campaign',
            'description': 'Multi-week campaign showcasing Crooks & Castles heritage in street culture',
            'content_type': 'heritage_storytelling',
            'target_audience': 'culture-conscious streetwear consumers, brand loyalists',
            'conversion_goal': 'brand loyalty → repeat purchases',
            'content_formats': [
                'Documentary-style video series',
                'Historical timeline posts',
                'Founder/brand story content',
                'Community testimonials'
            ],
            'budget': min(2000, timeframe_days * 50),
            'kpis': ['Brand sentiment', 'Engagement rate', 'Share rate', 'Time spent'],
            'cultural_alignment': 'hip_hop_culture',
            'status': 'planned'
        }
        campaigns.append(heritage_campaign)
        
        # Campaign 2: Product Drop/Collection Focus
        if timeframe_days >= 14:
            product_campaign = {
                'date': (self.base_date + timedelta(days=14)).strftime('%Y-%m-%d'),
                'title': 'Limited Drop Anticipation Campaign',
                'description': 'Build anticipation for upcoming product releases with exclusive previews',
                'content_type': 'product_focused',
                'target_audience': 'high-intent purchasers, collectors, hypebeasts',
                'conversion_goal': 'anticipation → pre-orders → sales',
                'content_formats': [
                    'Teaser video content',
                    'Behind-the-scenes production',
                    'Styling/lookbook content',
                    'Influencer previews'
                ],
                'budget': min(3000, timeframe_days * 75),
                'kpis': ['Pre-order conversions', 'Email signups', 'Wishlist adds', 'Social saves'],
                'cultural_alignment': 'streetwear_drops',
                'status': 'planned'
            }
            campaigns.append(product_campaign)
        
        # Campaign 3: Community & Culture (if longer timeframe)
        if timeframe_days >= 30:
            community_campaign = {
                'date': (self.base_date + timedelta(days=21)).strftime('%Y-%m-%d'),
                'title': 'Community Culture Celebration',
                'description': 'Showcase real customers and community members wearing Crooks & Castles',
                'content_type': 'community_focused',
                'target_audience': 'community members, potential new customers, culture enthusiasts',
                'conversion_goal': 'community belonging → brand affinity → purchases',
                'content_formats': [
                    'Customer spotlight features',
                    'Street style photography',
                    'Community event coverage',
                    'User-generated content campaigns'
                ],
                'budget': min(2500, timeframe_days * 60),
                'kpis': ['UGC submissions', 'Community engagement', 'New follower quality', 'Conversion rate'],
                'cultural_alignment': 'community_culture',
                'status': 'planned'
            }
            campaigns.append(community_campaign)
        
        # Add trend-based campaigns if we have real trend data
        if streetwear_trends and timeframe_days >= 21:
            for i, trend in enumerate(streetwear_trends[:2]):  # Max 2 trend campaigns
                trend_campaign = {
                    'date': (self.base_date + timedelta(days=10 + i*14)).strftime('%Y-%m-%d'),
                    'title': f'Trend Response: {trend.get("trend", "Streetwear Trend").title()}',
                    'description': f'Content responding to trending topic: {trend.get("trend", "streetwear trend")}',
                    'content_type': 'trend_response',
                    'target_audience': 'trend-aware consumers, early adopters',
                    'conversion_goal': 'trend relevance → brand consideration → sales',
                    'content_formats': [
                        'Trend interpretation content',
                        'Product styling for trend',
                        'Influencer trend content',
                        'Community trend challenges'
                    ],
                    'budget': min(1500, timeframe_days * 40),
                    'kpis': ['Trend engagement', 'Hashtag performance', 'Viral potential', 'Sales lift'],
                    'cultural_alignment': 'streetwear_trends',
                    'trend_data': trend,
                    'status': 'planned'
                }
                campaigns.append(trend_campaign)
        
        # Add conversion opportunity campaigns if we have real signals
        if conversion_opportunities and timeframe_days >= 14:
            for i, opportunity in enumerate(conversion_opportunities[:1]):  # Max 1 conversion campaign
                conversion_campaign = {
                    'date': (self.base_date + timedelta(days=5 + i*7)).strftime('%Y-%m-%d'),
                    'title': f'Conversion Focus: {opportunity.get("signal", "Purchase Intent").title()}',
                    'description': f'Campaign targeting high-conversion signal: {opportunity.get("context", "purchase intent")}',
                    'content_type': 'conversion_focused',
                    'target_audience': 'high-intent purchasers, ready-to-buy consumers',
                    'conversion_goal': 'purchase intent → immediate sales',
                    'content_formats': [
                        'Direct response content',
                        'Product demonstration',
                        'Social proof content',
                        'Limited-time offers'
                    ],
                    'budget': min(2000, timeframe_days * 55),
                    'kpis': ['Conversion rate', 'ROAS', 'Cart additions', 'Purchase completions'],
                    'cultural_alignment': 'purchase_intent',
                    'opportunity_data': opportunity,
                    'status': 'high_priority'
                }
                campaigns.append(conversion_campaign)
        
        return campaigns

# Main calendar functions for API compatibility
def get_calendar(days=30):
    """Get content-focused calendar for streetwear campaign planning"""
    calendar = StreetWearContentCalendar()
    
    # Handle both integer days and view string parameters
    if isinstance(days, str):
        timeframe_map = {
            "7_day_view": 7,
            "30_day_view": 30,
            "60_day_view": 60,
            "90_day_view": 90
        }
        timeframe = timeframe_map.get(days, 30)
    else:
        timeframe = days
    
    campaigns = calendar.generate_content_campaigns(timeframe)
    
    # Return proper dictionary structure expected by API
    return {
        'campaigns': campaigns,
        'timeframe': f'{timeframe} days',
        'budget_allocated': timeframe * 150,  # $150 per day estimate
        'upcoming_events': len(campaigns),
        'active_campaigns': len([c for c in campaigns if 'active' in c.get('status', '')]),
        'content_focus': 'streetwear_conversion_optimization',
        'cultural_alignment': True
    }

def get_budget_summary():
    """Get simplified budget summary focused on content planning"""
    calendar = StreetWearContentCalendar()
    
    # Simple budget estimation based on content complexity
    view_budgets = {
        "7_day_view": 2000,   # Immediate content creation
        "30_day_view": 5000,  # Strategic campaigns
        "60_day_view": 8000,  # Product launches
        "90_day_view": 12000  # Quarterly strategy
    }
    
    return {
        "total_budget": sum(view_budgets.values()),
        "view_budgets": view_budgets,
        "budget_focus": "content_creation_and_campaign_execution"
    }

if __name__ == "__main__":
    # Test content-focused calendar
    calendar = StreetWearContentCalendar()
    result = get_calendar(7)
    print(f"Calendar returns: {type(result)}")
    print(f"Keys: {list(result.keys())}")
    print(f"Campaigns: {len(result['campaigns'])}")
    print(f"Budget: ${result['budget_allocated']}")
