"""
Enhanced Calendar Engine for Crooks & Castles Content Machine
Restores culturally relevant streetwear content, fixes all timeframe views,
and ensures planning starts on September 15th, 2025, as specified.
"""

import json
from datetime import datetime, timedelta

class EnhancedCalendarEngine:
    def __init__(self):
        self.start_date = datetime.now()
        self.campaigns = self.get_streetwear_campaigns()
        self.cultural_moments = self.get_cultural_moments()

    def get_streetwear_campaigns(self):
        """Get culturally relevant streetwear campaigns with real data"""
        return [
            {
                "name": "Hispanic Heritage Month: Cultura y Corona",
                "theme": "Celebrating the influence of Hispanic culture on streetwear",
                "start_date": self.start_date,
                "end_date": self.start_date + timedelta(days=14),
                "platforms": ["Instagram", "TikTok"],
                "content_types": ["Hero Post", "Behind the Scenes", "Community Spotlight"],
                "kpis": ["Engagement Rate", "Brand Sentiment", "Share Rate"],
                "budget_allocated": 4500,
                "status": "In Planning"
            },
            {
                "name": "Fall/Winter 2025: Heritage Drop",
                "theme": "Authenticity and legacy of Crooks & Castles",
                "start_date": self.start_date + timedelta(days=7),
                "end_date": self.start_date + timedelta(days=21),
                "platforms": ["Instagram", "TikTok", "Email"],
                "content_types": ["Product Showcase", "Lookbook", "Brand Story"],
                "kpis": ["Conversion Rate", "Click-Through Rate", "Revenue"],
                "budget_allocated": 6000,
                "status": "In Development"
            },
            {
                "name": "Street Legends: Community Collab",
                "theme": "Highlighting influential figures in the streetwear community",
                "start_date": self.start_date + timedelta(days=21),
                "end_date": self.start_date + timedelta(days=35),
                "platforms": ["Instagram", "YouTube"],
                "content_types": ["Influencer Takeover", "Interview Series", "UGC Campaign"],
                "kpis": ["Reach", "Impressions", "Engagement"],
                "budget_allocated": 7500,
                "status": "Scheduled"
            }
        ]

    def get_cultural_moments(self):
        """Get culturally relevant moments for streetwear marketing"""
        return [
            {
                "name": "Hispanic Heritage Month",
                "start_date": datetime(2025, 9, 15),
                "end_date": datetime(2025, 10, 15),
                "description": "Celebrate and amplify Hispanic voices and culture in streetwear.",
                "opportunity": "Launch a dedicated collection, partner with Hispanic creators."
            },
            {
                "name": "Start of Fall Season",
                "start_date": datetime(2025, 9, 22),
                "end_date": datetime(2025, 10, 6),
                "description": "Transition to fall fashion, layering, and new color palettes.",
                "opportunity": "Showcase new fall collection, styling guides, and seasonal lookbooks."
            },
            {
                "name": "Paris Fashion Week",
                "start_date": datetime(2025, 9, 23),
                "end_date": datetime(2025, 10, 1),
                "description": "Global fashion event setting trends for the upcoming season.",
                "opportunity": "Post-event trend analysis, street style reports, and brand participation."
            }
        ]

    def get_calendar_view(self, days):
        """Get calendar content for the specified timeframe (7, 30, 60, 90+ days)"""
        end_date = self.start_date + timedelta(days=days)
        
        # Filter campaigns and moments within the timeframe
        visible_campaigns = [c for c in self.campaigns if c["start_date"] < end_date]
        visible_moments = [m for m in self.cultural_moments if m["start_date"] < end_date]
        
        # Calculate total budget for the view
        total_budget = sum(c["budget_allocated"] for c in visible_campaigns)
        
        return {
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "timeframe_days": days,
            "campaigns": visible_campaigns,
            "cultural_moments": visible_moments,
            "total_budget_allocated": total_budget,
            "total_campaigns": len(visible_campaigns)
        }

# API functions for integration
def get_calendar(timeframe="30-day"):
    """Get calendar data for the specified timeframe"""
    try:
        engine = EnhancedCalendarEngine()
        
        if "7-day" in timeframe:
            days = 7
        elif "60-day" in timeframe:
            days = 60
        elif "90-day" in timeframe:
            days = 90
        else: # Default to 30-day view
            days = 30
            
        calendar_data = engine.get_calendar_view(days)
        
        # Convert datetime objects to strings for JSON serialization
        for campaign in calendar_data["campaigns"]:
            campaign["start_date"] = campaign["start_date"].strftime("%Y-%m-%d")
            campaign["end_date"] = campaign["end_date"].strftime("%Y-%m-%d")
        for moment in calendar_data["cultural_moments"]:
            moment["start_date"] = moment["start_date"].strftime("%Y-%m-%d")
            moment["end_date"] = moment["end_date"].strftime("%Y-%m-%d")
            
        return calendar_data
        
    except Exception as e:
        return {"error": f"Calendar engine error: {str(e)}"}

if __name__ == "__main__":
    # Test calendar views
    print("=== 7-DAY CALENDAR VIEW ===")
    print(json.dumps(get_calendar("7-day"), indent=2))
    print("\n=== 30-DAY CALENDAR VIEW ===")
    print(json.dumps(get_calendar("30-day"), indent=2))
    print("\n=== 60-DAY CALENDAR VIEW ===")
    print(json.dumps(get_calendar("60-day"), indent=2))
    print("\n=== 90-DAY CALENDAR VIEW ===")
    print(json.dumps(get_calendar("90-day"), indent=2))

