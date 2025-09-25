import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path
import os

class ShopifyIntegration:
    """Shopify integration for pulling sales, traffic, and conversion data"""
    
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}.myshopify.com/admin/api/2023-10"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        # Ensure data directory exists
        self.data_dir = Path("data/shopify")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Shopify API connection"""
        try:
            response = requests.get(f"{self.base_url}/shop.json", headers=self.headers)
            if response.status_code == 200:
                shop_data = response.json()["shop"]
                return {
                    "success": True,
                    "shop_name": shop_data["name"],
                    "domain": shop_data["domain"],
                    "currency": shop_data["currency"],
                    "timezone": shop_data["timezone"]
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
        """Pull daily sales data from Shopify"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get orders
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
                
                response = requests.get(f"{self.base_url}/orders.json", headers=self.headers, params=params)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Failed to fetch orders: {response.text}"}
                
                data = response.json()
                orders = data.get("orders", [])
                all_orders.extend(orders)
                
                # Check for pagination
                link_header = response.headers.get("Link", "")
                if "rel=\"next\"" in link_header:
                    # Extract next page info from Link header
                    next_link = [link.strip() for link in link_header.split(",") if "rel=\"next\"" in link][0]
                    page_info = next_link.split("page_info=")[1].split(">")[0]
                else:
                    break
            
            # Process orders into daily metrics
            daily_data = {}
            total_revenue = 0
            total_orders = len(all_orders)
            
            for order in all_orders:
                order_date = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).date()
                order_value = float(order.get("total_price", 0))
                
                if order_date not in daily_data:
                    daily_data[order_date] = {
                        "date": order_date.isoformat(),
                        "orders": 0,
                        "revenue": 0,
                        "avg_order_value": 0,
                        "items_sold": 0
                    }
                
                daily_data[order_date]["orders"] += 1
                daily_data[order_date]["revenue"] += order_value
                daily_data[order_date]["items_sold"] += len(order.get("line_items", []))
                total_revenue += order_value
            
            # Calculate averages
            for date_data in daily_data.values():
                if date_data["orders"] > 0:
                    date_data["avg_order_value"] = date_data["revenue"] / date_data["orders"]
            
            # Save data
            sales_file = self.data_dir / f"sales_data_{datetime.now().strftime('%Y%m%d')}.json"
            with open(sales_file, 'w') as f:
                json.dump({
                    "daily_data": {str(k): v for k, v in daily_data.items()},
                    "summary": {
                        "total_orders": total_orders,
                        "total_revenue": total_revenue,
                        "avg_order_value": total_revenue / total_orders if total_orders > 0 else 0,
                        "date_range": f"{start_date.date()} to {end_date.date()}"
                    }
                }, f, indent=2)
            
            return {
                "success": True,
                "daily_data": list(daily_data.values()),
                "summary": {
                    "total_orders": total_orders,
                    "total_revenue": round(total_revenue, 2),
                    "avg_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
                    "days_analyzed": days_back
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get sales data: {str(e)}"}
    
    def get_traffic_data(self, days_back: int = 30) -> Dict[str, Any]:
        """Get website traffic data from Shopify Analytics"""
        try:
            # Note: Shopify doesn't provide detailed traffic analytics via API
            # This would typically require Google Analytics integration
            # For now, we'll use order data as a proxy for traffic conversion
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get customer data as traffic proxy
            params = {
                "created_at_min": start_date.isoformat(),
                "created_at_max": end_date.isoformat(),
                "limit": 250
            }
            
            response = requests.get(f"{self.base_url}/customers.json", headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch customer data: {response.text}"}
            
            customers = response.json().get("customers", [])
            
            # Process into daily metrics
            daily_traffic = {}
            for customer in customers:
                created_date = datetime.fromisoformat(customer["created_at"].replace("Z", "+00:00")).date()
                
                if created_date not in daily_traffic:
                    daily_traffic[created_date] = {
                        "date": created_date.isoformat(),
                        "new_customers": 0,
                        "returning_customers": 0
                    }
                
                # Check if customer has previous orders
                orders_count = int(customer.get("orders_count", 0))
                if orders_count <= 1:
                    daily_traffic[created_date]["new_customers"] += 1
                else:
                    daily_traffic[created_date]["returning_customers"] += 1
            
            return {
                "success": True,
                "daily_traffic": list(daily_traffic.values()),
                "summary": {
                    "total_new_customers": sum(d["new_customers"] for d in daily_traffic.values()),
                    "total_returning_customers": sum(d["returning_customers"] for d in daily_traffic.values()),
                    "days_analyzed": days_back
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get traffic data: {str(e)}"}
    
    def get_product_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """Get product performance data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get orders with line items
            params = {
                "created_at_min": start_date.isoformat(),
                "created_at_max": end_date.isoformat(),
                "status": "any",
                "limit": 250
            }
            
            response = requests.get(f"{self.base_url}/orders.json", headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch orders: {response.text}"}
            
            orders = response.json().get("orders", [])
            
            # Analyze product performance
            product_performance = {}
            
            for order in orders:
                for item in order.get("line_items", []):
                    product_id = item.get("product_id")
                    product_title = item.get("title", "Unknown Product")
                    quantity = int(item.get("quantity", 0))
                    price = float(item.get("price", 0))
                    
                    if product_id not in product_performance:
                        product_performance[product_id] = {
                            "product_id": product_id,
                            "title": product_title,
                            "units_sold": 0,
                            "revenue": 0,
                            "orders": 0
                        }
                    
                    product_performance[product_id]["units_sold"] += quantity
                    product_performance[product_id]["revenue"] += price * quantity
                    product_performance[product_id]["orders"] += 1
            
            # Sort by revenue
            top_products = sorted(product_performance.values(), key=lambda x: x["revenue"], reverse=True)
            
            return {
                "success": True,
                "top_products": top_products[:10],  # Top 10 products
                "total_products_sold": len(product_performance)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get product performance: {str(e)}"}

def correlate_social_with_sales(social_data: pd.DataFrame, sales_data: List[Dict]) -> Dict[str, Any]:
    """Correlate social media trends with sales performance"""
    
    if social_data.empty or not sales_data:
        return {
            "correlation_found": False,
            "message": "Insufficient data for correlation analysis"
        }
    
    try:
        # Convert sales data to DataFrame
        sales_df = pd.DataFrame(sales_data)
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        
        # Extract social media posting dates
        if 'date' in social_data.columns:
            social_data['date'] = pd.to_datetime(social_data['date'])
        elif 'created_at' in social_data.columns:
            social_data['date'] = pd.to_datetime(social_data['created_at'])
        else:
            return {
                "correlation_found": False,
                "message": "No date column found in social data"
            }
        
        # Group social data by date
        daily_social = social_data.groupby(social_data['date'].dt.date).agg({
            'likes': 'sum' if 'likes' in social_data.columns else lambda x: 0,
            'comments': 'sum' if 'comments' in social_data.columns else lambda x: 0,
            'shares': 'sum' if 'shares' in social_data.columns else lambda x: 0
        }).reset_index()
        
        # Merge social and sales data
        sales_df['date_only'] = sales_df['date'].dt.date
        merged_data = pd.merge(daily_social, sales_df, left_on='date', right_on='date_only', how='inner')
        
        if len(merged_data) < 3:
            return {
                "correlation_found": False,
                "message": "Not enough overlapping data points for correlation"
            }
        
        # Calculate correlations
        correlations = {}
        
        if 'likes' in merged_data.columns and merged_data['likes'].sum() > 0:
            correlations['likes_revenue'] = merged_data['likes'].corr(merged_data['revenue'])
            correlations['likes_orders'] = merged_data['likes'].corr(merged_data['orders'])
        
        if 'comments' in merged_data.columns and merged_data['comments'].sum() > 0:
            correlations['comments_revenue'] = merged_data['comments'].corr(merged_data['revenue'])
            correlations['comments_orders'] = merged_data['comments'].corr(merged_data['orders'])
        
        # Find strongest correlations
        strong_correlations = {k: v for k, v in correlations.items() if abs(v) > 0.3}
        
        # Identify high-performing social days
        if 'likes' in merged_data.columns:
            top_social_days = merged_data.nlargest(3, 'likes')[['date', 'likes', 'revenue', 'orders']]
        else:
            top_social_days = merged_data.nlargest(3, 'revenue')[['date', 'revenue', 'orders']]
        
        return {
            "correlation_found": True,
            "correlations": correlations,
            "strong_correlations": strong_correlations,
            "top_performing_days": top_social_days.to_dict('records'),
            "insights": generate_correlation_insights(correlations, strong_correlations),
            "data_points": len(merged_data)
        }
        
    except Exception as e:
        return {
            "correlation_found": False,
            "error": f"Correlation analysis failed: {str(e)}"
        }

def generate_correlation_insights(correlations: Dict[str, float], strong_correlations: Dict[str, float]) -> List[str]:
    """Generate actionable insights from correlation analysis"""
    
    insights = []
    
    if not correlations:
        insights.append("No social media metrics available for correlation analysis")
        return insights
    
    # Analyze likes correlation
    if 'likes_revenue' in correlations:
        likes_revenue_corr = correlations['likes_revenue']
        if likes_revenue_corr > 0.5:
            insights.append(f"Strong positive correlation ({likes_revenue_corr:.2f}) between social media likes and revenue")
        elif likes_revenue_corr > 0.3:
            insights.append(f"Moderate positive correlation ({likes_revenue_corr:.2f}) between likes and sales")
        elif likes_revenue_corr < -0.3:
            insights.append(f"Negative correlation ({likes_revenue_corr:.2f}) between likes and revenue - investigate content quality")
    
    # Analyze comments correlation
    if 'comments_revenue' in correlations:
        comments_revenue_corr = correlations['comments_revenue']
        if comments_revenue_corr > 0.4:
            insights.append(f"High engagement (comments) strongly correlates with revenue ({comments_revenue_corr:.2f})")
        elif comments_revenue_corr > 0.2:
            insights.append(f"Comments show positive impact on sales ({comments_revenue_corr:.2f})")
    
    # Strategic recommendations
    if strong_correlations:
        best_metric = max(strong_correlations.items(), key=lambda x: abs(x[1]))
        insights.append(f"Focus on {best_metric[0].split('_')[0]} - strongest predictor of sales performance")
    
    if not strong_correlations:
        insights.append("No strong correlations found - consider longer data collection period or different content strategies")
    
    return insights

def analyze_hashtag_revenue_impact(social_data: pd.DataFrame, sales_data: List[Dict]) -> Dict[str, Any]:
    """Analyze which hashtags correlate with revenue spikes"""
    
    if social_data.empty or not sales_data:
        return {"success": False, "message": "Insufficient data"}
    
    try:
        # Convert sales data
        sales_df = pd.DataFrame(sales_data)
        sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
        
        # Extract hashtags and dates from social data
        hashtag_performance = {}
        
        for _, row in social_data.iterrows():
            if 'hashtags' in row and pd.notna(row['hashtags']):
                post_date = None
                if 'date' in row:
                    post_date = pd.to_datetime(row['date']).date()
                elif 'created_at' in row:
                    post_date = pd.to_datetime(row['created_at']).date()
                
                if post_date:
                    # Find corresponding sales data
                    sales_match = sales_df[sales_df['date'] == post_date]
                    if not sales_match.empty:
                        revenue = sales_match.iloc[0]['revenue']
                        
                        # Extract hashtags
                        import re
                        hashtags = re.findall(r'#\w+', str(row['hashtags']).lower())
                        
                        for hashtag in hashtags:
                            if hashtag not in hashtag_performance:
                                hashtag_performance[hashtag] = {
                                    "hashtag": hashtag,
                                    "total_revenue": 0,
                                    "post_count": 0,
                                    "avg_revenue_per_post": 0
                                }
                            
                            hashtag_performance[hashtag]["total_revenue"] += revenue
                            hashtag_performance[hashtag]["post_count"] += 1
        
        # Calculate averages and sort by performance
        for hashtag_data in hashtag_performance.values():
            if hashtag_data["post_count"] > 0:
                hashtag_data["avg_revenue_per_post"] = hashtag_data["total_revenue"] / hashtag_data["post_count"]
        
        # Sort by average revenue per post
        top_hashtags = sorted(hashtag_performance.values(), key=lambda x: x["avg_revenue_per_post"], reverse=True)
        
        return {
            "success": True,
            "top_revenue_hashtags": top_hashtags[:10],
            "total_hashtags_analyzed": len(hashtag_performance)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Hashtag analysis failed: {str(e)}"}

# Configuration helper
def setup_shopify_config(shop_domain: str, access_token: str) -> Dict[str, Any]:
    """Setup and validate Shopify configuration"""
    
    config_dir = Path("data/config")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "shop_domain": shop_domain,
        "access_token": access_token,
        "setup_date": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Test connection
    shopify = ShopifyIntegration(shop_domain, access_token)
    test_result = shopify.test_connection()
    
    if test_result["success"]:
        config["shop_info"] = test_result
        config["status"] = "connected"
        
        # Save config
        config_file = config_dir / "shopify_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "message": f"Successfully connected to {test_result['shop_name']}",
            "config": config
        }
    else:
        config["status"] = "error"
        config["error"] = test_result["error"]
        
        return {
            "success": False,
            "message": "Failed to connect to Shopify",
            "error": test_result["error"]
        }
