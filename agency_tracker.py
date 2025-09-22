import os
import json
from datetime import datetime, timedelta

def get_agency_status():
    """Get comprehensive agency status for High Voltage Digital"""
    return {
        'agency_name': 'High Voltage Digital',
        'current_phase': 'Phase 1',
        'phase_status': 'active',
        'monthly_budget': 4000,
        'budget_utilized': 2800,
        'budget_remaining': 1200,
        'utilization_rate': 70,
        'contract_start': '2025-09-01',
        'contract_end': '2025-12-31',
        'performance_metrics': {
            'on_time_delivery': 100,
            'quality_score': 95,
            'client_satisfaction': 92,
            'response_time': '< 4 hours'
        },
        'active_projects': 4,
        'completed_projects': 2,
        'upcoming_milestones': [
            {
                'milestone': 'Q4 Strategic Planning',
                'due_date': '2025-10-15',
                'status': 'scheduled'
            },
            {
                'milestone': 'Cultural Intelligence Report',
                'due_date': '2025-09-30',
                'status': 'in_progress'
            }
        ],
        'next_phase': {
            'phase': 'Phase 2',
            'start_date': '2025-11-01',
            'budget': 6000,
            'new_services': ['Video Production', 'Influencer Outreach', 'Community Management']
        }
    }

def update_project_status(project_id, status, notes=None):
    """Update project status for tracking"""
    
    # Simulate project status update
    project_updates = {
        'project_id': project_id,
        'status': status,
        'updated_at': datetime.now().isoformat(),
        'notes': notes or f'Status updated to {status}',
        'updated_by': 'system'
    }
    
    return {
        'success': True,
        'message': f'Project {project_id} status updated to {status}',
        'update_details': project_updates
    }

def get_deliverables():
    """Get current deliverables status - REQUIRED BY APP.PY"""
    
    deliverables = [
        {
            'id': 'hvd_001',
            'title': 'Hispanic Heritage Campaign',
            'category': 'cultural_marketing',
            'status': 'completed',
            'progress': 100,
            'due_date': '2025-09-15',
            'completed_date': '2025-09-14',
            'budget_allocated': 1500,
            'budget_used': 1450,
            'priority': 'high',
            'deliverable_items': [
                'Instagram Story Series (10 posts)',
                'TikTok Cultural Content (5 videos)',
                'Community Engagement Strategy',
                'Performance Analytics Report'
            ],
            'performance_metrics': {
                'engagement_rate': 8.5,
                'reach': 45000,
                'impressions': 120000,
                'cultural_relevance_score': 92
            },
            'assets_created': [
                'sept_15_hispanic_heritage_launch(3).png',
                'sept_16_cultural_fusion(3).png',
                'real_instagram_story_rebel_rooftop(1).png'
            ]
        },
        {
            'id': 'hvd_002',
            'title': 'Hip-Hop Anniversary Tribute',
            'category': 'cultural_content',
            'status': 'completed',
            'progress': 100,
            'due_date': '2025-09-19',
            'completed_date': '2025-09-18',
            'budget_allocated': 800,
            'budget_used': 750,
            'priority': 'high',
            'deliverable_items': [
                'Hip-Hop Heritage Story Series',
                'Castle & Medusa Brand Integration',
                'Community Tribute Content',
                'Engagement Analytics'
            ],
            'performance_metrics': {
                'engagement_rate': 12.3,
                'reach': 62000,
                'impressions': 180000,
                'cultural_authenticity_score': 95
            },
            'assets_created': [
                'sept_19_hiphop_anniversary.png',
                'castle_story.png',
                'medusa_story(1).png'
            ]
        },
        {
            'id': 'hvd_003',
            'title': 'Q4 Strategic Planning',
            'category': 'strategic_planning',
            'status': 'in_progress',
            'progress': 60,
            'due_date': '2025-10-15',
            'budget_allocated': 500,
            'budget_used': 200,
            'priority': 'medium',
            'deliverable_items': [
                'Q4 Content Calendar',
                'Budget Allocation Strategy',
                'Cultural Moment Mapping',
                'Competitive Analysis Update'
            ],
            'next_milestones': [
                'Draft calendar review (Oct 1)',
                'Budget approval (Oct 8)',
                'Final strategy presentation (Oct 15)'
            ]
        },
        {
            'id': 'hvd_004',
            'title': 'Cultural Intelligence Report',
            'category': 'intelligence',
            'status': 'in_progress',
            'progress': 75,
            'due_date': '2025-09-30',
            'budget_allocated': 300,
            'budget_used': 150,
            'priority': 'high',
            'deliverable_items': [
                'Competitive Landscape Analysis',
                'Cultural Trend Identification',
                'Hashtag Performance Review',
                'Actionable Recommendations'
            ],
            'current_focus': 'Finalizing trend analysis and recommendations'
        }
    ]
    
    # Calculate summary statistics
    total_deliverables = len(deliverables)
    completed = len([d for d in deliverables if d['status'] == 'completed'])
    in_progress = len([d for d in deliverables if d['status'] == 'in_progress'])
    total_budget = sum(d['budget_allocated'] for d in deliverables)
    total_used = sum(d.get('budget_used', 0) for d in deliverables)
    
    return {
        'deliverables': deliverables,
        'summary': {
            'total_deliverables': total_deliverables,
            'completed': completed,
            'in_progress': in_progress,
            'completion_rate': round((completed / total_deliverables) * 100, 1),
            'total_budget_allocated': total_budget,
            'total_budget_used': total_used,
            'budget_utilization': round((total_used / total_budget) * 100, 1)
        },
        'upcoming_deadlines': [
            d for d in deliverables 
            if d['status'] == 'in_progress' and 'due_date' in d
        ]
    }

def track_budget_usage():
    """Track budget usage across all projects - REQUIRED BY APP.PY"""
    
    # Get current deliverables for budget tracking
    deliverables_data = get_deliverables()
    agency_status = get_agency_status()
    
    budget_breakdown = {
        'monthly_budget': agency_status['monthly_budget'],
        'total_allocated': deliverables_data['summary']['total_budget_allocated'],
        'total_used': deliverables_data['summary']['total_budget_used'],
        'remaining_budget': agency_status['budget_remaining'],
        'utilization_rate': deliverables_data['summary']['budget_utilization'],
        'budget_efficiency': 'High' if deliverables_data['summary']['budget_utilization'] > 80 else 'Medium'
    }
    
    # Category breakdown
    category_spending = {}
    for deliverable in deliverables_data['deliverables']:
        category = deliverable['category']
        if category not in category_spending:
            category_spending[category] = {
                'allocated': 0,
                'used': 0,
                'projects': 0
            }
        category_spending[category]['allocated'] += deliverable['budget_allocated']
        category_spending[category]['used'] += deliverable.get('budget_used', 0)
        category_spending[category]['projects'] += 1
    
    # Monthly projections
    current_month_spending = deliverables_data['summary']['total_budget_used']
    projected_monthly = current_month_spending * 1.2  # 20% buffer for remaining projects
    
    budget_tracking = {
        'current_period': {
            'period': 'September 2025',
            'budget_allocated': agency_status['monthly_budget'],
            'budget_used': current_month_spending,
            'budget_remaining': agency_status['budget_remaining'],
            'utilization_percentage': round((current_month_spending / agency_status['monthly_budget']) * 100, 1)
        },
        'category_breakdown': category_spending,
        'projections': {
            'projected_monthly_total': projected_monthly,
            'projected_overage': max(0, projected_monthly - agency_status['monthly_budget']),
            'budget_status': 'On Track' if projected_monthly <= agency_status['monthly_budget'] else 'Over Budget'
        },
        'efficiency_metrics': {
            'cost_per_deliverable': round(current_month_spending / len(deliverables_data['deliverables']), 2),
            'roi_estimate': 'High' if deliverables_data['summary']['completion_rate'] > 80 else 'Medium',
            'budget_variance': round(((current_month_spending - (agency_status['monthly_budget'] * 0.7)) / (agency_status['monthly_budget'] * 0.7)) * 100, 1)
        }
    }
    
    return budget_tracking

def get_project_timeline():
    """Get project timeline and milestones"""
    
    deliverables = get_deliverables()['deliverables']
    
    timeline_events = []
    
    for deliverable in deliverables:
        if deliverable['status'] == 'completed':
            timeline_events.append({
                'date': deliverable.get('completed_date', deliverable['due_date']),
                'event': f"Completed: {deliverable['title']}",
                'type': 'completion',
                'status': 'completed'
            })
        elif deliverable['status'] == 'in_progress':
            timeline_events.append({
                'date': deliverable['due_date'],
                'event': f"Due: {deliverable['title']}",
                'type': 'deadline',
                'status': 'upcoming'
            })
    
    # Sort by date
    timeline_events.sort(key=lambda x: x['date'])
    
    return {
        'timeline': timeline_events,
        'next_milestone': timeline_events[0] if timeline_events else None,
        'upcoming_deadlines': [e for e in timeline_events if e['status'] == 'upcoming'][:3]
    }

def calculate_agency_roi():
    """Calculate return on investment for agency services"""
    
    deliverables = get_deliverables()
    budget_data = track_budget_usage()
    
    # Calculate performance metrics
    completed_deliverables = [d for d in deliverables['deliverables'] if d['status'] == 'completed']
    
    total_reach = sum(d.get('performance_metrics', {}).get('reach', 0) for d in completed_deliverables)
    total_impressions = sum(d.get('performance_metrics', {}).get('impressions', 0) for d in completed_deliverables)
    avg_engagement = sum(d.get('performance_metrics', {}).get('engagement_rate', 0) for d in completed_deliverables) / len(completed_deliverables) if completed_deliverables else 0
    
    # Calculate ROI metrics
    cost_per_impression = budget_data['current_period']['budget_used'] / total_impressions if total_impressions > 0 else 0
    cost_per_reach = budget_data['current_period']['budget_used'] / total_reach if total_reach > 0 else 0
    
    roi_analysis = {
        'financial_metrics': {
            'total_investment': budget_data['current_period']['budget_used'],
            'cost_per_impression': round(cost_per_impression, 4),
            'cost_per_reach': round(cost_per_reach, 4),
            'budget_efficiency': budget_data['efficiency_metrics']['roi_estimate']
        },
        'performance_metrics': {
            'total_reach': total_reach,
            'total_impressions': total_impressions,
            'average_engagement_rate': round(avg_engagement, 2),
            'completed_projects': len(completed_deliverables),
            'on_time_delivery_rate': 100  # Based on current performance
        },
        'value_assessment': {
            'roi_rating': 'High' if avg_engagement > 8 and total_reach > 100000 else 'Medium',
            'strategic_value': 'High',  # Cultural intelligence and brand positioning
            'recommendation': 'Continue partnership' if avg_engagement > 6 else 'Review strategy'
        }
    }
    
    return roi_analysis

def get_deliverable_status(deliverable_id=None):
    """Get status of specific deliverable or all deliverables"""
    
    deliverables_data = get_deliverables()
    
    if deliverable_id:
        # Return specific deliverable
        for deliverable in deliverables_data['deliverables']:
            if deliverable['id'] == deliverable_id:
                return deliverable
        return None
    
    # Return all deliverables with status summary
    return deliverables_data

def generate_agency_comparison():
    """Generate comparison with other potential agencies"""
    
    hvd_performance = get_agency_status()
    roi_data = calculate_agency_roi()
    
    comparison_data = {
        'current_agency': {
            'name': 'High Voltage Digital',
            'monthly_cost': hvd_performance['monthly_budget'],
            'performance_score': hvd_performance['performance_metrics']['quality_score'],
            'on_time_delivery': hvd_performance['performance_metrics']['on_time_delivery'],
            'client_satisfaction': hvd_performance['performance_metrics']['client_satisfaction'],
            'specialization': 'Streetwear & Cultural Marketing',
            'roi_rating': roi_data['value_assessment']['roi_rating']
        },
        'market_alternatives': [
            {
                'name': 'Urban Culture Agency',
                'estimated_monthly_cost': 5500,
                'estimated_performance_score': 88,
                'specialization': 'Urban Fashion Marketing',
                'pros': ['Larger team', 'More resources'],
                'cons': ['Higher cost', 'Less cultural authenticity']
            },
            {
                'name': 'Street Brand Collective',
                'estimated_monthly_cost': 3200,
                'estimated_performance_score': 82,
                'specialization': 'Street Fashion Content',
                'pros': ['Lower cost', 'Fast turnaround'],
                'cons': ['Less strategic depth', 'Limited cultural intelligence']
            }
        ],
        'recommendation': {
            'current_agency_ranking': 1,
            'key_advantages': [
                'Superior cultural intelligence',
                'Authentic streetwear understanding',
                'Excellent performance metrics',
                'Cost-effective pricing'
            ],
            'areas_for_improvement': [
                'Expand video production capabilities',
                'Increase social media posting frequency'
            ],
            'overall_assessment': 'High Voltage Digital provides excellent value with strong cultural authenticity and performance metrics.'
        }
    }
    
    return comparison_data

def calculate_total_spend():
    """Calculate total spending across all agency services"""
    
    budget_tracking = track_budget_usage()
    deliverables = get_deliverables()
    
    total_spend_analysis = {
        'current_month': {
            'total_spent': budget_tracking['current_period']['budget_used'],
            'budget_allocated': budget_tracking['current_period']['budget_allocated'],
            'variance': budget_tracking['current_period']['budget_used'] - budget_tracking['current_period']['budget_allocated'] * 0.7,
            'utilization_rate': budget_tracking['current_period']['utilization_percentage']
        },
        'project_breakdown': [
            {
                'project': d['title'],
                'allocated': d['budget_allocated'],
                'spent': d.get('budget_used', 0),
                'remaining': d['budget_allocated'] - d.get('budget_used', 0),
                'status': d['status']
            }
            for d in deliverables['deliverables']
        ],
        'quarterly_projection': {
            'q4_estimated_total': budget_tracking['current_period']['budget_used'] * 3,  # 3 months
            'monthly_average': budget_tracking['current_period']['budget_used'],
            'projected_annual': budget_tracking['current_period']['budget_used'] * 12
        },
        'cost_efficiency': {
            'cost_per_deliverable': budget_tracking['efficiency_metrics']['cost_per_deliverable'],
            'roi_assessment': budget_tracking['efficiency_metrics']['roi_estimate'],
            'budget_variance_percentage': budget_tracking['efficiency_metrics']['budget_variance']
        }
    }
    
    return total_spend_analysis

def get_agency_performance_metrics():
    """Get comprehensive agency performance metrics"""
    
    agency_status = get_agency_status()
    deliverables = get_deliverables()
    roi_data = calculate_agency_roi()
    
    performance_metrics = {
        'operational_metrics': {
            'on_time_delivery_rate': agency_status['performance_metrics']['on_time_delivery'],
            'quality_score': agency_status['performance_metrics']['quality_score'],
            'client_satisfaction': agency_status['performance_metrics']['client_satisfaction'],
            'response_time': agency_status['performance_metrics']['response_time'],
            'project_completion_rate': deliverables['summary']['completion_rate']
        },
        'financial_metrics': {
            'budget_utilization': deliverables['summary']['budget_utilization'],
            'cost_efficiency': roi_data['financial_metrics']['budget_efficiency'],
            'roi_rating': roi_data['value_assessment']['roi_rating'],
            'cost_per_deliverable': roi_data['financial_metrics']['cost_per_impression']
        },
        'strategic_metrics': {
            'cultural_authenticity_score': 94,  # Based on completed cultural campaigns
            'brand_alignment_score': 92,
            'innovation_score': 88,
            'market_positioning_improvement': 'Significant'
        },
        'engagement_metrics': {
            'average_engagement_rate': roi_data['performance_metrics']['average_engagement_rate'],
            'total_reach_achieved': roi_data['performance_metrics']['total_reach'],
            'total_impressions': roi_data['performance_metrics']['total_impressions'],
            'content_performance': 'Above Average'
        }
    }
    
    return performance_metrics
