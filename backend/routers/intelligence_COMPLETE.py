from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import re
from collections import Counter

router = APIRouter()

class ReportRequest(BaseModel):
    days_back: int = 30
    include_competitors: bool = True
    include_trends: bool = True

def safe_load_uploaded_data() -> pd.DataFrame:
    """Load all uploaded data files safely"""
    try:
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent
        data_dir = backend_dir / "data"
        if not data_dir.exists():
            return pd.DataFrame()
        
        all_data = []
        for file_path in data_dir.glob("*.jsonl"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if data:  # Only add non-empty data
                                all_data.append(data)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        
        # Also check for JSON files
        for file_path in data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict):
                        all_data.append(data)
            except Exception:
                continue
        
        if not all_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        
        # Remove duplicates based on content
        if 'text' in df.columns:
            df = df.drop_duplicates(subset=['text'], keep='first')
        elif 'id' in df.columns:
            df = df.drop_duplicates(subset=['id'], keep='first')
        
        return df
        
    except Exception:
        return pd.DataFrame()

def enhanced_sentiment_analysis(text: str) -> Dict[str, float]:
    """Enhanced sentiment analysis with cultural context"""
    try:
        if not text or not isinstance(text, str):
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "compound": 0.0}
        
        text = text.lower()
        
        # Streetwear/culture specific positive words
        positive_words = [
            'fire', 'dope', 'sick', 'clean', 'fresh', 'hard', 'cold', 'heat',
            'love', 'amazing', 'perfect', 'excellent', 'awesome', 'great', 'good',
            'vibes', 'mood', 'aesthetic', 'style', 'drip', 'fit', 'look'
        ]
        
        # Negative words
        negative_words = [
            'trash', 'wack', 'mid', 'basic', 'boring', 'ugly', 'hate', 'bad',
            'terrible', 'awful', 'worst', 'sucks', 'lame', 'weak', 'corny'
        ]
        
        # Neutral/descriptive words
        neutral_words = [
            'okay', 'alright', 'decent', 'normal', 'regular', 'standard',
            'typical', 'average', 'fine', 'whatever'
        ]
        
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "compound": 0.0}
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        neutral_count = sum(1 for word in neutral_words if word in text)
        
        # Calculate scores with cultural weighting
        positive_score = min((positive_count / total_words) * 15, 1.0)
        negative_score = min((negative_count / total_words) * 15, 1.0)
        neutral_score = min((neutral_count / total_words) * 10, 1.0)
        
        # Normalize scores
        total_score = positive_score + negative_score + neutral_score
        if total_score > 1.0:
            positive_score /= total_score
            negative_score /= total_score
            neutral_score /= total_score
        else:
            # Fill remaining with neutral
            remaining = 1.0 - total_score
            neutral_score += remaining
        
        compound_score = positive_score - negative_score
        
        return {
            "positive": round(positive_score, 3),
            "negative": round(negative_score, 3),
            "neutral": round(neutral_score, 3),
            "compound": round(compound_score, 3)
        }
        
    except Exception:
        return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "compound": 0.0}

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags with streetwear context"""
    try:
        if not text or not isinstance(text, str):
            return []
        
        # Find hashtags
        hashtags = re.findall(r'#\w+', text.lower())
        
        # Remove duplicates and filter relevant ones
        unique_hashtags = list(set(hashtags))
        
        # Prioritize streetwear/fashion hashtags
        streetwear_hashtags = [
            h for h in unique_hashtags 
            if any(keyword in h for keyword in [
                'street', 'wear', 'fashion', 'style', 'fit', 'outfit',
                'hypebeast', 'supreme', 'nike', 'jordan', 'yeezy',
                'crooks', 'castles', 'urban', 'hip', 'hop'
            ])
        ]
        
        # Return streetwear hashtags first, then others
        return streetwear_hashtags + [h for h in unique_hashtags if h not in streetwear_hashtags]
        
    except Exception:
        return []

def detect_brands(text: str) -> List[str]:
    """Detect brand mentions in text"""
    try:
        if not text or not isinstance(text, str):
            return []
        
        text = text.lower()
        
        # Comprehensive brand list
        brands = [
            'crooks', 'castles', 'crooks & castles', 'crooksandcastles',
            'supreme', 'nike', 'adidas', 'jordan', 'yeezy', 'off-white',
            'balenciaga', 'gucci', 'louis vuitton', 'prada', 'versace',
            'fear of god', 'essentials', 'stone island', 'palm angels',
            'rhude', 'amiri', 'gallery dept', 'human made', 'bape',
            'kith', 'uniqlo', 'zara', 'h&m', 'forever 21'
        ]
        
        detected_brands = []
        for brand in brands:
            if brand in text:
                detected_brands.append(brand)
        
        return list(set(detected_brands))  # Remove duplicates
        
    except Exception:
        return []

def calculate_competitor_momentum(df: pd.DataFrame) -> Dict[str, str]:
    """Calculate momentum indicators for competitors"""
    try:
        if df.empty or 'brand' not in df.columns:
            return {}
        
        # Simple momentum calculation based on post frequency
        brand_counts = df['brand'].value_counts()
        momentum = {}
        
        for brand, count in brand_counts.items():
            if count > 50:
                momentum[brand] = "rising"  # ↗
            elif count > 20:
                momentum[brand] = "stable"  # →
            else:
                momentum[brand] = "declining"  # ↘
        
        return momentum
        
    except Exception:
        return {}

def generate_strategic_insights(df: pd.DataFrame, sentiment_data: List[Dict], hashtag_data: List[Dict]) -> List[str]:
    """Generate strategic insights from data analysis"""
    try:
        insights = []
        
        if df.empty:
            return [
                "Upload competitor data to begin strategic analysis",
                "Connect social media scrapers for real-time insights",
                "Add more data sources for comprehensive intelligence"
            ]
        
        total_posts = len(df)
        brands_tracked = df['brand'].nunique() if 'brand' in df.columns else 0
        
        # Basic insights
        insights.append(f"Analyzing {total_posts} posts from {brands_tracked} competitors")
        
        # Sentiment insights
        if sentiment_data:
            avg_positive = sum(s['positive'] for s in sentiment_data) / len(sentiment_data)
            if avg_positive > 0.6:
                insights.append("High positive sentiment detected - market is receptive to current trends")
            elif avg_positive < 0.3:
                insights.append("Low positive sentiment - opportunity for differentiation")
            else:
                insights.append(f"Balanced sentiment landscape - {avg_positive*100:.1f}% positive engagement")
        
        # Hashtag insights
        if hashtag_data:
            top_hashtag = hashtag_data[0]
            insights.append(f"Trending: {top_hashtag['hashtag']} with {top_hashtag['count']} uses")
            
            # Look for opportunities
            streetwear_hashtags = [h for h in hashtag_data if 'street' in h['hashtag'] or 'wear' in h['hashtag']]
            if streetwear_hashtags:
                insights.append("Strong streetwear conversation - align content with #streetwear trends")
        
        # Competitor insights
        if 'brand' in df.columns:
            top_brands = df['brand'].value_counts().head(3)
            insights.append(f"Most active competitors: {', '.join(top_brands.index.tolist())}")
            
            # Crooks & Castles specific insights
            if 'crooks' in df['brand'].str.lower().values or 'castles' in df['brand'].str.lower().values:
                insights.append("Crooks & Castles mentioned in competitor data - monitor brand perception")
        
        # Content gap analysis
        if hashtag_data:
            culture_hashtags = [h for h in hashtag_data if any(term in h['hashtag'] for term in ['culture', 'heritage', 'community'])]
            if not culture_hashtags:
                insights.append("Opportunity: Limited cultural content - leverage heritage storytelling")
        
        return insights[:6]  # Return top 6 insights
        
    except Exception:
        return [
            "Error generating insights - check data quality",
            "Ensure uploaded files contain proper brand and text data",
            "Contact support if issues persist"
        ]

@router.post("/report")
async def generate_intelligence_report(request: ReportRequest):
    """Generate comprehensive intelligence report"""
    try:
        # Load data
        df = safe_load_uploaded_data()
        
        # Debug logging
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame empty: {df.empty}")
        print(f"DEBUG: DataFrame columns: {list(df.columns) if not df.empty else 'No columns'}")
        
        if df.empty:
            return JSONResponse({
                "success": True,
                "data_status": "no_data",
                "message": "No data uploaded yet. Upload competitor data to see insights.",
                "total_posts": 0,
                "brands_tracked": 0,
                "sentiment_analysis": {
                    "overall_positive": 0,
                    "overall_negative": 0,
                    "overall_neutral": 0,
                    "compound_score": 0
                },
                "competitor_rankings": [],
                "trending_hashtags": [],
                "strategic_insights": [
                    "Upload competitor data to begin analysis",
                    "Connect social media scrapers for real-time insights",
                    "Add more data sources for comprehensive intelligence"
                ],
                "momentum_indicators": {},
                "content_opportunities": [],
                "last_updated": datetime.now().isoformat()
            })
        
        # Basic metrics
        total_posts = len(df)
        brands_tracked = df['brand'].nunique() if 'brand' in df.columns else 0
        
        # Enhanced sentiment analysis
        sentiment_scores = []
        if 'text' in df.columns:
            for text in df['text'].fillna('').astype(str):
                sentiment = enhanced_sentiment_analysis(text)
                sentiment_scores.append(sentiment)
        
        # Calculate average sentiment
        if sentiment_scores:
            avg_positive = sum(s['positive'] for s in sentiment_scores) / len(sentiment_scores)
            avg_negative = sum(s['negative'] for s in sentiment_scores) / len(sentiment_scores)
            avg_neutral = sum(s['neutral'] for s in sentiment_scores) / len(sentiment_scores)
            avg_compound = sum(s['compound'] for s in sentiment_scores) / len(sentiment_scores)
        else:
            avg_positive = avg_negative = avg_neutral = 0.33
            avg_compound = 0.0
        
        # Competitor analysis with momentum
        competitor_rankings = []
        momentum_indicators = {}
        
        if 'brand' in df.columns:
            brand_counts = df['brand'].value_counts()
            momentum_indicators = calculate_competitor_momentum(df)
            
            for i, (brand, count) in enumerate(brand_counts.head(15).items()):
                momentum = momentum_indicators.get(brand, "stable")
                competitor_rankings.append({
                    "rank": i + 1,
                    "brand": brand,
                    "posts": int(count),
                    "percentage": round((count / total_posts) * 100, 1),
                    "momentum": momentum,
                    "trend_indicator": "↗" if momentum == "rising" else "→" if momentum == "stable" else "↘"
                })
        
        # Enhanced hashtag analysis
        all_hashtags = []
        if 'text' in df.columns:
            for text in df['text'].fillna('').astype(str):
                hashtags = extract_hashtags(text)
                all_hashtags.extend(hashtags)
        
        if 'hashtags' in df.columns:
            for hashtag_text in df['hashtags'].fillna('').astype(str):
                hashtags = extract_hashtags(hashtag_text)
                all_hashtags.extend(hashtags)
        
        hashtag_counts = Counter(all_hashtags)
        trending_hashtags = [
            {
                "hashtag": tag,
                "count": count,
                "trend": "rising" if count > 10 else "stable",
                "category": "streetwear" if any(term in tag for term in ['street', 'wear', 'fashion', 'style']) else "general"
            }
            for tag, count in hashtag_counts.most_common(15)
        ]
        
        # Generate strategic insights
        strategic_insights = generate_strategic_insights(df, sentiment_scores, trending_hashtags)
        
        # Content opportunities
        content_opportunities = []
        if trending_hashtags:
            # Find underutilized hashtags
            mid_tier_hashtags = [h for h in trending_hashtags if 5 <= h['count'] <= 20]
            if mid_tier_hashtags:
                content_opportunities.append({
                    "type": "hashtag_opportunity",
                    "description": f"Leverage emerging hashtag: {mid_tier_hashtags[0]['hashtag']}",
                    "impact": "medium",
                    "effort": "low"
                })
        
        # Brand mention opportunities
        if 'text' in df.columns:
            all_text = ' '.join(df['text'].fillna('').astype(str))
            crooks_mentions = all_text.lower().count('crooks')
            if crooks_mentions < 5:
                content_opportunities.append({
                    "type": "brand_visibility",
                    "description": "Low Crooks & Castles brand mentions - increase brand presence",
                    "impact": "high",
                    "effort": "medium"
                })
        
        return JSONResponse({
            "success": True,
            "data_status": "real_data",
            "total_posts": total_posts,
            "brands_tracked": brands_tracked,
            "sentiment_analysis": {
                "overall_positive": round(avg_positive * 100, 1),
                "overall_negative": round(avg_negative * 100, 1),
                "overall_neutral": round(avg_neutral * 100, 1),
                "compound_score": round(avg_compound, 3)
            },
            "competitor_rankings": competitor_rankings,
            "trending_hashtags": trending_hashtags,
            "strategic_insights": strategic_insights,
            "momentum_indicators": momentum_indicators,
            "content_opportunities": content_opportunities,
            "analysis_period": f"last_{request.days_back}_days",
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Intelligence report generation failed: {str(e)}",
            "data_status": "error",
            "total_posts": 0,
            "brands_tracked": 0,
            "sentiment_analysis": {
                "overall_positive": 0,
                "overall_negative": 0,
                "overall_neutral": 0,
                "compound_score": 0
            },
            "competitor_rankings": [],
            "trending_hashtags": [],
            "strategic_insights": [
                "Unable to generate intelligence report",
                "Check server logs for detailed error information",
                "Ensure data files are properly formatted"
            ],
            "momentum_indicators": {},
            "content_opportunities": []
        })

@router.get("/competitors")
async def get_competitor_analysis():
    """Get detailed competitor analysis"""
    try:
        df = safe_load_uploaded_data()
        
        if df.empty:
            return JSONResponse({
                "success": True,
                "competitors": [],
                "message": "No competitor data available. Upload data to see analysis."
            })
        
        competitors = []
        if 'brand' in df.columns:
            brand_groups = df.groupby('brand')
            
            for brand, group in brand_groups:
                post_count = len(group)
                
                # Enhanced sentiment analysis for each brand
                sentiment_scores = []
                if 'text' in group.columns:
                    for text in group['text'].fillna('').astype(str):
                        sentiment = enhanced_sentiment_analysis(text)
                        sentiment_scores.append(sentiment)
                
                if sentiment_scores:
                    avg_sentiment = sum(s['compound'] for s in sentiment_scores) / len(sentiment_scores)
                    avg_positive = sum(s['positive'] for s in sentiment_scores) / len(sentiment_scores)
                else:
                    avg_sentiment = 0
                    avg_positive = 0.33
                
                # Hashtag analysis for this brand
                brand_hashtags = []
                if 'text' in group.columns:
                    for text in group['text'].fillna('').astype(str):
                        hashtags = extract_hashtags(text)
                        brand_hashtags.extend(hashtags)
                
                top_hashtags = dict(Counter(brand_hashtags).most_common(5))
                
                # Activity classification
                if post_count > 50:
                    activity_level = "high"
                elif post_count > 20:
                    activity_level = "medium"
                else:
                    activity_level = "low"
                
                competitors.append({
                    "brand": brand,
                    "posts": post_count,
                    "avg_sentiment": round(avg_sentiment, 3),
                    "positive_sentiment": round(avg_positive * 100, 1),
                    "top_hashtags": top_hashtags,
                    "activity_level": activity_level,
                    "market_share": round((post_count / len(df)) * 100, 1)
                })
        
        # Sort by post count
        competitors.sort(key=lambda x: x['posts'], reverse=True)
        
        return JSONResponse({
            "success": True,
            "competitors": competitors,
            "total_competitors": len(competitors),
            "analysis_date": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Competitor analysis failed: {str(e)}",
            "competitors": [],
            "total_competitors": 0
        })

@router.get("/trends")
async def get_trend_analysis():
    """Get comprehensive trend analysis"""
    try:
        df = safe_load_uploaded_data()
        
        if df.empty:
            return JSONResponse({
                "success": True,
                "trends": [],
                "message": "No data available for trend analysis. Upload competitor data first."
            })
        
        # Extract all hashtags
        all_hashtags = []
        if 'text' in df.columns:
            for text in df['text'].fillna('').astype(str):
                hashtags = extract_hashtags(text)
                all_hashtags.extend(hashtags)
        
        # Analyze hashtag trends
        hashtag_counts = Counter(all_hashtags)
        
        trends = []
        for hashtag, count in hashtag_counts.most_common(25):
            # Categorize hashtags
            if any(term in hashtag for term in ['street', 'wear', 'fashion', 'style', 'fit', 'outfit']):
                category = "streetwear"
            elif any(term in hashtag for term in ['culture', 'heritage', 'community', 'hip', 'hop']):
                category = "culture"
            elif any(term in hashtag for term in ['brand', 'nike', 'supreme', 'jordan']):
                category = "brands"
            else:
                category = "general"
            
            # Determine trend direction based on usage
            if count > 20:
                trend_direction = "rising"
            elif count > 10:
                trend_direction = "stable"
            else:
                trend_direction = "emerging"
            
            trends.append({
                "hashtag": hashtag,
                "count": count,
                "percentage": round((count / len(all_hashtags)) * 100, 2) if all_hashtags else 0,
                "trend_direction": trend_direction,
                "category": category,
                "momentum": "↗" if trend_direction == "rising" else "→" if trend_direction == "stable" else "↗"
            })
        
        return JSONResponse({
            "success": True,
            "trends": trends,
            "total_hashtags": len(set(all_hashtags)),
            "categories": {
                "streetwear": len([t for t in trends if t['category'] == 'streetwear']),
                "culture": len([t for t in trends if t['category'] == 'culture']),
                "brands": len([t for t in trends if t['category'] == 'brands']),
                "general": len([t for t in trends if t['category'] == 'general'])
            },
            "analysis_period": "last_30_days",
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Trend analysis failed: {str(e)}",
            "trends": [],
            "total_hashtags": 0
        })

@router.get("/health")
async def intelligence_health_check():
    """Health check for intelligence module"""
    try:
        df = safe_load_uploaded_data()
        
        return JSONResponse({
            "status": "healthy",
            "data_available": not df.empty,
            "total_records": len(df),
            "unique_brands": df['brand'].nunique() if 'brand' in df.columns else 0,
            "data_sources": len(list(Path("data/uploads").glob("*.jsonl"))) + len(list(Path("data/uploads").glob("*.json"))),
            "last_check": datetime.now().isoformat(),
            "message": "Intelligence module operational with enhanced analytics"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "data_available": False,
            "total_records": 0,
            "error": str(e),
            "message": "Intelligence module health check failed"
        })
