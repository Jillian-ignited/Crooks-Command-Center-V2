import os, json, glob
from flask import Flask, jsonify, render_template, request, send_file, abort, Response
from asset_manager import (
    scan_upload_directory, categorize_assets, generate_thumbnails,
    handle_file_upload, serve_file_download, _load_catalog
)
from data_processor import (
    load_jsonl_data, analyze_hashtags, calculate_engagement_metrics,
    identify_cultural_moments, competitive_analysis, generate_intelligence_report
)
from calendar_engine import get_calendar
from agency_tracker import get_agencies

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

@app.route('/')
def dashboard():
    return render_template('index.html')

def _collect_posts():
    # Gather JSONL/JSON in uploads/intel and uploads/*
    patterns = [
        os.path.join('uploads', 'intel', '*.jsonl'),
        os.path.join('uploads', 'intel', '*.json'),
        os.path.join('uploads', '*.jsonl'),
        os.path.join('uploads', '*.json'),
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
                rows = json.load(open(p, 'r', encoding='utf-8', errors='ignore'))
                if isinstance(rows, dict):
                    rows = [rows]
            except Exception:
                rows = []
        if isinstance(rows, list):
            all_posts.extend(rows)
    return all_posts

@app.route('/api/intelligence')
def api_intelligence():
    posts = _collect_posts()
    metrics = calculate_engagement_metrics(posts)
    hashtags = analyze_hashtags(posts)
    moments = identify_cultural_moments(posts)
    comp = competitive_analysis({'all_posts': posts})
    data = {
        'all_posts': posts,
        'engagement': metrics,
        'hashtags': hashtags,
        'cultural_moments': moments,
        'competitive': comp
    }
    return jsonify(data)

@app.route('/api/assets')
def api_assets():
    cat = _load_catalog()
    # ensure thumbs for images
    image_files = [a['path'] for a in cat.get('assets', []) if a.get('type') == 'images']
    if image_files:
        generate_thumbnails(image_files)
        cat = _load_catalog()

    grouped = categorize_assets(cat.get('assets', []))
    return jsonify({'catalog': cat, 'groups': grouped})

@app.route('/api/assets/<asset_id>/download')
def download_asset(asset_id):
    path, name = serve_file_download(asset_id)
    if not path:
        abort(404)
    return send_file(path, as_attachment=True, download_name=name)

@app.route('/api/assets/search')
def api_assets_search():
    q = (request.args.get('q') or '').lower().strip()
    cat = _load_catalog()
    results = []
    for a in cat.get('assets', []):
        if q in a.get('filename', '').lower():
            results.append(a)
    return jsonify({'query': q, 'results': results})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    files = request.files.getlist('files')
    results = []
    for f in files:
        results.append(handle_file_upload(f))
    return jsonify({'results': results})

@app.route('/api/calendar/<view>')
def api_calendar(view):
    cal = get_calendar()
    if view not in cal:
        return jsonify({'error': 'invalid view'}), 400
    # Map assets to events
    cat = _load_catalog()
    from asset_manager import map_assets_to_campaigns
    mapping = map_assets_to_campaigns(cat.get('assets', []), cal)
    return jsonify({'view': view, 'events': cal[view], 'mapping': mapping})

# Full calendar (all views)
@app.route('/api/calendar')
def api_calendar_root():
    cal = get_calendar()
    return jsonify(cal)

# Calendar export (CSV for ops handoff)
@app.route('/api/calendar/export.csv')
def api_calendar_export():
    import csv, io
    cal = get_calendar()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['date','title','description','budget_allocation','deliverables','assets_mapped','cultural_context','target_kpis','status'])
    for view in ['7_day_view','30_day_view','60_day_view','90_day_view']:
        for ev in cal.get(view, []):
            writer.writerow([
                ev.get('date',''),
                ev.get('title',''),
                ev.get('description',''),
                ev.get('budget_allocation',''),
                '; '.join(ev.get('deliverables',[])),
                '; '.join(ev.get('assets_mapped',[])),
                ev.get('cultural_context',''),
                json.dumps(ev.get('target_kpis',{})),
                ev.get('status','')
            ])
    return Response(buf.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition':'attachment; filename=calendar_export.csv'})

@app.route('/api/agency')
def api_agency():
    return jsonify(get_agencies())

# Agency export (CSV)
@app.route('/api/agency/export.csv')
def api_agency_export():
    import csv, io
    data = get_agencies()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['name','phase','monthly_budget','budget_used','on_time_delivery','quality_score','project','status','due_date'])
    for ag in data.get('agencies', []):
        for pr in ag.get('current_projects', []):
            writer.writerow([
                ag['name'], ag['phase'], ag['monthly_budget'], ag['budget_used'],
                ag['on_time_delivery'], ag['quality_score'],
                pr['name'], pr['status'], pr['due_date']
            ])
    return Response(buf.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition':'attachment; filename=agency_export.csv'})

@app.route('/api/reports/generate')
def generate_report():
    posts = _collect_posts()
    metrics = calculate_engagement_metrics(posts)
    hashtags = analyze_hashtags(posts)
    moments = identify_cultural_moments(posts)
    comp = competitive_analysis({'all_posts': posts})
    report = generate_intelligence_report({
        'all_posts': posts,
        'engagement': metrics,
        'hashtags': hashtags,
        'cultural_moments': moments,
        'competitive': comp
    })
    os.makedirs('data', exist_ok=True)
    out_path = os.path.join('data', 'intelligence_report.json')
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    return send_file(out_path, as_attachment=True, download_name='intelligence_report.json')

if __name__ == '__main__':
    app.run(debug=True)
