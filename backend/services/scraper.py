"""
Mock scraper service for Crooks & Castles Command Center V2
This provides placeholder functionality for social media data loading.
"""

import pandas as pd
from typing import Dict, Any, List
import json
from pathlib import Path

def load_all_uploaded_frames() -> pd.DataFrame:
    """
    Load all uploaded social media data frames.
    Returns a DataFrame with competitive intelligence data.
    """
    try:
        # Check for processed data files
        data_dir = Path("data")
        if not data_dir.exists():
            return pd.DataFrame()
        
        all_data = []
        
        # Look for JSON files in the data directory
        for json_file in data_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict):
                        all_data.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
        
        if not all_data:
            # Return mock data structure for testing
            return pd.DataFrame({
                'brand': ['crooks_castles', 'competitor_1', 'competitor_2'],
                'text': ['Sample post 1', 'Sample post 2', 'Sample post 3'],
                'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
                'engagement': [100, 150, 200],
                'hashtags': ['#streetwear', '#fashion', '#style']
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Ensure required columns exist
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df
        
    except Exception as e:
        print(f"Error in load_all_uploaded_frames: {e}")
        return pd.DataFrame()

def get_competitor_data() -> Dict[str, Any]:
    """
    Get competitor analysis data.
    """
    df = load_all_uploaded_frames()
    
    if df.empty:
        return {
            "total_posts": 0,
            "brands_tracked": 0,
            "date_range": "No data",
            "top_brands": []
        }
    
    return {
        "total_posts": len(df),
        "brands_tracked": df['brand'].nunique() if 'brand' in df.columns else 0,
        "date_range": f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else "Unknown",
        "top_brands": df['brand'].value_counts().head(5).to_dict() if 'brand' in df.columns else {}
    }

def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text content.
    """
    if not text or not isinstance(text, str):
        return []
    
    import re
    hashtags = re.findall(r'#\w+', text)
    return [tag.lower() for tag in hashtags]

def analyze_engagement_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze engagement patterns in the data.
    """
    if df.empty:
        return {"error": "No data available for analysis"}
    
    analysis = {
        "total_posts": len(df),
        "average_engagement": df['engagement'].mean() if 'engagement' in df.columns else 0,
        "top_performing_posts": [],
        "engagement_trends": {}
    }
    
    if 'engagement' in df.columns:
        top_posts = df.nlargest(5, 'engagement')
        analysis["top_performing_posts"] = top_posts.to_dict('records')
    
    return analysis
