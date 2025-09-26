# /backend/routers/executive.py - REAL DATA EXECUTIVE OVERVIEW - NO MOCK DATA

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import statistics
import os
from collections import defaultdict, Counter
import re

router = APIRouter()

# Data directories
SHOPIFY_DATA_DIR = Path("data/shopify")
COMPETITIVE_DATA_DIR = Path("data/competitive") 
UPLOADS_DIR = Path("data/uploads")

# Ensure directories exist
for dir_path in [SHOPIFY_DATA_DIR, COMPETITIVE_DATA_DIR, UPLOADS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# All 12 brands for competitive analysis
ALL_BRANDS = [
    "crooks & castles", "stussy", "supreme", "bape", "off-white", 
    "fear of god", "essentials", "rhude", "palm angels", "amiri", 
    "chrome hearts", "gallery dept"
]

def load_real_shopify_data(days: int = 30) -> Dict[str, Any]:
    """Load and analyze REAL Shopify sales data - NO MOCK DATA"""
    shopify_files = list(SHOPIFY_DATA_DIR.glob("*.csv")) + list(SHOPIFY_DATA_DIR.glob("*.json"))
    
    if not shopify_files:
        return {
            "total_sales": None,
            "total_orders": None,
            "conversion_rate": None,
            "aov": None,
            "traffic": None,
            "status": "no_data",
            "revenue_by_day": [],
            "top_products": [],
            "customer_segments": {}
        }
    
    all_orders = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in shopify_files:
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                # Handle common Shopify CSV column names
                if 'Name' in df.columns:
                    df = df.rename(columns={'Name': 'order_name'})
                if 'Email' in df.columns:
                    df = df.rename(columns={'Email': 'customer_email'})
                if 'Total' in df.columns:
                    df = df.rename(columns={'Total': 'total_price'})
                all_orders.extend(df.to_dict('records'))
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_orders.extend(data)
                    else:
                        all_orders.append(data)
        except Exception as e:
            print(f"Error loading Shopify file {file_path}: {e}")
            continue
    
    if not all_orders:
        return {
            "total_sales": None,
            "total_orders": None, 
            "conversion_rate": None,
            "aov": None,
            "traffic": None,
            "status": "files_but_no_data",
            "revenue_by_day": [],
            "top_products": [],
            "customer_segments": {}
        }
    
    # Filter by date range
    recent_orders = []
    for order in all_orders:
        try:
            # Handle multiple possible date column names
            order_date = None
            for date_col in ['created_at', 'date', 'order_date', 'Created at']:
                if date_col in order and order[date_col]:
                    order_date = pd.to_datetime(order[date_col])
                    break
            
            if order_date and order_date >= cutoff_date:
                recent_orders.append(order)
        except:
            continue
    
    if not recent_orders:
        return {
            "total_sales": 0,
            "total_orders": 0,
            "conversion_rate": None,
            "aov": 0,
            "traffic": None,
            "status": "no_recent_data",
            "revenue_by_day": [],
            "top_products": [],
            "customer_segments": {}
        }
    
    # Calculate REAL metrics from actual data
    sales_values = []
    for order in recent_orders:
        # Handle multiple possible total price column names
        total = 0
        for price_col in ['total_price', 'Total', 'total', 'amount', 'line_total']:
            if price_col in order and order[price_col]:
                try:
                    # Clean currency symbols and convert to float
                    price_str = str(order[price_col]).replace('$', '').replace(',', '').strip()
                    total = float(price_str)
                    break
                except:
                    continue
        sales_values.append(total)
    
    total_sales = sum(sales_values)
    total_orders = len(recent_orders)
    aov = total_sales / max(total_orders, 1)
    
    # Analyze revenue by day
    revenue_by_day = {}
    for order in recent_orders:
        order_date = None
        for date_col in ['created_at', 'date', 'order_date', 'Created at']:
            if date_col in order and order[date_col]:
                try:
                    order_date = pd.to_datetime(order[date_col]).date()
                    break
                except:
                    continue
        
        if order_date:
            date_str = order_date.strftime('%Y-%m-%d')
            if date_str not in revenue_by_day:
                revenue_by_day[date_str] = {'sales': 0, 'orders': 0}
            
            # Get order value
            order_value = 0
            for price_col in ['total_price', 'Total', 'total', 'amount']:
                if price_col in order and order[price_col]:
                    try:
                        price_str = str(order[price_col]).replace('$', '').replace(',', '').strip()
                        order_value = float(price_str)
                        break
                    except:
                        continue
            
            revenue_by_day[date_str]['sales'] += order_value
            revenue_by_day[date_str]['orders'] += 1
    
    # Analyze top products
    product_performance = defaultdict(lambda: {'quantity': 0, 'revenue': 0})
    for order in recent_orders:
        # Handle product information
        for prod_col in ['Lineitem name', 'product_title', 'title', 'product']:
            if prod_col in order and order[prod_col]:
                product = str(order[prod_col])
                
                # Get quantity
                quantity = 1
                for qty_col in ['Lineitem quantity', 'quantity', 'qty']:
                    if qty_col in order and order[qty_col]:
                        try:
                            quantity = int(order[qty_col])
                            break
                        except:
                            continue
                
                # Get product revenue
                product_revenue = 0
                for price_col in ['total_price', 'Total', 'total', 'amount']:
                    if price_col in order and order[price_col]:
                        try:
                            price_str = str(order[price_col]).replace('$', '').replace(',', '').strip()
                            product_revenue = float(price_str)
                            break
                        except:
                            continue
                
                product_performance[product]['quantity'] += quantity
                product_performance[product]['revenue'] += product_revenue
                break
    
    # Top products by revenue
    top_products = sorted(
        [{'name': name, **metrics} for name, metrics in product_performance.items()],
        key=lambda x: x['revenue'],
        reverse=True
    )[:10]
    
    return {
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "conversion_rate": None,  # Would need traffic data
        "aov": round(aov, 2),
        "traffic": None,  # Would need analytics data
        "status": "active",
        "revenue_by_day": [
            {"date": date, "sales": round(data['sales'], 2), "orders": data['orders']}
            for date, data in sorted(revenue_by_day.items())
        ],
        "top_products": top_products,
        "customer_segments": {}  # Would analyze customer data if available
    }

def load_real_competitive_data() -> Dict[str, Any]:
    """Load and analyze REAL competitive data from Apify scraping - NO MOCK DATA"""
    comp_files = list(COMPETITIVE_DATA_DIR.glob("*.json")) + list(COMPETITIVE_DATA_DIR.glob("*.csv")) + list(UPLOADS_DIR.glob("*.json")) + list(UPLOADS_DIR.glob("*.csv"))
    
    if not comp_files:
        return {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "competitive_gaps": [],
            "status": "no_data"
        }
    
    # Load all competitive data
    all_competitor_data = []
    for file_path in comp_files:
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                all_competitor_data.extend(df.to_dict('records'))
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_competitor_data.extend(data)
                    else:
                        all_competitor_data.append(data)
        except Exception as e:
            print(f"Error loading competitive file {file_path}: {e}")
            continue
    
    if not all_competitor_data:
        return {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "competitive_gaps": [],
            "status": "files_but_no_data"
        }
    
    # Group data by brand
    brand_data = defaultdict(list)
    for item in all_competitor_data:
        brand = str(item.get('brand', '')).lower().strip()
        
        # Match to our tracked brands
        for tracked_brand in ALL_BRANDS:
            if any(word in brand for word in tracked_brand.split()):
                brand_data[tracked_brand].append(item)
                break
    
    if not brand_data:
        return {
            "brands_analyzed": 0,
            "crooks_rank": None,
            "market_share": {},
            "performance_comparison": {},
            "competitive_gaps": [],
            "status": "no_matching_brands"
        }
    
    # Calculate performance metrics for each brand
    brand_metrics = {}
    for brand, posts in brand_data.items():
        if not posts:
            continue
            
        # Calculate real engagement metrics
        total_engagement = []
        likes_data = []
        comments_data = []
        shares_data = []
        
        for post in posts:
            likes = int(post.get('likes', 0))
            comments = int(post.get('comments', 0))
            shares = int(post.get('shares', 0))
            
            likes_data.append(likes)
            comments_data.append(comments)
            shares_data.append(shares)
            total_engagement.append(likes + comments + shares)
        
        brand_metrics[brand] = {
            "total_posts": len(posts),
            "avg_engagement": statistics.mean(total_engagement) if total_engagement else 0,
            "avg_likes": statistics.mean(likes_data) if likes_data else 0,
            "avg_comments": statistics.mean(comments_data) if comments_data else 0,
            "avg_shares": statistics.mean(shares_data) if shares_data else 0,
            "total_engagement": sum(total_engagement),
            "max_engagement": max(total_engagement) if total_engagement else 0
        }
    
    # Calculate market share based on total engagement
    total_market_engagement = sum([metrics['total_engagement'] for metrics in brand_metrics.values()])
    market_share = {}
    for brand, metrics in brand_metrics.items():
        market_share[brand] = round((metrics['total_engagement'] / max(total_market_engagement, 1)) * 100, 2)
    
    # Rank brands by average engagement
    ranked_brands = sorted(
        brand_metrics.items(),
        key=lambda x: x[1]['avg_engagement'],
        reverse=True
    )
    
    # Find Crooks & Castles rank
    crooks_rank = None
    for rank, (brand, _) in enumerate(ranked_brands, 1):
        if brand == 'crooks & castles':
            crooks_rank = rank
            break
    
    # Performance comparison
    performance_comparison = {}
    crooks_metrics = brand_metrics.get('crooks & castles', {})
    
    for metric in ['avg_engagement', 'avg_likes', 'avg_comments', 'total_posts']:
        crooks_value = crooks_metrics.get(metric, 0)
        competitor_values = [
            brand_metrics[brand][metric] 
            for brand in brand_metrics 
            if brand != 'crooks & castles' and brand_metrics[brand].get(metric, 0) > 0
        ]
        
        if competitor_values:
            competitor_avg = statistics.mean(competitor_values)
            performance_vs_avg = ((crooks_value - competitor_avg) / max(competitor_avg, 1)) * 100
            
            performance_comparison[metric] = {
                "crooks_value": round(crooks_value, 2),
                "competitor_avg": round(competitor_avg, 2),
                "performance_vs_avg": round(performance_vs_avg, 1),
                "rank": sum(1 for v in competitor_values if v > crooks_value) + 1
            }
    
    # Identify competitive gaps
    competitive_gaps = []
    if crooks_rank and crooks_rank > 3:
        top_performers = [brand for brand, _ in ranked_brands[:3]]
        competitive_gaps.append({
            "gap_type": "engagement_leadership",
            "description": f"Ranked #{crooks_rank} vs top performers: {', '.join(top_performers)}",
            "gap_size": round(ranked_brands[0][1]['avg_engagement'] - crooks_metrics.get('avg_engagement', 0), 2)
        })
    
    return {
        "brands_analyzed": len(brand_metrics),
        "crooks_rank": crooks_rank,
        "market_share": market_share,
        "performance_comparison": performance_comparison,
        "competitive_gaps": competitive_gaps,
        "brand_metrics": brand_metrics,
        "status": "active"
    }

def extract_real_trending_topics(days: int = 30) -> List[Dict[str, Any]]:
    """Extract REAL trending topics from actual social media data"""
    # Load social media data
    social_files = list(UPLOADS_DIR.glob("*.csv")) + list(UPLOADS_DIR.glob("*.json"))
    
    if not social_files:
        return []
    
    all_posts = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in social_files:
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                all_posts.extend(df.to_dict('records'))
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_posts.extend(data)
                    else:
                        all_posts.append(data)
        except Exception as e:
            continue
    
    if not all_posts:
        return []
    
    # Extract text content and analyze trends
    all_text = []
    hashtags = []
    mentions = []
    
    for post in all_posts:
        text = post.get('text', post.get('caption', post.get('content', '')))
        if text:
            text_lower = text.lower()
            all_text.append(text_lower)
            
            # Extract hashtags
            hashtags.extend(re.findall(r'#(\w+)', text_lower))
            
            # Extract mentions
            mentions.extend(re.findall(r'@(\w+)', text_lower))
    
    # Count frequencies
    hashtag_counts = Counter(hashtags)
    mention_counts = Counter(mentions)
    
    # Extract keywords
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = []
    for text in all_text:
        clean_text = re.sub(r'[#@]\w+', '', text)
        words = re.findall(r'\b[a-z]{4,}\b', clean_text)
        keywords.extend([w for w in words if w not in stop_words])
    
    keyword_counts = Counter(keywords)
    
    # Build trending topics
    trending_topics = []
    
    # Top hashtags
    for hashtag, count in hashtag_counts.most_common(15):
        if count >= 3:
            trending_topics.append({
                "term": f"#{hashtag}",
                "type": "hashtag",
                "frequency": count,
                "trend_score": count * 2.5,
                "category": "social"
            })
    
    # Top keywords
    for keyword, count in keyword_counts.most_common(10):
        if count >= 5:
            trending_topics.append({
                "term": keyword,
                "type": "keyword",
                "frequency": count,
                "trend_score": count * 1.8,
                "category": "content"
            })
    
    # Sort by trend score
    trending_topics.sort(key=lambda x: x['trend_score'], reverse=True)
    
    return trending_topics[:20]

def generate_real_strategic_recommendations(shopify_data: Dict, competitive_data: Dict, trending_topics: List) -> List[Dict[str, Any]]:
    """Generate REAL strategic recommendations based on actual data analysis"""
    recommendations = []
    
    # E-commerce performance recommendations
    if shopify_data.get('status') == 'active':
        total_sales = shopify_data.get('total_sales', 0)
        total_orders = shopify_data.get('total_orders', 0)
        aov = shopify_data.get('aov', 0)
        
        # AOV optimization
        if aov < 75:  # Below streetwear industry average
            recommendations.append({
                "title": "Increase Average Order Value Through Product Bundling",
                "description": f"Current AOV: ${aov:.2f}. Streetwear industry average: $75-120. Revenue opportunity through strategic bundling.",
                "priority": "high",
                "context": f"Analysis of {shopify_data.get('total_orders', 0)} orders shows AOV below optimal range. Top products: {', '.join([p['name'] for p in shopify_data.get('top_products', [])[:3]])}",
                "expected_impact": f"${(75 - aov) * shopify_data.get('total_orders', 0):,.0f} additional revenue with industry-standard AOV",
                "time_to_implement": "2-3 weeks",
                "success_metrics": ["AOV increase to $75+", "Bundle purchase rate >15%", "Revenue per customer improvement"],
                "specific_actions": [
                    "Create product bundles with complementary items",
                    "Implement upselling at checkout for orders under $75",
                    "Offer tiered discounts for larger orders"
                ]
            })
        
        # Revenue trend analysis
        if shopify_data.get('revenue_by_day'):
            daily_sales = [day['sales'] for day in shopify_data['revenue_by_day']]
            if len(daily_sales) >= 7:
                recent_avg = statistics.mean(daily_sales[-7:])
                earlier_avg = statistics.mean(daily_sales[:-7]) if len(daily_sales) > 7 else recent_avg
                
                if recent_avg < earlier_avg * 0.9:  # 10% decline
                    recommendations.append({
                        "title": "Address Declining Revenue Trend",
                        "description": f"Revenue declining: Recent 7-day average (${recent_avg:.0f}) vs earlier period (${earlier_avg:.0f})",
                        "priority": "high",
                        "context": "Sales data shows downward trend requiring immediate attention to prevent further decline.",
                        "expected_impact": "Revenue stabilization and recovery to previous levels",
                        "time_to_implement": "1-2 weeks",
                        "success_metrics": ["Daily revenue recovery", "Order volume stabilization"],
                        "specific_actions": [
                            "Analyze traffic sources for recent decline",
                            "Review and optimize current marketing campaigns",
                            "Consider promotional strategies to boost immediate sales"
                        ]
                    })
    
    # Competitive positioning (if competitive data available)
    if competitive_data.get('status') == 'active':
        crooks_rank = competitive_data.get('crooks_rank')
        brands_analyzed = competitive_data.get('brands_analyzed', 0)
        
        if crooks_rank and crooks_rank > brands_analyzed // 2:  # Bottom half
            performance_comp = competitive_data.get('performance_comparison', {})
            engagement_data = performance_comp.get('avg_engagement', {})
            
            recommendations.append({
                "title": "Improve Competitive Market Position",
                "description": f"Currently ranked #{crooks_rank} of {brands_analyzed} tracked competitors in engagement performance.",
                "priority": "high",
                "context": f"Competitive analysis shows engagement gap: {engagement_data.get('crooks_value', 0):.0f} vs competitor average {engagement_data.get('competitor_avg', 0):.0f}",
                "expected_impact": "Movement to top 3 market position within 6 months",
                "time_to_implement": "4-8 weeks",
                "success_metrics": ["Engagement rate improvement", "Market rank advancement", "Share of voice increase"],
                "specific_actions": [
                    "Adopt successful content strategies from top-ranked competitors",
                    "Increase posting frequency to match market leaders",
                    "Focus on high-engagement content formats identified in competitor analysis"
                ]
            })
        
        # Market share analysis
        market_share = competitive_data.get('market_share', {})
        crooks_share = market_share.get('crooks & castles', 0)
        
        if crooks_share < 100 / brands_analyzed:  # Below equal share
            recommendations.append({
                "title": "Expand Digital Market Share",
                "description": f"Current market share: {crooks_share:.1f}% of total engagement. Below proportional share ({100/brands_analyzed:.1f}%).",
                "priority": "medium",
                "context": f"Market share analysis across {brands_analyzed} brands shows opportunity for growth in digital presence.",
                "expected_impact": f"Target {100/brands_analyzed*1.5:.1f}% market share (50% above proportional)",
                "time_to_implement": "6-12 weeks", 
                "success_metrics": ["Market share percentage increase", "Total engagement growth", "Follower acquisition rate"],
                "specific_actions": [
                    "Increase content production volume",
                    "Expand to additional social platforms",
                    "Implement consistent cross-platform strategy"
                ]
            })
    
    # Trending topics opportunities
    if trending_topics:
        high_value_trends = [t for t in trending_topics if t['frequency'] >= 10]
        
        if high_value_trends:
            recommendations.append({
                "title": "Capitalize on High-Frequency Trending Topics",
                "description": f"High-opportunity trends identified: {', '.join([t['term'] for t in high_value_trends[:3]])}",
                "priority": "medium",
                "context": f"Analysis of {len(trending_topics)} trending topics shows {len(high_value_trends)} with significant engagement potential",
                "expected_impact": "25-40% engagement increase on trending content",
                "time_to_implement": "1-2 weeks",
                "success_metrics": ["Trending content engagement rate", "Hashtag performance", "Topic relevance score"],
                "specific_actions": [
                    f"Create content series around {high_value_trends[0]['term']} ({high_value_trends[0]['frequency']} mentions)",
                    "Develop trending topic monitoring system",
                    "Implement rapid content creation process for trending opportunities"
                ]
            })
    
    return recommendations

@router.get("/overview")
async def get_executive_overview(days: int = Query(30, ge=1, le=365)):
    """
    Generate comprehensive executive overview using ONLY real data - NO MOCK DATA
    """
    try:
        # Load REAL data from all sources
        shopify_data = load_real_shopify_data(days)
        competitive_data = load_real_competitive_data()
        trending_topics = extract_real_trending_topics(days)
        
        # Generate strategic recommendations based on real analysis
        recommendations = generate_real_strategic_recommendations(
            shopify_data, competitive_data, trending_topics
        )
        
        # Determine alerts based on actual data status
        alerts = []
        
        if shopify_data.get('status') == 'no_data':
            alerts.append({
                "level": "critical",
                "message": "No Shopify sales data detected",
                "action": "Upload Shopify order export files to /data/shopify/ directory"
            })
        
        if competitive_data.get('status') == 'no_data':
            alerts.append({
                "level": "critical",
                "message": "No competitive intelligence data loaded",
                "action": "Upload Apify scraping results or competitive analysis files"
            })
        
        if not trending_topics:
            alerts.append({
                "level": "warning",
                "message": "No trending topics data available",
                "action": "Upload recent social media data to enable trend analysis"
            })
        
        # Revenue intelligence insights
        revenue_insights = []
        if shopify_data.get('status') == 'active':
            revenue_insights.append(f"${shopify_data['total_sales']:,.2f} revenue from {shopify_data['total_orders']} orders")
            revenue_insights.append(f"${shopify_data['aov']:.2f} average order value")
            
            if shopify_data.get('top_products'):
                top_product = shopify_data['top_products'][0]
                revenue_insights.append(f"Top product: {top_product['name']} (${top_product['revenue']:,.2f} revenue)")
        
        # Competitive intelligence insights
        competitive_insights = []
        if competitive_data.get('status') == 'active':
            if competitive_data.get('crooks_rank'):
                competitive_insights.append(f"Market position: #{competitive_data['crooks_rank']} of {competitive_data['brands_analyzed']} tracked brands")
            
            market_share = competitive_data.get('market_share', {}).get('crooks & castles', 0)
            competitive_insights.append(f"Digital market share: {market_share:.1f}%")
        
        # Data source status
        data_sources = {
            "shopify": shopify_data.get('status') == 'active',
            "competitive": competitive_data.get('status') == 'active', 
            "social": len(trending_topics) > 0
        }
        
        return {
            "success": True,
            "timeframe_days": days,
            "shopify_metrics": shopify_data,
            "competitive_analysis": competitive_data,
            "trending_topics": trending_topics,
            "recommendations": recommendations,
            "alerts": alerts,
            "revenue_insights": revenue_insights,
            "competitive_insights": competitive_insights,
            "data_sources": data_sources,
            "analysis_confidence": {
                "revenue": 95 if shopify_data.get('status') == 'active' else 0,
                "competitive": 90 if competitive_data.get('brands_analyzed', 0) >= 8 else 50 if competitive_data.get('brands_analyzed', 0) > 0 else 0,
                "trending": 85 if len(trending_topics) >= 10 else 60 if len(trending_topics) > 0 else 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive overview generation failed: {str(e)}")
