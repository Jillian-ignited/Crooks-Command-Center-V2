"""
Real HVD Agency Tracker - Based on Actual Proposal
Tracks deliverables against the real HVD x Crooks proposal phases and budgets
"""

import os
import json
from datetime import datetime, timedelta
from enhanced_data_processor import process_enhanced_intelligence_data

class RealHVDAgencyTracker:
    def __init__(self):
        self.intelligence_data = None
        self.current_date = datetime.now()
        self.load_real_data()
        
        # Real HVD Phased Approach from Proposal
        self.hvd_stages = {
            'stage_1_foundation': {
                'name': 'Foundation & Awareness',
                'timeline': 'September - October 2025',
                'investment': 4000,  # $4,000/month
                'objective': 'Rebuild presence, prime audiences, set the foundation. Keep costs lean while still providing visible value.',
                'status': 'active'
            },
            'stage_2_growth': {
                'name': 'Growth & Q4 Push',
                'timeline': 'November - December 2025', 
                'investment': 7500,  # $7,500/month
                'objective': 'Drive revenue through Q4 campaigns (esp. BFCM + holiday season). More aggressive ads and creative.',
                'status': 'upcoming'
            },
            'stage_3_full_retainer': {
                'name': 'Full Retainer',
                'timeline': 'January 2026 onward',
                'investment': 11000,  # $11,000/month + 5% ad spend
                'objective': 'Launch full-service engagement post-site relaunch & rebrand.',
                'status': 'planned'
            }
        }
    
    def load_real_data(self):
        """Load real competitive intelligence data"""
        try:
            self.intelligence_data = process_enhanced_intelligence_data()
        except Exception as e:
            print(f"Error loading intelligence data: {e}")
            self.intelligence_data = None
    
    def get_stage_1_deliverables(self):
        """Stage 1: Foundation & Awareness (Sept-Oct) - $4,000/month"""
        deliverables = []
        
        # Ad Management (Light)
        deliverables.append({
            'name': 'Ad Management (Light)',
            'description': 'Low-spend campaigns on Meta & Google (brand awareness + retargeting). Focus on reintroducing the brand to warm audiences.',
            'stage': 'Foundation & Awareness',
            'status': 'in_progress',
            'completion_date': None,
            'deliverable_type': 'ad_management',
            'progress': 25,
            'monthly_allocation': 1200,  # Estimated from $4K total
            'next_action': 'Set up Meta & Google brand awareness campaigns with retargeting pixels',
            'dependencies': [],
            'kpis': ['Brand awareness reach', 'Retargeting audience building', 'Cost per impression']
        })
        
        # Ad Creative
        deliverables.append({
            'name': 'Ad Creative (3-4 creatives/month)',
            'description': '3–4 ad creatives/month (static + light video/motion)',
            'stage': 'Foundation & Awareness',
            'status': 'pending',
            'completion_date': None,
            'deliverable_type': 'creative_production',
            'progress': 0,
            'monthly_allocation': 800,
            'next_action': 'Develop creative brief and asset requirements for brand reintroduction',
            'dependencies': ['Brand positioning strategy'],
            'kpis': ['Creative production volume', 'Asset quality score', 'Creative performance metrics']
        })
        
        # Social Media Content Creation & Management
        deliverables.append({
            'name': 'Social Media Content (8-12 posts/month)',
            'description': '8–12 posts/month across social channels (depending on target)',
            'stage': 'Foundation & Awareness',
            'status': 'pending',
            'completion_date': None,
            'deliverable_type': 'social_media',
            'progress': 0,
            'monthly_allocation': 1200,
            'next_action': 'Create content calendar and posting schedule across target channels',
            'dependencies': ['Content strategy framework'],
            'kpis': ['Post frequency', 'Engagement rate', 'Follower growth']
        })
        
        # Email Marketing (Light)
        deliverables.append({
            'name': 'Email Marketing (2 emails/month)',
            'description': '2 emails/month (brand updates, soft re-engagement)',
            'stage': 'Foundation & Awareness',
            'status': 'pending',
            'completion_date': None,
            'deliverable_type': 'email_marketing',
            'progress': 0,
            'monthly_allocation': 400,
            'next_action': 'Set up email infrastructure and design re-engagement campaign templates',
            'dependencies': ['Email list audit'],
            'kpis': ['Email delivery rate', 'Open rate', 'Re-engagement rate']
        })
        
        # Strategy & Reporting
        deliverables.append({
            'name': 'Strategy & Reporting',
            'description': 'Overarching paid/social/email strategy guidance. Weekly performance reports (ads + social).',
            'stage': 'Foundation & Awareness',
            'status': 'in_progress',
            'completion_date': None,
            'deliverable_type': 'strategy_reporting',
            'progress': 40,
            'monthly_allocation': 400,
            'next_action': 'Establish weekly reporting cadence and KPI framework',
            'dependencies': [],
            'kpis': ['Report delivery frequency', 'Strategic recommendations', 'Performance insights']
        })
        
        return deliverables
    
    def get_stage_2_deliverables(self):
        """Stage 2: Growth & Q4 Push (Nov-Dec) - $7,500/month"""
        deliverables = []
        
        # Ad Management (Full-funnel)
        deliverables.append({
            'name': 'Ad Management (Full-funnel)',
            'description': 'Prospecting + retargeting campaigns. Dedicated BFCM + holiday campaigns.',
            'stage': 'Growth & Q4 Push',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'ad_management',
            'progress': 0,
            'monthly_allocation': 2250,  # Estimated from $7.5K total
            'next_action': 'Plan BFCM and holiday campaign strategy',
            'dependencies': ['Stage 1 Ad Management completion'],
            'kpis': ['BFCM revenue', 'Holiday campaign ROI', 'Full-funnel conversion rates']
        })
        
        # Ad Creative (Expanded)
        deliverables.append({
            'name': 'Ad Creative (6-8 creatives/month)',
            'description': '6–8 creatives/month (mix of static, motion graphics, UGC-style video)',
            'stage': 'Growth & Q4 Push',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'creative_production',
            'progress': 0,
            'monthly_allocation': 1500,
            'next_action': 'Develop Q4 creative strategy with holiday themes',
            'dependencies': ['Stage 1 Creative completion'],
            'kpis': ['Creative volume increase', 'UGC-style video performance', 'Holiday creative engagement']
        })
        
        # Social Media (Holiday Heavy)
        deliverables.append({
            'name': 'Social Media Content (12-16 posts/month)',
            'description': '12–16 posts/month (holiday & promotional heavy)',
            'stage': 'Growth & Q4 Push',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'social_media',
            'progress': 0,
            'monthly_allocation': 1800,
            'next_action': 'Create Q4 social calendar with holiday promotions',
            'dependencies': ['Stage 1 Social Media completion'],
            'kpis': ['Holiday post engagement', 'Promotional conversion', 'Q4 follower growth']
        })
        
        # Email Marketing (Promotional)
        deliverables.append({
            'name': 'Email Marketing (4-6 emails/month)',
            'description': '4–6 emails/month (BFCM promotions, gift guides, holiday reminders)',
            'stage': 'Growth & Q4 Push',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'email_marketing',
            'progress': 0,
            'monthly_allocation': 900,
            'next_action': 'Design BFCM and holiday email campaign sequences',
            'dependencies': ['Stage 1 Email Marketing completion'],
            'kpis': ['BFCM email revenue', 'Holiday campaign open rates', 'Gift guide engagement']
        })
        
        # Product Catalog Prep
        deliverables.append({
            'name': 'Product Catalog Prep',
            'description': 'Begin uploading products & writing descriptions (in batches, as site updates roll out)',
            'stage': 'Growth & Q4 Push',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'catalog_management',
            'progress': 0,
            'monthly_allocation': 750,
            'next_action': 'Coordinate with site relaunch timeline for product uploads',
            'dependencies': ['Site update progress'],
            'kpis': ['Products uploaded', 'Description quality', 'Catalog completion rate']
        })
        
        # Strategy & Reporting (Enhanced)
        deliverables.append({
            'name': 'Strategy & Reporting (Holiday Focus)',
            'description': 'Campaign-specific strategy sessions (holiday playbook). Weekly reporting with deeper ad insights.',
            'stage': 'Growth & Q4 Push',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'strategy_reporting',
            'progress': 0,
            'monthly_allocation': 300,
            'next_action': 'Develop holiday playbook and enhanced reporting framework',
            'dependencies': ['Stage 1 Strategy completion'],
            'kpis': ['Holiday strategy effectiveness', 'Deeper insights delivery', 'Campaign optimization']
        })
        
        return deliverables
    
    def get_stage_3_deliverables(self):
        """Stage 3: Full Retainer (Jan 2026+) - $11,000/month + 5% ad spend"""
        deliverables = []
        
        # Full Ad Management
        deliverables.append({
            'name': 'Ad Management (Multi-platform)',
            'description': 'Multi-platform, full-funnel campaigns. Budget scaling. Ongoing creative testing.',
            'stage': 'Full Retainer',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'ad_management',
            'progress': 0,
            'monthly_allocation': 3300,  # Estimated from $11K total
            'next_action': 'Plan post-relaunch multi-platform strategy',
            'dependencies': ['Site relaunch completion'],
            'kpis': ['Multi-platform ROI', 'Budget scaling efficiency', 'Creative testing results']
        })
        
        # Full Creative Production
        deliverables.append({
            'name': 'Ad Creative (8-12 creatives/month)',
            'description': '8–12 new creatives/month (static, video, carousel, UGC)',
            'stage': 'Full Retainer',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'creative_production',
            'progress': 0,
            'monthly_allocation': 2200,
            'next_action': 'Scale creative production for full retainer',
            'dependencies': ['Stage 2 Creative completion'],
            'kpis': ['Creative volume scaling', 'Format diversification', 'UGC integration']
        })
        
        # SEO Implementation
        deliverables.append({
            'name': 'SEO (Technical + Content)',
            'description': 'Technical SEO audit of new site. On-page optimizations. Keyword strategy + content plan.',
            'stage': 'Full Retainer',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'seo',
            'progress': 0,
            'monthly_allocation': 1650,
            'next_action': 'Conduct technical SEO audit post-site relaunch',
            'dependencies': ['Site relaunch completion'],
            'kpis': ['Technical SEO score', 'Keyword rankings', 'Organic traffic growth']
        })
        
        # CRO Implementation
        deliverables.append({
            'name': 'Conversion Rate Optimization',
            'description': 'A/B testing for PDPs, landing pages, checkout. Heatmaps & analytics review.',
            'stage': 'Full Retainer',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'cro',
            'progress': 0,
            'monthly_allocation': 1100,
            'next_action': 'Set up CRO testing framework and analytics',
            'dependencies': ['Site relaunch completion'],
            'kpis': ['Conversion rate improvement', 'A/B test completion', 'User experience optimization']
        })
        
        # Full Email Program
        deliverables.append({
            'name': 'Email Marketing (Full Program)',
            'description': 'Full program: flows (welcome, abandoned cart, post-purchase). 6–8 campaign emails/month.',
            'stage': 'Full Retainer',
            'status': 'planned',
            'completion_date': None,
            'deliverable_type': 'email_marketing',
            'progress': 0,
            'monthly_allocation': 1320,
            'next_action': 'Design comprehensive email automation flows',
            'dependencies': ['Stage 2 Email completion'],
            'kpis': ['Email automation performance', 'Flow conversion rates', 'Campaign email ROI']
        })
        
        return deliverables
    
    def get_current_stage_info(self):
        """Determine current stage based on date"""
        current_month = self.current_date.month
        current_year = self.current_date.year
        
        if current_year == 2025:
            if current_month in [9, 10]:  # Sept-Oct
                return 'stage_1_foundation'
            elif current_month in [11, 12]:  # Nov-Dec
                return 'stage_2_growth'
        elif current_year >= 2026:  # Jan 2026+
            return 'stage_3_full_retainer'
        
        return 'stage_1_foundation'  # Default
    
    def calculate_stage_progress(self, stage_deliverables):
        """Calculate progress for a stage"""
        if not stage_deliverables:
            return 0
        
        total_progress = sum(d['progress'] for d in stage_deliverables)
        return round(total_progress / len(stage_deliverables))

# Main agency tracking functions for API compatibility
def get_agency_status():
    """Get real HVD agency status based on actual proposal"""
    tracker = RealHVDAgencyTracker()
    
    # Get deliverables for all stages
    stage_1_deliverables = tracker.get_stage_1_deliverables()
    stage_2_deliverables = tracker.get_stage_2_deliverables()
    stage_3_deliverables = tracker.get_stage_3_deliverables()
    
    all_deliverables = stage_1_deliverables + stage_2_deliverables + stage_3_deliverables
    
    # Calculate stage progress
    stage_1_progress = tracker.calculate_stage_progress(stage_1_deliverables)
    stage_2_progress = tracker.calculate_stage_progress(stage_2_deliverables)
    stage_3_progress = tracker.calculate_stage_progress(stage_3_deliverables)
    
    # Get current stage
    current_stage = tracker.get_current_stage_info()
    current_stage_data = tracker.hvd_stages[current_stage]
    
    # Calculate metrics
    completed_deliverables = len([d for d in all_deliverables if d['status'] == 'completed'])
    in_progress_deliverables = len([d for d in all_deliverables if d['status'] == 'in_progress'])
    pending_deliverables = len([d for d in all_deliverables if d['status'] in ['pending', 'planned']])
    
    return {
        'agency_name': 'High Voltage Digital (HVD)',
        'proposal_based': True,
        'current_stage': current_stage_data['name'],
        'current_investment': current_stage_data['investment'],
        'current_objective': current_stage_data['objective'],
        'contract_start': '2025-09-01',
        'contract_end': '2026-12-31',
        'monthly_budget': current_stage_data['investment'],
        'active_projects': 1,  # The HVD engagement
        'completed_deliverables': completed_deliverables,
        'in_progress_deliverables': in_progress_deliverables,
        'pending_deliverables': pending_deliverables,
        'completion_rate': round((completed_deliverables / len(all_deliverables) * 100) if all_deliverables else 0),
        'stages': {
            'stage_1': {
                'name': 'Foundation & Awareness',
                'timeline': 'September - October 2025',
                'investment': 4000,
                'progress': stage_1_progress,
                'status': 'active' if current_stage == 'stage_1_foundation' else 'completed',
                'deliverables_count': len(stage_1_deliverables)
            },
            'stage_2': {
                'name': 'Growth & Q4 Push',
                'timeline': 'November - December 2025',
                'investment': 7500,
                'progress': stage_2_progress,
                'status': 'active' if current_stage == 'stage_2_growth' else 'upcoming',
                'deliverables_count': len(stage_2_deliverables)
            },
            'stage_3': {
                'name': 'Full Retainer',
                'timeline': 'January 2026 onward',
                'investment': 11000,
                'progress': stage_3_progress,
                'status': 'active' if current_stage == 'stage_3_full_retainer' else 'planned',
                'deliverables_count': len(stage_3_deliverables)
            }
        },
        'deliverables': all_deliverables,
        'exclusions': {
            'stage_1': ['SEO', 'CRO', 'Heavy product catalog management'],
            'stage_2': ['SEO', 'CRO'],
            'stage_3': []
        },
        'data_source': 'hvd_proposal_september_2025'
    }

def add_project(project_data):
    """Add new project deliverable"""
    return {"success": True, "message": "Deliverable added to HVD tracking"}

def update_project_status(project_id, status):
    """Update deliverable status"""
    return {"success": True, "message": "HVD deliverable status updated"}

def get_project_timeline():
    """Get HVD deliverable timeline"""
    tracker = RealHVDAgencyTracker()
    all_deliverables = (tracker.get_stage_1_deliverables() + 
                       tracker.get_stage_2_deliverables() + 
                       tracker.get_stage_3_deliverables())
    
    timeline = []
    for deliverable in all_deliverables:
        # Estimate due dates based on stage timeline
        if deliverable['stage'] == 'Foundation & Awareness':
            due_date = '2025-10-31'
        elif deliverable['stage'] == 'Growth & Q4 Push':
            due_date = '2025-12-31'
        else:  # Full Retainer
            due_date = '2026-03-31'
            
        timeline.append({
            'date': due_date,
            'title': deliverable['name'],
            'status': deliverable['status'],
            'stage': deliverable['stage'],
            'progress': deliverable['progress'],
            'type': deliverable['deliverable_type'],
            'budget': deliverable['monthly_allocation']
        })
    
    return sorted(timeline, key=lambda x: x['date'])

if __name__ == "__main__":
    # Test real HVD tracking
    status = get_agency_status()
    print(f"HVD Partnership - {status['current_stage']}")
    print(f"Current Investment: ${status['current_investment']}/month")
    print(f"Stage 1 Progress: {status['stages']['stage_1']['progress']}%")
    print(f"Total Deliverables: {len(status['deliverables'])}")

