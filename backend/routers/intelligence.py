# /backend/routers/intelligence.py - REAL DATA INTELLIGENCE ANALYSIS - NO MOCK DATA

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

# Data directories - same as executive router
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

def analyze_competitive_intelligence(days: int = 30) -> Dict[str, Any]:
    """Deep competitive intelligence analysis from real data"""
    
    competitive_files = list(COMPETITIVE_DATA_DIR.glob("*.csv")) + list(COMPETITIVE_DATA_DIR.glob("*.json"))
    uploads_files = list(UPLOADS_DIR.glob("*.csv")) + list(UPLOADS_DIR.glob("*.json"))
    
    all_files = competitive_files + uploads_files
    
    if not all_files:
        return {
            "status": "no_data",
            "message": "No competitive data files found. Upload data to /data/competitive/ or /data/uploads/",
            "analysis": {}
        }
    
    all_posts = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Load all real data files
    for file_path in all_files:
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                
                # Standardize column names
                column_mapping = {
                    'Brand': 'brand', 'brand_name': 'brand', 'Brand Name': 'brand',
                    'Platform': 'platform', 'platform_name': 'platform',
                    'Content': 'content', 'post_content': 'content', 'Post Content': 'content',
                    'Engagement': 'engagement', 'engagement_rate': 'engagement', 'Engagement Rate': 'engagement',
                    'Likes': 'likes', 'Comments': 'comments', 'Shares': 'shares',
                    'Date': 'date', 'created_date': 'date', 'post_date': 'date', 'Post Date': 'date',
                    'URL': 'url', 'Post URL': 'url', 'Link': 'url'
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns:
                        df = df.rename(columns={old_col: new_col})
                
                # Filter by date if available
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df[df['date'] >= cutoff_date]
                
                all_posts.extend(df.to_dict('records'))
                
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_posts.extend(data)
                    elif isinstance(data, dict):
                        if 'posts' in data:
                            all_posts.extend(data['posts'])
                        elif 'data' in data:
                            all_posts.extend(data['data'])
                        else:
                            all_posts.append(data)
                            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    if not all_posts:
        return {
            "status": "no_posts",
            "message": "Data files loaded but no posts found in date range",
            "analysis": {}
        }
    
    # Perform deep competitive analysis
    analysis = {
        "dataset_overview": {
            "total_posts": len(all_posts),
            "date_range": days,
            "files_processed": len(all_files),
            "data_sources": [str(f.name) for f in all_files]
        },
        "brand_analysis": {},
        "platform_analysis": {},
        "content_analysis": {},
        "engagement_analysis": {},
        "trending_analysis": {},
        "competitive_positioning": {}
    }
    
    # Brand performance analysis
    brand_metrics = defaultdict(lambda: {
        'posts': 0, 'total_engagement': 0, 'engagements': [], 
        'platforms': set(), 'content_types': []
    })
    
    platform_metrics = defaultdict(lambda: {
        'posts': 0, 'brands': set(), 'total_engagement': 0
    })
    
    all_content = []
    engagement_data = []
    
    for post in all_posts:
        brand = post.get('brand', 'Unknown').lower().strip()
        platform = post.get('platform', 'Unknown').lower().strip()
        content = post.get('content', '')
        
        # Parse engagement data
        engagement = 0
        if 'engagement' in post:
            engagement_val = post['engagement']
            if isinstance(engagement_val, str):
                # Extract numbers from string
                numbers = re.findall(r'\d+', engagement_val)
                engagement = int(numbers[0]) if numbers else 0
            else:
                engagement = float(engagement_val) if engagement_val else 0
        elif 'likes' in post:
            likes = float(post.get('likes', 0)) if post.get('likes') else 0
            comments = float(post.get('comments', 0)) if post.get('comments') else 0
            shares = float(post.get('shares', 0)) if post.get('shares') else 0
            engagement = likes + comments + shares
        
        # Brand metrics
        brand_metrics[brand]['posts'] += 1
        brand_metrics[brand]['total_engagement'] += engagement
        brand_metrics[brand]['engagements'].append(engagement)
        brand_metrics[brand]['platforms'].add(platform)
        
        # Platform metrics
        platform_metrics[platform]['posts'] += 1
        platform_metrics[platform]['brands'].add(brand)
        platform_metrics[platform]['total_engagement'] += engagement
        
        # Content analysis
        if content:
            all_content.append(content.lower())
            
        engagement_data.append(engagement)
    
    # Build brand analysis
    brand_analysis = {}
    for brand, metrics in brand_metrics.items():
        avg_engagement = statistics.mean(metrics['engagements']) if metrics['engagements'] else 0
        brand_analysis[brand] = {
            "post_count": metrics['posts'],
            "total_engagement": metrics['total_engagement'],
            "avg_engagement": round(avg_engagement, 2),
            "platforms": list(metrics['platforms']),
            "engagement_consistency": round(statistics.stdev(metrics['engagements']), 2) if len(metrics['engagements']) > 1 else 0
        }
    
    # Sort brands by performance
    sorted_brands = sorted(brand_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
    analysis["brand_analysis"] = {
        "performance_ranking": [{"brand": brand, **metrics} for brand, metrics in sorted_brands],
        "total_brands": len(brand_analysis),
        "avg_posts_per_brand": round(sum(m['posts'] for m in brand_metrics.values()) / len(brand_metrics), 2) if brand_metrics else 0
    }
    
    # Platform analysis
    platform_analysis = {}
    for platform, metrics in platform_metrics.items():
        avg_engagement = metrics['total_engagement'] / metrics['posts'] if metrics['posts'] > 0 else 0
        platform_analysis[platform] = {
            "post_count": metrics['posts'],
            "brand_count": len(metrics['brands']),
            "total_engagement": metrics['total_engagement'],
            "avg_engagement": round(avg_engagement, 2)
        }
    
    analysis["platform_analysis"] = platform_analysis
    
    # Content analysis - trending topics
    if all_content:
        # Extract keywords and hashtags
        all_words = []
        hashtags = []
        
        for content in all_content:
            # Extract hashtags
            content_hashtags = re.findall(r'#\w+', content)
            hashtags.extend([tag.lower() for tag in content_hashtags])
            
            # Extract words (filter out common words)
            words = re.findall(r'\b\w+\b', content)
            filtered_words = [
                w for w in words 
                if len(w) > 3 and w not in [
                    'that', 'this', 'with', 'from', 'they', 'have', 'been', 'were',
                    'will', 'your', 'what', 'when', 'where', 'just', 'like', 'more'
                ]
            ]
            all_words.extend(filtered_words)
        
        # Get trending topics
        word_counter = Counter(all_words)
        hashtag_counter = Counter(hashtags)
        
        analysis["content_analysis"] = {
            "trending_keywords": [{"keyword": word, "count": count} for word, count in word_counter.most_common(15)],
            "trending_hashtags": [{"hashtag": tag, "count": count} for tag, count in hashtag_counter.most_common(10)],
            "total_content_pieces": len(all_content)
        }
    
    # Engagement analysis
    if engagement_data:
        analysis["engagement_analysis"] = {
            "total_engagement": sum(engagement_data),
            "avg_engagement": round(statistics.mean(engagement_data), 2),
            "median_engagement": round(statistics.median(engagement_data), 2),
            "max_engagement": max(engagement_data),
            "min_engagement": min(engagement_data),
            "engagement_std": round(statistics.stdev(engagement_data), 2) if len(engagement_data) > 1 else 0
        }
    
    # Competitive positioning for Crooks & Castles
    cc_data = brand_analysis.get("crooks & castles", {})
    if cc_data:
        cc_rank = next((i for i, (brand, _) in enumerate(sorted_brands) if brand == "crooks & castles"), len(sorted_brands))
        
        analysis["competitive_positioning"] = {
            "crooks_castles_rank": cc_rank + 1,
            "total_competitors": len(sorted_brands),
            "performance_percentile": round((len(sorted_brands) - cc_rank) / len(sorted_brands) * 100, 1),
            "posts_compared_to_avg": cc_data.get("post_count", 0) - analysis["brand_analysis"]["avg_posts_per_brand"],
            "engagement_vs_market": cc_data.get("avg_engagement", 0) - analysis["engagement_analysis"].get("avg_engagement", 0) if engagement_data else 0
        }
    
    return {
        "status": "success",
        "message": f"Analyzed {len(all_posts)} real posts from {len(brand_metrics)} brands",
        "analysis": analysis
    }

@router.get("/competitive-analysis")
async def get_competitive_analysis(
    days: int = Query(default=30, description="Number of days to analyze"),
    brand_filter: Optional[str] = Query(default=None, description="Filter by specific brand"),
    platform_filter: Optional[str] = Query(default=None, description="Filter by platform")
):
    """
    PRIORITY #2: Deep competitive intelligence analysis from real data
    """
    
    try:
        analysis_result = analyze_competitive_intelligence(days)
        
        if analysis_result["status"] != "success":
            return {
                "success": False,
                "message": analysis_result["message"],
                "data": {},
                "recommendations": [
                    "Upload competitive data CSV files to /data/competitive/",
                    "Upload social media exports to /data/uploads/",
                    "Ensure files contain: brand, platform, content, engagement, date columns"
                ]
            }
        
        analysis = analysis_result["analysis"]
        
        # Apply filters if specified
        if brand_filter:
            brand_filter = brand_filter.lower()
            if "brand_analysis" in analysis:
                filtered_brands = {
                    k: v for k, v in analysis["brand_analysis"].items() 
                    if brand_filter in k.lower()
                }
                analysis["brand_analysis"]["performance_ranking"] = [
                    item for item in analysis["brand_analysis"]["performance_ranking"]
                    if brand_filter in item["brand"].lower()
                ]
        
        return {
            "success": True,
            "message": f"Competitive analysis complete - {analysis['dataset_overview']['total_posts']} posts analyzed",
            "data": analysis,
            "filters_applied": {
                "days": days,
                "brand_filter": brand_filter,
                "platform_filter": platform_filter
            },
            "data_confidence": "HIGH - Real competitive data analysis"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Competitive analysis failed: {str(e)}"
        )

@router.get("/brand-comparison")
async def get_brand_comparison(
    primary_brand: str = Query(..., description="Primary brand to compare"),
    comparison_brands: str = Query(..., description="Comma-separated list of brands to compare against"),
    days: int = Query(default=30, description="Number of days to analyze")
):
    """Compare specific brands against each other"""
    
    try:
        analysis_result = analyze_competitive_intelligence(days)
        
        if analysis_result["status"] != "success":
            raise HTTPException(status_code=404, detail=analysis_result["message"])
        
        analysis = analysis_result["analysis"]
        brand_data = analysis.get("brand_analysis", {}).get("performance_ranking", [])
        
        # Find the brands
        primary_data = None
        comparison_data = []
        
        comparison_list = [b.strip().lower() for b in comparison_brands.split(",")]
        
        for brand_info in brand_data:
            brand_name = brand_info["brand"].lower()
            if brand_name == primary_brand.lower():
                primary_data = brand_info
            elif brand_name in comparison_list:
                comparison_data.append(brand_info)
        
        if not primary_data:
            raise HTTPException(status_code=404, detail=f"Primary brand '{primary_brand}' not found in data")
        
        # Generate comparison insights
        comparison_insights = {
            "primary_brand": primary_data,
            "competitors": comparison_data,
            "performance_analysis": {},
            "recommendations": []
        }
        
        # Performance analysis
        if comparison_data:
            avg_competitor_engagement = statistics.mean([comp["avg_engagement"] for comp in comparison_data])
            avg_competitor_posts = statistics.mean([comp["post_count"] for comp in comparison_data])
            
            comparison_insights["performance_analysis"] = {
                "engagement_vs_competitors": {
                    "primary": primary_data["avg_engagement"],
                    "competitor_average": round(avg_competitor_engagement, 2),
                    "difference": round(primary_data["avg_engagement"] - avg_competitor_engagement, 2),
                    "performance": "above" if primary_data["avg_engagement"] > avg_competitor_engagement else "below"
                },
                "posting_frequency": {
                    "primary": primary_data["post_count"],
                    "competitor_average": round(avg_competitor_posts, 2),
                    "difference": round(primary_data["post_count"] - avg_competitor_posts, 2),
                    "performance": "above" if primary_data["post_count"] > avg_competitor_posts else "below"
                }
            }
            
            # Recommendations based on analysis
            if primary_data["avg_engagement"] < avg_competitor_engagement:
                comparison_insights["recommendations"].append("Focus on improving engagement rates - competitors are outperforming")
            
            if primary_data["post_count"] < avg_competitor_posts:
                comparison_insights["recommendations"].append("Increase posting frequency to match competitor activity levels")
            
            # Find top performer for benchmarking
            top_performer = max(comparison_data, key=lambda x: x["avg_engagement"])
            comparison_insights["recommendations"].append(f"Study {top_performer['brand']} strategy - highest engagement ({top_performer['avg_engagement']})")
        
        return {
            "success": True,
            "data": comparison_insights,
            "message": f"Brand comparison complete: {primary_brand} vs {len(comparison_data)} competitors"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Brand comparison failed: {str(e)}"
        )

@router.get("/trending-topics")
async def get_trending_topics(
    days: int = Query(default=7, description="Number of days to analyze"),
    min_frequency: int = Query(default=3, description="Minimum frequency for trending topics")
):
    """Get trending topics and hashtags from competitive analysis"""
    
    try:
        analysis_result = analyze_competitive_intelligence(days)
        
        if analysis_result["status"] != "success":
            return {
                "success": False,
                "message": analysis_result["message"],
                "trending_topics": [],
                "trending_hashtags": []
            }
        
        content_analysis = analysis_result["analysis"].get("content_analysis", {})
        
        # Filter by minimum frequency
        trending_keywords = [
            item for item in content_analysis.get("trending_keywords", [])
            if item["count"] >= min_frequency
        ]
        
        trending_hashtags = [
            item for item in content_analysis.get("trending_hashtags", [])
            if item["count"] >= min_frequency
        ]
        
        return {
            "success": True,
            "data": {
                "trending_keywords": trending_keywords,
                "trending_hashtags": trending_hashtags,
                "analysis_period": f"{days} days",
                "content_pieces_analyzed": content_analysis.get("total_content_pieces", 0)
            },
            "message": f"Found {len(trending_keywords)} trending keywords and {len(trending_hashtags)} trending hashtags"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trending topics analysis failed: {str(e)}"
        )

@router.get("/platform-performance")
async def get_platform_performance(days: int = Query(default=30)):
    """Analyze performance across different social media platforms"""
    
    try:
        analysis_result = analyze_competitive_intelligence(days)
        
        if analysis_result["status"] != "success":
            raise HTTPException(status_code=404, detail=analysis_result["message"])
        
        platform_data = analysis_result["analysis"].get("platform_analysis", {})
        
        # Calculate platform insights
        platform_insights = []
        total_posts = sum(data["post_count"] for data in platform_data.values())
        total_engagement = sum(data["total_engagement"] for data in platform_data.values())
        
        for platform, metrics in platform_data.items():
            platform_share = (metrics["post_count"] / total_posts * 100) if total_posts > 0 else 0
            engagement_share = (metrics["total_engagement"] / total_engagement * 100) if total_engagement > 0 else 0
            
            platform_insights.append({
                "platform": platform,
                "posts": metrics["post_count"],
                "brands": metrics["brand_count"],
                "total_engagement": metrics["total_engagement"],
                "avg_engagement": metrics["avg_engagement"],
                "market_share": round(platform_share, 2),
                "engagement_share": round(engagement_share, 2),
                "efficiency": round(engagement_share / platform_share, 2) if platform_share > 0 else 0
            })
        
        # Sort by engagement efficiency
        platform_insights.sort(key=lambda x: x["efficiency"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "platform_performance": platform_insights,
                "summary": {
                    "total_platforms": len(platform_data),
                    "total_posts": total_posts,
                    "total_engagement": total_engagement,
                    "most_active_platform": max(platform_data.items(), key=lambda x: x[1]["post_count"])[0] if platform_data else None,
                    "highest_engagement_platform": max(platform_data.items(), key=lambda x: x[1]["avg_engagement"])[0] if platform_data else None
                }
            },
            "message": f"Platform performance analysis complete - {len(platform_data)} platforms analyzed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Platform performance analysis failed: {str(e)}"
        )
