# backend/ai_processor.py
import os
import json

def analyze_social_data(data: list, source_type: str = "social_media") -> dict:
    """
    Send data to OpenAI for analysis and recommendations
    """
    
    # Check if API key exists before attempting to import/use OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ai_processor] No OPENAI_API_KEY found")
        return {
            "insights": ["OpenAI API key not configured"],
            "trending_topics": [],
            "recommendations": ["Add OPENAI_API_KEY to environment variables"],
            "hashtag_strategy": "Configure AI to enable analysis"
        }
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        sample_data = data[:100] if len(data) > 100 else data
        
        prompt = f"""Analyze this {source_type} data and provide insights as JSON with these keys:
- insights: array of 3-5 key findings
- trending_topics: array of top 5 topics
- recommendations: array of 5 actionable content ideas
- hashtag_strategy: string with hashtag recommendations

Data: {json.dumps(sample_data[:10], indent=2)}
Total records: {len(sample_data)}"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a streetwear marketing analyst for Crooks & Castles. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result.startswith("```"):
            result = result.split("```json")[1] if "```json" in result else result.split("```")[1]
            result = result.rsplit("```")[0].strip()
        
        return json.loads(result)
            
    except Exception as e:
        print(f"[ai_processor] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "insights": [f"AI analysis failed: {str(e)}"],
            "trending_topics": [],
            "recommendations": ["Fix AI configuration to enable insights"],
            "hashtag_strategy": "N/A"
        }
