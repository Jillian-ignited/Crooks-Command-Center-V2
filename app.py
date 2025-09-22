import os, json, glob
from flask import Flask, jsonify, render_template, request, send_file, abort
from asset_manager import scan_upload_directory, categorize_assets, generate_thumbnails, handle_file_upload, serve_file_download, _load_catalog
from data_processor import load_jsonl_data, analyze_hashtags, calculate_engagement_metrics, identify_cultural_moments, competitive_analysis, generate_intelligence_report
from calendar_engine import get_calendar
from agency_tracker import get_agencies

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

@app.route('/')
def dashboard():
    return render_template('index.html')

def _collect_posts():
    # Gather JSONL in uploads/intel + any .jsonl directly under uploads
    paths = []
    for p in glob.glob(os.path.join('uploads', 'intel', '*.jsonl')):
        paths.append(p)
    for p in glob.glob(os.path.join('uploads', '*.jsonl')):
        paths.append(p)

    all_posts = []
    for p in paths:
        rows = load_jsonl_data(p)
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
        return jsonify({'error':'invalid view'}), 400
    # Map assets to events
    cat = _load_catalog()
    from asset_manager import map_assets_to_campaigns
    mapping = map_assets_to_campaigns(cat.get('assets', []), cal)
    return jsonify({'view': view, 'events': cal[view], 'mapping': mapping})

@app.route('/api/agency')
def api_agency():
    return jsonify(get_agencies())

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
