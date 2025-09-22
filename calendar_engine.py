import json, os

DATA_PATH = os.path.join('data', 'calendar.json')

DEFAULT_CAL = {
  "7_day_view": [
    {
      "date": "2025-09-23",
      "title": "Hip-Hop Heritage Story Series Launch",
      "description": "Launch authentic hip-hop heritage content series with street photography and cultural elements showcasing Crooks & Castles legacy in hip-hop culture",
      "budget_allocation": 500,
      "deliverables": ["Instagram post (1080x1080)", "Instagram story series (1080x1920)", "TikTok video (9:16)", "Community engagement"],
      "assets_mapped": ["sept_19_hiphop_anniversary.png", "model1_story.png"],
      "cultural_context": "Hip-Hop Anniversary celebration with authentic street culture positioning",
      "target_kpis": {"engagement_rate": "4.5%", "reach": "25K", "saves": "500"},
      "status": "assets_ready"
    },
    {
      "date": "2025-09-25",
      "title": "Cultural Fusion Content Drop",
      "description": "Showcase cultural fusion in streetwear with diverse models and lifestyle context, emphasizing Crooks & Castles multicultural heritage",
      "budget_allocation": 750,
      "deliverables": ["Instagram carousel (5 slides)", "Story highlights series", "TikTok trend participation", "Community spotlights"],
      "assets_mapped": ["sept_16_cultural_fusion(3).png", "real_instagram_story_rebel_rooftop(1).png"],
      "cultural_context": "Multicultural streetwear positioning with authentic community representation",
      "target_kpis": {"engagement_rate": "5.2%", "reach": "35K", "shares": "200"},
      "status": "in_production"
    }
  ],
  "30_day_view": [
    {
      "date": "2025-10-02",
      "title": "Hispanic Heritage Month Celebration Campaign",
      "description": "Authentic celebration of Hispanic heritage in streetwear with community partnerships, featuring Latino artists and cultural elements in Crooks & Castles designs",
      "budget_allocation": 2000,
      "deliverables": ["Campaign hero creative (multiple formats)", "Community partnership content", "Educational heritage content", "Artist collaboration posts"],
      "assets_mapped": ["sept_15_hispanic_heritage_launch(3).png", "wordmark_story(1).png", "410f528c-980e-497b-bcf0-a6294a39631b.mp4"],
      "cultural_context": "Hispanic Heritage Month with authentic community representation and cultural sensitivity",
      "target_kpis": {"engagement_rate": "6.8%", "reach": "100K", "community_mentions": "50", "cultural_sentiment": "90%+"},
      "status": "community_outreach"
    }
  ],
  "60_day_view": [
    {
      "date": "2025-11-15",
      "title": "Black Friday Cultural Commerce Campaign",
      "description": "Strategic BFCM campaign balancing commercial goals with cultural authenticity, featuring community-driven content and heritage pieces",
      "budget_allocation": 5000,
      "deliverables": ["BFCM campaign creative suite", "Cultural commerce messaging", "Community-driven content", "Heritage collection spotlight"],
      "cultural_context": "Commercial campaign with maintained cultural authenticity and community respect",
      "target_kpis": {"conversion_rate": "3.5%", "roas": "4.2x", "cultural_sentiment": "85%+", "community_engagement": "70%"},
      "status": "creative_development"
    }
  ],
  "90_day_view": [
    {
      "date": "2025-12-15",
      "title": "Q1 2026 Cultural Brand Evolution",
      "description": "Strategic brand evolution for new year positioning with enhanced cultural authenticity and community-first approach to streetwear",
      "budget_allocation": 8000,
      "deliverables": ["Brand evolution strategy", "Cultural positioning manifesto", "Community partnership framework", "Q1 launch campaign"],
      "cultural_context": "Strategic brand evolution with deepened cultural authenticity and community focus",
      "target_kpis": {"brand_evolution_awareness": "+25%", "cultural_authenticity_score": "95%+", "community_advocacy": "+30%"},
      "status": "strategic_planning"
    }
  ]
}

def get_calendar():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CAL
    # seed
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w') as f:
        json.dump(DEFAULT_CAL, f, indent=2)
    return DEFAULT_CAL
