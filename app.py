import os, json, glob, traceback
from datetime import date
from flask import Flask, jsonify, render_template, request, send_file, abort, Response, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge
from sqlalchemy import select
from content_planning import plan_campaign, list_campaigns, campaign_overview, update_milestone_status, retitle_milestone, delete_campaign
from enhanced_competitor_analysis import build_competitor_intel

from db import init_db, SessionLocal, Asset, CalendarEvent, Agency, AgencyProject
from asset_manager import (
    load_catalog, categorize_assets, generate_thumbnails,
    handle_file_upload, serve_file_download, map_assets_to_campaigns, UPLOAD_DIR
)
from data_processor import (
    load_jsonl_data, analyze_hashtags, calculate_engagement_metrics,
    identify_cultural_moments, competitive_analysis, generate_intelligence_report
)
from calendar_engine import load_calendar
from agency_tracker import load_agency

app = Flask(__name__)
CORS(app)

# Limits
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
init_db()

# ---------- Error handler: JSON for /api/* ----------
@app.errorhandler(Exception)
def json_api_errors(e):
    if request.path.startswith('/api/'):
        code = 500
        if isinstance(e, RequestEntityTooLarge): code = 413
        elif isinstance(e, HTTPException): code = e.code or 500
        return jsonify({'error': type(e).__name__, 'detail': str(e)}), code
    raise e

# ---------- UI ----------
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# ---------- helpers ----------
def _collect_posts():
    patterns = [
        os.path.join(UPLOAD_DIR, 'intel', '*.jsonl'),
        os.path.join(UPLOAD_DIR, 'intel', '*.json'),
        os.path.join(UPLOAD_DIR, '*.jsonl'),
        os.path.join(UPLOAD_DIR, '*.json'),
    ]
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(pat))
    all_posts = []
    for p in paths:
        if p.endswith('.jsonl'):
            rows = load_jsonl_data(p)
        else:
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    rows = json.load(f)
                if isinstance(rows, dict):
                    rows = [rows]
            except Exception:
                rows = []
        if isinstance(rows, list):
            all_posts.extend(rows)
    return all_posts

# ---------- Intelligence ----------
@app.route('/api/intelligence')
def api_intelligence():
    posts = _collect_posts()
    payload = {
        'engagement': calculate_engagement_metrics(posts),
        'hashtags': analyze_hashtags(posts),
        'cultural_moments': identify_cultural_moments(posts),
        'competitive': competitive_analysis({'all_posts': posts}),
        'posts_count': len(posts)
    }
    if request.args.get('debug'):
        payload['_debug'] = {
            'upload_dir': UPLOAD_DIR,
            'jsonl_found': glob.glob(os.path.join(UPLOAD_DIR, '*.jsonl')) + glob.glob(os.path.join(UPLOAD_DIR, 'intel', '*.jsonl')),
            'json_found': glob.glob(os.path.join(UPLOAD_DIR, '*.json')) + glob.glob(os.path.join(UPLOAD_DIR, 'intel', '*.json'))
        }
    return jsonify(payload)
# --- Campaign Planning ---
@app.route('/api/planning/campaigns', methods=['GET','POST'])
def api_campaigns():
    if request.method == 'GET':
        prefix = request.args.get('q','').strip()
        return jsonify(list_campaigns(prefix=prefix))
    data = request.get_json(force=True)
    return jsonify(plan_campaign(
        campaign=data['campaign'],
        window_start=data['window_start'],
        window_end=data['window_end'],
        deliverables=data.get('deliverables', []),
        assets_mapped=data.get('assets_mapped', []),
        budget_allocation=float(data.get('budget_allocation', 0) or 0),
        cultural_context=data.get('cultural_context', ''),
        target_kpis=data.get('target_kpis', {}),
        status=data.get('status', 'planned'),
    ))
@app.route('/api/intelligence/competitors')
def api_competitors():
    posts = _collect_posts()
    intel = build_competitor_intel(posts)
    return jsonify(intel)

@app.route('/api/planning/<campaign>/overview')
def api_campaign_overview(campaign):
    return jsonify(campaign_overview(campaign))

@app.route('/api/planning/milestones/<int:event_id>', methods=['PUT','DELETE'])
def api_campaign_milestone(event_id):
    if request.method == 'DELETE':
        # soft-delete by retitling or truly delete via Calendar endpoints if you prefer
        return jsonify({"error":"use /api/calendar/<id> DELETE"}), 405
    data = request.get_json(force=True)
    if 'status' in data:
        return jsonify(update_milestone_status(event_id, data['status']))
    if 'milestone' in data:
        return jsonify(retitle_milestone(event_id, data['milestone']))
    return jsonify({"error":"no_action"}), 400

@app.route('/api/reports/generate')
def api_report_generate():
    posts = _collect_posts()
    report = generate_intelligence_report({
        'all_posts': posts,
        'engagement': calculate_engagement_metrics(posts),
        'hashtags': analyze_hashtags(posts),
        'cultural_moments': identify_cultural_moments(posts),
        'competitive': competitive_analysis({'all_posts': posts})
    })
    os.makedirs('data', exist_ok=True)
    out_path = os.path.join('data', 'intelligence_report.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    return send_file(out_path, as_attachment=True, download_name='intelligence_report.json')

# ---------- Assets ----------
@app.route('/api/assets')
def api_assets():
    cat = load_catalog()
    image_or_video = [a['path'] for a in cat.get('assets', []) if a.get('type') in ('images','videos') and not a.get('thumbnail')]
    if image_or_video:
        generate_thumbnails(image_or_video)
        cat = load_catalog()
    grouped = categorize_assets(cat.get('assets', []))
    return jsonify({'catalog': cat, 'groups': grouped})

@app.route('/api/assets/<int:asset_id>/download')
def api_asset_download(asset_id):
    path, name = serve_file_download(asset_id)
    if not path: abort(404)
    return send_file(path, as_attachment=True, download_name=name)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    files = request.files.getlist('files')
    results = [handle_file_upload(f) for f in files]
    return jsonify({'results': results})

# ---------- Calendar ----------
@app.route('/api/calendar/<view>')
def api_calendar_view(view):
    cal = load_calendar()
    if view not in cal:
        return jsonify({'error': 'invalid_view'}), 400
    mapping = map_assets_to_campaigns(load_catalog().get('assets', []), cal)
    return jsonify({'view': view, 'events': cal[view], 'mapping': mapping})

@app.route('/api/calendar', methods=['GET','POST'])
def api_calendar_all():
    if request.method == 'GET':
        return jsonify(load_calendar())
    data = request.get_json(force=True)
    ev = CalendarEvent(
        date=date.fromisoformat(data['date']),
        title=data['title'],
        description=data.get('description',''),
        budget_allocation=float(data.get('budget_allocation',0) or 0),
        deliverables=data.get('deliverables',[]),
        assets_mapped=data.get('assets_mapped',[]),
        cultural_context=data.get('cultural_context',''),
        target_kpis=data.get('target_kpis',{}),
        status=data.get('status','planned')
    )
    with SessionLocal() as s:
        s.add(ev); s.commit(); s.refresh(ev)
        return jsonify({"ok": True, "id": ev.id})

@app.route('/api/calendar/<int:event_id>', methods=['PUT','DELETE'])
def api_calendar_item(event_id):
    with SessionLocal() as s:
        ev = s.get(CalendarEvent, event_id)
        if not ev: return jsonify({"error":"not_found"}), 404
        if request.method == 'DELETE':
            s.delete(ev); s.commit(); return jsonify({"ok": True})
        data = request.get_json(force=True)
        for k in ["title","description","cultural_context","status"]:
            if k in data: setattr(ev, k, data[k])
        for k in ["budget_allocation"]:
            if k in data: setattr(ev, k, float(data[k] or 0))
        for k in ["deliverables","assets_mapped","target_kpis"]:
            if k in data: setattr(ev, k, data[k])
        if "date" in data: ev.date = date.fromisoformat(data["date"])
        s.commit(); return jsonify({"ok": True})

@app.route('/api/calendar/export.csv')
def api_calendar_export():
    import csv, io
    cal = load_calendar()
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(['date','title','description','budget_allocation','deliverables','assets_mapped','cultural_context','target_kpis','status'])
    for key in ['7_day_view','30_day_view','60_day_view','90_day_view']:
        for ev in cal.get(key, []):
            w.writerow([
                ev.get('date',''), ev.get('title',''), ev.get('description',''),
                ev.get('budget_allocation',''),
                '; '.join(ev.get('deliverables',[])),
                '; '.join(ev.get('assets_mapped',[])),
                ev.get('cultural_context',''),
                json.dumps(ev.get('target_kpis',{})), ev.get('status','')
            ])
    return Response(buf.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition':'attachment; filename=calendar_export.csv'})

# ---------- Agency ----------
@app.route('/api/agency', methods=['GET','POST'])
def api_agency():
    if request.method == 'GET':
        return jsonify(load_agency())
    data = request.get_json(force=True)
    ag = Agency(
        name=data['name'], phase=int(data.get('phase',1)),
        monthly_budget=float(data.get('monthly_budget',0) or 0),
        budget_used=float(data.get('budget_used',0) or 0),
        on_time_delivery=float(data.get('on_time_delivery',0) or 0),
        quality_score=float(data.get('quality_score',0) or 0),
        current_deliverables=int(data.get('current_deliverables',0) or 0),
        response_time=data.get('response_time',''),
        revision_rounds=data.get('revision_rounds',''),
        client_satisfaction=data.get('client_satisfaction','')
    )
    with SessionLocal() as s:
        s.add(ag); s.commit(); s.refresh(ag)
        return jsonify({"ok": True, "id": ag.id})

@app.route('/api/agency/<int:agency_id>', methods=['PUT','DELETE'])
def api_agency_item(agency_id):
    with SessionLocal() as s:
        ag = s.get(Agency, agency_id)
        if not ag: return jsonify({"error":"not_found"}), 404
        if request.method == 'DELETE':
            s.delete(ag); s.commit(); return jsonify({"ok": True})
        data = request.get_json(force=True)
        for k,v in data.items():
            if hasattr(ag, k): setattr(ag, k, v)
        s.commit(); return jsonify({"ok": True})

@app.route('/api/agency/<int:agency_id>/projects', methods=['POST'])
def api_agency_project_create(agency_id):
    data = request.get_json(force=True)
    with SessionLocal() as s:
        ag = s.get(Agency, agency_id)
        if not ag: return jsonify({"error":"not_found"}), 404
        due = date.fromisoformat(data['due_date']) if data.get('due_date') else None
        pr = AgencyProject(agency_id=agency_id, name=data['name'], status=data.get('status','pending'), due_date=due)
        s.add(pr); s.commit(); s.refresh(pr)
        return jsonify({"ok": True, "project_id": pr.id})

@app.route('/api/agency/projects/<int:project_id>', methods=['PUT','DELETE'])
def api_agency_project_item(project_id):
    with SessionLocal() as s:
        pr = s.get(AgencyProject, project_id)
        if not pr: return jsonify({"error":"not_found"}), 404
        if request.method == 'DELETE':
            s.delete(pr); s.commit(); return jsonify({"ok": True})
        data = request.get_json(force=True)
        for k in ["name","status"]:
            if k in data: setattr(pr, k, data[k])
        if "due_date" in data: pr.due_date = date.fromisoformat(data["due_date"]) if data["due_date"] else None
        s.commit(); return jsonify({"ok": True})

@app.route('/api/agency/export.csv')
def api_agency_export():
    import csv, io
    with SessionLocal() as s:
        agencies = s.scalars(select(Agency)).all()
        buf = io.StringIO(); w = csv.writer(buf)
        w.writerow(['name','phase','monthly_budget','budget_used','on_time_delivery','quality_score','project','status','due_date'])
        for ag in agencies:
            projs = s.scalars(select(AgencyProject).where(AgencyProject.agency_id==ag.id)).all()
            for pr in projs:
                w.writerow([ag.name, ag.phase, ag.monthly_budget, ag.budget_used,
                            ag.on_time_delivery, ag.quality_score, pr.name, pr.status,
                            (pr.due_date.isoformat() if pr.due_date else '')])
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition':'attachment; filename=agency_export.csv'})
# ADD THIS TO YOUR EXISTING app.py (don't replace, just add)

# 11 Competitor Intelligence Database
COMPETITORS = {
    'supreme': {
        'name': 'Supreme',
        'tier': 'luxury',
        'target_audience': 'hype-collectors',
        'price_range': 'premium',
        'instagram_handle': '@supremenewyork',
        'tiktok_handle': '@supreme',
        'key_strengths': ['exclusivity', 'drops', 'celebrity_endorsements'],
        'content_style': 'minimal_aesthetic'
    },
    'stussy': {
        'name': 'Stussy', 
        'tier': 'heritage',
        'target_audience': 'streetwear-og',
        'price_range': 'mid-premium',
        'instagram_handle': '@stussy',
        'tiktok_handle': '@stussy',
        'key_strengths': ['heritage', 'surf_culture', 'authenticity'],
        'content_style': 'lifestyle_focused'
    },
    'hellstar': {
        'name': 'Hellstar',
        'tier': 'emerging',
        'target_audience': 'gen-z-alt',
        'price_range': 'mid-tier',
        'instagram_handle': '@hellstar',
        'tiktok_handle': '@hellstar',
        'key_strengths': ['viral_content', 'influencer_network', 'trending'],
        'content_style': 'edgy_viral'
    },
    'godspeed': {
        'name': 'Godspeed',
        'tier': 'emerging',
        'target_audience': 'streetwear-purist',
        'price_range': 'mid-tier',
        'instagram_handle': '@godspeed',
        'tiktok_handle': '@godspeed',
        'key_strengths': ['quality', 'community', 'craftsmanship'],
        'content_style': 'product_focused'
    },
    'fog_essentials': {
        'name': 'Fear of God Essentials',
        'tier': 'luxury',
        'target_audience': 'minimalist-luxury',
        'price_range': 'premium',
        'instagram_handle': '@fearofgodessentials',
        'tiktok_handle': '@fearofgod',
        'key_strengths': ['designer_backing', 'quality', 'minimalism'],
        'content_style': 'luxury_minimal'
    },
    'smoke_rise': {
        'name': 'Smoke Rise',
        'tier': 'established',
        'target_audience': 'urban-contemporary',
        'price_range': 'mid-tier',
        'instagram_handle': '@smokerise',
        'tiktok_handle': '@smokerise',
        'key_strengths': ['urban_culture', 'music_ties', 'accessibility'],
        'content_style': 'urban_lifestyle'
    },
    'reason_clothing': {
        'name': 'Reason Clothing',
        'tier': 'established',
        'target_audience': 'urban-lifestyle',
        'price_range': 'accessible',
        'instagram_handle': '@reasonclothing',
        'tiktok_handle': '@reasonclothing',
        'key_strengths': ['affordability', 'variety', 'consistency'],
        'content_style': 'diverse_content'
    },
    'lrg': {
        'name': 'LRG',
        'tier': 'heritage',
        'target_audience': 'skatewear-culture',
        'price_range': 'accessible',
        'instagram_handle': '@lrgclothing',
        'tiktok_handle': '@lrg',
        'key_strengths': ['heritage', 'skate_culture', 'authenticity'],
        'content_style': 'skate_lifestyle'
    },
    'diamond_supply': {
        'name': 'Diamond Supply Co.',
        'tier': 'established',
        'target_audience': 'skate-culture',
        'price_range': 'mid-tier',
        'instagram_handle': '@diamondsupplyco',
        'tiktok_handle': '@diamondsupply',
        'key_strengths': ['skate_heritage', 'iconic_logo', 'collaborations'],
        'content_style': 'skate_focused'
    },
    'ed_hardy': {
        'name': 'Ed Hardy',
        'tier': 'legacy',
        'target_audience': 'nostalgic-revival',
        'price_range': 'mid-tier',
        'instagram_handle': '@edhardyofficial',
        'tiktok_handle': '@edhardy',
        'key_strengths': ['nostalgia', 'tattoo_culture', 'y2k_revival'],
        'content_style': 'retro_revival'
    },
    'von_dutch': {
        'name': 'Von Dutch',
        'tier': 'legacy',
        'target_audience': 'y2k-revival',
        'price_range': 'premium',
        'instagram_handle': '@vondutchoriginals',
        'tiktok_handle': '@vondutch',
        'key_strengths': ['iconic_status', 'celebrity_history', 'y2k_trend'],
        'content_style': 'celebrity_focused'
    }
}

# ADD THESE API ROUTES TO YOUR EXISTING app.py

@app.route('/api/competitors')
def get_competitors():
    """Get all competitor data"""
    return jsonify(COMPETITORS)

@app.route('/api/competitive-analysis')
def competitive_analysis():
    """Generate competitive analysis from your Apify data"""
    try:
        # Process your real JSONL data files
        analysis_data = process_competitor_data()
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({'error': 'Unable to process data', 'details': str(e)}), 500

@app.route('/api/brand-comparison/<competitor_key>')
def brand_comparison(competitor_key):
    """Head-to-head comparison with specific competitor"""
    if competitor_key not in COMPETITORS:
        return jsonify({'error': 'Competitor not found'}), 404
    
    try:
        comparison_data = generate_brand_comparison(competitor_key)
        return jsonify(comparison_data)
    except Exception as e:
        return jsonify({'error': 'Unable to generate comparison', 'details': str(e)}), 500

@app.route('/api/competitive-insights')
def competitive_insights():
    """Get strategic insights based on competitive analysis"""
    try:
        insights = generate_competitive_insights()
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': 'Unable to generate insights', 'details': str(e)}), 500

# HELPER FUNCTIONS - ADD THESE TO YOUR app.py

def process_competitor_data():
    """Process your real Apify JSONL files for competitive intelligence"""
    competitor_metrics = {}
    
    # Process each competitor's data from your JSONL files
    for comp_key, comp_info in COMPETITORS.items():
        # Look for JSONL files that match this competitor
        competitor_files = find_competitor_files(comp_key, comp_info)
        
        if competitor_files:
            metrics = analyze_competitor_files(competitor_files)
            competitor_metrics[comp_key] = {
                'name': comp_info['name'],
                'tier': comp_info['tier'],
                'metrics': metrics,
                'competitive_position': assess_competitive_position(metrics, comp_info['tier']),
                'key_strengths': comp_info['key_strengths'],
                'content_strategy': analyze_content_strategy(metrics)
            }
    
    return competitor_metrics

def find_competitor_files(comp_key, comp_info):
    """Find JSONL files that belong to this competitor"""
    competitor_files = []
    
    # Search in uploads directory for files matching this competitor
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if filename.endswith('.jsonl'):
                # Check if filename contains competitor identifiers
                filename_lower = filename.lower()
                brand_name_lower = comp_info['name'].lower().replace(' ', '_')
                
                if (comp_key in filename_lower or 
                    brand_name_lower in filename_lower or
                    comp_info['instagram_handle'].replace('@', '') in filename_lower):
                    competitor_files.append(os.path.join(upload_dir, filename))
    
    return competitor_files

def analyze_competitor_files(file_paths):
    """Analyze competitor JSONL files to extract metrics"""
    total_posts = 0
    total_engagement = 0
    hashtags = []
    posting_dates = []
    content_types = {'image': 0, 'video': 0, 'carousel': 0}
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            post = json.loads(line)
                            total_posts += 1
                            
                            # Extract engagement metrics
                            likes = post.get('likesCount', 0) or post.get('likes', 0)
                            comments = post.get('commentsCount', 0) or post.get('comments', 0)
                            shares = post.get('sharesCount', 0) or post.get('shares', 0)
                            total_engagement += likes + comments + shares
                            
                            # Extract hashtags
                            caption = post.get('text', '') or post.get('caption', '')
                            if caption:
                                hashtags.extend(re.findall(r'#\w+', caption))
                            
                            # Extract posting date
                            post_date = post.get('timestamp') or post.get('date')
                            if post_date:
                                posting_dates.append(post_date)
                            
                            # Determine content type
                            if post.get('videoUrl') or post.get('video'):
                                content_types['video'] += 1
                            elif post.get('images') and len(post.get('images', [])) > 1:
                                content_types['carousel'] += 1
                            else:
                                content_types['image'] += 1
                                
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            continue
    
    # Calculate averages and insights
    avg_engagement = total_engagement / max(total_posts, 1)
    top_hashtags = [tag for tag, count in Counter(hashtags).most_common(10)]
    
    return {
        'total_posts': total_posts,
        'avg_engagement_per_post': round(avg_engagement, 2),
        'total_engagement': total_engagement,
        'top_hashtags': top_hashtags,
        'content_distribution': content_types,
        'posting_frequency': calculate_posting_frequency(posting_dates),
        'engagement_rate': calculate_engagement_rate(total_engagement, total_posts)
    }

def assess_competitive_position(metrics, tier):
    """Assess competitive position based on metrics and tier"""
    engagement_score = metrics.get('avg_engagement_per_post', 0)
    
    # Tier-based benchmarks
    tier_benchmarks = {
        'luxury': {'high': 5000, 'medium': 2000},
        'heritage': {'high': 3000, 'medium': 1000},
        'established': {'high': 2000, 'medium': 800},
        'emerging': {'high': 1500, 'medium': 500},
        'legacy': {'high': 1000, 'medium': 400}
    }
    
    benchmark = tier_benchmarks.get(tier, {'high': 1000, 'medium': 500})
    
    if engagement_score >= benchmark['high']:
        return 'strong'
    elif engagement_score >= benchmark['medium']:
        return 'moderate'
    else:
        return 'developing'

def analyze_content_strategy(metrics):
    """Analyze content strategy effectiveness"""
    content_dist = metrics.get('content_distribution', {})
    total_content = sum(content_dist.values())
    
    if total_content == 0:
        return 'insufficient_data'
    
    video_ratio = content_dist.get('video', 0) / total_content
    carousel_ratio = content_dist.get('carousel', 0) / total_content
    
    if video_ratio > 0.6:
        return 'video_first'
    elif video_ratio > 0.3 and carousel_ratio > 0.2:
        return 'mixed_media'
    elif carousel_ratio > 0.4:
        return 'carousel_focused'
    else:
        return 'image_focused'

def calculate_posting_frequency(dates):
    """Calculate posting frequency from dates"""
    if len(dates) < 2:
        return 'insufficient_data'
    
    # This would need more sophisticated date parsing based on your data format
    # For now, return posts per week estimation
    posts_per_week = len(dates) / max(1, len(set(dates[:7])))  # Rough estimate
    
    if posts_per_week > 7:
        return 'daily_plus'
    elif posts_per_week > 3:
        return 'regular'
    elif posts_per_week > 1:
        return 'weekly'
    else:
        return 'infrequent'

def calculate_engagement_rate(total_engagement, total_posts):
    """Calculate engagement rate category"""
    avg_rate = total_engagement / max(total_posts, 1)
    
    if avg_rate > 5000:
        return 'high'
    elif avg_rate > 1000:
        return 'medium'
    else:
        return 'low'

def generate_brand_comparison(competitor_key):
    """Generate detailed comparison with specific competitor"""
    competitor_info = COMPETITORS[competitor_key]
    competitor_files = find_competitor_files(competitor_key, competitor_info)
    
    if not competitor_files:
        return {
            'competitor': competitor_info,
            'comparison': 'no_data',
            'message': f'No data files found for {competitor_info["name"]}'
        }
    
    # Get competitor metrics
    competitor_metrics = analyze_competitor_files(competitor_files)
    
    # Get Crooks & Castles metrics (from your own data)
    crooks_files = find_crooks_files()
    crooks_metrics = analyze_competitor_files(crooks_files) if crooks_files else {}
    
    comparison = {
        'competitor': competitor_info,
        'metrics_comparison': {
            'crooks_castles': crooks_metrics,
            'competitor': competitor_metrics
        },
        'strategic_insights': generate_comparison_insights(crooks_metrics, competitor_metrics, competitor_info),
        'recommended_actions': generate_comparison_recommendations(crooks_metrics, competitor_metrics, competitor_info)
    }
    
    return comparison

def find_crooks_files():
    """Find your own Crooks & Castles data files"""
    crooks_files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if filename.endswith('.jsonl'):
                filename_lower = filename.lower()
                if ('crooks' in filename_lower or 
                    'castles' in filename_lower or
                    'crooksandcastles' in filename_lower):
                    crooks_files.append(os.path.join(upload_dir, filename))
    
    return crooks_files

def generate_comparison_insights(crooks_metrics, competitor_metrics, competitor_info):
    """Generate strategic insights from comparison"""
    insights = []
    
    if not crooks_metrics or not competitor_metrics:
        return ['Insufficient data for comparison']
    
    # Engagement comparison
    crooks_engagement = crooks_metrics.get('avg_engagement_per_post', 0)
    comp_engagement = competitor_metrics.get('avg_engagement_per_post', 0)
    
    if comp_engagement > crooks_engagement * 1.5:
        insights.append(f"{competitor_info['name']} shows significantly higher engagement rates")
    elif crooks_engagement > comp_engagement * 1.5:
        insights.append(f"Strong engagement advantage over {competitor_info['name']}")
    
    # Content strategy comparison
    crooks_strategy = analyze_content_strategy(crooks_metrics)
    comp_strategy = analyze_content_strategy(competitor_metrics)
    
    if crooks_strategy != comp_strategy:
        insights.append(f"Different content strategies: Crooks uses {crooks_strategy}, {competitor_info['name']} uses {comp_strategy}")
    
    # Hashtag strategy
    crooks_hashtags = set(crooks_metrics.get('top_hashtags', []))
    comp_hashtags = set(competitor_metrics.get('top_hashtags', []))
    common_hashtags = crooks_hashtags.intersection(comp_hashtags)
    
    if len(common_hashtags) > 3:
        insights.append(f"High hashtag overlap suggests competing for similar audiences")
    
    return insights

def generate_comparison_recommendations(crooks_metrics, competitor_metrics, competitor_info):
    """Generate actionable recommendations"""
    recommendations = []
    
    if not crooks_metrics or not competitor_metrics:
        return ['Upload more data files for detailed recommendations']
    
    # Engagement recommendations
    comp_engagement = competitor_metrics.get('avg_engagement_per_post', 0)
    crooks_engagement = crooks_metrics.get('avg_engagement_per_post', 0)
    
    if comp_engagement > crooks_engagement:
        recommendations.append(f"Study {competitor_info['name']}'s high-performing content formats")
    
    # Content strategy recommendations
    comp_content = competitor_metrics.get('content_distribution', {})
    crooks_content = crooks_metrics.get('content_distribution', {})
    
    comp_video_ratio = comp_content.get('video', 0) / max(sum(comp_content.values()), 1)
    crooks_video_ratio = crooks_content.get('video', 0) / max(sum(crooks_content.values()), 1)
    
    if comp_video_ratio > crooks_video_ratio + 0.2:
        recommendations.append("Consider increasing video content ratio to match competitor performance")
    
    # Hashtag recommendations
    comp_hashtags = competitor_metrics.get('top_hashtags', [])
    unique_comp_hashtags = [tag for tag in comp_hashtags[:5] if tag not in crooks_metrics.get('top_hashtags', [])]
    
    if unique_comp_hashtags:
        recommendations.append(f"Test competitor hashtags: {', '.join(unique_comp_hashtags[:3])}")
    
    return recommendations[:5]  # Top 5 recommendations

def generate_competitive_insights():
    """Generate overall competitive landscape insights"""
    all_competitor_data = process_competitor_data()
    
    insights = {
        'market_leaders': [],
        'emerging_threats': [],
        'content_trends': {},
        'opportunity_gaps': [],
        'strategic_recommendations': []
    }
    
    # Identify market leaders by engagement
    engagement_rankings = []
    for comp_key, data in all_competitor_data.items():
        metrics = data.get('metrics', {})
        engagement = metrics.get('avg_engagement_per_post', 0)
        engagement_rankings.append((comp_key, data['name'], engagement, data['tier']))
    
    engagement_rankings.sort(key=lambda x: x[2], reverse=True)
    
    # Top 3 by engagement
    insights['market_leaders'] = [
        {'name': name, 'engagement': eng, 'tier': tier} 
        for _, name, eng, tier in engagement_rankings[:3]
    ]
    
    # Emerging threats (high engagement in emerging/established tiers)
    insights['emerging_threats'] = [
        {'name': name, 'engagement': eng} 
        for _, name, eng, tier in engagement_rankings 
        if tier in ['emerging', 'established'] and eng > 1000
    ][:3]
    
    # Content trends analysis
    video_performers = []
    for comp_key, data in all_competitor_data.items():
        strategy = data.get('metrics', {}).get('content_distribution', {})
        total = sum(strategy.values())
        if total > 0:
            video_ratio = strategy.get('video', 0) / total
            if video_ratio > 0.5:
                video_performers.append(data['name'])
    
    insights['content_trends']['video_first_brands'] = video_performers
    
    # Strategic recommendations
    if len(all_competitor_data) > 0:
        insights['strategic_recommendations'] = [
            "Monitor emerging competitors with high engagement growth",
            "Analyze content strategies of top-performing brands in your tier",
            "Consider video-first approach if competitors are outperforming",
            "Track hashtag trends across competitive landscape",
            "Benchmark posting frequency against tier leaders"
        ]
    
    return insights
