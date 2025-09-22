import os
import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict

def get_enhanced_calendar(view='30'):
    """Get enhanced calendar with streetwear cultural intelligence"""
    
    # Convert view to integer
    try:
        days = int(view)
    except (ValueError, TypeError):
        days = 30
    
    # Generate calendar events based on view
    events = []
    start_date = datetime.now()
    
    if days == 7:
        events = generate_7_day_calendar(start_date)
    elif days == 30:
        events = generate_30_day_calendar(start_date)
    elif days == 60:
        events = generate_60_day_calendar(start_date)
    elif days >= 90:
        events = generate_90_day_calendar(start_date)
    else:
        events = generate_30_day_calendar(start_date)  # Default
    
    # Calculate summary statistics
    total_budget = sum(event.get('budget', 0) for event in events)
    active_campaigns = len([e for e in events if e.get('status') == 'active'])
    
    return {
        'view': f"{days}_day",
        'events': events,
        'summary': {
            'total_events': len(events),
            'total_budget': total_budget,
            'active_campaigns': active_campaigns,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': (start_date + timedelta(days=days)).strftime('%Y-%m-%d')
            }
        },
        'generated_at': datetime.now().isoformat()
    }

def generate_7_day_calendar(start_date):
    """Generate 7-day tactical calendar with immediate opportunities"""
    events = []
    
    for i in range(7):
        date = start_date + timedelta(days=i)
        day_name = date.strftime('%A')
        
        if i == 0:  # Today
            events.append({
                'id': str(uuid.uuid4()),
                'title': 'Hip-Hop Heritage Story Series',
                'date': date.strftime('%Y-%m-%d'),
                'category': 'cultural_content',
                'status': 'active',
                'priority': 'high',
                'budget': 500,
                'description': 'Launch daily story series celebrating hip-hop culture and Crooks & Castles heritage',
                'assets': ['sept_19_hiphop_anniversary.png', 'castle_story.png'],
                'deliverables': ['Instagram Stories', 'TikTok Content', 'Community Engagement'],
                'kpis': {
                    'target_reach': 50000,
                    'target_engagement': '5%',
                    'story_completion_rate': '70%'
                },
                'cultural_context': 'Hip-hop 52nd anniversary celebration with authentic street culture connection'
            })
        
        elif i == 2:  # Day 3
            events.append({
                'id': str(uuid.uuid4()),
                'title': 'Cultural Fusion Content Drop',
                'date': date.strftime('%Y-%m-%d'),
                'category': 'product_launch',
                'status': 'planned',
                'priority': 'high',
                'budget': 800,
                'description': 'Release cultural fusion collection with Hispanic Heritage and streetwear elements',
                'assets': ['sept_16_cultural_fusion(3).png', 'real_instagram_story_rebel_rooftop(1).png'],
                'deliverables': ['Product Photography', 'Social Media Campaign', 'Influencer Outreach'],
                'kpis': {
                    'target_sales': 25000,
                    'target_engagement': '7%',
                    'conversion_rate': '3%'
                },
                'cultural_context': 'Authentic fusion of Hispanic heritage with streetwear aesthetics'
            })
        
        elif i == 5:  # Day 6
            events.append({
                'id': str(uuid.uuid4()),
                'title': 'Weekly Intelligence Recap',
                'date': date.strftime('%Y-%m-%d'),
                'category': 'intelligence',
                'status': 'scheduled',
                'priority': 'medium',
                'budget': 200,
                'description': 'Compile and analyze weekly competitive intelligence and cultural trends',
                'assets': ['dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl'],
                'deliverables': ['Intelligence Report', 'Trend Analysis', 'Competitive Insights'],
                'kpis': {
                    'data_points_analyzed': 1000,
                    'actionable_insights': 5,
                    'trend_accuracy': '85%'
                },
                'cultural_context': 'Data-driven insights for authentic cultural positioning'
            })
    
    return events

def generate_30_day_calendar(start_date):
    """Generate 30-day strategic calendar with cultural campaigns"""
    events = []
    
    # Week 1: Hispanic Heritage Month Launch
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Hispanic Heritage Month Campaign Launch',
        'date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
        'category': 'cultural_campaign',
        'status': 'active',
        'priority': 'high',
        'budget': 5000,
        'description': 'Comprehensive Hispanic Heritage Month celebration with authentic cultural representation',
        'assets': ['sept_15_hispanic_heritage_launch(3).png', 'model1_story.png', 'model2_story.png'],
        'deliverables': ['Social Media Campaign', 'Community Events', 'Cultural Partnerships', 'Video Content'],
        'kpis': {
            'target_reach': 200000,
            'target_engagement': '8%',
            'cultural_authenticity_score': '95%',
            'community_participation': 500
        },
        'cultural_context': 'Celebrating Hispanic Heritage Month (Sept 15 - Oct 15) with authentic storytelling and community engagement'
    })
    
    # Week 2: Hip-Hop Anniversary Tribute
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Hip-Hop 52nd Anniversary Tribute',
        'date': (start_date + timedelta(days=10)).strftime('%Y-%m-%d'),
        'category': 'cultural_campaign',
        'status': 'planned',
        'priority': 'high',
        'budget': 4000,
        'description': 'Tribute to hip-hop culture with heritage collection and community celebration',
        'assets': ['sept_19_hiphop_anniversary.png', 'castle_story.png', 'medusa_story(1).png'],
        'deliverables': ['Heritage Collection Launch', 'Artist Collaborations', 'Documentary Content', 'Community Events'],
        'kpis': {
            'target_sales': 75000,
            'artist_collaborations': 3,
            'documentary_views': 100000,
            'cultural_impact_score': '90%'
        },
        'cultural_context': 'Honoring hip-hop\'s 52nd anniversary with authentic street culture celebration'
    })
    
    # Week 3: Streetwear Culture Documentation
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Streetwear Culture Documentation Project',
        'date': (start_date + timedelta(days=17)).strftime('%Y-%m-%d'),
        'category': 'content_creation',
        'status': 'planned',
        'priority': 'medium',
        'budget': 2500,
        'description': 'Document authentic streetwear culture and community stories',
        'assets': ['model2_story.png', 'wordmark_story(1).png'],
        'deliverables': ['Documentary Series', 'Community Interviews', 'Cultural Archive', 'Educational Content'],
        'kpis': {
            'interviews_conducted': 20,
            'documentary_episodes': 5,
            'archive_entries': 100,
            'educational_reach': 50000
        },
        'cultural_context': 'Preserving and sharing authentic streetwear culture and community narratives'
    })
    
    # Week 4: Community Engagement Initiative
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Community Engagement & Feedback Initiative',
        'date': (start_date + timedelta(days=24)).strftime('%Y-%m-%d'),
        'category': 'community',
        'status': 'planned',
        'priority': 'medium',
        'budget': 1500,
        'description': 'Engage community for feedback and co-creation opportunities',
        'assets': ['real_instagram_story_rebel_rooftop(1).png'],
        'deliverables': ['Community Surveys', 'Focus Groups', 'Co-creation Workshops', 'Feedback Integration'],
        'kpis': {
            'survey_responses': 1000,
            'focus_group_participants': 50,
            'workshop_attendees': 100,
            'feedback_implementation': '80%'
        },
        'cultural_context': 'Building authentic community connections and collaborative design processes'
    })
    
    return events

def generate_60_day_calendar(start_date):
    """Generate 60-day strategic calendar with seasonal campaigns"""
    events = generate_30_day_calendar(start_date)  # Include 30-day events
    
    # Add 60-day specific events
    
    # Week 5-6: Pre-Black Friday Cultural Positioning
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Pre-Black Friday Cultural Positioning',
        'date': (start_date + timedelta(days=35)).strftime('%Y-%m-%d'),
        'category': 'commercial_campaign',
        'status': 'planned',
        'priority': 'high',
        'budget': 8000,
        'description': 'Position brand culturally before Black Friday with authentic value proposition',
        'assets': ['410f528c-980e-497b-bcf0-a6294a39631b.mp4', '9dd8a1ec-8b07-460b-884d-8e0d8a0260d9.mov'],
        'deliverables': ['Brand Positioning Campaign', 'Value Proposition Content', 'Cultural Authenticity Messaging'],
        'kpis': {
            'brand_awareness_lift': '15%',
            'cultural_relevance_score': '90%',
            'pre_sale_engagement': '12%'
        },
        'cultural_context': 'Establishing authentic cultural value before commercial season'
    })
    
    # Week 7-8: Black Friday Cultural Commerce Campaign
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Black Friday Cultural Commerce Campaign',
        'date': (start_date + timedelta(days=45)).strftime('%Y-%m-%d'),
        'category': 'commercial_campaign',
        'status': 'planned',
        'priority': 'high',
        'budget': 12000,
        'description': 'Black Friday campaign focused on cultural commerce and community value',
        'assets': ['medusa_story(1).png', 'castle_story.png'],
        'deliverables': ['Sales Campaign', 'Cultural Commerce Strategy', 'Community Rewards Program'],
        'kpis': {
            'target_revenue': 250000,
            'conversion_rate': '8%',
            'community_participation': '25%',
            'cultural_authenticity_maintenance': '85%'
        },
        'cultural_context': 'Balancing commercial success with cultural authenticity and community value'
    })
    
    return events

def generate_90_day_calendar(start_date):
    """Generate 90+ day strategic calendar with quarterly planning"""
    events = generate_60_day_calendar(start_date)  # Include 60-day events
    
    # Add 90+ day strategic events
    
    # Week 9-12: Holiday Cultural Fusion Campaign
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Holiday Cultural Fusion Campaign',
        'date': (start_date + timedelta(days=65)).strftime('%Y-%m-%d'),
        'category': 'seasonal_campaign',
        'status': 'planned',
        'priority': 'high',
        'budget': 15000,
        'description': 'Holiday season campaign celebrating cultural diversity and unity',
        'assets': ['sept_16_cultural_fusion(3).png', 'wordmark_story(1).png'],
        'deliverables': ['Holiday Collection', 'Cultural Unity Campaign', 'Gift Guide', 'Community Celebrations'],
        'kpis': {
            'holiday_sales_target': 400000,
            'cultural_diversity_representation': '100%',
            'community_events': 10,
            'gift_guide_engagement': '15%'
        },
        'cultural_context': 'Celebrating cultural diversity during holiday season with inclusive messaging'
    })
    
    # Week 13-16: Year-End Cultural Impact Report
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Year-End Cultural Impact Report & Planning',
        'date': (start_date + timedelta(days=80)).strftime('%Y-%m-%d'),
        'category': 'strategic_planning',
        'status': 'planned',
        'priority': 'medium',
        'budget': 3000,
        'description': 'Comprehensive cultural impact assessment and next year strategic planning',
        'assets': ['instagram_competitive_data.jsonl'],
        'deliverables': ['Impact Report', 'Cultural Metrics Analysis', '2026 Strategy Plan', 'Community Feedback Summary'],
        'kpis': {
            'cultural_impact_score': '95%',
            'community_growth': '30%',
            'brand_authenticity_rating': '90%',
            'strategic_goals_achievement': '85%'
        },
        'cultural_context': 'Measuring authentic cultural impact and planning for continued community growth'
    })
    
    # Week 17-20: Q1 2026 Cultural Brand Evolution
    events.append({
        'id': str(uuid.uuid4()),
        'title': 'Q1 2026 Cultural Brand Evolution Initiative',
        'date': (start_date + timedelta(days=95)).strftime('%Y-%m-%d'),
        'category': 'brand_evolution',
        'status': 'planned',
        'priority': 'high',
        'budget': 20000,
        'description': 'Strategic brand evolution based on cultural insights and community feedback',
        'assets': ['model1_story.png', 'model2_story.png'],
        'deliverables': ['Brand Evolution Strategy', 'New Cultural Partnerships', 'Community Co-creation Program'],
        'kpis': {
            'brand_evolution_acceptance': '90%',
            'new_partnerships': 5,
            'co_creation_participants': 200,
            'cultural_relevance_increase': '20%'
        },
        'cultural_context': 'Evolving brand identity based on authentic cultural insights and community collaboration'
    })
    
    return events

def add_calendar_event(title, date, category, description, budget=0, assets=None):
    """Add new calendar event"""
    try:
        event = {
            'id': str(uuid.uuid4()),
            'title': title,
            'date': date,
            'category': category,
            'description': description,
            'budget': budget,
            'assets': assets or [],
            'status': 'planned',
            'priority': 'medium',
            'created_at': datetime.now().isoformat(),
            'deliverables': [],
            'kpis': {},
            'cultural_context': 'Custom event'
        }
        
        # In a real implementation, you'd save this to a database
        return {'success': True, 'event': event}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def remove_calendar_event(event_id):
    """Remove calendar event"""
    try:
        # In a real implementation, you'd remove from database
        return {'success': True, 'message': f'Event {event_id} removed'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_calendar_view(view='30'):
    """Get calendar view (alias for get_enhanced_calendar)"""
    return get_enhanced_calendar(view)

def get_cultural_intelligence():
    """Get cultural intelligence insights"""
    return {
        'cultural_moments': {
            'hispanic_heritage_month': {
                'period': 'September 15 - October 15',
                'relevance_score': 95,
                'opportunity': 'Authentic cultural celebration and community engagement',
                'recommended_actions': ['Cultural partnerships', 'Heritage storytelling', 'Community events']
            },
            'hiphop_anniversary': {
                'period': 'Ongoing celebration',
                'relevance_score': 90,
                'opportunity': 'Street culture authenticity and music connections',
                'recommended_actions': ['Artist collaborations', 'Heritage content', 'Community tributes']
            },
            'back_to_school': {
                'period': 'August - September',
                'relevance_score': 80,
                'opportunity': 'Youth market engagement and campus culture',
                'recommended_actions': ['Student partnerships', 'Campus events', 'Educational content']
            }
        },
        'cultural_trends': {
            'authenticity_focus': {
                'trend': 'Increased demand for authentic cultural representation',
                'impact': 'High',
                'recommendation': 'Emphasize heritage storytelling and community connections'
            },
            'community_collaboration': {
                'trend': 'Growing preference for community-driven brand experiences',
                'impact': 'High',
                'recommendation': 'Develop co-creation programs and community partnerships'
            },
            'cultural_fusion': {
                'trend': 'Appreciation for respectful cultural fusion and diversity',
                'impact': 'Medium',
                'recommendation': 'Create inclusive campaigns celebrating cultural diversity'
            }
        },
        'generated_at': datetime.now().isoformat()
    }

def get_budget_allocation(view='30'):
    """Get budget allocation for calendar view"""
    calendar_data = get_enhanced_calendar(view)
    events = calendar_data.get('events', [])
    
    budget_by_category = defaultdict(int)
    budget_by_priority = defaultdict(int)
    budget_by_month = defaultdict(int)
    
    for event in events:
        budget = event.get('budget', 0)
        category = event.get('category', 'other')
        priority = event.get('priority', 'medium')
        
        # Parse date for monthly allocation
        try:
            event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d')
            month_key = event_date.strftime('%Y-%m')
            budget_by_month[month_key] += budget
        except (ValueError, TypeError):
            pass
        
        budget_by_category[category] += budget
        budget_by_priority[priority] += budget
    
    return {
        'total_budget': sum(event.get('budget', 0) for event in events),
        'by_category': dict(budget_by_category),
        'by_priority': dict(budget_by_priority),
        'by_month': dict(budget_by_month),
        'average_per_event': sum(event.get('budget', 0) for event in events) / len(events) if events else 0,
        'budget_efficiency': calculate_budget_efficiency(events),
        'generated_at': datetime.now().isoformat()
    }

def calculate_budget_efficiency(events):
    """Calculate budget efficiency metrics"""
    if not events:
        return {'efficiency_score': 0, 'recommendations': []}
    
    total_budget = sum(event.get('budget', 0) for event in events)
    high_priority_budget = sum(event.get('budget', 0) for event in events if event.get('priority') == 'high')
    
    efficiency_score = (high_priority_budget / total_budget * 100) if total_budget > 0 else 0
    
    recommendations = []
    if efficiency_score < 60:
        recommendations.append('Consider reallocating budget to high-priority cultural campaigns')
    if total_budget > 50000:
        recommendations.append('Review budget allocation for optimal ROI across cultural initiatives')
    
    return {
        'efficiency_score': round(efficiency_score, 2),
        'high_priority_allocation': round((high_priority_budget / total_budget * 100) if total_budget > 0 else 0, 2),
        'recommendations': recommendations
    }

def get_upcoming_events(days=7):
    """Get upcoming events within specified days"""
    calendar_data = get_enhanced_calendar(str(days))
    return calendar_data.get('events', [])

def get_event_by_id(event_id):
    """Get specific event by ID"""
    # In a real implementation, you'd query the database
    # For now, return a sample event structure
    return {
        'id': event_id,
        'title': 'Sample Event',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'category': 'cultural_campaign',
        'status': 'planned',
        'budget': 1000,
        'description': 'Sample event description'
    }
