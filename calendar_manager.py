import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

class CalendarManager:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.events_file = os.path.join(data_folder, 'calendar_events.json')
        self.templates_file = os.path.join(data_folder, 'event_templates.json')
        
        # Ensure data folder exists
        os.makedirs(data_folder, exist_ok=True)
        
        # Initialize with default templates if file doesn't exist
        if not os.path.exists(self.templates_file):
            self.create_default_templates()
        
        # Initialize events file if it doesn't exist
        if not os.path.exists(self.events_file):
            self.create_initial_events()

    def create_default_templates(self):
        """Create default event templates for different campaign types"""
        templates = {
            'product_launch': {
                'name': 'Product Launch Campaign',
                'duration_days': 30,
                'milestones': [
                    {'name': 'Concept Development', 'days_before': 30, 'type': 'planning'},
                    {'name': 'Asset Creation Start', 'days_before': 21, 'type': 'production'},
                    {'name': 'First Draft Review', 'days_before': 14, 'type': 'review'},
                    {'name': 'Final Assets Due', 'days_before': 7, 'type': 'deadline'},
                    {'name': 'Campaign Launch', 'days_before': 0, 'type': 'launch'}
                ],
                'required_assets': [
                    'hero_image', 'product_shots', 'lifestyle_photos', 
                    'social_media_posts', 'email_header', 'website_banner'
                ],
                'color': '#FF1493'  # Bright Pink
            },
            'frequency_collective': {
                'name': 'Frequency Collective Campaign',
                'duration_days': 21,
                'milestones': [
                    {'name': 'Ambassador Recruitment', 'days_before': 21, 'type': 'planning'},
                    {'name': 'Content Creation', 'days_before': 14, 'type': 'production'},
                    {'name': 'UGC Collection', 'days_before': 7, 'type': 'collection'},
                    {'name': 'Campaign Launch', 'days_before': 0, 'type': 'launch'}
                ],
                'required_assets': [
                    'ambassador_photos', 'ugc_templates', 'recruitment_graphics',
                    'social_media_kit', 'campus_materials'
                ],
                'color': '#00CED1'  # Vibrant Turquoise
            },
            'seasonal_drop': {
                'name': 'Seasonal Collection Drop',
                'duration_days': 45,
                'milestones': [
                    {'name': 'Collection Planning', 'days_before': 45, 'type': 'planning'},
                    {'name': 'Photoshoot Prep', 'days_before': 30, 'type': 'planning'},
                    {'name': 'Photoshoot Execution', 'days_before': 21, 'type': 'production'},
                    {'name': 'Asset Processing', 'days_before': 14, 'type': 'production'},
                    {'name': 'Marketing Materials', 'days_before': 7, 'type': 'production'},
                    {'name': 'Collection Launch', 'days_before': 0, 'type': 'launch'}
                ],
                'required_assets': [
                    'collection_hero', 'individual_products', 'styling_shots',
                    'countdown_graphics', 'email_campaign', 'website_assets'
                ],
                'color': '#8A2BE2'  # Rich Purple
            },
            'content_creation': {
                'name': 'Content Creation Sprint',
                'duration_days': 14,
                'milestones': [
                    {'name': 'Content Planning', 'days_before': 14, 'type': 'planning'},
                    {'name': 'Creation Phase', 'days_before': 10, 'type': 'production'},
                    {'name': 'Review & Revisions', 'days_before': 5, 'type': 'review'},
                    {'name': 'Content Delivery', 'days_before': 0, 'type': 'deadline'}
                ],
                'required_assets': [
                    'social_media_posts', 'blog_images', 'video_content',
                    'graphics', 'photography'
                ],
                'color': '#32CD32'  # Lime Green
            }
        }
        
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)

    def create_initial_events(self):
        """Create some initial sample events"""
        initial_events = [
            {
                'id': str(uuid.uuid4()),
                'title': 'Gratitude Collection Launch',
                'description': 'Launch new gratitude-themed apparel collection',
                'start_date': (datetime.now() + timedelta(days=6)).isoformat(),
                'end_date': (datetime.now() + timedelta(days=6)).isoformat(),
                'type': 'product_launch',
                'status': 'scheduled',
                'campaign_type': 'product_launch',
                'priority': 'high',
                'color': '#FF1493',
                'created_date': datetime.now().isoformat(),
                'assets_required': ['hero_image', 'product_shots', 'social_media_posts'],
                'assets_completed': [],
                'progress': 30
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Frequency Collective Recruitment Drive',
                'description': 'Campus ambassador program recruitment campaign',
                'start_date': (datetime.now() + timedelta(days=11)).isoformat(),
                'end_date': (datetime.now() + timedelta(days=25)).isoformat(),
                'type': 'marketing',
                'status': 'planning',
                'campaign_type': 'frequency_collective',
                'priority': 'medium',
                'color': '#00CED1',
                'created_date': datetime.now().isoformat(),
                'assets_required': ['recruitment_graphics', 'social_media_kit'],
                'assets_completed': [],
                'progress': 10
            }
        ]
        
        with open(self.events_file, 'w') as f:
            json.dump(initial_events, f, indent=2)

    def load_events(self) -> List[Dict]:
        """Load all events from storage"""
        try:
            with open(self.events_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_events(self, events: List[Dict]):
        """Save events to storage"""
        with open(self.events_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)

    def get_events_in_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get events within a specific date range"""
        events = self.load_events()
        filtered_events = []
        
        for event in events:
            event_start = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event['end_date'].replace('Z', '+00:00'))
            
            # Check if event overlaps with the requested range
            if (event_start <= end_date and event_end >= start_date):
                filtered_events.append(event)
        
        return sorted(filtered_events, key=lambda x: x['start_date'])

    def get_rolling_calendar(self, days_back: int = 7, days_forward: int = 60) -> Dict:
        """Get a rolling calendar view"""
        today = datetime.now()
        start_date = today - timedelta(days=days_back)
        end_date = today + timedelta(days=days_forward)
        
        events = self.get_events_in_range(start_date, end_date)
        
        # Group events by week for better visualization
        weeks = {}
        current_date = start_date
        
        while current_date <= end_date:
            week_start = current_date - timedelta(days=current_date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            
            if week_key not in weeks:
                weeks[week_key] = {
                    'week_start': week_start.isoformat(),
                    'week_end': (week_start + timedelta(days=6)).isoformat(),
                    'events': []
                }
            
            current_date += timedelta(days=7)
        
        # Assign events to weeks
        for event in events:
            event_date = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
            week_start = event_date - timedelta(days=event_date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            
            if week_key in weeks:
                weeks[week_key]['events'].append(event)
        
        return {
            'range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'weeks': weeks,
            'total_events': len(events),
            'upcoming_deadlines': self.get_upcoming_deadlines(7)
        }

    def get_upcoming_deadlines(self, days: int = 7) -> List[Dict]:
        """Get upcoming deadlines within specified days"""
        today = datetime.now()
        end_date = today + timedelta(days=days)
        
        events = self.get_events_in_range(today, end_date)
        deadlines = []
        
        for event in events:
            event_date = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
            days_until = (event_date - today).days
            
            if event['type'] in ['deadline', 'launch', 'product_launch'] or event['priority'] == 'high':
                deadlines.append({
                    'event': event,
                    'days_until': days_until,
                    'urgency': 'critical' if days_until <= 2 else 'high' if days_until <= 5 else 'medium'
                })
        
        return sorted(deadlines, key=lambda x: x['days_until'])

    def create_event(self, event_data: Dict) -> Dict:
        """Create a new event"""
        events = self.load_events()
        
        new_event = {
            'id': str(uuid.uuid4()),
            'title': event_data.get('title', 'New Event'),
            'description': event_data.get('description', ''),
            'start_date': event_data.get('start_date', datetime.now().isoformat()),
            'end_date': event_data.get('end_date', datetime.now().isoformat()),
            'type': event_data.get('type', 'general'),
            'status': event_data.get('status', 'planned'),
            'campaign_type': event_data.get('campaign_type', 'general'),
            'priority': event_data.get('priority', 'medium'),
            'color': event_data.get('color', '#008B8B'),
            'created_date': datetime.now().isoformat(),
            'assets_required': event_data.get('assets_required', []),
            'assets_completed': [],
            'progress': 0
        }
        
        events.append(new_event)
        self.save_events(events)
        
        return new_event

    def update_event(self, event_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing event"""
        events = self.load_events()
        
        for i, event in enumerate(events):
            if event['id'] == event_id:
                events[i].update(updates)
                events[i]['modified_date'] = datetime.now().isoformat()
                self.save_events(events)
                return events[i]
        
        return None

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        events = self.load_events()
        original_length = len(events)
        
        events = [event for event in events if event['id'] != event_id]
        
        if len(events) < original_length:
            self.save_events(events)
            return True
        
        return False

    def create_campaign_from_template(self, template_name: str, launch_date: datetime, campaign_title: str) -> List[Dict]:
        """Create a full campaign timeline from a template"""
        with open(self.templates_file, 'r') as f:
            templates = json.load(f)
        
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = templates[template_name]
        created_events = []
        
        # Create main campaign event
        main_event = self.create_event({
            'title': campaign_title,
            'description': f"{template['name']} campaign",
            'start_date': launch_date.isoformat(),
            'end_date': launch_date.isoformat(),
            'type': 'launch',
            'campaign_type': template_name,
            'priority': 'high',
            'color': template['color'],
            'assets_required': template['required_assets']
        })
        created_events.append(main_event)
        
        # Create milestone events
        for milestone in template['milestones']:
            milestone_date = launch_date - timedelta(days=milestone['days_before'])
            
            milestone_event = self.create_event({
                'title': f"{campaign_title}: {milestone['name']}",
                'description': f"{milestone['name']} for {campaign_title}",
                'start_date': milestone_date.isoformat(),
                'end_date': milestone_date.isoformat(),
                'type': milestone['type'],
                'campaign_type': template_name,
                'priority': 'high' if milestone['type'] in ['deadline', 'launch'] else 'medium',
                'color': template['color'],
                'parent_campaign': main_event['id']
            })
            created_events.append(milestone_event)
        
        return created_events

    def get_campaign_progress(self, campaign_id: str) -> Dict:
        """Get progress information for a campaign"""
        events = self.load_events()
        campaign_events = [e for e in events if e.get('parent_campaign') == campaign_id or e['id'] == campaign_id]
        
        if not campaign_events:
            return {}
        
        total_milestones = len([e for e in campaign_events if e.get('parent_campaign')])
        completed_milestones = len([e for e in campaign_events if e.get('status') == 'completed'])
        
        main_campaign = next((e for e in campaign_events if e['id'] == campaign_id), None)
        if not main_campaign:
            return {}
        
        total_assets = len(main_campaign.get('assets_required', []))
        completed_assets = len(main_campaign.get('assets_completed', []))
        
        return {
            'campaign_id': campaign_id,
            'title': main_campaign['title'],
            'milestone_progress': (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0,
            'asset_progress': (completed_assets / total_assets * 100) if total_assets > 0 else 0,
            'overall_progress': main_campaign.get('progress', 0),
            'status': main_campaign.get('status', 'planned'),
            'days_until_launch': (datetime.fromisoformat(main_campaign['start_date']) - datetime.now()).days
        }

    def update_asset_completion(self, event_id: str, asset_name: str, completed: bool = True):
        """Mark an asset as completed for an event"""
        events = self.load_events()
        
        for event in events:
            if event['id'] == event_id:
                if 'assets_completed' not in event:
                    event['assets_completed'] = []
                
                if completed and asset_name not in event['assets_completed']:
                    event['assets_completed'].append(asset_name)
                elif not completed and asset_name in event['assets_completed']:
                    event['assets_completed'].remove(asset_name)
                
                # Update progress
                total_assets = len(event.get('assets_required', []))
                completed_assets = len(event['assets_completed'])
                event['progress'] = (completed_assets / total_assets * 100) if total_assets > 0 else 0
                
                self.save_events(events)
                break

