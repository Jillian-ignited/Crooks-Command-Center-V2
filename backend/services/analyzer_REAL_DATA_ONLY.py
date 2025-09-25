from typing import List, Dict, Any
import pandas as pd
import numpy as np
import re
import json
import os
from collections import Counter
from pathlib import Path
from services.scraper import load_all_uploaded_frames

# Enhanced sentiment analysis using VADER (free library)
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

def keyword_extract(texts: List[str], top_k=10) -> List[str]:
    """Extract top keywords from texts"""
    bag = []
    for t in texts:
        if not isinstance(t, str):
            continue
        t = t.lower()
        t = re.sub(r"[^a-z0-9\s]", " ", t)
        words = [w for w in t.split() if len(w) > 3 and w not in ["the","and","for","with","this","that","from"]]
        bag.extend(words)
    return [w for w, _ in Counter(bag).most_common(top_k)]

def enhanced_sentiment_analysis(texts: List[str]) -> Dict[str, Any]:
    """Enhanced sentiment analysis with multiple dimensions"""
    if not texts:
        return {"positive": 0, "negative": 0, "neutral": 0, "compound": 0, "overall_sentiment": "no_data"}
    
    if VADER_AVAILABLE:
        analyzer = SentimentIntensityAnalyzer()
        scores = []
        for text in texts:
            if isinstance(text, str):
                score = analyzer.polarity_scores(text)
                scores.append(score)
        
        if scores:
            avg_positive = np.mean([s['pos'] for s in scores])
            avg_negative = np.mean([s['neg'] for s in scores])
            avg_neutral = np.mean([s['neu'] for s in scores])
            avg_compound = np.mean([s['compound'] for s in scores])
            
            return {
                "positive": round(avg_positive * 100, 1),
                "negative": round(avg_negative * 100, 1),
                "neutral": round(avg_neutral * 100, 1),
                "compound": round(avg_compound, 3),
                "overall_sentiment": "positive" if avg_compound > 0.05 else "negative" if avg_compound < -0.05 else "neutral"
            }
    
    # Fallback basic sentiment analysis
    positive_words = ["good", "great", "awesome", "love", "amazing", "excellent", "perfect", "best", "fire", "dope"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "trash", "weak"]
    
    positive_count = 0
    negative_count = 0
    total_count = 0
    
    for text in texts:
        if isinstance(text, str):
            text_lower = text.lower()
            total_count += 1
            if any(word in text_lower for word in positive_words):
                positive_count += 1
            elif any(word in text_lower for word in negative_words):
                negative_count += 1
    
    if total_count > 0:
        positive_pct = (positive_count / total_count) * 100
        negative_pct = (negative_count / total_count) * 100
        neutral_pct = 100 - positive_pct - negative_pct
    else:
        positive_pct = negative_pct = neutral_pct = 0
    
    return {
        "positive": round(positive_pct, 1),
        "negative": round(negative_pct, 1),
        "neutral": round(neutral_pct, 1),
        "compound": 0,
        "overall_sentiment": "positive" if positive_pct > negative_pct else "negative" if negative_pct > positive_pct else "neutral"
    }

def calculate_momentum(brand_data: pd.DataFrame) -> str:
    """Calculate brand momentum based on engagement trends"""
    if len(brand_data) < 2:
        return "→"
    
    # Sort by date if available
    if 'date' in brand_data.columns:
        brand_data = brand_data.sort_values('date')
    
    # Calculate engagement trend
    if 'likes' in brand_data.columns:
        recent_engagement = brand_data['likes'].tail(len(brand_data)//2).mean()
        older_engagement = brand_data['likes'].head(len(brand_data)//2).mean()
        
        if recent_engagement > older_engagement * 1.1:
            return "↗"  # Rising
        elif recent_engagement < older_engagement * 0.9:
            return "↘"  # Declining
        else:
            return "→"  # Stable
    
    return "→"

def detect_content_gaps(all_data: pd.DataFrame, brand: str) -> List[str]:
    """Detect content opportunities for the brand"""
    gaps = []
    
    if all_data.empty:
        return ["No data available for gap analysis"]
    
    # Analyze hashtag usage
    if 'hashtags' in all_data.columns:
        all_hashtags = []
        brand_hashtags = []
        
        for _, row in all_data.iterrows():
            if isinstance(row.get('hashtags'), str):
                hashtags = re.findall(r'#\w+', row['hashtags'].lower())
                all_hashtags.extend(hashtags)
                
                if row.get('brand', '').lower() == brand.lower():
                    brand_hashtags.extend(hashtags)
        
        # Find popular hashtags not used by the brand
        all_hashtag_counts = Counter(all_hashtags)
        brand_hashtag_set = set(brand_hashtags)
        
        for hashtag, count in all_hashtag_counts.most_common(20):
            if hashtag not in brand_hashtag_set and count > 5:
                gaps.append(f"Underutilized hashtag: {hashtag}")
    
    # Content type analysis
    if 'content_type' in all_data.columns:
        brand_content = all_data[all_data['brand'].str.lower() == brand.lower()]
        competitor_content = all_data[all_data['brand'].str.lower() != brand.lower()]
        
        brand_types = set(brand_content['content_type'].dropna())
        competitor_types = set(competitor_content['content_type'].dropna())
        
        missing_types = competitor_types - brand_types
        for content_type in missing_types:
            gaps.append(f"Missing content type: {content_type}")
    
    if not gaps:
        gaps = ["No significant content gaps identified"]
    
    return gaps[:5]  # Return top 5 gaps

def weekly_summary() -> Dict[str, Any]:
    """Generate weekly summary ONLY from real uploaded data"""
    
    # Load all uploaded data
    df = load_all_uploaded_frames()
    
    if df.empty:
        # Return clear "no data" indicators instead of mock data
        return {
            "total_posts": 0,
            "total_brands": 0,
            "positive_sentiment": 0,
            "cc_rank": "N/A",
            "engagement_rate": 0,
            "top_hashtags": [],
            "weekly_highlights": [
                "No data uploaded yet",
                "Upload scraper data to see real insights",
                "Waiting for competitive intelligence data"
            ],
            "key_metrics": {
                "reach_estimate": 0,
                "engagement_growth": "N/A",
                "sentiment_trend": "no_data",
                "competitor_position": "no_data"
            },
            "data_status": "no_data"
        }
    
    # Process ONLY real data
    total_posts = len(df)
    unique_brands = df['brand'].nunique() if 'brand' in df.columns else 0
    
    # Enhanced sentiment analysis from real text
    text_columns = ['caption', 'description', 'text', 'content']
    all_texts = []
    for col in text_columns:
        if col in df.columns:
            all_texts.extend(df[col].dropna().astype(str).tolist())
    
    sentiment_analysis = enhanced_sentiment_analysis(all_texts)
    
    # Extract trending hashtags from real data
    trending_hashtags = []
    if 'hashtags' in df.columns:
        all_hashtags = []
        for hashtag_str in df['hashtags'].dropna():
            if isinstance(hashtag_str, str):
                hashtags = re.findall(r'#\w+', hashtag_str.lower())
                all_hashtags.extend(hashtags)
        trending_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(5)]
    
    # Calculate Crooks & Castles rank from real data
    cc_rank = "Not Found"
    if 'brand' in df.columns:
        brand_engagement = {}
        for brand in df['brand'].unique():
            brand_df = df[df['brand'] == brand]
            if 'likes' in brand_df.columns:
                avg_engagement = brand_df['likes'].mean()
                brand_engagement[brand] = avg_engagement
        
        # Sort brands by engagement
        if brand_engagement:
            sorted_brands = sorted(brand_engagement.items(), key=lambda x: x[1], reverse=True)
            for i, (brand, _) in enumerate(sorted_brands):
                if 'crooks' in brand.lower() or 'castles' in brand.lower():
                    cc_rank = i + 1
                    break
    
    # Generate real insights
    weekly_highlights = [
        f"Analyzed {total_posts} real posts from uploaded data",
        f"Tracking {unique_brands} brands from your scraped data",
        f"Market sentiment: {sentiment_analysis.get('overall_sentiment', 'neutral')} ({sentiment_analysis.get('positive', 0)}% positive)"
    ]
    
    if trending_hashtags:
        weekly_highlights.append(f"Top trending hashtag: {trending_hashtags[0]}")
    
    return {
        "total_posts": total_posts,
        "total_brands": unique_brands,
        "positive_sentiment": sentiment_analysis.get('positive', 0),
        "cc_rank": cc_rank,
        "engagement_rate": 0,  # Calculate from real data if available
        "top_hashtags": trending_hashtags,
        "weekly_highlights": weekly_highlights,
        "key_metrics": {
            "reach_estimate": total_posts * 100 if total_posts > 0 else 0,  # Conservative estimate
            "engagement_growth": "N/A",  # Need historical data
            "sentiment_trend": sentiment_analysis.get('overall_sentiment', 'no_data'),
            "competitor_position": f"#{cc_rank}" if isinstance(cc_rank, int) else cc_rank
        },
        "data_status": "real_data"
    }

def brand_intelligence(brands: List[str], lookback_days: int = 7) -> Dict[str, Any]:
    """Enhanced brand intelligence using ONLY real uploaded data"""
    
    # Load all uploaded data
    df = load_all_uploaded_frames()
    
    if df.empty:
        # Return clear "no data" indicators instead of mock data
        return {
            "timeframe_days": lookback_days,
            "metrics": {
                "total_posts": 0,
                "total_brands": 0,
                "positive_sentiment": 0,
                "engagement_rate": 0,
                "reach_estimate": 0
            },
            "highlights": [
                "No competitive data uploaded yet",
                "Upload scraper data to see real brand intelligence",
                "Waiting for social media data to analyze"
            ],
            "prioritized_actions": [
                "Upload competitive intelligence data",
                "Add social media scraper results",
                "Import brand performance data"
            ],
            "competitor_analysis": [],
            "trending_hashtags": [],
            "content_gaps": ["No data available for gap analysis"],
            "data_status": "no_data"
        }
    
    # Process ONLY real data
    total_posts = len(df)
    unique_brands = df['brand'].nunique() if 'brand' in df.columns else 0
    
    # Enhanced sentiment analysis from real text
    text_columns = ['caption', 'description', 'text', 'content']
    all_texts = []
    for col in text_columns:
        if col in df.columns:
            all_texts.extend(df[col].dropna().astype(str).tolist())
    
    sentiment_analysis = enhanced_sentiment_analysis(all_texts)
    
    # Real competitor analysis with momentum
    competitor_data = []
    if 'brand' in df.columns and not df['brand'].empty:
        for brand in df['brand'].unique():
            if pd.isna(brand):
                continue
                
            brand_df = df[df['brand'] == brand]
            brand_texts = []
            for col in text_columns:
                if col in brand_df.columns:
                    brand_texts.extend(brand_df[col].dropna().astype(str).tolist())
            
            brand_sentiment = enhanced_sentiment_analysis(brand_texts)
            momentum = calculate_momentum(brand_df)
            
            # Calculate engagement score from real data
            engagement_score = 0
            if 'likes' in brand_df.columns:
                engagement_score = brand_df['likes'].mean()
            elif 'engagement' in brand_df.columns:
                engagement_score = brand_df['engagement'].mean()
            
            competitor_data.append({
                "brand": brand,
                "momentum": momentum,
                "sentiment": brand_sentiment.get('positive', 0),
                "posts": len(brand_df),
                "engagement_score": engagement_score
            })
        
        # Rank by engagement score
        competitor_data.sort(key=lambda x: x['engagement_score'], reverse=True)
        for i, comp in enumerate(competitor_data):
            comp['rank'] = i + 1
    
    # Extract trending hashtags from real data
    trending_hashtags = []
    if 'hashtags' in df.columns:
        all_hashtags = []
        for hashtag_str in df['hashtags'].dropna():
            if isinstance(hashtag_str, str):
                hashtags = re.findall(r'#\w+', hashtag_str.lower())
                all_hashtags.extend(hashtags)
        trending_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(10)]
    
    # Real content gap analysis
    content_gaps = detect_content_gaps(df, "Crooks & Castles")
    
    # Generate real insights
    highlights = [
        f"Analyzed {total_posts} real posts from uploaded data",
        f"Tracking {unique_brands} brands from your competitive intelligence",
        f"Market sentiment from real data: {sentiment_analysis.get('overall_sentiment', 'neutral')} ({sentiment_analysis.get('positive', 0)}% positive)"
    ]
    
    if trending_hashtags:
        highlights.append(f"Top performing hashtag from data: {trending_hashtags[0]}")
    
    prioritized_actions = []
    if content_gaps and content_gaps[0] != "No data available for gap analysis":
        prioritized_actions.extend(content_gaps[:3])
    
    if trending_hashtags:
        prioritized_actions.append(f"Leverage trending hashtag: {trending_hashtags[0]}")
    
    if not prioritized_actions:
        prioritized_actions = ["Upload more competitive data for actionable insights"]
    
    return {
        "timeframe_days": lookback_days,
        "metrics": {
            "total_posts": total_posts,
            "total_brands": unique_brands,
            "positive_sentiment": sentiment_analysis.get('positive', 0),
            "engagement_rate": 0,  # Calculate from real data if available
            "reach_estimate": total_posts * 100 if total_posts > 0 else 0
        },
        "highlights": highlights,
        "prioritized_actions": prioritized_actions,
        "competitor_analysis": competitor_data[:10],  # Top 10 competitors from real data
        "trending_hashtags": trending_hashtags,
        "content_gaps": content_gaps,
        "sentiment_breakdown": sentiment_analysis,
        "data_status": "real_data"
    }

def get_asset_library() -> Dict[str, Any]:
    """Get interactive asset library with real uploaded files"""
    upload_dir = Path("data/uploads")
    assets = []
    
    if upload_dir.exists():
        for file_path in upload_dir.glob("*"):
            if file_path.is_file():
                # Get file info
                file_size = file_path.stat().st_size
                file_ext = file_path.suffix.lower()
                
                # Determine file type
                if file_ext in ['.json', '.jsonl']:
                    file_type = "Data"
                    icon = "📊"
                elif file_ext in ['.csv']:
                    file_type = "Spreadsheet"
                    icon = "📈"
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    file_type = "Image"
                    icon = "🖼️"
                elif file_ext in ['.mp4', '.mov', '.avi']:
                    file_type = "Video"
                    icon = "🎥"
                else:
                    file_type = "Document"
                    icon = "📄"
                
                # Try to get record count for data files
                record_count = 0
                if file_ext == '.jsonl':
                    try:
                        with open(file_path, 'r') as f:
                            record_count = sum(1 for line in f if line.strip())
                    except:
                        record_count = 0
                elif file_ext == '.json':
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                record_count = len(data)
                            elif isinstance(data, dict) and 'items' in data:
                                record_count = len(data['items'])
                    except:
                        record_count = 0
                
                assets.append({
                    "name": file_path.name,
                    "type": file_type,
                    "icon": icon,
                    "size": f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB",
                    "records": record_count if record_count > 0 else None,
                    "path": str(file_path),
                    "downloadable": True
                })
    
    return {
        "assets": assets,
        "total_files": len(assets),
        "total_size": sum(Path(asset["path"]).stat().st_size for asset in assets if Path(asset["path"]).exists()),
        "data_status": "real_data" if assets else "no_data"
    }

def get_content_calendar(timeframe: str = "30") -> Dict[str, Any]:
    """Generate strategic content calendar"""
    
    # Cultural moments and strategic dates
    cultural_moments = {
        "September": ["Hispanic Heritage Month (Sep 15 - Oct 15)", "Back to School", "Fashion Week"],
        "October": ["Hispanic Heritage Month (continues)", "Halloween", "BFCM Prep"],
        "November": ["Black Friday/Cyber Monday", "Thanksgiving", "Holiday Season Kickoff"],
        "December": ["Holiday Season", "New Year Prep", "Year-End Reflection"],
        "January": ["New Year New Me", "MLK Day", "Winter Fashion"],
        "February": ["Black History Month", "Valentine's Day", "All-Star Weekend"]
    }
    
    # Content themes based on Crooks & Castles brand
    content_themes = [
        "Street Culture Celebration",
        "Hip-Hop Heritage",
        "Community Spotlight",
        "Behind the Scenes",
        "Cultural Collaborations",
        "Lifestyle Content",
        "Product Showcases",
        "Artist Partnerships"
    ]
    
    # Optimal posting times (based on streetwear audience)
    optimal_times = {
        "Instagram": ["12:00 PM", "3:00 PM", "7:00 PM"],
        "TikTok": ["6:00 AM", "10:00 AM", "7:00 PM", "9:00 PM"],
        "Twitter": ["9:00 AM", "12:00 PM", "3:00 PM"]
    }
    
    return {
        "timeframe": f"{timeframe} days",
        "cultural_moments": cultural_moments,
        "content_themes": content_themes,
        "optimal_times": optimal_times,
        "strategic_campaigns": [
            {
                "name": "Heritage Celebration",
                "duration": "30 days",
                "platforms": ["Instagram", "TikTok"],
                "content_types": ["Stories", "Reels", "Posts"]
            },
            {
                "name": "Community Spotlight",
                "duration": "Ongoing",
                "platforms": ["All"],
                "content_types": ["User Generated Content", "Interviews"]
            }
        ],
        "recommendations": [
            "Increase posting frequency during cultural moments",
            "Focus on video content for higher engagement",
            "Collaborate with community artists and influencers",
            "Maintain authentic street culture voice"
        ],
        "data_status": "strategic_planning"
    }
