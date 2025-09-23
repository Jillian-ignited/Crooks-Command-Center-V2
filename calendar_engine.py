"""
Content-Focused Calendar Engine for Streetwear Campaign Planning
Uses real competitive intelligence to plan content that converts streetwear customers
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
        
        streetwear_trends = self.extract_streetwear_trends()
        conversion_opportunities = self.identify_conversion_opportunities()
        cultural_moments = self.get_cultural_moments()
        
        if timeframe_days <= 7:
            campaigns.extend(self.create_immediate_content(streetwear_trends, conversion_opportunities))
        elif timeframe_days <= 30:
            campaigns.extend(self.create_strategic_campaigns(cultural_moments, conversion_opportunities))
        elif timeframe_days <= 60:
            campaigns.extend(self.create_product_campaigns(streetwear_trends))
        else:
            campaigns.extend(self.create_quarterly_strategy(cultural_moments))
        
        return campaigns
    
    def create_immediate_content(self, trends, opportunities):
        """Create 7-day immediate content opportunities"""
        campaigns = []
        
        # Trend activation campaigns
        for i, trend in enumerate(trends[:2]):
            campaign_date = self.base_date + timedelta(days=i*2 + 1)
            
            campaign = {
                "date": campaign_date.strftime('%Y-%m-%d'),
                "title": f"Trend Activation: {trend.get('trend', 'Streetwear Trend')}",
                "description": f"Capitalize on {trend.get('trend', 'trend')} momentum with authentic streetwear content",
                "content_type": "trend_activation",
                "target_audience": "streetwear enthusiasts, trend-conscious consumers",
                "conversion_goal": "brand awareness → consideration",
                "content_formats": [
                    "Instagram post (1080x1080) - trend styling",
                    "TikTok video (9:16) - trend participation", 
                    "Instagram Stories - behind-the-scenes"
                ],
                "asset_requirements": [
                    "Model wearing Crooks & Castles pieces",
                    "Street photography aesthetic",
                    "Trend-relevant styling"
                ],
                "copy_direction": f"Authentic take on {trend.get('trend', 'trend')} with Crooks & Castles heritage",
                "hashtag_strategy": [trend.get('trend', ''), "#crooksandcastles", "#streetwear", "#authentic"],
                "success_metrics": {
                    "engagement_rate": "target 4.5%+",
                    "saves": "500+",
                    "trend_participation": "track hashtag usage"
                },
                "conversion_elements": [
                    "Product tags on featured items",
                    "Swipe-up to shop (Stories)",
                    "Bio link to collection"
                ],
                "cultural_context": f"Real trend momentum: {trend.get('momentum', 0):+.1f}%",
                "priority": "high",
                "data_source": "real_trend_analysis"
            }
            campaigns.append(campaign)
        
        # Conversion opportunity campaigns
        for i, opp in enumerate(opportunities[:1]):
            campaign_date = self.base_date + timedelta(days=i*3 + 3)
            
            campaign = {
                "date": campaign_date.strftime('%Y-%m-%d'),
                "title": f"Consumer Response: {opp.get('signal', 'Engagement').title()}",
                "description": f"Address consumer signal '{opp.get('signal', '')}' with targeted streetwear content",
                "content_type": "consumer_response",
                "target_audience": "ready-to-purchase streetwear customers",
                "conversion_goal": "consideration → purchase",
                "content_formats": [
                    "Instagram carousel - product showcase",
                    "Stories highlight - customer testimonials",
                    "TikTok - styling/fit content"
                ],
                "asset_requirements": [
                    "Product photography - lifestyle context",
                    "Customer testimonials/reviews",
                    "Fit and styling videos"
                ],
                "copy_direction": f"Direct response to '{opp.get('signal', '')}' consumer need",
                "conversion_elements": [
                    "Clear call-to-action",
                    "Limited-time offer consideration",
                    "Size/fit guidance",
                    "Customer reviews/social proof"
                ],
                "success_metrics": {
                    "click_through_rate": "target 2.5%+",
                    "conversion_rate": "track purchases",
                    "engagement_quality": "comments with purchase intent"
                },
                "cultural_context": f"Consumer insight: {opp.get('context', '')[:100]}...",
                "priority": "high" if opp.get('conversion_potential') == 'high' else "medium",
                "data_source": "real_consumer_signals"
            }
            campaigns.append(campaign)
        
        return campaigns
    
    def create_strategic_campaigns(self, cultural_moments, opportunities):
        """Create 30-day strategic campaigns"""
        campaigns = []
        
        # Cultural heritage campaign
        campaign_date = self.base_date + timedelta(days=7)
        
        campaign = {
            "date": campaign_date.strftime('%Y-%m-%d'),
            "title": "Streetwear Heritage & Authenticity Campaign",
            "description": "Multi-week campaign showcasing Crooks & Castles heritage in street culture",
            "content_type": "heritage_storytelling",
            "target_audience": "culture-conscious streetwear consumers, brand loyalists",
            "conversion_goal": "brand loyalty → repeat purchases",
            "content_formats": [
                "Documentary-style video series",
                "Historical timeline posts",
                "Founder/brand story content",
                "Community testimonials"
            ],
            "asset_requirements": [
                "Archive photography/video",
                "Founder interviews",
                "Community member features",
                "Heritage product showcases"
            ],
            "copy_direction": "Authentic storytelling about brand's role in street culture evolution",
            "conversion_elements": [
                "Heritage collection highlights",
                "Limited edition drops",
                "Community membership/loyalty program",
                "Exclusive access offers"
            ],
            "success_metrics": {
                "brand_sentiment": "track positive mentions",
                "story_completion": "60%+ video completion",
                "community_engagement": "comments with brand affinity"
            },
            "cultural_context": "Authentic street culture positioning with heritage emphasis",
            "priority": "high",
            "data_source": "cultural_intelligence"
        }
        campaigns.append(campaign)
        
        # Product styling campaign
        campaign_date = self.base_date + timedelta(days=14)
        
        campaign = {
            "date": campaign_date.strftime('%Y-%m-%d'),
            "title": "Street Styling & Fit Content Series",
            "description": "Educational content showing how to style Crooks & Castles pieces",
            "content_type": "styling_education",
            "target_audience": "style-conscious consumers, fit-focused shoppers",
            "conversion_goal": "education → purchase confidence → sales",
            "content_formats": [
                "Styling tutorials (video)",
                "Fit guides (carousel posts)",
                "Mix-and-match content",
                "Size guide content"
            ],
            "asset_requirements": [
                "Multiple model sizes/types",
                "Various styling scenarios",
                "Close-up fit details",
                "Lifestyle context shots"
            ],
            "copy_direction": "Educational, helpful tone focusing on versatility and fit",
            "conversion_elements": [
                "Size guide links",
                "Product recommendations",
                "Complete-the-look suggestions",
                "Fit guarantee messaging"
            ],
            "success_metrics": {
                "saves": "high save rate for reference",
                "shares": "styling inspiration sharing",
                "product_clicks": "track product page visits"
            },
            "cultural_context": "Practical streetwear styling with authentic street aesthetic",
            "priority": "medium",
            "data_source": "consumer_education_needs"
        }
        campaigns.append(campaign)
        
        return campaigns
    
    def create_product_campaigns(self, trends):
        """Create 60-day product-focused campaigns"""
        campaigns = []
        
        campaign_date = self.base_date + timedelta(days=30)
        
        campaign = {
            "date": campaign_date.strftime('%Y-%m-%d'),
            "title": "New Collection Launch Campaign",
            "description": "Strategic product launch with cultural positioning and trend integration",
            "content_type": "product_launch",
            "target_audience": "core customers, new prospects, trend followers",
            "conversion_goal": "awareness → desire → purchase",
            "content_formats": [
                "Teaser campaign (Stories/posts)",
                "Launch day content blitz",
                "Product detail content",
                "Customer early access"
            ],
            "asset_requirements": [
                "Professional product photography",
                "Lifestyle/street context shots",
                "Detail/texture close-ups",
                "Model/fit photography"
            ],
            "copy_direction": "Exclusive, limited, culturally relevant messaging",
            "conversion_elements": [
                "Early access for community",
                "Limited quantity messaging",
                "Pre-order/waitlist options",
                "Bundle/collection offers"
            ],
            "success_metrics": {
                "pre_orders": "track early sales",
                "waitlist_signups": "demand indication",
                "launch_day_sales": "conversion success"
            },
            "cultural_context": "Product positioned within current street culture trends",
            "priority": "high",
            "data_source": "product_strategy"
        }
        campaigns.append(campaign)
        
        return campaigns
    
    def create_quarterly_strategy(self, cultural_moments):
        """Create 90+ day strategic planning"""
        campaigns = []
        
        campaign_date = self.base_date + timedelta(days=60)
        
        campaign = {
            "date": campaign_date.strftime('%Y-%m-%d'),
            "title": "Quarterly Brand Positioning & Culture Strategy",
            "description": "Long-term brand positioning within street culture ecosystem",
            "content_type": "strategic_positioning",
            "target_audience": "brand community, culture influencers, industry",
            "conversion_goal": "brand authority → market leadership → sales growth",
            "content_formats": [
                "Culture report/manifesto",
                "Industry thought leadership",
                "Community partnership announcements",
                "Brand evolution content"
            ],
            "asset_requirements": [
                "Brand strategy visuals",
                "Community partnership content",
                "Industry recognition content",
                "Future vision materials"
            ],
            "copy_direction": "Authoritative, visionary, culturally grounded",
            "conversion_elements": [
                "Brand membership/community",
                "Exclusive collaborations",
                "Limited partnerships",
                "Cultural event access"
            ],
            "success_metrics": {
                "brand_mentions": "industry recognition",
                "community_growth": "loyal customer base",
                "market_share": "competitive positioning"
            },
            "cultural_context": "Strategic positioning as authentic street culture leader",
            "priority": "strategic",
            "data_source": "long_term_intelligence"
        }
        campaigns.append(campaign)
        
        return campaigns

# Main calendar functions for API compatibility
def get_calendar(view="30_day_view"):
    """Get content-focused calendar for streetwear campaign planning"""
    calendar = StreetWearContentCalendar()
    
    # Extract timeframe from view
    timeframe_map = {
        "7_day_view": 7,
        "30_day_view": 30,
        "60_day_view": 60,
        "90_day_view": 90
    }
    
    timeframe = timeframe_map.get(view, 30)
    campaigns = calendar.generate_content_campaigns(timeframe)
    
    return campaigns

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
    campaigns_7d = calendar.generate_content_campaigns(7)
    print(f"Generated {len(campaigns_7d)} streetwear content campaigns for 7-day view")
    
    for campaign in campaigns_7d:
        print(f"- {campaign['title']}: {campaign['conversion_goal']}")
        print(f"  Target: {campaign['target_audience']}")
        print(f"  Formats: {', '.join(campaign['content_formats'][:2])}")
        print()
