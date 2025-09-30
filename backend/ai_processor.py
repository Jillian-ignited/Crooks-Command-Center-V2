# backend/ai_processor.py
import os
import json

def analyze_social_data(data: list, source_type: str = "social_media") -> dict:
    """
    Send data to OpenAI for analysis and recommendations
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        sample_data = data[:100] if len(data) > 100 else data
        
        prompt = f"""Analyze this {source_type} data and provide:

1. KEY INSIGHTS (3-5 bullet points)
2. TRENDING TOPICS (top 5)
3. CONTENT RECOMMENDATIONS (5 actionable ideas)
4. HASHTAG STRATEGY (top hashtags)

Data sample (first 10 records):
{json.dumps(sample_data[:10], indent=2)}

Total records: {len(sample_data)}

Return as JSON with keys: insights, trending_topics, recommendations, hashtag_strategy"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a streetwear marketing analyst for Crooks & Castles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        
        try:
            return json.loads(result)
        except:
            return {"insights": [result], "raw_analysis": result}
            
    except Exception as e:
        print(f"[ai_processor] Error: {e}")
        return {
            "error": str(e),
            "insights": ["AI processing unavailable"],
            "trending_topics": [],
            "recommendations": ["Upload data to generate insights"],
            "hashtag_strategy": "N/A"
        }
