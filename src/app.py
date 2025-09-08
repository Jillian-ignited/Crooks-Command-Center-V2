#!/usr/bin/env python3
"""
Crooks & Castles — Command Center (Render-friendly)
- No Postgres. No psycopg2. Pure Flask + filesystem + optional seed JSON.
- Clean JSON uploads. Stable calendar + assets + agency endpoints.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, jsonify, send_from_directory, request, Response, render_template_string
from flask_cors import CORS

# ----------------------------
# App setup
# ----------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("crooks")

# When deploying under repo root, BASE_DIR is project root on Render
BASE_DIR = Path(os.environ.get("BASE_DIR", Path(__file__).resolve().parent))
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"  # if you keep Manus HTML here (optional)

# Ensure dirs exist
for p in [DATA_DIR, UPLOADS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

SEED_CALENDAR_FILE = DATA_DIR / "seed_calendar.json"
SEED_ASSETS_FILE = DATA_DIR / "seed_assets.json"
ASSET_INDEX = DATA_DIR / "assets_index.json"  # persistent lightweight index

# ----------------------------
# Helpers
# ----------------------------
def read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning(f"Failed reading JSON {path}: {e}")
    return default

def write_json(path: Path, payload: Any):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        log.error(f"Failed writing JSON {path}: {e}")
        return False

def ext_for_mime(mime: str) -> str:
    if not mime:
        return ""
    if mime.startswith("image/"):
        return "." + mime.split("/", 1)[1]
    if mime.startswith("video/"):
        return "." + mime.split("/", 1)[1]
    return ""

def safe_filename(original: str) -> str:
    base = Path(original).name
    return base.replace("..", "_").replace("/", "_").replace("\\", "_")

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

# Asset index schema:
# {
#   "assets": [
#     {
#       "id": "uuid",
#       "filename": "stored_name.ext",
#       "original_name": "...",
#       "mime": "image/png",
#       "size": 12345,
#       "source": "upload|seed",
#       "uploaded_at": "iso",
#       "badge_score": 90,
#       "code": "Code 11: Culture"
#     }
#   ]
# }
def load_asset_index() -> Dict[str, Any]:
    data = read_json(ASSET_INDEX, {"assets": []})
    # prune records whose files are gone
    assets = []
    for a in data.get("assets", []):
        if (UPLOADS_DIR / a.get("filename", "")).exists() or (DATA_DIR / "assets" / a.get("filename", "")).exists():
            assets.append(a)
    data["assets"] = assets
    return data

def save_asset_index(index: Dict[str, Any]):
    write_json(ASSET_INDEX, index)

def calc_badge_score(name: str, mime: str) -> int:
    score = 75
    n = (name or "").lower()
    if mime and mime.startswith("image/"):
        score += 10
    if mime and mime.startswith("video/"):
        score += 15
    if any(k in n for k in ["crooks", "castle", "heritage", "street"]):
        score += 10
    return min(score, 100)

def default_calendar_payload(days: int) -> List[Dict[str, Any]]:
    today = datetime.utcnow()
    result = []
    for i in range(days):
        dt = today + timedelta(days=i)
        result.append({
            "date": dt.strftime("%Y-%m-%d"),
            "day_name": dt.strftime("%A"),
            "formatted_date": dt.strftime("%b %d"),
            "posts": []
        })
    return result

# ----------------------------
# Flask app
# ----------------------------
app = Flask(__name__)
CORS(app)

# ----------------------------
# UI (tries to serve Manus HTML if present; else a simple console)
# ----------------------------
@app.route("/")
def home():
    # If you added Manus HTML at src/static/index_enhanced_planning.html, serve it
    html_path = STATIC_DIR / "index_enhanced_planning.html"
    if html_path.exists():
        # Let the HTML make fetch calls to our /api/* endpoints
        return send_from_directory(str(STATIC_DIR), "index_enhanced_planning.html")

    # Fallback minimal console so you have working buttons even without Manus HTML
    return render_template_string(
        """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Crooks & Castles Command Center</title>
  <style>
    body { font-family: Inter, system-ui, -apple-system, Arial; background:#0a0a0a; color:#fff; padding:24px; }
    a, button { color:#22c55e; }
    .row { margin: 10px 0; }
    .card { background:#111; border:1px solid #222; border-radius:8px; padding:16px; margin-bottom:12px; }
    .btn { background:#22c55e; color:#000; padding:8px 12px; border-radius:6px; border:none; cursor:pointer; font-weight:600; }
    .muted { color:#9ca3af; font-size:12px; }
    code { background:#111827; padding:2px 6px; border-radius:4px; }
  </style>
</head>
<body>
  <h1>🏰 Crooks & Castles Command Center <span class="muted">— minimal console</span></h1>
  <div class="card">
    <div class="row">
      <strong>Quick actions</strong>
    </div>
    <div class="row">
      <button class="btn" onclick="seedDemo()">Seed demo data</button>
      <button class="btn" onclick="debug()">Debug check</button>
      <button class="btn" onclick="resetDB()">Reset DB</button>
    </div>
    <div class="row muted">APIs: <code>/api/calendar/7day</code> <code>/api/assets</code> <code>/api/deliverables</code></div>
  </div>

  <div class="card">
    <div class="row"><strong>Asset upload</strong></div>
    <div class="row">
      <input type="file" id="fileInput" multiple>
      <button class="btn" onclick="upload()">Upload</button>
    </div>
    <pre id="out" class="row muted"></pre>
  </div>

<script>
  async function seedDemo() {
    const r = await fetch('/seed-demo', {method:'POST'});
    document.getElementById('out').textContent = await r.text();
  }
  async function debug() {
    const r = await fetch('/debug');
    document.getElementById('out').textContent = await r.text();
  }
  async function resetDB() {
    const r = await fetch('/reset-db', {method:'POST'});
    document.getElementById('out').textContent = await r.text();
  }
  async function upload() {
    const fi = document.getElementById('fileInput');
    if (!fi.files.length) { alert('Pick files'); return; }
    const fd = new FormData();
    for (const f of fi.files) fd.append('files', f);
    const r = await fetch('/api/upload-assets', { method:'POST', body: fd });
    const t = await r.text(); // always JSON; if HTML error page, you'll see it here
    document.getElementById('out').textContent = t;
  }
</script>
</body>
</html>
        """
    )

# Serve other static files (CSS/JS/assets) for Manus UI if it exists
@app.route("/static/<path:filename>")
def static_files(filename):
    target = STATIC_DIR / filename
    if target.exists():
        return send_from_directory(str(STATIC_DIR), filename)
    return Response("Not found", status=404)

# ----------------------------
# Health + Debug
# ----------------------------
@app.route("/healthz")
def healthz():
    return jsonify({
        "ok": True,
        "time": now_iso(),
        "base_dir": str(BASE_DIR),
        "uploads_dir": str(UPLOADS_DIR),
        "data_dir": str(DATA_DIR),
        "static_dir": str(STATIC_DIR)
    })

@app.route("/debug")
def debug():
    index = load_asset_index()
    seeds = {
        "has_seed_calendar": SEED_CALENDAR_FILE.exists(),
        "has_seed_assets": SEED_ASSETS_FILE.exists(),
    }
    return jsonify({
        "ok": True,
        "assets_index_count": len(index.get("assets", [])),
        "uploads_files": sorted([p.name for p in UPLOADS_DIR.glob("*")]),
        "seeds": seeds
    })

# ----------------------------
# Calendar APIs
# ----------------------------
def _calendar_payload(days: int):
    # If a seed file exists, prefer it.
    seed = read_json(SEED_CALENDAR_FILE, None)
    if seed and isinstance(seed, dict):
        # Expect keys "7day","30day","60day","90day" in seed
        key = "7day" if days == 7 else "30day" if days == 30 else "60day" if days == 60 else "90day"
        if key in seed:
            return seed[key]
    # else synthesize empty structure
    return default_calendar_payload(days)

@app.get("/api/calendar/7day")
def api_calendar_7():
    return jsonify({"success": True, "view_type": "7day", "calendar_data": _calendar_payload(7)})

@app.get("/api/calendar/30day")
def api_calendar_30():
    return jsonify({"success": True, "view_type": "30day", "calendar_data": _calendar_payload(30)})

@app.get("/api/calendar/60day")
def api_calendar_60():
    # In seed, you can put opportunity objects; fallback gives empty shell
    payload = read_json(SEED_CALENDAR_FILE, {})
    opportunities = payload.get("60day", [])
    return jsonify({"success": True, "view_type": "60day", "opportunities": opportunities})

@app.get("/api/calendar/90day")
def api_calendar_90():
    payload = read_json(SEED_CALENDAR_FILE, {})
    long_range = payload.get("90day", [])
    return jsonify({"success": True, "view_type": "90day", "long_range": long_range})

# ----------------------------
# Assets APIs
# ----------------------------
@app.get("/api/assets")
def api_assets():
    """
    Returns both:
    - uploaded files in /uploads
    - seeded assets (optional) stored under data/assets/<filename> with records in seed_assets.json
    """
    index = load_asset_index()

    # Add any loose files in /uploads that aren't indexed yet
    known = {a["filename"] for a in index["assets"]}
    for file in UPLOADS_DIR.glob("*"):
        if file.is_file() and file.name not in known:
            # best-effort mime guess
            mime = "image/" + file.suffix[1:] if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".webp"] else "application/octet-stream"
            asset_id = str(uuid.uuid4())
            index["assets"].append({
                "id": asset_id,
                "filename": file.name,
                "original_name": file.name,
                "mime": mime,
                "size": file.stat().st_size,
                "source": "upload",
                "uploaded_at": now_iso(),
                "badge_score": calc_badge_score(file.name, mime),
                "code": "Code 11: Culture"
            })
    save_asset_index(index)

    # Combine assets (already includes uploads; seed assets will be added via /seed-demo)
    return jsonify({"success": True, "assets": index["assets"]})

@app.post("/api/upload-assets")
def api_upload_assets():
    """
    Robust upload endpoint:
    - Always returns JSON (no HTML error page).
    - Accepts multiple files under field name 'files'.
    - Saves to /uploads and updates assets_index.json.
    """
    try:
        if "files" not in request.files:
            return jsonify({"success": False, "message": "No files provided (expected field 'files')"}), 400

        files = request.files.getlist("files")
        if not files:
            return jsonify({"success": False, "message": "Empty file list"}), 400

        index = load_asset_index()
        added = []

        for f in files:
            if not f or not f.filename:
                continue
            orig = safe_filename(f.filename)
            mime = f.mimetype or "application/octet-stream"
            ext = Path(orig).suffix
            # Generate a stored filename to avoid collisions
            uid = str(uuid.uuid4())
            stored = f"{uid}{ext}"
            dest = UPLOADS_DIR / stored
            f.save(str(dest))

            record = {
                "id": uid,
                "filename": stored,
                "original_name": orig,
                "mime": mime,
                "size": dest.stat().st_size,
                "source": "upload",
                "uploaded_at": now_iso(),
                "badge_score": calc_badge_score(orig, mime),
                "code": "Code 11: Culture"
            }
            index["assets"].append(record)
            added.append(record)

        save_asset_index(index)
        return jsonify({"success": True, "uploaded_count": len(added), "assets": added})
    except Exception as e:
        log.exception("Upload failed")
        # Still JSON
        return jsonify({"success": False, "message": f"Upload error: {str(e)}"}), 500

@app.get("/assets/<path:filename>")
def serve_asset(filename: str):
    """
    Serves files from uploads/ (primary) or data/assets/ (seeded).
    Your front end can reference /assets/<filename>.
    """
    file_path = UPLOADS_DIR / filename
    if file_path.exists():
        return send_from_directory(str(UPLOADS_DIR), filename)

    seed_path = DATA_DIR / "assets" / filename
    if seed_path.exists():
        return send_from_directory(str(DATA_DIR / "assets"), filename)

    return jsonify({"success": False, "message": "Asset not found"}), 404

# ----------------------------
# Agency / Deliverables
# ----------------------------
@app.get("/api/deliverables")
def api_deliverables():
    """
    Computes deliverable progress from:
    - 7-day calendar posts (if present in seed)
    - asset count (uploads + seeds)
    Email count is simulated unless your seed uses platform:"Email".
    """
    # current phase by month (demo logic)
    now = datetime.utcnow()
    if now.month in [9, 10] and now.year == 2025:
        phase = ("phase1", "Foundation & Awareness", "Sep-Oct 2025", "$4,000/month",
                 {"social_posts": 12, "ad_creatives": 4, "email_campaigns": 2})
    elif now.month in [11, 12] and now.year == 2025:
        phase = ("phase2", "Growth & Q4 Push", "Nov-Dec 2025", "$7,500/month",
                 {"social_posts": 16, "ad_creatives": 8, "email_campaigns": 6})
    else:
        phase = ("phase3", "Full Retainer + TikTok Shop", "Jan 2026+", "$10,000/month",
                 {"social_posts": 20, "ad_creatives": 12, "email_campaigns": 8})

    _, name, period, budget, targets = phase

    # posts: count from 7-day seed if provided
    seed = read_json(SEED_CALENDAR_FILE, {})
    posts_count = 0
    emails_count = 0
    seven = seed.get("7day", [])
    for day in seven:
        for p in day.get("posts", []):
            posts_count += 1
            if str(p.get("platform", "")).lower() == "email":
                emails_count += 1

    # assets = indexed assets
    assets_index = load_asset_index()
    creatives_count = len(assets_index.get("assets", []))

    def pct(cur, tgt): 
        return min(100, round((cur / tgt) * 100, 1) if tgt else 0.0)

    p_prog = pct(posts_count, targets["social_posts"])
    c_prog = pct(creatives_count, targets["ad_creatives"])
    e_prog = pct(emails_count, targets["email_campaigns"])
    overall = round((p_prog + c_prog + e_prog) / 3, 1)

    def status(cur, tgt, prog):
        if cur > tgt: return "ahead"
        if prog >= 80: return "on_track"
        return "behind"

    return jsonify({
        "success": True,
        "current_phase": {"name": name, "period": period, "budget": budget},
        "current_progress": {
            "social_posts": {
                "current": posts_count, "target": targets["social_posts"],
                "progress": p_prog, "outstanding": max(0, targets["social_posts"] - posts_count),
                "status": status(posts_count, targets["social_posts"], p_prog)
            },
            "ad_creatives": {
                "current": creatives_count, "target": targets["ad_creatives"],
                "progress": c_prog, "outstanding": max(0, targets["ad_creatives"] - creatives_count),
                "status": status(creatives_count, targets["ad_creatives"], c_prog)
            },
            "email_campaigns": {
                "current": emails_count, "target": targets["email_campaigns"],
                "progress": e_prog, "outstanding": max(0, targets["email_campaigns"] - emails_count),
                "status": status(emails_count, targets["email_campaigns"], e_prog)
            }
        },
        "overall_progress": overall
    })

# ----------------------------
# Maintenance routes
# ----------------------------
@app.post("/seed-demo")
def seed_demo():
    """
    Loads seed_assets.json (copies files from data/assets/* into index),
    ensures seed_calendar.json is recognized.
    """
    # 1) Seed assets metadata
    index = load_asset_index()
    assets = index.get("assets", [])
    before = len(assets)

    seed_assets = read_json(SEED_ASSETS_FILE, {"assets": []}).get("assets", [])
    seed_folder = DATA_DIR / "assets"
    seed_folder.mkdir(parents=True, exist_ok=True)

    for rec in seed_assets:
        # Expect fields: filename (file must exist under data/assets), original_name, mime
        fname = rec.get("filename")
        if not fname:
            continue
        # record if file exists
        if not (seed_folder / fname).exists():
            # seed listing says file exists but it's missing on disk — skip, but keep going
            continue
        # If already present in index, skip
        if any(a.get("filename") == fname for a in assets):
            continue
        uid = str(uuid.uuid4())
        assets.append({
            "id": uid,
            "filename": fname,  # served via /assets/<filename> out of data/assets
            "original_name": rec.get("original_name", fname),
            "mime": rec.get("mime", "image/png"),
            "size": (seed_folder / fname).stat().st_size,
            "source": "seed",
            "uploaded_at": now_iso(),
            "badge_score": calc_badge_score(fname, rec.get("mime", "")),
            "code": rec.get("code", "Code 11: Culture")
        })

    index["assets"] = assets
    save_asset_index(index)

    # 2) Calendar seed — nothing to do here except acknowledge presence
    has_cal = SEED_CALENDAR_FILE.exists()

    return jsonify({
        "success": True,
        "added_assets": len(index["assets"]) - before,
        "has_calendar_seed": has_cal
    })

@app.post("/reset-db")
def reset_db():
    """
    Clears asset index (doesn't delete files), so you can re-seed cleanly.
    """
    write_json(ASSET_INDEX, {"assets": []})
    return jsonify({"success": True, "message": "Asset index cleared. Files on disk were not deleted."})

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    # Local run: flask dev server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5103)), debug=False)
