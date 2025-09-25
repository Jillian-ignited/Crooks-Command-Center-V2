import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from dateutil import parser
import re

class ShopifyIntegration:
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain.replace('.myshopify.com', '')
        self.access_token = access_token
        self.base_url = f"https://{self.shop_domain}.myshopify.com/admin/api/2023-10"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        # Ensure data directories exist
        Path("data/shopify").mkdir(parents=True, exist_ok=True)
        Path("data/config").mkdir(parents=True, exist_ok=True)

    def test_connection(self) -> Dict[str, Any]:
        """Test the Shopify API connection"""
        try:
            response = requests.get(f"{self.base_url}/shop.json", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json()["shop"]
                return {
                    "success": True,
                    "shop_name": shop_data["name"],
                    "shop_domain": shop_data["domain"],
                    "currency": shop_data["currency"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }

    def get_daily_sales_data(self, days_back: int = 30) -> Dict[str, Any]:
        """Get daily sales data with conversion metrics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get orders
            orders_url = f"{self.base_url}/orders.json"
            params = {
                "created_at_min": start_date.isoformat(),
                "created_at_max": end_date.isoformat(),
                "status": "any",
                "limit": 250
            }
            
            all_orders = []
            page_info = None
            
            while True:
                if page_info:
                    params["page_info"] = page_info
                
                response = requests.get(orders_url, headers=self.headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Orders API error: {response.status_code}"}
                
                data = response.json()
                all_orders.extend(data["orders"])
                
                # Check for pagination
                link_header = response.headers.get("Link", "")
                if "rel=\"next\"" in link_header:
                    # Extract next page info
                    next_link = re.search(r'<([^>]+)>; rel="next"', link_header)
                    if next_link:
                        next_url = next_link.group(1)
                        page_info = re.search(r'page_info=([^&]+)', next_url)
                        if page_info:
                            page_info = page_info.group(1)
                        else:
                            break
                    else:
                        break
                else:
                    break
            
            # Process orders into daily data with conversion tracking
            daily_data = {}
            total_revenue = 0
            total_orders = len(all_orders)
            
            for order in all_orders:
                order_date = parser.parse(order["created_at"]).date()
                order_value = float(order["total_price"])
                
                if order_date not in daily_data:
                    daily_data[order_date] = {
                        "date": order_date.isoformat(),
                        "revenue": 0,
                        "orders": 0,
                        "customers": set(),
                        "traffic_sources": {},
                        "conversion_data": {
                            "total_sessions": 0,
                            "orders": 0,
                            "conversion_rate": 0
                        }
                    }
                
                daily_data[order_date]["revenue"] += order_value
                daily_data[order_date]["orders"] += 1
                daily_data[order_date]["customers"].add(order.get("customer", {}).get("id", "unknown"))
                daily_data[order_date]["conversion_data"]["orders"] += 1
                
                # Track referral sources
                referring_site = order.get("referring_site", "direct")
                if referring_site:
                    source_key = self._categorize_traffic_source(referring_site)
                    daily_data[order_date]["traffic_sources"][source_key] = daily_data[order_date]["traffic_sources"].get(source_key, 0) + 1
                
                total_revenue += order_value
            
            # Convert sets to counts and calculate conversion rates
            processed_daily_data = []
            for date_key, data in daily_data.items():
                data["unique_customers"] = len(data["customers"])
                del data["customers"]  # Remove set object for JSON serialization
                
                # Estimate sessions (basic approximation)
                # In a real implementation, you'd get this from Google Analytics or Shopify Analytics
                estimated_sessions = max(data["orders"] * 10, 50)  # Rough estimate: 10 sessions per order minimum
                data["conversion_data"]["total_sessions"] = estimated_sessions
                data["conversion_data"]["conversion_rate"] = (data["orders"] / estimated_sessions) * 100 if estimated_sessions > 0 else 0
                
                processed_daily_data.append(data)
            
            # Calculate summary metrics
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            total_customers = len(set(order.get("customer", {}).get("id", f"unknown_{i}") for i, order in enumerate(all_orders)))
            
            # Calculate overall conversion metrics
            total_estimated_sessions = sum(day["conversion_data"]["total_sessions"] for day in processed_daily_data)
            overall_conversion_rate = (total_orders / total_estimated_sessions) * 100 if total_estimated_sessions > 0 else 0
            
            # Traffic source analysis
            all_traffic_sources = {}
            for day in processed_daily_data:
                for source, count in day["traffic_sources"].items():
                    all_traffic_sources[source] = all_traffic_sources.get(source, 0) + count
            
            return {
                "success": True,
                "daily_data": processed_daily_data,
                "summary": {
                    "total_revenue": total_revenue,
                    "total_orders": total_orders,
                    "total_customers": total_customers,
                    "avg_order_value": avg_order_value,
                    "date_range": f"{start_date.date()} to {end_date.date()}",
                    "conversion_metrics": {
                        "overall_conversion_rate": round(overall_conversion_rate, 2),
                        "total_sessions": total_estimated_sessions,
                        "orders_per_session": round(total_orders / total_estimated_sessions, 4) if total_estimated_sessions > 0 else 0,
                        "revenue_per_session": round(total_revenue / total_estimated_sessions, 2) if total_estimated_sessions > 0 else 0
                    },
                    "traffic_sources": all_traffic_sources
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Sales data error: {str(e)}"}

    def get_traffic_data(self, days_back: int = 30) -> Dict[str, Any]:
        """Get traffic and conversion data (basic implementation)"""
        try:
            # Note: Shopify doesn't provide detailed traffic analytics via API
            # This would typically integrate with Google Analytics
            # For now, we'll provide estimated metrics based on orders
            
            sales_data = self.get_daily_sales_data(days_back)
            if not sales_data["success"]:
                return sales_data
            
            # Estimate traffic metrics based on conversion assumptions
            total_orders = sales_data["summary"]["total_orders"]
            estimated_conversion_rate = 2.5  # Industry average for e-commerce
            estimated_sessions = int(total_orders / (estimated_conversion_rate / 100))
            estimated_pageviews = estimated_sessions * 3  # Average pages per session
            
            traffic_summary = {
                "estimated_sessions": estimated_sessions,
                "estimated_pageviews": estimated_pageviews,
                "estimated_bounce_rate": 65.0,  # Industry average
                "avg_session_duration": 180,  # 3 minutes average
                "conversion_rate": estimated_conversion_rate,
                "note": "Traffic metrics are estimated. Connect Google Analytics for precise data."
            }
            
            return {
                "success": True,
                "traffic_summary": traffic_summary,
                "conversion_funnel": {
                    "sessions": estimated_sessions,
                    "product_views": int(estimated_sessions * 0.6),
                    "add_to_cart": int(estimated_sessions * 0.15),
                    "checkout_started": int(estimated_sessions * 0.08),
                    "orders_completed": total_orders,
                    "conversion_rates": {
                        "session_to_product_view": 60.0,
                        "session_to_cart": 15.0,
                        "session_to_checkout": 8.0,
                        "session_to_purchase": estimated_conversion_rate,
                        "cart_to_checkout": 53.3,
                        "checkout_to_purchase": 31.25
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Traffic data error: {str(e)}"}

    def get_product_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """Get product performance with conversion metrics"""
        try:
            # Get products
            products_response = requests.get(f"{self.base_url}/products.json", headers=self.headers, timeout=30)
            if products_response.status_code != 200:
                return {"success": False, "error": "Failed to fetch products"}
            
            products = products_response.json()["products"]
            
            # Get sales data
            sales_data = self.get_daily_sales_data(days_back)
            if not sales_data["success"]:
                return sales_data
            
            # Analyze product performance (simplified)
            product_performance = []
            for product in products[:10]:  # Limit to top 10 products
                product_performance.append({
                    "id": product["id"],
                    "title": product["title"],
                    "handle": product["handle"],
                    "product_type": product["product_type"],
                    "vendor": product["vendor"],
                    "estimated_views": 150,  # Would come from analytics
                    "estimated_conversion_rate": 2.8,
                    "price": product["variants"][0]["price"] if product["variants"] else "0.00"
                })
            
            return {
                "success": True,
                "products": product_performance,
                "summary": {
                    "total_products": len(products),
                    "analyzed_products": len(product_performance),
                    "avg_conversion_rate": 2.8,
                    "note": "Product conversion metrics are estimated. Connect analytics for precise data."
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Product performance error: {str(e)}"}

    def _categorize_traffic_source(self, referring_site: str) -> str:
        """Categorize traffic sources for conversion analysis"""
        if not referring_site or referring_site.lower() in ["direct", "", "null"]:
            return "direct"
        
        referring_site = referring_site.lower()
        
        # Social media sources
        social_platforms = ["instagram", "facebook", "twitter", "tiktok", "youtube", "pinterest", "snapchat"]
        for platform in social_platforms:
            if platform in referring_site:
                return f"social_{platform}"
        
        # Search engines
        search_engines = ["google", "bing", "yahoo", "duckduckgo"]
        for engine in search_engines:
            if engine in referring_site:
                return f"search_{engine}"
        
        # Other categorizations
        if any(term in referring_site for term in ["email", "newsletter", "mailchimp"]):
            return "email"
        elif any(term in referring_site for term in ["ad", "ads", "campaign"]):
            return "paid_ads"
        else:
            return "referral"

def correlate_social_with_sales(social_df: pd.DataFrame, sales_data: List[Dict]) -> Dict[str, Any]:
    """Enhanced correlation analysis with conversion metrics"""
    try:
        if social_df.empty or not sales_data:
            return {"success": False, "error": "Insufficient data for correlation analysis"}
        
        # Convert sales data to DataFrame
        sales_df = pd.DataFrame(sales_data)
        sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
        
        # Prepare social data
        if 'date' in social_df.columns:
            social_df['date'] = pd.to_datetime(social_df['date']).dt.date
        elif 'created_at' in social_df.columns:
            social_df['date'] = pd.to_datetime(social_df['created_at']).dt.date
        else:
            return {"success": False, "error": "No date column found in social data"}
        
        # Aggregate social data by date
        daily_social = social_df.groupby('date').agg({
            'brand': 'count',  # Total posts per day
            'text': lambda x: len(' '.join(x.astype(str))) if len(x) > 0 else 0,  # Total text length
        }).rename(columns={'brand': 'total_posts', 'text': 'total_text_length'})
        
        # Add hashtag and engagement metrics if available
        if 'hashtags' in social_df.columns:
            daily_social['total_hashtags'] = social_df.groupby('date')['hashtags'].apply(
                lambda x: len([tag for tags in x.dropna() for tag in str(tags).split() if tag.startswith('#')])
            )
        
        if 'engagement' in social_df.columns:
            daily_social['avg_engagement'] = social_df.groupby('date')['engagement'].mean()
        
        # Merge with sales data
        merged_df = sales_df.set_index('date').join(daily_social, how='inner')
        
        if len(merged_df) < 3:
            return {"success": False, "error": "Not enough overlapping dates for correlation analysis"}
        
        # Calculate correlations
        correlations = {}
        conversion_correlations = {}
        
        # Revenue correlations
        if 'total_posts' in merged_df.columns:
            correlations['posts_revenue'] = merged_df['total_posts'].corr(merged_df['revenue'])
            conversion_correlations['posts_conversion'] = merged_df['total_posts'].corr(
                merged_df['conversion_data'].apply(lambda x: x['conversion_rate'])
            )
        
        if 'total_hashtags' in merged_df.columns:
            correlations['hashtags_revenue'] = merged_df['total_hashtags'].corr(merged_df['revenue'])
            conversion_correlations['hashtags_conversion'] = merged_df['total_hashtags'].corr(
                merged_df['conversion_data'].apply(lambda x: x['conversion_rate'])
            )
        
        if 'avg_engagement' in merged_df.columns:
            correlations['engagement_revenue'] = merged_df['avg_engagement'].corr(merged_df['revenue'])
            conversion_correlations['engagement_conversion'] = merged_df['avg_engagement'].corr(
                merged_df['conversion_data'].apply(lambda x: x['conversion_rate'])
            )
        
        # Determine correlation strength
        max_correlation = max([abs(v) for v in correlations.values() if pd.notna(v)], default=0)
        correlation_found = max_correlation > 0.2
        strong_correlations = max_correlation > 0.5
        
        # Generate insights
        insights = []
        if correlation_found:
            if correlations.get('posts_revenue', 0) > 0.3:
                insights.append(f"Higher social media activity correlates with increased revenue (r={correlations['posts_revenue']:.2f})")
            if conversion_correlations.get('posts_conversion', 0) > 0.3:
                insights.append(f"More social posts correlate with better conversion rates (r={conversion_correlations['posts_conversion']:.2f})")
            if correlations.get('hashtags_revenue', 0) > 0.3:
                insights.append(f"Hashtag usage shows positive correlation with sales (r={correlations['hashtags_revenue']:.2f})")
        else:
            insights.append("No strong correlation found between social activity and revenue")
            insights.append("Consider analyzing longer time periods or different social metrics")
        
        return {
            "success": True,
            "correlation_found": correlation_found,
            "strong_correlations": strong_correlations,
            "correlations": correlations,
            "conversion_correlations": conversion_correlations,
            "insights": insights,
            "data_points": len(merged_df),
            "date_range": f"{merged_df.index.min()} to {merged_df.index.max()}"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Correlation analysis failed: {str(e)}"}

def analyze_hashtag_revenue_impact(social_df: pd.DataFrame, sales_data: List[Dict]) -> Dict[str, Any]:
    """Enhanced hashtag analysis with conversion impact"""
    try:
        if social_df.empty or not sales_data:
            return {"success": False, "error": "Insufficient data for hashtag analysis"}
        
        # Extract hashtags from social data
        all_hashtags = []
        for _, row in social_df.iterrows():
            post_date = pd.to_datetime(row.get('date', row.get('created_at', datetime.now()))).date()
            
            # Extract hashtags from text or hashtags column
            hashtags_text = str(row.get('hashtags', '')) + ' ' + str(row.get('text', ''))
            hashtags = re.findall(r'#\w+', hashtags_text.lower())
            
            for hashtag in hashtags:
                all_hashtags.append({
                    'hashtag': hashtag,
                    'date': post_date,
                    'brand': row.get('brand', 'unknown')
                })
        
        if not all_hashtags:
            return {"success": False, "error": "No hashtags found in social data"}
        
        hashtags_df = pd.DataFrame(all_hashtags)
        sales_df = pd.DataFrame(sales_data)
        sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
        
        # Analyze hashtag performance
        hashtag_performance = []
        
        for hashtag in hashtags_df['hashtag'].unique():
            hashtag_dates = hashtags_df[hashtags_df['hashtag'] == hashtag]['date'].unique()
            
            # Calculate revenue and conversion metrics for days with this hashtag
            hashtag_sales = sales_df[sales_df['date'].isin(hashtag_dates)]
            
            if len(hashtag_sales) > 0:
                total_revenue = hashtag_sales['revenue'].sum()
                total_orders = hashtag_sales['orders'].sum()
                avg_conversion_rate = hashtag_sales['conversion_data'].apply(lambda x: x['conversion_rate']).mean()
                post_count = len(hashtags_df[hashtags_df['hashtag'] == hashtag])
                
                hashtag_performance.append({
                    'hashtag': hashtag,
                    'post_count': post_count,
                    'total_revenue': total_revenue,
                    'total_orders': total_orders,
                    'avg_revenue_per_post': total_revenue / post_count if post_count > 0 else 0,
                    'avg_orders_per_post': total_orders / post_count if post_count > 0 else 0,
                    'avg_conversion_rate': avg_conversion_rate,
                    'days_active': len(hashtag_dates)
                })
        
        # Sort by revenue per post
        hashtag_performance.sort(key=lambda x: x['avg_revenue_per_post'], reverse=True)
        
        return {
            "success": True,
            "top_revenue_hashtags": hashtag_performance[:10],
            "total_hashtags_analyzed": len(hashtag_performance),
            "conversion_insights": {
                "best_converting_hashtag": max(hashtag_performance, key=lambda x: x['avg_conversion_rate'])['hashtag'] if hashtag_performance else None,
                "highest_revenue_hashtag": hashtag_performance[0]['hashtag'] if hashtag_performance else None,
                "avg_conversion_rate": sum(h['avg_conversion_rate'] for h in hashtag_performance) / len(hashtag_performance) if hashtag_performance else 0
            }
        }
        
    except Exception as e:
        return {"success": False, "error": f"Hashtag analysis failed: {str(e)}"}

def setup_shopify_config(shop_domain: str, access_token: str) -> Dict[str, Any]:
    """Setup and test Shopify configuration with conversion tracking"""
    try:
        shopify = ShopifyIntegration(shop_domain, access_token)
        test_result = shopify.test_connection()
        
        if test_result["success"]:
            config = {
                "shop_domain": shop_domain,
                "access_token": access_token,
                "setup_date": datetime.now().isoformat(),
                "status": "connected",
                "shop_info": {
                    "shop_name": test_result["shop_name"],
                    "shop_domain": test_result["shop_domain"],
                    "currency": test_result["currency"]
                },
                "features": {
                    "sales_tracking": True,
                    "conversion_tracking": True,
                    "traffic_estimation": True,
                    "product_performance": True
                }
            }
            
            # Save configuration
            config_file = Path("data/config/shopify_config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {
                "success": True,
                "message": f"Successfully connected to {test_result['shop_name']}",
                "config": config
            }
        else:
            return {
                "success": False,
                "error": test_result["error"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Configuration setup failed: {str(e)}"
        }
