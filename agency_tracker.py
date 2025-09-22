import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict

def get_agency_status():
    """Get comprehensive agency status and project tracking"""
    
    # High Voltage Digital - Primary Agency
    hvd_status = {
        'agency_name': 'High Voltage Digital',
        'contract_status': 'active',
        'current_phase': 'Phase 1',
        'monthly_budget': 4000,
        'budget_utilized': 2800,
        'budget_remaining': 1200,
        'start_date': '2025-09-01',
        'current_deliverables': [
            {
                'id': 'hvd_001',
                'title': 'Hispanic Heritage Month Campaign',
                'status': 'in_progress',
                'due_date': '2025-10-15',
                'completion': 75,
                'budget_allocated': 1500,
                'priority': 'high'
            },
            {
                'id': 'hvd_002', 
                'title': 'Hip-Hop Anniversary Content Series',
                'status': 'completed',
                'due_date': '2025-09-19',
                'completion': 100,
                'budget_allocated': 800,
                'priority': 'high'
            },
            {
                'id': 'hvd_003',
                'title': 'Q4 Strategic Planning',
                'status': 'planned',
                'due_date': '2025-10-30',
                'completion': 0,
                'budget_allocated': 500,
                'priority': 'medium'
            },
            {
                'id': 'hvd_004',
                'title': 'Cultural Intelligence Report',
                'status': 'in_progress',
                'due_date': '2025-09-30',
                'completion': 60,
                'budget_allocated': 300,
                'priority': 'medium'
            }
        ],
        'performance_metrics': {
            'on_time_delivery': 100,  # Percentage
            'quality_score': 95,      # Out of 100
            'budget_efficiency': 85,  # Percentage
            'client_satisfaction': 92 # Out of 100
        },
        'next_phase_requirements': {
            'phase_2_budget': 6000,
            'additional_services': ['Video Production', 'Influencer Outreach', 'Community Management'],
            'timeline': '2025-11-01 to 2026-01-31',
            'key_objectives': [
                'Scale cultural campaigns',
                'Expand community engagement',
                'Launch video content series'
            ]
        },
        'contact_info': {
            'primary_contact': 'Sarah Martinez',
            'email': 'sarah@highvoltagedigital.com',
            'phone': '+1-555-0123',
            'project_manager': 'Alex Chen',
            'creative_director': 'Maria Rodriguez'
        }
    }
    
    # Additional agencies for comparison
    other_agencies = [
        {
            'agency_name': 'Street Culture Media',
            'contract_status': 'proposal_stage',
            'specialization': 'Streetwear Content Creation',
            'proposed_budget': 3500,
            'proposal_date': '2025-09-15'
        },
        {
            'agency_name': 'Urban Influence Co.',
            'contract_status': 'past_client',
            'last_project': 'Summer 2025 Campaign',
            'performance_rating': 78,
            'end_date': '2025-08-31'
        }
    ]
    
    return {
        'primary_agency': hvd_status,
        'other_agencies': other_agencies,
        'agency_comparison': generate_agency_comparison(),
        'total_agency_spend': calculate_total_spend(),
        'generated_at': datetime.now().isoformat()
    }

def update_project_status(project_id, status, completion=None, notes=None):
    """Update project status and completion"""
    try:
        update_data = {
            'project_id': project_id,
            'status': status,
            'updated_at': datetime.now().isoformat(),
            'updated_by': 'system'
        }
        
        if completion is not None:
            update_data['completion'] = min(100, max(0, completion))
        
        if notes:
            update_data['notes'] = notes
        
        # In a real implementation, this would update a database
        return {'success': True, 'update': update_data}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_project_timeline(agency_name='High Voltage Digital'):
    """Get project timeline and milestones"""
    
    if agency_name == 'High Voltage Digital':
        timeline = [
            {
                'date': '2025-09-01',
                'milestone': 'Contract Signed & Project Kickoff',
                'status': 'completed',
                'deliverables': ['Strategy Document', 'Creative Brief', 'Timeline']
            },
            {
                'date': '2025-09-15',
                'milestone': 'Hispanic Heritage Campaign Launch',
                'status': 'completed',
                'deliverables': ['Campaign Assets', 'Social Content', 'Community Outreach']
            },
            {
                'date': '2025-09-19',
                'milestone': 'Hip-Hop Anniversary Content',
                'status': 'completed',
                'deliverables': ['Video Content', 'Social Posts', 'Community Engagement']
            },
            {
                'date': '2025-09-30',
                'milestone': 'Cultural Intelligence Report',
                'status': 'in_progress',
                'deliverables': ['Data Analysis', 'Trend Report', 'Recommendations']
            },
            {
                'date': '2025-10-15',
                'milestone': 'Hispanic Heritage Campaign Completion',
                'status': 'planned',
                'deliverables': ['Final Assets', 'Performance Report', 'ROI Analysis']
            },
            {
                'date': '2025-10-30',
                'milestone': 'Q4 Strategic Planning',
                'status': 'planned',
                'deliverables': ['Q4 Strategy', 'Budget Planning', 'Campaign Calendar']
            },
            {
                'date': '2025-11-01',
                'milestone': 'Phase 2 Kickoff',
                'status': 'planned',
                'deliverables': ['Expanded Services', 'Video Production', 'Influencer Program']
            }
        ]
        
        return {
            'agency': agency_name,
            'timeline': timeline,
            'total_milestones': len(timeline),
            'completed_milestones': len([m for m in timeline if m['status'] == 'completed']),
            'progress_percentage': round(len([m for m in timeline if m['status'] == 'completed']) / len(timeline) * 100, 1)
        }
    
    return {'error': 'Agency not found'}

def calculate_agency_roi(agency_name='High Voltage Digital'):
    """Calculate ROI for agency partnerships"""
    
    if agency_name == 'High Voltage Digital':
        # Sample ROI calculation based on performance metrics
        investment = 4000  # Monthly budget
        
        # Estimated returns based on campaign performance
        returns = {
            'brand_awareness_lift': 2500,    # Estimated value
            'engagement_increase': 1800,     # Estimated value
            'lead_generation': 1200,         # Estimated value
            'cultural_authenticity_value': 800,  # Estimated value
            'community_growth': 600          # Estimated value
        }
        
        total_return = sum(returns.values())
        roi_percentage = ((total_return - investment) / investment) * 100
        
        return {
            'agency': agency_name,
            'investment': investment,
            'returns': returns,
            'total_return': total_return,
            'roi_percentage': round(roi_percentage, 2),
            'roi_rating': 'Excellent' if roi_percentage > 100 else 'Good' if roi_percentage > 50 else 'Fair',
            'calculation_date': datetime.now().isoformat()
        }
    
    return {'error': 'Agency not found'}

def get_deliverable_status():
    """Get detailed status of all deliverables"""
    
    deliverables = [
        {
            'id': 'hvd_001',
            'title': 'Hispanic Heritage Month Campaign',
            'agency': 'High Voltage Digital',
            'status': 'in_progress',
            'priority': 'high',
            'due_date': '2025-10-15',
            'completion': 75,
            'budget_allocated': 1500,
            'budget_spent': 1125,
            'tasks': [
                {'task': 'Creative Development', 'status': 'completed', 'completion': 100},
                {'task': 'Asset Creation', 'status': 'completed', 'completion': 100},
                {'task': 'Community Outreach', 'status': 'in_progress', 'completion': 60},
                {'task': 'Performance Tracking', 'status': 'in_progress', 'completion': 40},
                {'task': 'Final Report', 'status': 'planned', 'completion': 0}
            ],
            'cultural_context': 'Celebrating Hispanic Heritage Month (Sept 15 - Oct 15) with authentic community engagement',
            'success_metrics': {
                'target_reach': 100000,
                'current_reach': 75000,
                'target_engagement': '8%',
                'current_engagement': '9.2%',
                'cultural_authenticity_score': 95
            }
        },
        {
            'id': 'hvd_002',
            'title': 'Hip-Hop Anniversary Content Series',
            'agency': 'High Voltage Digital',
            'status': 'completed',
            'priority': 'high',
            'due_date': '2025-09-19',
            'completion': 100,
            'budget_allocated': 800,
            'budget_spent': 750,
            'tasks': [
                {'task': 'Content Strategy', 'status': 'completed', 'completion': 100},
                {'task': 'Video Production', 'status': 'completed', 'completion': 100},
                {'task': 'Social Distribution', 'status': 'completed', 'completion': 100},
                {'task': 'Community Engagement', 'status': 'completed', 'completion': 100},
                {'task': 'Performance Analysis', 'status': 'completed', 'completion': 100}
            ],
            'cultural_context': 'Hip-hop 52nd anniversary celebration with authentic street culture connection',
            'success_metrics': {
                'target_reach': 50000,
                'achieved_reach': 62000,
                'target_engagement': '6%',
                'achieved_engagement': '8.4%',
                'cultural_authenticity_score': 98
            }
        },
        {
            'id': 'hvd_003',
            'title': 'Q4 Strategic Planning',
            'agency': 'High Voltage Digital',
            'status': 'planned',
            'priority': 'medium',
            'due_date': '2025-10-30',
            'completion': 0,
            'budget_allocated': 500,
            'budget_spent': 0,
            'tasks': [
                {'task': 'Market Analysis', 'status': 'planned', 'completion': 0},
                {'task': 'Campaign Planning', 'status': 'planned', 'completion': 0},
                {'task': 'Budget Allocation', 'status': 'planned', 'completion': 0},
                {'task': 'Timeline Development', 'status': 'planned', 'completion': 0},
                {'task': 'Strategy Presentation', 'status': 'planned', 'completion': 0}
            ],
            'cultural_context': 'Q4 holiday season planning with cultural sensitivity and authenticity focus'
        }
    ]
    
    return {
        'deliverables': deliverables,
        'summary': {
            'total_deliverables': len(deliverables),
            'completed': len([d for d in deliverables if d['status'] == 'completed']),
            'in_progress': len([d for d in deliverables if d['status'] == 'in_progress']),
            'planned': len([d for d in deliverables if d['status'] == 'planned']),
            'total_budget': sum(d['budget_allocated'] for d in deliverables),
            'total_spent': sum(d['budget_spent'] for d in deliverables),
            'average_completion': round(sum(d['completion'] for d in deliverables) / len(deliverables), 1)
        }
    }

def generate_agency_comparison():
    """Generate comparison between different agencies"""
    
    agencies = [
        {
            'name': 'High Voltage Digital',
            'status': 'active',
            'performance_score': 95,
            'cost_efficiency': 85,
            'cultural_expertise': 98,
            'delivery_speed': 92,
            'communication': 94,
            'strengths': ['Cultural authenticity', 'Community engagement', 'Strategic thinking'],
            'areas_for_improvement': ['Video production scale', 'Influencer network']
        },
        {
            'name': 'Street Culture Media',
            'status': 'proposal',
            'performance_score': 82,
            'cost_efficiency': 90,
            'cultural_expertise': 85,
            'delivery_speed': 88,
            'communication': 80,
            'strengths': ['Cost-effective', 'Fast delivery', 'Streetwear focus'],
            'areas_for_improvement': ['Cultural depth', 'Strategic planning']
        },
        {
            'name': 'Urban Influence Co.',
            'status': 'past_client',
            'performance_score': 78,
            'cost_efficiency': 75,
            'cultural_expertise': 70,
            'delivery_speed': 85,
            'communication': 82,
            'strengths': ['Quick turnaround', 'Basic social media'],
            'areas_for_improvement': ['Cultural understanding', 'Strategic depth', 'Quality consistency']
        }
    ]
    
    return {
        'agencies': agencies,
        'recommendation': 'High Voltage Digital shows superior cultural expertise and strategic thinking',
        'comparison_date': datetime.now().isoformat()
    }

def calculate_total_spend():
    """Calculate total agency spending and projections"""
    
    current_spend = {
        'high_voltage_digital': {
            'monthly_budget': 4000,
            'months_active': 1,
            'total_spent': 2800,
            'projected_annual': 48000
        }
    }
    
    total_current = sum(agency['total_spent'] for agency in current_spend.values())
    total_projected = sum(agency['projected_annual'] for agency in current_spend.values())
    
    return {
        'current_month_spend': total_current,
        'projected_annual_spend': total_projected,
        'average_monthly_spend': total_projected / 12,
        'spend_breakdown': current_spend,
        'budget_utilization': round((total_current / 4000) * 100, 1),
        'calculation_date': datetime.now().isoformat()
    }

def get_agency_performance_metrics():
    """Get detailed performance metrics for all agencies"""
    
    metrics = {
        'high_voltage_digital': {
            'projects_completed': 2,
            'projects_in_progress': 2,
            'average_completion_time': 18,  # days
            'client_satisfaction': 95,
            'budget_adherence': 95,
            'quality_score': 95,
            'cultural_authenticity': 98,
            'innovation_score': 90,
            'communication_rating': 94,
            'recent_achievements': [
                'Hip-Hop Anniversary campaign exceeded engagement targets by 40%',
                'Hispanic Heritage campaign achieved 95% cultural authenticity score',
                'Delivered all projects on time with 100% quality approval'
            ]
        }
    }
    
    return {
        'metrics': metrics,
        'overall_performance': 'Excellent',
        'key_strengths': ['Cultural expertise', 'Strategic thinking', 'Community engagement'],
        'growth_opportunities': ['Video production scaling', 'Influencer network expansion'],
        'generated_at': datetime.now().isoformat()
    }

def add_project_milestone(project_id, milestone_title, due_date, deliverables=None):
    """Add new milestone to existing project"""
    try:
        milestone = {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'title': milestone_title,
            'due_date': due_date,
            'status': 'planned',
            'deliverables': deliverables or [],
            'created_at': datetime.now().isoformat()
        }
        
        return {'success': True, 'milestone': milestone}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_budget_utilization():
    """Get detailed budget utilization across all agencies"""
    
    budget_data = {
        'total_allocated': 4000,
        'total_spent': 2800,
        'remaining': 1200,
        'utilization_percentage': 70,
        'spending_by_category': {
            'creative_development': 800,
            'content_production': 600,
            'community_outreach': 500,
            'strategy_consulting': 400,
            'performance_tracking': 300,
            'cultural_research': 200
        },
        'monthly_burn_rate': 2800,
        'projected_monthly_spend': 3200,
        'budget_efficiency_score': 85,
        'cost_per_deliverable': 700,
        'roi_metrics': {
            'cost_per_engagement': 0.12,
            'cost_per_reach': 0.04,
            'cultural_impact_per_dollar': 2.4
        }
    }
    
    return budget_data

def generate_agency_report():
    """Generate comprehensive agency performance report"""
    
    report = {
        'report_period': f"{datetime.now().strftime('%Y-%m')}",
        'primary_agency': 'High Voltage Digital',
        'executive_summary': {
            'overall_performance': 'Excellent',
            'key_achievements': [
                'Completed Hip-Hop Anniversary campaign with 40% above target engagement',
                'Hispanic Heritage campaign showing 95% cultural authenticity score',
                'Maintained 100% on-time delivery rate',
                '95% client satisfaction score achieved'
            ],
            'budget_performance': 'On track - 70% utilization with strong ROI',
            'cultural_impact': 'High - authentic community engagement and brand positioning'
        },
        'detailed_metrics': get_agency_performance_metrics(),
        'budget_analysis': get_budget_utilization(),
        'deliverable_status': get_deliverable_status(),
        'recommendations': [
            'Continue partnership with High Voltage Digital for Phase 2',
            'Expand video production capabilities in next phase',
            'Increase community management budget allocation',
            'Develop influencer partnership program'
        ],
        'next_steps': [
            'Finalize Phase 2 contract terms',
            'Plan Q4 cultural campaign calendar',
            'Expand team for increased scope',
            'Implement performance tracking improvements'
        ],
        'generated_at': datetime.now().isoformat()
    }
    
    return report
