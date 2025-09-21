from datetime import datetime, timedelta, date
import json
import os
from typing import Dict, List, Optional, Any
import calendar

class CrooksCalendarManager:
    """Enhanced Calendar Management System for Crooks & Castles Command Center"""
    
    def __init__(self):
        self.events_file = 'data/calendar_events.json'
        self.templates_file = 'data/calendar_templates.json'
        self.ensure_data_directory()
        self.load_events()
        self.load_templates()
        
        # Crooks & Castles specific event types
        self.event_types = {
            'product_drop': {
                'name': 'Product Drop',
                'color': '#FFD700',  # Gold
                'icon': '👑',
                'priority': 'high'
            },
            'design_session': {
                'name': 'Design Session',
                'color': '#000000',  # Black
                'icon': '🎨',
                'priority': 'medium'
            },
            'brand_meeting': {
                'name': 'Brand Strategy Meeting',
                'color': '#333333',  # Dark Gray
                'icon': '🏰',
                'priority': 'high'
            },
            'competitive_analysis': {
                'name': 'Competitive Analysis',
                'color': '#8B0000',  # Dark Red
                'icon': '📊',
                'priority': 'medium'
            },
            'cultural_review': {
                'name': 'Cultural Radar Review',
                'color': '#4B0082',  # Indigo
                'icon': '📡',
                'priority': 'medium'
            },
            'collaboration': {
                'name': 'Artist Collaboration',
                'color': '#FF6347',  # Tomato
                'icon': '🤝',
                'priority': 'high'
            },
            'photoshoot': {
                'name': 'Product Photoshoot',
                'color': '#32CD32',  # Lime Green
                'icon': '📸',
                'priority': 'medium'
            },
            'marketing_campaign': {
                'name': 'Marketing Campaign',
                'color': '#FF1493',  # Deep Pink
                'icon': '📢',
                'priority': 'high'
            },
            'archive_curation': {
                'name': 'Archive Curation',
                'color': '#8B4513',  # Saddle Brown
                'icon': '📚',
                'priority': 'low'
            },
            'trend_analysis': {
                'name': 'Trend Analysis',
                'color': '#20B2AA',  # Light Sea Green
                'icon': '📈',
                'priority': 'medium'
            }
        }
        
        # Strategic planning cycles
        self.planning_cycles = {
            '7_day': 'Weekly Tactical Planning',
            '30_day': 'Monthly Strategic Planning',
            '60_day': 'Quarterly Brand Planning',
            '90_day': 'Seasonal Collection Planning'
        }
        
    def ensure_data_directory(self):
        """Ensure data directory exists for storing calendar data"""
        os.makedirs('data', exist_ok=True)
        
    def load_events(self):
        """Load events from JSON file"""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r') as f:
                    self.events = json.load(f)
            else:
                self.events = self.create_default_events()
                self.save_events()
        except Exception as e:
            print(f"Error loading events: {e}")
            self.events = self.create_default_events()
            
    def load_templates(self):
        """Load event templates from JSON file"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r') as f:
                    self.templates = json.load(f)
            else:
                self.templates = self.create_default_templates()
                self.save_templates()
        except Exception as e:
            print(f"Error loading templates: {e}")
            self.templates = self.create_default_templates()
            
    def save_events(self):
        """Save events to JSON file"""
        try:
            with open(self.events_file, 'w') as f:
                json.dump(self.events, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving events: {e}")
            
    def save_templates(self):
        """Save templates to JSON file"""
        try:
            with open(self.templates_file, 'w') as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            print(f"Error saving templates: {e}")
            
    def create_default_events(self):
        """Create default Crooks & Castles events"""
        today = datetime.now()
        events = []
        
        # Upcoming strategic events
        events.extend([
            {
                'id': 'archive_drop_planning',
                'title': 'Archive Remastered Collection Planning',
                'description': 'Strategic planning for Y2K revival archive drop based on cultural intelligence',
                'start_date': (today + timedelta(days=2)).isoformat(),
                'end_date': (today + timedelta(days=2, hours=2)).isoformat(),
                'event_type': 'product_drop',
                'priority': 'high',
                'attendees': ['Design Team', 'Brand Strategy', 'Cultural Intelligence'],
                'location': 'Design Studio',
                'status': 'scheduled',
                'tags': ['archive', 'y2k', 'heritage', 'drop_planning']
            },
            {
                'id': 'competitive_intel_review',
                'title': 'Weekly Competitive Intelligence Review',
                'description': 'Review Apify data and competitive positioning analysis',
                'start_date': (today + timedelta(days=1)).isoformat(),
                'end_date': (today + timedelta(days=1, hours=1)).isoformat(),
                'event_type': 'competitive_analysis',
                'priority': 'high',
                'attendees': ['Brand Strategy', 'Marketing'],
                'location': 'Command Center',
                'status': 'scheduled',
                'tags': ['competitive_intelligence', 'apify_data', 'strategy']
            },
            {
                'id': 'cultural_radar_analysis',
                'title': 'Cultural Radar Deep Dive',
                'description': 'Analyze TikTok trends and hashtag velocity for cultural opportunities',
                'start_date': (today + timedelta(days=3)).isoformat(),
                'end_date': (today + timedelta(days=3, hours=1.5)).isoformat(),
                'event_type': 'cultural_review',
                'priority': 'medium',
                'attendees': ['Cultural Intelligence', 'Creative Team'],
                'location': 'Trend Lab',
                'status': 'scheduled',
                'tags': ['cultural_trends', 'tiktok', 'hashtag_analysis']
            },
            {
                'id': 'sean_paul_collab_review',
                'title': 'Sean Paul Collaboration Performance Review',
                'description': 'Analyze engagement and cultural impact of Sean Paul collaboration',
                'start_date': (today + timedelta(days=5)).isoformat(),
                'end_date': (today + timedelta(days=5, hours=1)).isoformat(),
                'event_type': 'collaboration',
                'priority': 'high',
                'attendees': ['Brand Strategy', 'Marketing', 'Cultural Intelligence'],
                'location': 'Conference Room',
                'status': 'scheduled',
                'tags': ['sean_paul', 'collaboration', 'performance_review']
            },
            {
                'id': 'medusa_heritage_photoshoot',
                'title': 'Medusa Heritage Collection Photoshoot',
                'description': 'Product photography for heritage Medusa pieces targeting resale market',
                'start_date': (today + timedelta(days=7)).isoformat(),
                'end_date': (today + timedelta(days=7, hours=4)).isoformat(),
                'event_type': 'photoshoot',
                'priority': 'medium',
                'attendees': ['Creative Team', 'Photography', 'Styling'],
                'location': 'Studio A',
                'status': 'scheduled',
                'tags': ['medusa', 'heritage', 'photography', 'resale_market']
            }
        ])
        
        # Recurring events
        events.extend(self.create_recurring_events(today))
        
        return events
        
    def create_recurring_events(self, start_date):
        """Create recurring strategic events"""
        recurring_events = []
        
        # Weekly competitive intelligence reviews (Mondays)
        for week in range(4):
            monday = start_date + timedelta(days=(7 - start_date.weekday()) + (week * 7))
            recurring_events.append({
                'id': f'weekly_intel_{week}',
                'title': 'Weekly Competitive Intelligence Briefing',
                'description': 'Review fresh Apify data and competitive landscape changes',
                'start_date': monday.replace(hour=9, minute=0).isoformat(),
                'end_date': monday.replace(hour=10, minute=0).isoformat(),
                'event_type': 'competitive_analysis',
                'priority': 'high',
                'recurring': 'weekly',
                'attendees': ['Brand Strategy', 'Marketing', 'Leadership'],
                'location': 'Command Center',
                'status': 'scheduled',
                'tags': ['weekly_review', 'competitive_intelligence', 'apify_data']
            })
            
        # Bi-weekly cultural radar sessions (Wednesdays)
        for week in range(0, 4, 2):
            wednesday = start_date + timedelta(days=(9 - start_date.weekday()) + (week * 7))
            recurring_events.append({
                'id': f'cultural_radar_{week}',
                'title': 'Cultural Radar Analysis Session',
                'description': 'Deep dive into TikTok trends and hashtag velocity patterns',
                'start_date': wednesday.replace(hour=14, minute=0).isoformat(),
                'end_date': wednesday.replace(hour=15, minute=30).isoformat(),
                'event_type': 'cultural_review',
                'priority': 'medium',
                'recurring': 'bi-weekly',
                'attendees': ['Cultural Intelligence', 'Creative Team', 'Marketing'],
                'location': 'Trend Lab',
                'status': 'scheduled',
                'tags': ['cultural_trends', 'tiktok_analysis', 'hashtag_velocity']
            })
            
        return recurring_events
        
    def create_default_templates(self):
        """Create default event templates for Crooks & Castles"""
        return {
            'product_drop_planning': {
                'title': 'Product Drop Planning Session',
                'description': 'Strategic planning for upcoming product release',
                'duration_hours': 2,
                'event_type': 'product_drop',
                'priority': 'high',
                'default_attendees': ['Design Team', 'Brand Strategy', 'Marketing'],
                'checklist': [
                    'Review competitive landscape',
                    'Analyze cultural trends',
                    'Define target audience',
                    'Set pricing strategy',
                    'Plan marketing timeline',
                    'Coordinate production schedule'
                ]
            },
            'competitive_analysis_session': {
                'title': 'Competitive Analysis Deep Dive',
                'description': 'Comprehensive review of competitive intelligence data',
                'duration_hours': 1.5,
                'event_type': 'competitive_analysis',
                'priority': 'high',
                'default_attendees': ['Brand Strategy', 'Marketing', 'Cultural Intelligence'],
                'checklist': [
                    'Review Apify Instagram data',
                    'Analyze hashtag velocity trends',
                    'Assess TikTok cultural moments',
                    'Update competitive rankings',
                    'Identify strategic opportunities',
                    'Generate action items'
                ]
            },
            'cultural_trend_review': {
                'title': 'Cultural Trend Analysis',
                'description': 'Review and analyze emerging cultural trends',
                'duration_hours': 1,
                'event_type': 'cultural_review',
                'priority': 'medium',
                'default_attendees': ['Cultural Intelligence', 'Creative Team'],
                'checklist': [
                    'Review TikTok viral content',
                    'Analyze hashtag performance',
                    'Identify emerging themes',
                    'Assess cultural authenticity',
                    'Recommend strategic actions'
                ]
            },
            'brand_strategy_meeting': {
                'title': 'Brand Strategy Session',
                'description': 'Strategic brand positioning and planning meeting',
                'duration_hours': 2,
                'event_type': 'brand_meeting',
                'priority': 'high',
                'default_attendees': ['Leadership', 'Brand Strategy', 'Creative Team'],
                'checklist': [
                    'Review brand performance metrics',
                    'Assess competitive positioning',
                    'Evaluate cultural alignment',
                    'Define strategic priorities',
                    'Set quarterly objectives'
                ]
            }
        }
        
    def add_event(self, event_data: Dict[str, Any]) -> str:
        """Add a new event to the calendar"""
        event_id = event_data.get('id', f"event_{datetime.now().timestamp()}")
        
        # Ensure required fields
        event = {
            'id': event_id,
            'title': event_data.get('title', 'Untitled Event'),
            'description': event_data.get('description', ''),
            'start_date': event_data.get('start_date'),
            'end_date': event_data.get('end_date'),
            'event_type': event_data.get('event_type', 'brand_meeting'),
            'priority': event_data.get('priority', 'medium'),
            'attendees': event_data.get('attendees', []),
            'location': event_data.get('location', ''),
            'status': event_data.get('status', 'scheduled'),
            'tags': event_data.get('tags', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.events.append(event)
        self.save_events()
        return event_id
        
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing event"""
        for event in self.events:
            if event['id'] == event_id:
                event.update(updates)
                event['updated_at'] = datetime.now().isoformat()
                self.save_events()
                return True
        return False
        
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        self.events = [e for e in self.events if e['id'] != event_id]
        self.save_events()
        return True
        
    def get_events_by_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """Get events within a date range"""
        events_in_range = []
        
        for event in self.events:
            try:
                event_start = datetime.fromisoformat(event['start_date']).date()
                if start_date <= event_start <= end_date:
                    events_in_range.append(event)
            except (ValueError, KeyError):
                continue
                
        return sorted(events_in_range, key=lambda x: x['start_date'])
        
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get events by type"""
        return [e for e in self.events if e.get('event_type') == event_type]
        
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """Get upcoming events within specified days"""
        today = date.today()
        end_date = today + timedelta(days=days)
        return self.get_events_by_date_range(today, end_date)
        
    def get_high_priority_events(self) -> List[Dict]:
        """Get high priority events"""
        return [e for e in self.events if e.get('priority') == 'high']
        
    def create_event_from_template(self, template_name: str, start_date: datetime, **kwargs) -> str:
        """Create an event from a template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        template = self.templates[template_name]
        end_date = start_date + timedelta(hours=template['duration_hours'])
        
        event_data = {
            'title': kwargs.get('title', template['title']),
            'description': kwargs.get('description', template['description']),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'event_type': template['event_type'],
            'priority': template['priority'],
            'attendees': kwargs.get('attendees', template['default_attendees']),
            'location': kwargs.get('location', ''),
            'status': 'scheduled',
            'tags': kwargs.get('tags', []),
            'template_used': template_name,
            'checklist': template.get('checklist', [])
        }
        
        return self.add_event(event_data)
        
    def get_calendar_view(self, year: int, month: int) -> Dict[str, Any]:
        """Get calendar view for a specific month"""
        cal = calendar.monthcalendar(year, month)
        month_start = date(year, month, 1)
        
        # Get last day of month
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
            
        events = self.get_events_by_date_range(month_start, month_end)
        
        # Group events by day
        events_by_day = {}
        for event in events:
            try:
                event_date = datetime.fromisoformat(event['start_date']).date()
                day = event_date.day
                if day not in events_by_day:
                    events_by_day[day] = []
                events_by_day[day].append(event)
            except (ValueError, KeyError):
                continue
                
        return {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'calendar_grid': cal,
            'events_by_day': events_by_day,
            'total_events': len(events)
        }
        
    def get_strategic_planning_calendar(self) -> Dict[str, Any]:
        """Get strategic planning calendar with key milestones"""
        today = date.today()
        
        planning_calendar = {
            '7_day': {
                'period': 'Next 7 Days',
                'focus': 'Tactical Execution',
                'events': self.get_upcoming_events(7),
                'key_metrics': ['Daily engagement', 'Content performance', 'Immediate opportunities']
            },
            '30_day': {
                'period': 'Next 30 Days',
                'focus': 'Strategic Implementation',
                'events': self.get_upcoming_events(30),
                'key_metrics': ['Monthly growth', 'Competitive positioning', 'Cultural trend adoption']
            },
            '60_day': {
                'period': 'Next 60 Days',
                'focus': 'Brand Development',
                'events': self.get_upcoming_events(60),
                'key_metrics': ['Quarterly objectives', 'Market expansion', 'Brand evolution']
            },
            '90_day': {
                'period': 'Next 90 Days',
                'focus': 'Seasonal Planning',
                'events': self.get_upcoming_events(90),
                'key_metrics': ['Seasonal collections', 'Annual strategy', 'Long-term positioning']
            }
        }
        
        return planning_calendar
        
    def generate_intelligence_calendar(self, apify_schedule: Dict[str, str]) -> List[Dict]:
        """Generate calendar events based on Apify scraper schedule"""
        intelligence_events = []
        today = datetime.now()
        
        # Create events for next 4 weeks based on Apify schedule
        for week in range(4):
            week_start = today + timedelta(weeks=week)
            
            # Instagram scraper (daily at 7 AM CST)
            for day in range(7):
                event_date = week_start + timedelta(days=day)
                intelligence_events.append({
                    'id': f'instagram_scraper_{event_date.strftime("%Y%m%d")}',
                    'title': 'Instagram Competitive Intelligence Collection',
                    'description': 'Automated collection of competitor Instagram data via Apify',
                    'start_date': event_date.replace(hour=7, minute=0).isoformat(),
                    'end_date': event_date.replace(hour=7, minute=30).isoformat(),
                    'event_type': 'competitive_analysis',
                    'priority': 'medium',
                    'automated': True,
                    'data_source': 'apify_instagram',
                    'tags': ['automated', 'instagram', 'competitive_intelligence']
                })
                
            # Hashtag monitoring (M/W/F at 9 AM CST)
            for day_offset in [0, 2, 4]:  # Monday, Wednesday, Friday
                event_date = week_start + timedelta(days=day_offset)
                intelligence_events.append({
                    'id': f'hashtag_monitor_{event_date.strftime("%Y%m%d")}',
                    'title': 'Hashtag Velocity Monitoring',
                    'description': 'Cultural trend analysis via hashtag performance tracking',
                    'start_date': event_date.replace(hour=9, minute=0).isoformat(),
                    'end_date': event_date.replace(hour=9, minute=15).isoformat(),
                    'event_type': 'cultural_review',
                    'priority': 'medium',
                    'automated': True,
                    'data_source': 'apify_hashtags',
                    'tags': ['automated', 'hashtags', 'cultural_trends']
                })
                
            # TikTok intelligence (Sunday/Wednesday at 10 AM CST)
            for day_offset in [6, 2]:  # Sunday, Wednesday
                event_date = week_start + timedelta(days=day_offset)
                intelligence_events.append({
                    'id': f'tiktok_intel_{event_date.strftime("%Y%m%d")}',
                    'title': 'TikTok Cultural Intelligence Collection',
                    'description': 'Gen Z cultural moment analysis and trend detection',
                    'start_date': event_date.replace(hour=10, minute=0).isoformat(),
                    'end_date': event_date.replace(hour=10, minute=20).isoformat(),
                    'event_type': 'cultural_review',
                    'priority': 'medium',
                    'automated': True,
                    'data_source': 'apify_tiktok',
                    'tags': ['automated', 'tiktok', 'cultural_intelligence']
                })
                
        return intelligence_events
        
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get calendar statistics and insights"""
        total_events = len(self.events)
        
        # Count by type
        type_counts = {}
        for event in self.events:
            event_type = event.get('event_type', 'unknown')
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
        # Count by priority
        priority_counts = {}
        for event in self.events:
            priority = event.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
        # Upcoming events
        upcoming = self.get_upcoming_events(7)
        high_priority_upcoming = [e for e in upcoming if e.get('priority') == 'high']
        
        return {
            'total_events': total_events,
            'events_by_type': type_counts,
            'events_by_priority': priority_counts,
            'upcoming_7_days': len(upcoming),
            'high_priority_upcoming': len(high_priority_upcoming),
            'most_common_type': max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }
        
    def export_calendar(self, format_type: str = 'json') -> str:
        """Export calendar data in specified format"""
        if format_type == 'json':
            return json.dumps(self.events, indent=2, default=str)
        elif format_type == 'ical':
            # Basic iCal export (would need icalendar library for full implementation)
            ical_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:Crooks & Castles Command Center\n"
            
            for event in self.events:
                ical_content += "BEGIN:VEVENT\n"
                ical_content += f"UID:{event['id']}\n"
                ical_content += f"SUMMARY:{event['title']}\n"
                ical_content += f"DESCRIPTION:{event['description']}\n"
                ical_content += f"DTSTART:{event['start_date']}\n"
                ical_content += f"DTEND:{event['end_date']}\n"
                ical_content += "END:VEVENT\n"
                
            ical_content += "END:VCALENDAR"
            return ical_content
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
