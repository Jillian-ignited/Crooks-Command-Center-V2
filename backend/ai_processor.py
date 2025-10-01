# backend/ai_processor.py
import os
import json

def analyze_social_data(data: list, source_type: str = "social_media") -> dict:
    """
    Send data to OpenAI for analysis and recommendations
    """
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
        
        # CRITICAL: Only pass api_key - no other parameters
        client = OpenAI(api_key=api_key)
        
        sample_data = data[:100] if len(data) > 100 else data
        
        prompt = f"""Analyze this {source_type} data and provide insights as JSON:

Data sample (first 10 records):
{json.dumps(sample_data[:10], indent=2)}

Total records analyzed: {len(sample_data)}

Respond ONLY with valid JSON containing:
- insights: array of 3-5 key findings
- trending_topics: array of top 5 topics/themes
- recommendations: array of 5 actionable content ideas
- hashtag_strategy: string with hashtag recommendations
- posting_recommendations: string with best posting times/strategies"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a streetwear marketing analyst for Crooks & Castles. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean markdown code blocks if present
        if result.startswith("```"):
            if "```json" in result:
                result = result.split("```json")[1]
            else:
                result = result.split("```")[1]
            result = result.rsplit("```")[0].strip()
        
        parsed = json.loads(result)
        print(f"[ai_processor] Successfully analyzed {len(sample_data)} records")
        return parsed
            
    except json.JSONDecodeError as e:
        print(f"[ai_processor] JSON parse error: {e}")
        print(f"[ai_processor] Response was: {result[:200]}")
        return {
            "insights": ["AI returned invalid JSON format"],
            "trending_topics": [],
            "recommendations": ["Try uploading data again"],
            "hashtag_strategy": "N/A"
        }
    except Exception as e:
        print(f"[ai_processor] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "insights": [f"AI analysis failed: {str(e)}"],
            "trending_topics": [],
            "recommendations": ["Check OpenAI API configuration"],
            "hashtag_strategy": "N/A"
        }