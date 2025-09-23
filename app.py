from __future__ import annotations
import os, json, glob, csv, io
from datetime import datetime, date
from typing import Any, Dict, List
from flask import (
    Flask, jsonify, request, render_template, send_file,
    make_response
)
from flask_cors import CORS

# -----------------------------------------------------------------------------
# App bootstrap
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DATA_DIR   = os.path.join(UPLOAD_DIR, "data")
THUMBS_DIR = os.path.join(UPLOAD_DIR, "thumbnails")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR,   exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.url_map.strict_slashes = False
CORS(app)

# Kill cache for HTML/JS/CSS while we iterate
@app.after_request
def no_cache(resp):
    ct = (resp.headers.get("Content-Type") or "").lower()
    if any(k in ct for k in ("text/html", "text/css", "javascript")):
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

# -----------------------------------------------------------------------------
# Optional module imports (use if available)
# -----------------------------------------------------------------------------
# Everything below has safe fallbacks so a missing module won't crash the app.
try:
    from data_processor import (
        load_jsonl_data as _dp_load,
        analyze_hashtags as _dp_hashtags,
        calculate_engagement_metrics as _dp_eng,
        identify_cultural_moments as _dp_moments,
        competitive_analysis as _dp_competitive,
        generate_intelligence_report as _dp_report,
    )
except Exception:
    _dp_load = _dp_hashtags = _dp_eng = _dp_moments = _dp_competitive = _dp_report = None

try:
    from enhanced_competitor_analysis import build_competitor_intel as _build_competitor_intel
except Exception:
    _build_competitor_intel = None

try:
    from asset_manager import (
        scan_upload_directory as _am_scan,
        handle_file_upload as _am_upload,
        serve_file_download as _am_download,
    )
except Exception:
    _am_scan = _am_upload = _am_download = None

try:
    from calendar_engine import get_calendar_views as _cal_views  # preferred
except Exception:
    _cal_views = None

try:
    from agency_tracker import get_agency_snapshot as _agency_snapshot
except Exception:
    _agency_snapshot = None

# Campaign planning (optional)
try:
    from content_planning import (
        plan_campaign, list_campaigns, campaign_overview,
        update_milestone_status, retitle_milestone, delete_campaign
    )
except Exception:
    plan_campaign = list_campaigns = campaign_overview = None
    update_milestone_status = retitle_milestone = delete_campaign = None


# -----------------------------------------------------------------------------
# Utilities / fallbacks
# -----------------------------------------------------------------------------
def _json_error(name: str, detail: str, http=500):
    return jsonify({"error": name, "detail": detail}), http

def _safe_jsonl(path: str) -> List[Dict[str, Any]]:
    items = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return items

def _collect_posts() -> List[Dict[str, Any]]:
    """
    Collect real data: canonical filenames + any *.jsonl under uploads/data.
    """
    posts: List[Dict[str, Any]] = []
    # Canonical names from spec
    ig = os.path.join(BASE_DIR, "dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl")
    tt = os.path.join(BASE_DIR, "dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl")
    posts += _safe_jsonl(ig)
    posts += _safe_jsonl(tt)
    # Uploaded data drops
    for path in glob.glob(os.path.join(DATA_DIR, "*.jsonl")):
        posts += _safe_jsonl(path)
    return posts

def _fallback_hashtags(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from collections import Counter
    c = Counter()
    for p in posts:
        tags = p.get("hashtags") or []
        if isinstance(tags, str):
            tags = [t for t in tags.split() if t.startswith("#")]
        for t in tags:
            t = t.lower().lstrip("#")
            if t:
                c[t] += 1
    return [{"hashtag": k, "count": v, "categories": []} for k, v in c.most_common(60)]

def _fallback_engagement(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    totals = dict(likes=0, comments=0, shares=0, views=0)
    for p in posts:
        totals["likes"]    += int(p.get("likesCount") or 0)
        totals["comments"] += int(p.get("commentsCount") or 0)
        totals["shares"]   += int(p.get("shareCount") or 0)
        totals["views"]    += int(p.get("viewCount") or 0)
    n = max(len(posts), 1)
    rate = round(((totals["likes"] + totals["comments"]) / max(totals["views"], 1)) * 100, 2)
    return {
        "totals": totals,
        "averages": {k: round(v / n, 2) for k, v in totals.items()},
        "engagement_rate_percent": rate,
        "trend": []
    }

def _fallback_moments(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    keys = ["hip-hop", "heritage", "anniversary", "streetwear", "collab", "hispanic", "community"]
    out = []
    for p in posts:
        text = (p.get("caption") or p.get("description") or "")
        lo = text.lower()
        hits = [k for k in keys if k in lo]
        if hits:
            out.append({
                "timestamp": p.get("timestamp"),
                "labels": hits,
                "summary": text[:220]
            })
    return out

def _fallback_competitors(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 11-brand minimal SOV using caption/description scan
    from collections import Counter, defaultdict
    brands = {
        "Crooks & Castles": ["crooks & castles", "crooks and castles", "crooks"],
        "Supreme": ["supreme"],
        "BAPE": ["bape", "a bathing ape"],
        "Kith": ["kith"],
        "Palace": ["palace skateboards", "palace"],
        "Fear of God": ["fear of god", "essentials"],
        "Off-White": ["off-white", "off white"],
        "Stüssy": ["stussy", "stüssy"],
        "Billionaire Boys Club": ["billionaire boys club", "bbc icecream", "icecream"],
        "Purple Brand": ["purple brand", "purpledenim"],
        "Noah": ["noah ny", "noahny"],
    }
    counts = Counter()
    agg = defaultdict(lambda: {"likes":0,"comments":0,"shares":0,"views":0,"posts":0})
    for p in posts:
        txt = (p.get("caption") or p.get("description") or "").lower()
        owner = None
        for b, aliases in brands.items():
            if any(a in txt for a in aliases):
                counts[b] += 1
                if not owner:
                    owner = b
        if owner:
            agg[owner]["likes"]    += int(p.get("likesCount") or 0)
            agg[owner]["comments"] += int(p.get("commentsCount") or 0)
            agg[owner]["shares"]   += int(p.get("shareCount") or 0)
            agg[owner]["views"]    += int(p.get("viewCount") or 0)
            agg[owner]["posts"]    += 1
    total = max(sum(counts.values()), 1)
    sov = [{"brand": b, "mentions": n, "share_pct": round(100.0 * n / total, 2)} for b, n in counts.most_common()]
    be  = []
    for b, v in agg.items():
        posts_n = max(v["posts"], 1)
        be.append({
            "brand": b,
            "avg_engagement": round((v["likes"]+v["comments"]+v["shares"]) / posts_n, 2),
            "avg_views": round(v["views"] / posts_n, 2),
            "posts": v["posts"]
        })
    be.sort(key=lambda x: (-x["avg_engagement"], -x["avg_views"]))
    return {"share_of_voice": sov, "brand_engagement": be, "trending_terms": [], "weekly_trend": []}

def _calendar_views_fallback() -> Dict[str, List[Dict[str, Any]]]:
    # Empty but valid structure to keep the UI alive if calendar_engine is absent.
    return {k: [] for k in ("7_day_view", "30_day_view", "60_day_view", "90_day_view")}

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/")
def dashboard():
    # Template must exist: templates/index.html
    return render_template("index.html")

# Route index (debug)
@app.get("/api/_routes")
def api_routes():
    rules = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(m for m in rule.methods if m not in ("HEAD","OPTIONS")))
        rules.append({"rule": str(rule), "methods": methods, "endpoint": rule.endpoint})
    return jsonify({"routes": sorted(rules, key=lambda x: x["rule"])})

@app.get("/api/ping")
def api_ping():
    return jsonify({"ok": True, "time": datetime.utcnow().isoformat() + "Z"})

# ---------- Intelligence ----------
@app.get("/api/intelligence")
def api_intelligence():
    try:
        # Use your data_processor if present; otherwise fallback
        posts = _collect_posts() if _dp_load is None else (
            (_dp_load(os.path.join(BASE_DIR, "dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl")) or []) +
            (_dp_load(os.path.join(BASE_DIR, "dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl")) or [])
        )
        hashtags = _dp_hashtags(posts) if _dp_hashtags else _fallback_hashtags(posts)
        engagement = _dp_eng(posts) if _dp_eng else _fallback_engagement(posts)
        moments = _dp_moments(posts) if _dp_moments else _fallback_moments(posts)

        return jsonify({
            "posts_count": len(posts),
            "engagement": engagement,
            "hashtags": hashtags,
            "cultural_moments": moments,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        })
    except Exception as e:
        return _json_error("intelligence_failed", str(e))

@app.get("/api/intelligence/competitors")
def api_competitors():
    try:
        if _build_competitor_intel:
            posts = _collect_posts()
            intel = _build_competitor_intel(posts)  # our enhanced module supports posts arg
            return jsonify(intel)
        # fallback
        posts = _collect_posts()
        return jsonify(_fallback_competitors(posts))
    except Exception as e:
        return _json_error("competitors_failed", str(e))

# ---------- Assets ----------
@app.get("/api/assets")
def api_assets():
    try:
        if _am_scan:
            cat = _am_scan()  # should return list of asset dicts OR {"assets":[...]}
            if isinstance(cat, dict) and "assets" in cat:
                return jsonify(cat)
            return jsonify({"assets": cat})
        # minimal fallback: list files in uploads
        assets = []
        for root, _, files in os.walk(UPLOAD_DIR):
            for fn in files:
                if fn.startswith("."): continue
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, BASE_DIR)
                assets.append({
                    "id": abs(hash(rel)) % (10**9),
                    "filename": fn,
                    "thumbnail": None,
                    "size_bytes": os.path.getsize(p),
                    "type": (os.path.splitext(fn)[1][1:].lower() or "file"),
                })
        return jsonify({"assets": assets})
    except Exception as e:
        return _json_error("assets_failed", str(e))

@app.get("/api/assets/<asset_id>/download")
def api_asset_download(asset_id):
    try:
        if _am_download:
            return _am_download(asset_id)
        # fallback: naive serve by filename hash -> not secure, encourage using asset_manager
        return _json_error("download_unavailable", "Use asset_manager.serve_file_download()"), 404
    except Exception as e:
        return _json_error("download_failed", str(e))

# ---------- Uploads ----------
@app.post("/api/upload")
def api_upload():
    try:
        files = request.files.getlist("files")
        if not files:
            return _json_error("no_files", "No files received", 400)
        results = []
        if _am_upload:
            for f in files:
                try:
                    r = _am_upload(f)  # expected to return a dict with ok/asset info
                    results.append(r if isinstance(r, dict) else {"ok": True, "detail": "uploaded"})
                except Exception as e:
                    results.append({"ok": False, "error": str(e), "filename": getattr(f, "filename", "")})
        else:
            # Minimal, safe save: /uploads/original_name (overwrites same name)
            for f in files:
                name = f.filename or "file"
                safe = os.path.basename(name)
                dest = os.path.join(UPLOAD_DIR, safe)
                f.save(dest)
                results.append({"ok": True, "filename": safe, "bytes": os.path.getsize(dest)})
        return jsonify({"results": results})
    except Exception as e:
        return _json_error("upload_failed", str(e))

# ---------- Calendar ----------
@app.get("/api/calendar/<view>")
def api_calendar(view):
    try:
        valid = {"7_day_view", "30_day_view", "60_day_view", "90_day_view"}
        if view not in valid:
            return _json_error("unknown_view", f"{view} not in {sorted(valid)}", 400)
        data = _cal_views() if _cal_views else _calendar_views_fallback()
        # Frontend expects {"events":[...]}
        return jsonify({"events": data.get(view, [])})
    except Exception as e:
        return _json_error("calendar_failed", str(e))

@app.get("/api/calendar/export.csv")
def api_calendar_export():
    # CSV export for business decks
    try:
        data = _cal_views() if _cal_views else _calendar_views_fallback()
        rows = []
        for k in ("7_day_view", "30_day_view", "60_day_view", "90_day_view"):
            for ev in data.get(k, []):
                rows.append({
                    "range": k,
                    "date": ev.get("date"),
                    "title": ev.get("title"),
                    "status": ev.get("status"),
                    "deliverables": ", ".join(ev.get("deliverables") or []),
                    "assets_mapped": ", ".join(ev.get("assets_mapped") or []),
                    "cultural_context": ev.get("cultural_context") or "",
                })
        sio = io.StringIO()
        writer = csv.DictWriter(sio, fieldnames=list(rows[0].keys()) if rows else
                                ["range","date","title","status","deliverables","assets_mapped","cultural_context"])
        writer.writeheader()
        for r in rows: writer.writerow(r)
        mem = io.BytesIO(sio.getvalue().encode("utf-8"))
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="calendar_export.csv")
    except Exception as e:
        return _json_error("calendar_export_failed", str(e))

# ---------- Agency ----------
@app.get("/api/agency")
def api_agency():
    try:
        if _agency_snapshot:
            snap = _agency_snapshot()
            return jsonify(snap)
        # minimal placeholder when module absent
        return jsonify({"agencies": []})
    except Exception as e:
        return _json_error("agency_failed", str(e))

@app.get("/api/agency/export.csv")
def api_agency_export():
    try:
        if not _agency_snapshot:
            return _json_error("export_unavailable", "agency_tracker not present", 400)
        snap = _agency_snapshot()
        agencies = snap.get("agencies", [])
        rows = []
        for a in agencies:
            rows.append({
                "name": a.get("name"),
                "phase": a.get("phase"),
                "monthly_budget": a.get("monthly_budget"),
                "budget_used": a.get("budget_used"),
                "on_time_delivery": a.get("on_time_delivery"),
                "quality_score": a.get("quality_score"),
                "current_deliverables": a.get("current_deliverables"),
            })
        sio = io.StringIO()
        writer = csv.DictWriter(sio, fieldnames=list(rows[0].keys()) if rows else
                                ["name","phase","monthly_budget","budget_used","on_time_delivery","quality_score","current_deliverables"])
        writer.writeheader()
        for r in rows: writer.writerow(r)
        mem = io.BytesIO(sio.getvalue().encode("utf-8"))
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="agency_export.csv")
    except Exception as e:
        return _json_error("agency_export_failed", str(e))

# ---------- Reports ----------
@app.get("/api/reports/generate")
def api_report_generate():
    try:
        posts = _collect_posts()
        if _dp_report:
            # Your data_processor can build a formatted report
            content = _dp_report(posts)
        else:
            # Fallback: build a lean, exportable JSON
            content = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "posts_count": len(posts),
                "engagement": _fallback_engagement(posts),
                "hashtags": _fallback_hashtags(posts),
                "cultural_moments": _fallback_moments(posts),
            }
        # Serve as a downloadable JSON file
        mem = io.BytesIO(json.dumps(content, indent=2).encode("utf-8"))
        return send_file(mem, mimetype="application/json", as_attachment=True,
                         download_name="intelligence_report.json")
    except Exception as e:
        return _json_error("report_failed", str(e))

# ---------- Optional: Planning APIs (only if content_planning is installed) ----------
@app.route("/api/planning/campaigns", methods=["GET", "POST"])
def api_planning_campaigns():
    if request.method == "GET":
        if not list_campaigns:
            return jsonify([])
        q = request.args.get("q", "").strip()
        return jsonify(list_campaigns(prefix=q))
    # POST
    if not plan_campaign:
        return _json_error("planning_unavailable", "content_planning not present", 400)
    data = request.get_json(force=True, silent=True) or {}
    try:
        out = plan_campaign(
            campaign=data["campaign"],
            window_start=data["window_start"],
            window_end=data["window_end"],
            deliverables=data.get("deliverables", []),
            assets_mapped=data.get("assets_mapped", []),
            budget_allocation=float(data.get("budget_allocation", 0) or 0),
            cultural_context=data.get("cultural_context", ""),
            target_kpis=data.get("target_kpis", {}),
            status=data.get("status", "planned"),
        )
        return jsonify(out)
    except Exception as e:
        return _json_error("planning_failed", str(e))

@app.get("/api/planning/<campaign>/overview")
def api_planning_overview(campaign):
    if not campaign_overview:
        return _json_error("planning_unavailable", "content_planning not present", 400)
    try:
        return jsonify(campaign_overview(campaign))
    except Exception as e:
        return _json_error("planning_failed", str(e))

@app.route("/api/planning/milestones/<int:event_id>", methods=["PUT", "DELETE"])
def api_planning_milestone(event_id):
    if request.method == "DELETE":
        return _json_error("use_calendar_delete", "Delete via calendar endpoint", 405)
    if not (update_milestone_status or retitle_milestone):
        return _json_error("planning_unavailable", "content_planning not present", 400)
    data = request.get_json(force=True, silent=True) or {}
    try:
        if "status" in data and update_milestone_status:
            return jsonify(update_milestone_status(event_id, data["status"]))
        if "milestone" in data and retitle_milestone:
            return jsonify(retitle_milestone(event_id, data["milestone"]))
        return _json_error("no_action", "Provide 'status' or 'milestone' in body", 400)
    except Exception as e:
        return _json_error("planning_failed", str(e))

# -----------------------------------------------------------------------------
# API-first error handlers (avoid HTML in /api/* responses)
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return _json_error("not_found", f"{request.path} not found", 404)
    return render_template("index.html"), 200

@app.errorhandler(500)
def internal_err(e):
    if request.path.startswith("/api/"):
        return _json_error("server_error", "internal error", 500)
    return render_template("index.html"), 200

# -----------------------------------------------------------------------------
# Gunicorn entrypoint (Render Start Command points at app:app)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
