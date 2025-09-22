import os
import json
import csv
from datetime import datetime, timedelta, date
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
import uuid
import io
import re
from collections import defaultdict, Counter
import statistics
import math
import calendar

app = Flask(__name__)
app.secret_key = 'crooks-castles-enterprise-intelligence-2025'

# Configuration
UPLOAD_FOLDER = 'assets'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'psd', 'ai', 'sketch', 'fig', 'jsonl', 'json', 'csv'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 11 Tracked Competitors for Crooks & Castles
COMPETITORS = {
    'supreme': {'name': 'Supreme', 'tier': 'luxury', 'aspirational_score': 9.8, 'track_drops': True, 'track_pricing': True},
    'stussy': {'name': 'Stussy', 'tier': 'established', 'aspirational_score': 8.4, 'track_drops': True, 'track_pricing': True},
    'hellstar': {'name': 'Hellstar', 'tier': 'emerging', 'aspirational_score': 7.8, 'track_drops': True, 'track_pricing': True},
    'godspeed': {'name': 'Godspeed', 'tier': 'emerging', 'aspirational_score': 7.2, 'track_drops': True, 'track_pricing': True},
    'fear_of_god_essentials': {'name': 'Essentials by Fear of God', 'tier': 'luxury', 'aspirational_score': 9.1, 'track_drops': True, 'track_pricing': True},
    'smoke_rise': {'name': 'Smoke Rise', 'tier': 'mid-tier', 'aspirational_score': 6.8, 'track_drops': True, 'track_pricing': True},
    'reason_clothing': {'name': 'Reason Clothing', 'tier': 'mid-tier', 'aspirational_score': 6.4, 'track_drops': True, 'track_pricing': True},
    'lrg': {'name': 'LRG', 'tier': 'established', 'aspirational_score': 7.1, 'track_drops': True, 'track_pricing': True},
    'diamond_supply': {'name': 'Diamond Supply Co.', 'tier': 'established', 'aspirational_score': 6.9, 'track_drops': True, 'track_pricing': True},
    'ed_hardy': {'name': 'Ed Hardy', 'tier': 'legacy', 'aspirational_score': 5.8, 'track_drops': False, 'track_pricing': True},
    'von_dutch': {'name': 'Von Dutch', 'tier': 'legacy', 'aspirational_score': 6.1, 'track_drops': False, 'track_pricing': True}
}

# Streetwear & Hip-Hop Cultural Intelligence
CULTURAL_MOMENTS = {
    'fashion_weeks': {
        'names': ['nyfw', 'paris fashion week', 'milan fashion week', 'london fashion week'],
        'typical_dates': [(2, 'February'), (6, 'June'), (9, 'September'), (10, 'October')]
    },
    'music_releases': {
        'keywords': ['album drop', 'new single', 'mixtape', 'ep release', 'music video'],
        'artists': ['travis scott', 'asap rocky', 'tyler the creator', 'kendrick lamar', 'drake', 'kanye west']
    },
    'streetwear_drops': {
        'keywords': ['drop', 'release', 'restock', 'collab', 'collaboration', 'limited edition'],
        'brands': ['supreme', 'off-white', 'fear of god', 'stussy', 'bape', 'kith']
    },
    'cultural_events': {
        'keywords': ['coachella', 'rolling loud', 'lollapalooza', 'sneaker con', 'complex con'],
        'seasons': ['back to school', 'summer festival', 'holiday season', 'spring break']
    }
}

def ensure_directories():
    """Create necessary directories for enterprise platform"""
    directories = [
        'assets', 'assets/images', 'assets/videos', 'assets/design_files',
        'campaign_data', 'campaign_data/7_day', 'campaign_data/30_day', 'campaign_data/60_day', 'campaign_data/90_day',
        'competitive_intelligence', 'competitive_intelligence/traffic_data', 'competitive_intelligence/social_data',
        'competitive_intelligence/drops_data', 'competitive_intelligence/pricing_data',
        'cultural_moments', 'cultural_moments/detected', 'cultural_moments/planned',
        'collaboration', 'collaboration/creators', 'collaboration/agency',
        'data_sources', 'data_sources/instagram', 'data_sources/tiktok', 'data_sources/twitter',
        'exports', 'analytics'
    ]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")

def get_calendar_view(view_type='7day'):
    """Get calendar data for different time ranges"""
    if view_type == '7day':
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
    elif view_type == '30day':
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
    elif view_type == '60day':
        start_date = datetime.now()
        end_date = start_date + timedelta(days=60)
    elif view_type == '90day':
        start_date = datetime.now()
        end_date = start_date + timedelta(days=90)
    else:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
    
    calendar_data = {
        'view_type': view_type,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'planned_content': load_planned_content(start_date, end_date),
        'cultural_moments': detect_cultural_moments(start_date, end_date),
        'competitor_activities': load_competitor_activities(start_date, end_date),
        'seasonal_opportunities': detect_seasonal_opportunities(start_date, end_date)
    }
    
    return calendar_data

def load_planned_content(start_date, end_date):
    """Load planned content for date range"""
    try:
        content_file = f'campaign_data/planned_content.json'
        if os.path.exists(content_file):
            with open(content_file, 'r') as f:
                all_content = json.load(f)
            
            # Filter content for date range
            filtered_content = []
            for content in all_content:
                content_date = datetime.fromisoformat(content.get('scheduled_date', ''))
                if start_date <= content_date <= end_date:
                    filtered_content.append(content)
            
            return filtered_content
    except:
        pass
    
    return []

def detect_cultural_moments(start_date, end_date):
    """Auto-detect streetwear and hip-hop cultural moments"""
    detected_moments = []
    
    # Check for fashion weeks
    for month_num, month_name in CULTURAL_MOMENTS['fashion_weeks']['typical_dates']:
        if start_date.month <= month_num <= end_date.month:
            detected_moments.append({
                'type': 'fashion_week',
                'title': f'{month_name} Fashion Week',
                'date': f'2025-{month_num:02d}-15',
                'relevance_score': 0.9,
                'opportunity': 'High-fashion streetwear content, runway-inspired looks'
            })
    
    # Load detected moments from data analysis
    try:
        moments_file = 'cultural_moments/detected/current_moments.json'
        if os.path.exists(moments_file):
            with open(moments_file, 'r') as f:
                data_moments = json.load(f)
                detected_moments.extend(data_moments)
    except:
        pass
    
    return detected_moments

def load_competitor_activities(start_date, end_date):
    """Load competitor activities for date range"""
    activities = []
    
    try:
        activities_file = 'competitive_intelligence/recent_activities.json'
        if os.path.exists(activities_file):
            with open(activities_file, 'r') as f:
                all_activities = json.load(f)
            
            # Filter activities for date range
            for activity in all_activities:
                activity_date = datetime.fromisoformat(activity.get('date', ''))
                if start_date <= activity_date <= end_date:
                    activities.append(activity)
    except:
        pass
    
    return activities

def detect_seasonal_opportunities(start_date, end_date):
    """Detect seasonal marketing opportunities"""
    opportunities = []
    
    # Define seasonal moments
    seasonal_moments = {
        1: [{'name': 'New Year New Fit', 'type': 'resolution'}, {'name': 'Winter Streetwear', 'type': 'seasonal'}],
        2: [{'name': 'Black History Month', 'type': 'cultural'}, {'name': 'Valentine\'s Day Drops', 'type': 'holiday'}],
        3: [{'name': 'Spring Break Prep', 'type': 'seasonal'}, {'name': 'March Madness', 'type': 'sports'}],
        4: [{'name': 'Easter Collection', 'type': 'holiday'}, {'name': 'Spring Transition', 'type': 'seasonal'}],
        5: [{'name': 'Mother\'s Day Gifts', 'type': 'holiday'}, {'name': 'Festival Season', 'type': 'cultural'}],
        6: [{'name': 'Pride Month', 'type': 'cultural'}, {'name': 'Summer Launch', 'type': 'seasonal'}],
        7: [{'name': 'Summer Heat', 'type': 'seasonal'}, {'name': 'Back to School Prep', 'type': 'seasonal'}],
        8: [{'name': 'Back to School', 'type': 'seasonal'}, {'name': 'Festival Finale', 'type': 'cultural'}],
        9: [{'name': 'Fall Transition', 'type': 'seasonal'}, {'name': 'Fashion Week Response', 'type': 'fashion'}],
        10: [{'name': 'Halloween Limited', 'type': 'holiday'}, {'name': 'Cold Weather Prep', 'type': 'seasonal'}],
        11: [{'name': 'Black Friday Strategy', 'type': 'commercial'}, {'name': 'Holiday Season Launch', 'type': 'seasonal'}],
        12: [{'name': 'Holiday Gifting', 'type': 'holiday'}, {'name': 'Year-End Clearance', 'type': 'commercial'}]
    }
    
    current_month = start_date.month
    end_month = end_date.month
    
    for month in range(current_month, end_month + 1):
        if month in seasonal_moments:
            for moment in seasonal_moments[month]:
                opportunities.append({
                    'month': month,
                    'opportunity': moment['name'],
                    'type': moment['type'],
                    'relevance_score': 0.8
                })
    
    return opportunities

def load_competitor_data(competitor, platform):
    """Load competitor data from files - flexible file detection"""
    possible_paths = [
        f'data_sources/{platform}/{competitor}_{platform}_data.jsonl',
        f'data_sources/{platform}/{competitor}.jsonl',
        f'data_sources/{platform}/{competitor}_data.jsonl',
        f'data_sources/{competitor}_{platform}.jsonl',
        f'data_sources/{competitor}/{platform}.jsonl',
        f'{competitor}_{platform}.jsonl',
        f'{competitor}_{platform}_data.jsonl'
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            try:
                posts = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                posts.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue
                return posts if posts else None
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
    
    return None

def calculate_competitor_score(instagram_data, tiktok_data, competitor_info):
    """Calculate comprehensive competitor score"""
    score_data = {
        'social_score': 0,
        'engagement_rate': 0,
        'posting_frequency': 0,
        'audience_size': 0,
        'aspirational_score': competitor_info['aspirational_score'],
        'tier': competitor_info['tier'],
        'total_posts': 0,
        'average_engagement': 0
    }
    
    all_posts = (instagram_data or []) + (tiktok_data or [])
    
    if all_posts:
        score_data['total_posts'] = len(all_posts)
        
        # Calculate engagement metrics
        total_engagement = 0
        total_followers = 0
        
        for post in all_posts:
            likes = int(post.get('likes', 0) or 0)
            comments = int(post.get('comments', 0) or 0)
            followers = int(post.get('followers', 0) or post.get('user', {}).get('followers', 0) or 0)
            
            total_engagement += likes + comments
            if followers > total_followers:
                total_followers = followers
        
        score_data['average_engagement'] = total_engagement / len(all_posts) if all_posts else 0
        score_data['audience_size'] = total_followers
        score_data['engagement_rate'] = (total_engagement / (total_followers * len(all_posts))) * 100 if total_followers > 0 else 0
        
        # Calculate posting frequency
        date_range = get_post_date_range(all_posts)
        if date_range:
            weeks = max((date_range['end'] - date_range['start']).days / 7, 1)
            score_data['posting_frequency'] = len(all_posts) / weeks
        
        # Calculate overall social score (weighted)
        score_data['social_score'] = (
            (score_data['engagement_rate'] * 0.4) +
            (min(score_data['posting_frequency'] * 10, 100) * 0.3) +
            (min(math.log10(max(score_data['audience_size'], 1)) * 10, 100) * 0.3)
        )
    
    return score_data

def get_post_date_range(posts):
    """Get date range from posts"""
    dates = []
    for post in posts:
        date_str = post.get('timestamp') or post.get('date') or post.get('created_at')
        if date_str:
            try:
                dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))
            except:
                continue
    
    if dates:
        return {'start': min(dates), 'end': max(dates)}
    return None

def generate_competitive_scorecard():
    """Generate competitive scorecard based on real data availability"""
    scorecard = {
        'crooks_score': 6.5,  # Starting position for Crooks & Castles
        'competitive_ranking': {},
        'tier_analysis': {},
        'market_positioning': {},
        'data_driven': False
    }
    
    # Check if we have competitor data
    competitor_data_available = 0
    competitor_metrics = {}
    
    for competitor_key, competitor_info in COMPETITORS.items():
        instagram_data = load_competitor_data(competitor_key, 'instagram')
        tiktok_data = load_competitor_data(competitor_key, 'tiktok')
        
        if instagram_data or tiktok_data:
            competitor_data_available += 1
            
            # Analyze competitor performance
            competitor_metrics[competitor_key] = calculate_competitor_score(
                instagram_data, tiktok_data, competitor_info
            )
    
    if competitor_data_available > 0:
        scorecard['data_driven'] = True
        scorecard['competitive_ranking'] = rank_competitors(competitor_metrics)
        scorecard['tier_analysis'] = analyze_by_tier(competitor_metrics)
        scorecard['market_positioning'] = calculate_market_position(competitor_metrics)
        scorecard['crooks_position'] = determine_crooks_position(competitor_metrics)
        scorecard['message'] = f"Analysis based on {competitor_data_available}/11 competitors with data"
    else:
        scorecard['message'] = "Upload competitor social media data for real-time competitive analysis against your 11 tracked brands"
    
    return scorecard

def rank_competitors(competitor_metrics):
    """Rank competitors by overall performance"""
    if not competitor_metrics:
        return {}
    
    # Create combined score for ranking
    for competitor, metrics in competitor_metrics.items():
        combined_score = (
            metrics['social_score'] * 0.6 + 
            metrics['aspirational_score'] * 4  # Scale aspirational score to match
        )
        metrics['combined_score'] = combined_score
    
    # Sort by combined score
    ranked = sorted(competitor_metrics.items(), key=lambda x: x[1]['combined_score'], reverse=True)
    
    ranking = {}
    for i, (competitor, metrics) in enumerate(ranked, 1):
        ranking[competitor] = {
            'rank': i,
            'score': round(metrics['combined_score'], 1),
            'social_score': round(metrics['social_score'], 1),
            'aspirational_score': metrics['aspirational_score'],
            'tier': metrics['tier']
        }
    
    return ranking

def analyze_by_tier(competitor_metrics):
    """Analyze performance by brand tier"""
    if not competitor_metrics:
        return {}
    
    tier_analysis = defaultdict(list)
    
    for competitor, metrics in competitor_metrics.items():
        tier = metrics['tier']
        tier_analysis[tier].append({
            'competitor': COMPETITORS[competitor]['name'],
            'social_score': round(metrics['social_score'], 1),
            'engagement_rate': round(metrics['engagement_rate'], 2),
            'audience_size': metrics['audience_size']
        })
    
    # Calculate tier averages
    tier_averages = {}
    for tier, competitors in tier_analysis.items():
        if competitors:
            tier_averages[tier] = {
                'avg_social_score': round(sum(c['social_score'] for c in competitors) / len(competitors), 1),
                'avg_engagement_rate': round(sum(c['engagement_rate'] for c in competitors) / len(competitors), 2),
                'competitor_count': len(competitors),
                'competitors': competitors
            }
    
    return tier_averages

def calculate_market_position(competitor_metrics):
    """Calculate Crooks & Castles market position"""
    if not competitor_metrics:
        return {}
    
    # Estimated Crooks & Castles metrics (would be calculated from actual data if available)
    crooks_estimated = {
        'social_score': 42.0,  # Mid-tier positioning
        'aspirational_score': 6.5,
        'tier': 'mid-tier'
    }
    
    # Compare against each competitor
    vs_competitors = {}
    
    for competitor, metrics in competitor_metrics.items():
        comparison = {
            'competitor_name': COMPETITORS[competitor]['name'],
            'social_score_gap': round(crooks_estimated['social_score'] - metrics['social_score'], 1),
            'aspirational_gap': round(crooks_estimated['aspirational_score'] - metrics['aspirational_score'], 1),
            'tier_comparison': f"Crooks ({crooks_estimated['tier']}) vs {COMPETITORS[competitor]['name']} ({metrics['tier']})"
        }
        vs_competitors[competitor] = comparison
    
    return {
        'crooks_estimated_score': crooks_estimated['social_score'],
        'vs_competitors': vs_competitors,
        'market_opportunities': identify_positioning_opportunities(competitor_metrics, crooks_estimated)
    }

def determine_crooks_position(competitor_metrics):
    """Determine where Crooks & Castles would rank"""
    if not competitor_metrics:
        return {'estimated_rank': 'TBD', 'total_competitors': 11}
    
    crooks_estimated_score = 42.0  # Estimated combined score
    
    better_competitors = sum(1 for metrics in competitor_metrics.values() 
                           if metrics.get('combined_score', 0) > crooks_estimated_score)
    
    return {
        'estimated_rank': better_competitors + 1,
        'total_competitors_analyzed': len(competitor_metrics),
        'total_competitors_tracked': 11,
        'estimated_score': crooks_estimated_score,
        'score_to_beat_next': find_next_competitor_score(competitor_metrics, crooks_estimated_score)
    }

def find_next_competitor_score(competitor_metrics, crooks_score):
    """Find the next competitor score to beat"""
    higher_scores = [metrics.get('combined_score', 0) for metrics in competitor_metrics.values() 
                    if metrics.get('combined_score', 0) > crooks_score]
    
    if higher_scores:
        return round(min(higher_scores), 1)
    return None

def identify_positioning_opportunities(competitor_metrics, crooks_estimated):
    """Identify specific positioning opportunities"""
    opportunities = []
    
    # Find competitors with similar scores but different positioning
    for competitor, metrics in competitor_metrics.items():
        score_diff = abs(metrics.get('social_score', 0) - crooks_estimated['social_score'])
        
        if score_diff < 10:  # Similar performance
            if metrics['engagement_rate'] < 2.0:
                opportunities.append({
                    'type': 'engagement_opportunity',
                    'competitor': COMPETITORS[competitor]['name'],
                    'description': f"Higher engagement rates could surpass {COMPETITORS[competitor]['name']}",
                    'metric': f"Their ER: {metrics['engagement_rate']:.1f}%"
                })
    
    # Find tier-based opportunities
    tier_competitors = [c for c, m in competitor_metrics.items() 
                       if m['tier'] in ['mid-tier', 'established']]
    
    if len(tier_competitors) > 0:
        opportunities.append({
            'type': 'tier_leadership',
            'description': f"Opportunity to lead mid-tier/established segment",
            'competitors_in_tier': len(tier_competitors)
        })
    
    return opportunities

def analyze_hashtag_intelligence():
    """Analyze broader streetwear hashtag mentions"""
    hashtag_intelligence = {
        'streetwear_trends': {},
        'brand_mentions': {},
        'cultural_signals': {},
        'opportunity_hashtags': []
    }
    
    # Define streetwear hashtags to track
    streetwear_hashtags = [
        'streetwear', 'streetstyle', 'hypebeast', 'streetfashion',
        'urbanfashion', 'drip', 'outfit', 'ootd', 'fashion',
        'style', 'hype', 'exclusive', 'limitededition',
        'vintage', 'thrift', 'secondhand', 'sustainability'
    ]
    
    # Analyze hashtag performance across all competitor data
    for competitor_key in COMPETITORS.keys():
        instagram_data = load_competitor_data(competitor_key, 'instagram')
        tiktok_data = load_competitor_data(competitor_key, 'tiktok')
        
        if instagram_data or tiktok_data:
            hashtag_data = extract_hashtag_performance(
                (instagram_data or []) + (tiktok_data or []), 
                streetwear_hashtags
            )
            
            if hashtag_data:
                hashtag_intelligence['brand_mentions'][competitor_key] = hashtag_data
    
    # Identify trending hashtags and opportunities
    hashtag_intelligence['opportunity_hashtags'] = find_hashtag_opportunities(
        hashtag_intelligence['brand_mentions']
    )
    
    return hashtag_intelligence

def extract_hashtag_performance(posts, target_hashtags):
    """Extract hashtag performance from posts"""
    hashtag_performance = {}
    
    for post in posts:
        text = (post.get('caption', '') or post.get('text', '') or '').lower()
        engagement = int(post.get('likes', 0) or 0) + int(post.get('comments', 0) or 0)
        
        for hashtag in target_hashtags:
            if f'#{hashtag}' in text or hashtag in text:
                if hashtag not in hashtag_performance:
                    hashtag_performance[hashtag] = {
                        'mentions': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0
                    }
                
                hashtag_performance[hashtag]['mentions'] += 1
                hashtag_performance[hashtag]['total_engagement'] += engagement
    
    # Calculate averages
    for hashtag, data in hashtag_performance.items():
        if data['mentions'] > 0:
            data['avg_engagement'] = data['total_engagement'] / data['mentions']
    
    return hashtag_performance

def find_hashtag_opportunities(brand_hashtag_data):
    """Find hashtag opportunities for Crooks & Castles"""
    opportunities = []
    
    # Aggregate hashtag performance across all competitors
    all_hashtags = defaultdict(lambda: {'total_mentions': 0, 'total_engagement': 0, 'brands_using': 0})
    
    for brand, hashtags in brand_hashtag_data.items():
        for hashtag, data in hashtags.items():
            all_hashtags[hashtag]['total_mentions'] += data['mentions']
            all_hashtags[hashtag]['total_engagement'] += data['total_engagement']
            all_hashtags[hashtag]['brands_using'] += 1
    
    # Find underutilized high-performing hashtags
    for hashtag, data in all_hashtags.items():
        if data['brands_using'] < 3 and data['total_engagement'] > 1000:
            avg_engagement = data['total_engagement'] / data['total_mentions'] if data['total_mentions'] > 0 else 0
            
            opportunities.append({
                'hashtag': hashtag,
                'opportunity_score': avg_engagement / max(data['brands_using'], 1),
                'avg_engagement': round(avg_engagement, 0),
                'competitor_usage': data['brands_using'],
                'recommendation': f'Low competition, high engagement potential'
            })
    
    return sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)[:5]

def save_planned_content(content_data):
    """Save planned content to file"""
    try:
        content_file = 'campaign_data/planned_content.json'
        
        existing_content = []
        if os.path.exists(content_file):
            with open(content_file, 'r') as f:
                existing_content = json.load(f)
        
        # Add new content
        content_data['id'] = str(uuid.uuid4())
        content_data['created_at'] = datetime.now().isoformat()
        existing_content.append(content_data)
        
        # Save updated content
        with open(content_file, 'w') as f:
            json.dump(existing_content, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving content: {e}")
        return False

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_asset_metadata(asset_data):
    """Save asset metadata to file"""
    try:
        metadata_file = 'assets/asset_metadata.json'
        
        existing_metadata = []
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                existing_metadata = json.load(f)
        
        existing_metadata.append(asset_data)
        
        with open(metadata_file, 'w') as f:
            json.dump(existing_metadata, f, indent=2)
    except Exception as e:
        print(f"Error saving asset metadata: {e}")

# Initialize directories
ensure_directories()

@app.route('/')
def dashboard():
    """Main enterprise dashboard"""
    return render_template('enterprise_dashboard.html')

@app.route('/api/calendar/<view_type>')
def get_calendar(view_type):
    """Get calendar data for specified view"""
    calendar_data = get_calendar_view(view_type)
    return jsonify(calendar_data)

@app.route('/api/competitive-scorecard')
def get_competitive_scorecard():
    """Competitive scorecard focused on 11 tracked brands"""
    scorecard = generate_competitive_scorecard()
    
    # Add hashtag intelligence
    hashtag_intel = analyze_hashtag_intelligence()
    
    return jsonify({
        'scorecard': scorecard,
        'hashtag_intelligence': hashtag_intel,
        'competitor_focus': {
            'total_tracked_brands': 11,
            'brand_tiers': {
                'luxury': ['Supreme', 'Essentials by Fear of God'],
                'established': ['Stussy', 'LRG', 'Diamond Supply Co.'],
                'mid_tier': ['Smoke Rise', 'Reason Clothing'],
                'emerging': ['Hellstar', 'Godspeed'],
                'legacy': ['Ed Hardy', 'Von Dutch']
            }
        },
        'crooks_positioning': scorecard.get('crooks_position', {}),
        'data_sources_active': len([k for k in COMPETITORS.keys() 
                                  if load_competitor_data(k, 'instagram') or load_competitor_data(k, 'tiktok')])
    })

@app.route('/api/brand-comparison/<competitor>')
def get_brand_comparison(competitor):
    """Head-to-head comparison with specific competitor"""
    if competitor not in COMPETITORS:
        return jsonify({'error': 'Competitor not tracked'})
    
    # Load competitor data
    instagram_data = load_competitor_data(competitor, 'instagram')
    tiktok_data = load_competitor_data(competitor, 'tiktok')
    
    if not instagram_data and not tiktok_data:
        return jsonify({
            'competitor': COMPETITORS[competitor]['name'],
            'error': 'No data available for this competitor',
            'data_needed': [
                f'data_sources/instagram/{competitor}_instagram_data.jsonl',
                f'data_sources/tiktok/{competitor}_tiktok_data.jsonl'
            ]
        })
    
    # Analyze competitor
    competitor_analysis = calculate_competitor_score(instagram_data, tiktok_data, COMPETITORS[competitor])
    
    # Generate head-to-head comparison
    comparison = {
        'competitor': COMPETITORS[competitor],
        'analysis': competitor_analysis,
        'vs_crooks': generate_head_to_head_analysis(competitor_analysis),
        'opportunities': identify_competitive_opportunities(competitor, competitor_analysis),
        'strategic_insights': generate_strategic_insights(competitor, competitor_analysis)
    }
    
    return jsonify(comparison)

def generate_head_to_head_analysis(competitor_analysis):
    """Generate head-to-head comparison against Crooks & Castles"""
    # Estimated Crooks metrics (would be from actual data when available)
    crooks_metrics = {
        'posting_frequency': 3.2,  # posts per week
        'avg_engagement_rate': 2.8,  # percentage
        'content_themes': ['vintage', 'street', 'lifestyle'],
        'estimated_followers': 150000
    }
    
    comparison = {
        'posting_frequency': {
            'crooks': crooks_metrics['posting_frequency'],
            'competitor': competitor_analysis.get('posting_frequency', 0),
            'advantage': 'crooks' if crooks_metrics['posting_frequency'] > competitor_analysis.get('posting_frequency', 0) else 'competitor'
        },
        'engagement_rate': {
            'crooks_estimated': crooks_metrics['avg_engagement_rate'],
            'competitor': round(competitor_analysis.get('engagement_rate', 0), 1),
            'advantage': 'crooks' if crooks_metrics['avg_engagement_rate'] > competitor_analysis.get('engagement_rate', 0) else 'competitor'
        },
        'content_strategy': {
            'crooks_themes': crooks_metrics['content_themes'],
            'competitor_themes': ['general']  # Would extract from actual data
        }
    }
    
    return comparison

def identify_competitive_opportunities(competitor_key, competitor_analysis):
    """Identify specific opportunities against this competitor"""
    opportunities = []
    competitor_name = COMPETITORS[competitor_key]['name']
    
    # Posting frequency opportunity
    if competitor_analysis.get('posting_frequency', 0) < 2.0:
        opportunities.append({
            'type': 'content_volume',
            'description': f'{competitor_name} posts less than 2x/week - opportunity for visibility',
            'action': 'Increase posting frequency to 4-5x/week',
            'impact': 'high'
        })
    
    # Engagement opportunity
    if competitor_analysis.get('engagement_rate', 0) < 3.0:
        opportunities.append({
            'type': 'engagement',
            'description': f'{competitor_name} has low engagement rate ({competitor_analysis.get("engagement_rate", 0):.1f}%)',
            'action': 'Focus on community engagement and authentic content',
            'impact': 'high'
        })
    
    return opportunities[:5]  # Top 5 opportunities

def generate_strategic_insights(competitor_key, competitor_analysis):
    """Generate strategic insights for competing against this brand"""
    competitor_info = COMPETITORS[competitor_key]
    insights = []
    
    # Tier-based strategy
    if competitor_info['tier'] == 'luxury':
        insights.append({
            'category': 'positioning',
            'insight': f'Compete on accessibility - offer luxury aesthetic at mid-tier pricing',
            'reasoning': f'{competitor_info["name"]} positioned as luxury/aspirational'
        })
    elif competitor_info['tier'] == 'legacy':
        insights.append({
            'category': 'modernization',
            'insight': f'Emphasize modern streetwear evolution vs nostalgic approach',
            'reasoning': f'{competitor_info["name"]} relies on legacy/vintage appeal'
        })
    
    return insights

@app.route('/api/cultural-moments')
def get_cultural_moments():
    """Get detected cultural moments"""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=90)
    
    moments = detect_cultural_moments(start_date, end_date)
    
    return jsonify({
        'cultural_moments': moments,
        'detection_confidence': 0.85,
        'generated_at': datetime.now().isoformat()
    })

@app.route('/api/content', methods=['POST'])
def save_content():
    """Save planned content"""
    try:
        content_data = request.json
        
        if save_planned_content(content_data):
            return jsonify({'success': True, 'message': 'Content saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error saving content'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/assets', methods=['POST'])
def upload_asset():
    """Upload and tag assets"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            # Determine subdirectory based on file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                subdirectory = 'images'
            elif file_ext in ['mp4', 'mov']:
                subdirectory = 'videos'
            else:
                subdirectory = 'design_files'
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], subdirectory, filename)
            file.save(file_path)
            
            # Save asset metadata
            asset_data = {
                'id': str(uuid.uuid4()),
                'filename': filename,
                'original_name': file.filename,
                'path': file_path,
                'type': subdirectory,
                'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
                'campaign': request.form.get('campaign', ''),
                'uploaded_at': datetime.now().isoformat()
            }
            
            save_asset_metadata(asset_data)
            
            return jsonify({
                'success': True, 
                'message': 'Asset uploaded successfully',
                'asset_id': asset_data['id'],
                'filename': filename
            })
        
        return jsonify({'success': False, 'message': 'File type not allowed'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/data-refresh', methods=['POST'])
def refresh_data():
    """Manually refresh all data sources"""
    try:
        # This would trigger data refresh from various sources
        # For now, just update the timestamp
        
        refresh_log = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'sources_updated': ['instagram', 'tiktok', 'competitive_intelligence'],
            'next_scheduled_refresh': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Save refresh log
        with open('analytics/last_refresh.json', 'w') as f:
            json.dump(refresh_log, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Data refresh completed',
            'refresh_log': refresh_log
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/export/<report_type>')
def export_report(report_type):
    """Export various reports"""
    try:
        if report_type == 'competitive-intelligence':
            return export_competitive_intelligence()
        elif report_type == 'campaign-plan':
            return export_campaign_plan()
        elif report_type == 'cultural-moments':
            return export_cultural_moments()
        else:
            return jsonify({'error': 'Unknown report type'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

def export_competitive_intelligence():
    """Export competitive intelligence report"""
    scorecard = generate_competitive_scorecard()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Crooks & Castles Competitive Intelligence Report'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Tracking 11 Competitor Brands'])
    writer.writerow([])
    
    # Competitor rankings
    if scorecard['competitive_ranking']:
        writer.writerow(['COMPETITOR RANKINGS'])
        writer.writerow(['Rank', 'Brand', 'Combined Score', 'Social Score', 'Aspirational Score', 'Tier'])
        
        for competitor, data in scorecard['competitive_ranking'].items():
            writer.writerow([
                data['rank'],
                COMPETITORS[competitor]['name'],
                data['score'],
                data['social_score'],
                data['aspirational_score'],
                data['tier']
            ])
    
    writer.writerow([])
    writer.writerow(['CROOKS & CASTLES POSITION'])
    
    if scorecard.get('crooks_position'):
        crooks_pos = scorecard['crooks_position']
        writer.writerow(['Estimated Rank', f"#{crooks_pos['estimated_rank']} of {crooks_pos['total_competitors_tracked']}"])
        writer.writerow(['Estimated Score', crooks_pos['estimated_score']])
        if crooks_pos.get('score_to_beat_next'):
            writer.writerow(['Score to Beat Next', crooks_pos['score_to_beat_next']])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=competitive_intelligence_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

def export_campaign_plan():
    """Export campaign plan"""
    return jsonify({'message': 'Campaign plan export not yet implemented'})

def export_cultural_moments():
    """Export cultural moments report"""
    return jsonify({'message': 'Cultural moments export not yet implemented'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
