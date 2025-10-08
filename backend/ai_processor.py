import os
import json
from typing import Optional, List, Dict

class AIProcessor:
    """Hybrid AI processor: tries Claude first, falls back to OpenAI"""
    
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize Claude (Anthropic)
        if self.anthropic_key:
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=self.anthropic_key)
                print("[AIProcessor] ✅ Claude (Anthropic) client initialized")
            except Exception as e:
                print(f"[AIProcessor] ⚠️ Failed to initialize Claude: {e}")
        
        # Initialize OpenAI (fallback)
        if self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                print("[AIProcessor] ✅ OpenAI client initialized (fallback)")
            except Exception as e:
                print(f"[AIProcessor] ⚠️ Failed to initialize OpenAI: {e}")
        
        if not self.anthropic_client and not self.openai_client:
            print("[AIProcessor] ❌ No AI clients available")
    
    def _call_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Call Claude API"""
        if not self.anthropic_client:
            raise Exception("Claude client not available")
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.content[0].text
    
    def _call_openai(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Call OpenAI API"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
    
    def _call_ai(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Hybrid AI call: tries Claude first, falls back to OpenAI"""
        
        # Try Claude first
        if self.anthropic_client:
            try:
                result = self._call_claude(system_prompt, user_prompt, max_tokens)
                print("[AIProcessor] ✅ Used Claude")
                return result
            except Exception as e:
                print(f"[AIProcessor] ⚠️ Claude failed: {e}, trying OpenAI...")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                result = self._call_openai(system_prompt, user_prompt, max_tokens)
                print("[AIProcessor] ✅ Used OpenAI (fallback)")
                return result
            except Exception as e:
                print(f"[AIProcessor] ❌ OpenAI also failed: {e}")
                raise Exception(f"Both AI services failed. Claude: {e if self.anthropic_client else 'N/A'}, OpenAI: {e}")
        
        raise Exception("No AI services available")
    
    def generate_summary(self, content: str, max_length: int = 500) -> str:
        """Generate a summary of the content"""
        
        if not self.anthropic_client and not self.openai_client:
            return "AI analysis unavailable - No API keys configured"
        
        if not content or len(content.strip()) == 0:
            return "No content to summarize"
        
        try:
            # Truncate very long content
            content_preview = content[:3000] if len(content) > 3000 else content
            
            system_prompt = "You are a marketing analyst for Crooks & Castles streetwear brand. Provide concise, actionable summaries."
            user_prompt = f"Summarize this content in 2-3 sentences focusing on key takeaways:\n\n{content_preview}"
            
            summary = self._call_ai(system_prompt, user_prompt, max_tokens=200)
            print(f"[AIProcessor] Generated summary ({len(summary)} chars)")
            return summary
            
        except Exception as e:
            print(f"[AIProcessor] Error generating summary: {e}")
            return f"Summary generation failed: {str(e)}"
    
    def extract_insights(self, content: str) -> List[str]:
        """Extract key insights from content"""
        
        if not self.anthropic_client and not self.openai_client:
            return ["AI analysis unavailable - No API keys configured"]
        
        if not content or len(content.strip()) == 0:
            return ["No content to analyze"]
        
        try:
            # Truncate very long content
            content_preview = content[:3000] if len(content) > 3000 else content
            
            system_prompt = "You are a marketing analyst for Crooks & Castles streetwear brand. Extract actionable insights."
            user_prompt = f"""Extract 3-5 key insights from this content. Return ONLY a JSON array of strings.

Content:
{content_preview}

Respond with ONLY valid JSON array format: ["insight 1", "insight 2", "insight 3"]"""
            
            result = self._call_ai(system_prompt, user_prompt, max_tokens=300)
            
            # Clean markdown code blocks if present
            if result.startswith("```"):
                if "```json" in result:
                    result = result.split("```json")[1]
                else:
                    result = result.split("```")[1]
                result = result.rsplit("```")[0].strip()
            
            insights = json.loads(result)
            
            if isinstance(insights, list):
                print(f"[AIProcessor] Extracted {len(insights)} insights")
                return insights[:5]  # Max 5 insights
            else:
                return ["Invalid insights format returned"]
                
        except json.JSONDecodeError as e:
            print(f"[AIProcessor] JSON parse error in extract_insights: {e}")
            return ["Failed to parse AI insights"]
        except Exception as e:
            print(f"[AIProcessor] Error extracting insights: {e}")
            return [f"Insight extraction failed: {str(e)}"]
    
    def analyze_competitive_intel(self, content: str, competitor_name: str) -> Dict:
        """Analyze competitive intelligence"""
        
        if not self.anthropic_client and not self.openai_client:
            return {
                "summary": "AI analysis unavailable",
                "insights": ["No API keys configured"],
                "strengths": [],
                "opportunities": []
            }
        
        try:
            content_preview = content[:3000] if len(content) > 3000 else content
            
            system_prompt = "You are a competitive intelligence analyst for Crooks & Castles streetwear brand."
            user_prompt = f"""Analyze this data about competitor "{competitor_name}". Return ONLY valid JSON with this structure:
{{
  "summary": "2-3 sentence overview",
  "insights": ["insight 1", "insight 2", "insight 3"],
  "strengths": ["strength 1", "strength 2"],
  "opportunities": ["opportunity 1", "opportunity 2"]
}}

Data:
{content_preview}"""
            
            result = self._call_ai(system_prompt, user_prompt, max_tokens=500)
            
            # Clean markdown code blocks
            if result.startswith("```"):
                if "```json" in result:
                    result = result.split("```json")[1]
                else:
                    result = result.split("```")[1]
                result = result.rsplit("```")[0].strip()
            
            analysis = json.loads(result)
            print(f"[AIProcessor] Analyzed competitive intel for {competitor_name}")
            return analysis
            
        except Exception as e:
            print(f"[AIProcessor] Error analyzing competitive intel: {e}")
            return {
                "summary": "Analysis failed",
                "insights": [str(e)],
                "strengths": [],
                "opportunities": []
            }
    
    def analyze_social_data(self, data: list, source_type: str = "social_media") -> dict:
        """Analyze social media data (legacy method for backwards compatibility)"""
        
        if not self.anthropic_client and not self.openai_client:
            return {
                "insights": ["AI services unavailable"],
                "trending_topics": [],
                "recommendations": ["Configure API keys"],
                "hashtag_strategy": "N/A"
            }
        
        try:
            sample_data = data[:100] if len(data) > 100 else data
            
            system_prompt = "You are a streetwear marketing analyst for Crooks & Castles. Always respond with valid JSON only."
            user_prompt = f"""Analyze this {source_type} data and provide insights as JSON:

Data sample (first 10 records):
{json.dumps(sample_data[:10], indent=2)}

Total records analyzed: {len(sample_data)}

Respond ONLY with valid JSON containing:
- insights: array of 3-5 key findings
- trending_topics: array of top 5 topics/themes
- recommendations: array of 5 actionable content ideas
- hashtag_strategy: string with hashtag recommendations
- posting_recommendations: string with best posting times/strategies"""
            
            result = self._call_ai(system_prompt, user_prompt, max_tokens=2000)
            
            # Clean markdown code blocks if present
            if result.startswith("```"):
                if "```json" in result:
                    result = result.split("```json")[1]
                else:
                    result = result.split("```")[1]
                result = result.rsplit("```")[0].strip()
            
            parsed = json.loads(result)
            print(f"[AIProcessor] Successfully analyzed {len(sample_data)} records")
            return parsed
                
        except json.JSONDecodeError as e:
            print(f"[AIProcessor] JSON parse error: {e}")
            return {
                "insights": ["AI returned invalid JSON format"],
                "trending_topics": [],
                "recommendations": ["Try uploading data again"],
                "hashtag_strategy": "N/A"
            }
        except Exception as e:
            print(f"[AIProcessor] Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "insights": [f"AI analysis failed: {str(e)}"],
                "trending_topics": [],
                "recommendations": ["Check API configuration"],
                "hashtag_strategy": "N/A"
            }


# Legacy standalone function for backwards compatibility
def analyze_social_data(data: list, source_type: str = "social_media") -> dict:
    """Legacy function - creates processor instance and calls method"""
    processor = AIProcessor()
    return processor.analyze_social_data(data, source_type)
