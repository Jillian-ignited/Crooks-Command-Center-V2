# backend/ai_processor.py
import os
import json
from openai import OpenAI

# Simple client initialization without extra parameters
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_social_data(data: list, source_type: str = "social_media") -> dict:
    """
    Send data to OpenAI for analysis and recommendations
    """
    # Limit to first 100 rows to stay within token limits
    sample_data = data[:100] if len(data) > 100 else data
    
    prompt = f"""Analyze this {source_type} data and provide:

1. KEY INSIGHTS (3-5 bullet points)
2. TRENDING TOPICS (top 5 with engagement metrics)
3. CONTENT RECOMMENDATIONS (5 specific actionable ideas)
4. COMPETITOR ANALYSIS (key findings)
5. HASHTAG STRATEGY (top performing hashtags)
6. POSTING RECOMMENDATIONS (best times, formats, themes)

Data sample:
{json.dumps(sample_data[:10], indent=2)}

Total records analyzed: {len(sample_data)}

Format response as JSON with these keys: insights, trending_topics, recommendations, competitor_analysis, hashtag_strategy, posting_recommendations"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a streetwear marketing analyst. Provide specific, actionable insights for Crooks & Castles brand."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to structured text
        try:
            return json.loads(result)
        except:
            return {
                "insights": [result],
                "raw_analysis": result
            }
    except Exception as e:
        return {
            "error": str(e),
            "insights": ["Failed to process data with AI"]
        }
