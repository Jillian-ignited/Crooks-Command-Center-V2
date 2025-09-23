import os, json, glob
from datetime import datetime, date
from flask import Flask, jsonify, render_template, request, send_file, abort, Response, send_from_directory
from sqlalchemy import select

from db import init_db, SessionLocal, Asset, CalendarEvent, Agency, AgencyProject
from asset_manager import (
    load_catalog, categorize_assets, generate_thumbnails,
    handle_file_upload, serve_file_download, map_assets_to_campaigns
)
from data_processor import (
    load_jsonl_data, analyze_hashtags, calculate_engagement_metrics,
    identify_cultural_moments, competitive_analysis, generate_intelligence_report
)
from calendar_engine import load_calendar
from agency_tracker import load_agency

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.environ.get('CCC_UPLOAD_DIR', 'uploads')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
init_db()

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

# ---------- intelligence ----------
@app.route('/api/intelligence')
def api_intelligence():
    posts = _collect_posts()
    return jsonify({
        'engagement': calculate_engagement_metrics(posts),
        'hashtags': analyze_hashtags(posts),
        'cultural_moments': identify_cultural_moments(posts),
        'competitive': competitive_analysis({'all_posts': posts}),
        'posts_count': len(posts)
    })

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

# ---------- assets ----------
@app.route('/api/assets')
def api_assets():
    cat = load_catalog()
    image_files = [a['path'] for a in cat.get('assets', []) if a.get('type') == 'images' and not a.get('thumbnail')]
    if image_files:
        generate_thumbnails(image_files)
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

# ---------- calendar (DB) ----------
@app.route('/api/calendar/<view>')
def api_calendar_view(view):
    cal = load_calendar()
    if view not in cal:
        return jsonify({'error': 'invalid view'}), 400
    mapping = map_assets_to_campaigns(load_catalog().get('assets', []), cal)
    return jsonify({'view': view, 'events': cal[view], 'mapping': mapping})

@app.route('/api/calendar', methods=['GET','POST'])
def api_calendar_all():
    if request.method == 'GET':
        return jsonify(load_calendar())
    # create event
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

# ---------- agency (DB) ----------
@app.route('/api/agency', methods=['GET','POST'])
def api_agency():
    if request.method == 'GET':
        return jsonify(load_agency())
    # create agency
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

if __name__ == '__main__':
    app.run(debug=True)
