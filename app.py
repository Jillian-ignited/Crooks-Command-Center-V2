#!/usr/bin/env python3
"""
CROOKS & CASTLES COMMAND CENTER — Render-stable + Auto-migrate
"""

import os, uuid, json, sqlite3, logging, csv
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS

try:
    from PIL import Image
except Exception:
    Image = None

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("crooks")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "agency_reports"
for d in (DATA_DIR, ASSETS_DIR, UPLOADS_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "content_machine.db"
DB_BACKUP = BASE_DIR / "content_machine.db.bak"

app = Flask(__name__)
CORS(app)

# ---------- DB helpers ----------
def db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

REQUIRED_SCHEMAS = {
    "assets": {"id","original_name","file_path","file_type","file_size","badge_score","assigned_code","cultural_relevance","created_date","thumbnail_path"},
    "posts": {"id","title","content","hashtags","platform","scheduled_date","assigned_code","mapped_asset_id","status","badge_score","created_date"},
    "performance_reports": {"id","filename","filepath","upload_date","insights"},
}

def table_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = {r["name"] for r in cur.fetchall()}
    return cols

def init_db():
    con = db(); cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        original_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        badge_score INTEGER DEFAULT 0,
        assigned_code INTEGER,
        cultural_relevance TEXT,
        created_date TEXT DEFAULT (datetime('now')),
        thumbnail_path TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        hashtags TEXT,
        platform TEXT,
        scheduled_date TEXT,
        assigned_code INTEGER,
        mapped_asset_id TEXT,
        status TEXT DEFAULT 'draft',
        badge_score INTEGER DEFAULT 0,
        created_date TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (mapped_asset_id) REFERENCES assets(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS performance_reports (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        insights TEXT NOT NULL
    )""")
    con.commit(); con.close()

def ensure_schema():
    """Auto-migrate: if a required table is missing or columns mismatch, back up DB and recreate fresh."""
    fresh_needed = False
    if not DB_PATH.exists():
        fresh_needed = True
    else:
        con = db()
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {r["name"] for r in cur.fetchall()}
        for t in REQUIRED_SCHEMAS:
            if t not in existing_tables:
                fresh_needed = True
                break
        if not fresh_needed:
            # verify columns
            for t, req_cols in REQUIRED_SCHEMAS.items():
                cols = table_columns(con, t)
                if not req_cols.issubset(cols):
                    log.warning("Schema mismatch for %s. Have: %s Need: %s", t, cols, req_cols)
                    fresh_needed = True
                    break
        con.close()

    if fresh_needed:
        if DB_PATH.exists():
            try:
                DB_BACKUP.write_bytes(DB_PATH.read_bytes())
                DB_PATH.unlink()
                log.info("Backed up old DB -> %s and recreated a fresh DB", DB_BACKUP)
            except Exception as e:
                log.error("Failed to backup old DB: %s", e)
        init_db()
    else:
        log.info("Schema OK")

ensure_schema()

# ---------- scoring ----------
def calculate_post_badge_score(row):
    score = 70
    content = (row["content"] or "")
    hashtags = (row["hashtags"] or "")
    platform = (row["platform"] or "").lower()
    if 100 <= len(content) <= 300: score += 10
    if hashtags and len(hashtags.split()) >= 3: score += 5
    if platform in ("instagram","instagram_reels","tiktok","ig","ig reel"): score += 5
    if row["assigned_code"]: score += 5
    return min(score, 100)

def calculate_asset_badge_score(filename, content_type):
    score = 75
    ct = str(content_type or "")
    if ct.startswith("image/"): score += 10
    if ct.startswith("video/"): score += 15
    name = (filename or "").lower()
    if any(k in name for k in ("crooks","castle","heritage","street")): score += 5
    return min(score, 100)

# ---------- UI (minimal shell; your data comes from APIs) ----------
@app.route("/")
def index():
    return render_template_string("""
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crooks & Castles Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>body{font-family:Inter,system-ui;background:#0a0a0a;color:#fff;margin:0} .wrap{max-width:1100px;margin:0 auto;padding:20px}
h1{font-size:20px} .card{background:#111;border:1px solid #222;border-radius:10px;padding:16px;margin:12px 0}
.btn{display:inline-block;background:#222;border:1px solid #444;color:#fff;padding:8px 12px;border-radius:6px;text-decoration:none}
.badge{display:inline-block;background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;margin-left:6px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.item{background:#151515;border:1px solid #222;border-radius:8px;padding:10px}</style></head>
<body><div class="wrap">
<h1>🏰 Crooks & Castles Command Center <span class="badge">Live</span></h1>
<div class="card">
  <div><a class="btn" href="/admin/seed">Seed demo data</a>
       <a class="btn" href="/debug/check">Debug check</a>
       <a class="btn" href="/admin/reset_db" onclick="return confirm('Reset DB?')">Reset DB</a></div>
  <p style="opacity:.8;margin-top:8px">APIs: <a class="btn" href="/api/calendar/7day">/api/calendar/7day</a> <a class="btn" href="/api/assets">/api/assets</a> <a class="btn" href="/api/deliverables">/api/deliverables</a></p>
</div>
<div class="card">
  <h3>Asset upload</h3>
  <input id="f" type="file" multiple><button class="btn" onclick="up()">Upload</button>
  <pre id="out" style="white-space:pre-wrap;background:#000;padding:10px;border-radius:6px;margin-top:10px"></pre>
</div>
<script>
async function up(){
  const i=document.getElementById('f'); if(!i.files.length){alert('choose files');return}
  const fd=new FormData(); [...i.files].forEach(f=>fd.append('files',f));
  const r=await fetch('/api/upload-assets',{method:'POST',body:fd}); document.getElementById('out').textContent=await r.text();
}
</script>
</div></body></html>
    """)

# ---------- Calendar ----------
def _row_to_post(row):
    badge = row["badge_score"] if row["badge_score"] is not None else calculate_post_badge_score(row)
    ts = "Not scheduled"
    if row["scheduled_date"]:
        try:
            ts = datetime.fromisoformat(row["scheduled_date"]).strftime("%H:%M CT")
        except:
            ts = row["scheduled_date"]
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"] or "",
        "hashtags": row["hashtags"] or "",
        "platform": row["platform"] or "",
        "time_slot": ts,
        "assigned_code": row["assigned_code"],
        "code_name": f"Code {row['assigned_code']}" if row["assigned_code"] else "No Code",
        "asset_name": row["mapped_asset_id"],
        "badge_score": badge,
        "status": "Castle Ready" if badge >= 95 else "Needs Review"
    }

@app.get("/api/calendar/<view_type>")
def api_calendar(view_type):
    con = db(); cur = con.cursor()
    today = datetime.utcnow().date()
    if view_type == "7day":
        out=[]
        for i in range(7):
            d = today + timedelta(days=i)
            dstr = d.isoformat()
            cur.execute("""
                SELECT * FROM posts
                WHERE date(substr(scheduled_date,1,10)) = ?
                ORDER BY scheduled_date
            """, (dstr,))
            posts=[_row_to_post(r) for r in cur.fetchall()]
            out.append({"date": dstr, "day_name": d.strftime("%A"), "formatted_date": d.strftime("%b %d"), "posts": posts})
        con.close()
        return jsonify({"success": True, "view_type":"7day", "calendar_data": out})
    elif view_type == "30day":
        out=[]
        for i in range(30):
            d = today + timedelta(days=i)
            dstr = d.isoformat()
            cur.execute("""
                SELECT * FROM posts
                WHERE date(substr(scheduled_date,1,10)) = ?
                ORDER BY scheduled_date
            """, (dstr,))
            posts=[_row_to_post(r) for r in cur.fetchall()]
            if posts:
                out.append({"date": dstr, "day_name": d.strftime("%A"), "formatted_date": d.strftime("%b %d"), "posts": posts})
        con.close()
        return jsonify({"success": True, "view_type":"30day", "calendar_data": out})
    elif view_type == "60day":
        con.close()
        return jsonify({"success": True, "view_type":"60day",
                        "opportunities":[{"date":"2025-10-15","event":"Hip Hop History Month","priority":"High"},
                                         {"date":"2025-11-01","event":"BFCM Prep Launch","priority":"Critical"}]})
    elif view_type == "90day":
        con.close()
        return jsonify({"success": True, "view_type":"90day",
                        "long_range":[{"date":"2026-01-15","milestone":"TikTok Shop Launch"},
                                      {"date":"2026-02-01","milestone":"Black History Month"}]})
    con.close()
    return jsonify({"success": False, "message":"unknown view"}), 400

# ---------- Assets ----------
@app.get("/api/assets")
def api_assets():
    con = db(); cur = con.cursor()
    cur.execute("SELECT * FROM assets ORDER BY created_date DESC")
    rows = cur.fetchall(); con.close()
    assets=[{
        "id": r["id"], "original_name": r["original_name"], "file_type": r["file_type"],
        "badge_score": r["badge_score"], "assigned_code": r["assigned_code"],
        "cultural_relevance": r["cultural_relevance"], "created_date": r["created_date"]
    } for r in rows]
    return jsonify({"success": True, "assets": assets})

@app.get("/api/thumbnail/<asset_id>")
def api_thumb(asset_id):
    con = db(); cur = con.cursor()
    cur.execute("SELECT file_path, file_type FROM assets WHERE id=?", (asset_id,))
    row = cur.fetchone(); con.close()
    if not row: return jsonify({"success": False, "message":"not found"}), 404
    p = Path(row["file_path"])
    if p.exists() and str(row["file_type"]).startswith("image/"):
        return send_file(str(p))
    return jsonify({"success": False, "message":"no thumbnail"}), 404

@app.get("/api/download/<asset_id>")
def api_download(asset_id):
    con = db(); cur = con.cursor()
    cur.execute("SELECT file_path, original_name FROM assets WHERE id=?", (asset_id,))
    row = cur.fetchone(); con.close()
    if not row: return jsonify({"success": False, "message":"not found"}), 404
    return send_file(row["file_path"], as_attachment=True, download_name=row["original_name"])

@app.post("/api/upload-assets")
def api_upload_assets():
    if "files" not in request.files: return jsonify({"success": False, "message":"no files"}), 400
    files = request.files.getlist("files")
    con = db(); cur = con.cursor()
    uploaded=0
    for f in files:
        if not f.filename: continue
        aid = uuid.uuid4().hex
        ext = os.path.splitext(f.filename)[1]
        dest = ASSETS_DIR / f"{aid}{ext}"
        f.save(dest)
        badge = calculate_asset_badge_score(f.filename, f.mimetype)
        cur.execute("""
            INSERT INTO assets (id, original_name, file_path, file_type, file_size, badge_score, assigned_code, cultural_relevance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (aid, f.filename, str(dest), f.mimetype or "application/octet-stream",
              dest.stat().st_size, badge, None, "User upload"))
        uploaded += 1
    con.commit(); con.close()
    return jsonify({"success": True, "uploaded_count": uploaded})

# ---------- Agency / Deliverables ----------
@app.get("/api/deliverables")
def api_deliverables():
    con = db(); cur = con.cursor()
    now = datetime.utcnow()
    month = now.strftime("%Y-%m")
    # counts
    cur.execute("SELECT COUNT(*) c FROM posts WHERE substr(scheduled_date,1,7)=?", (month,))
    posts = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM assets WHERE substr(created_date,1,7)=?", (month,))
    creatives = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM posts WHERE substr(scheduled_date,1,7)=? AND lower(platform)='email'", (month,))
    emails = cur.fetchone()["c"]
    con.close()
    # phases
    if now.year==2025 and now.month in (9,10):
        pid, name, period, budget, tp, tc, te = ("phase1","Foundation & Awareness","Sep–Oct 2025","$4,000/month",12,4,2)
    elif now.year==2025 and now.month in (11,12):
        pid, name, period, budget, tp, tc, te = ("phase2","Growth & Q4 Push","Nov–Dec 2025","$7,500/month",16,8,6)
    else:
        pid, name, period, budget, tp, tc, te = ("phase3","Full Retainer + TikTok Shop","Jan 2026+","$10,000/month",20,12,8)
    def pct(cur,tgt): return min(100, round(cur/max(1,tgt)*100,1))
    def status(cur,tgt,p): return "ahead" if cur>tgt else "on_track" if p>=80 else "behind"
    p1=pct(posts,tp); p2=pct(creatives,tc); p3=pct(emails,te)
    return jsonify({
        "success": True,
        "current_phase":{"id":pid,"name":name,"period":period,"budget":budget},
        "current_progress":{
            "social_posts":{"current":posts,"target":tp,"progress":p1,"outstanding":max(0,tp-posts),"status":status(posts,tp,p1)},
            "ad_creatives":{"current":creatives,"target":tc,"progress":p2,"outstanding":max(0,tc-creatives),"status":status(creatives,tc,p2)},
            "email_campaigns":{"current":emails,"target":te,"progress":p3,"outstanding":max(0,te-emails),"status":status(emails,te,p3)}
        },
        "overall_progress": round((p1+p2+p3)/3,1)
    })

# ---------- Admin: seed/reset/debug ----------
@app.get("/admin/seed")
def admin_seed():
    con = db(); cur = con.cursor()
    # clear demo posts (optional)
    cur.execute("DELETE FROM posts")
    today = datetime.utcnow().date()
    titles = [
        "NFL Season Kickoff Street Style",
        "Monday Night Football Prep",
        "Warehouse BTS: Embroidery",
        "Street Interview: Who Runs the Castle?",
        "Fit Check Friday: Crown + Denim",
        "Weekend Offer: 15% Off Select",
        "Drop Tease: Crown Logo Tee"
    ]
    platforms = ["Instagram Story","TikTok","IG Reel","TikTok","IG","Email","IG"]
    times = ["00:00","00:00","09:00","12:00","09:00","10:00","09:00"]
    for i in range(7):
        pid = uuid.uuid4().hex
        dt_iso = f"{(today+timedelta(days=i)).isoformat()}T{times[i]}:00"
        cur.execute("""
            INSERT INTO posts (id,title,content,hashtags,platform,scheduled_date,assigned_code,mapped_asset_id,status,badge_score)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (pid, titles[i],
              "Game day drip. Crown on. Street culture first.",
              "#crooksandcastles #street #culture",
              platforms[i], dt_iso, 5 if i%2==0 else 11, None, "planned", 92))
    # seed one asset
    aid = uuid.uuid4().hex
    p = ASSETS_DIR / f"{aid}.png"
    if Image:
        img = Image.new("RGB",(800,450),(18,18,18)); img.save(p)
    cur.execute("""
        INSERT INTO assets (id, original_name, file_path, file_type, file_size, badge_score, assigned_code, cultural_relevance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (aid, "seed_sample.png", str(p), "image/png", p.stat().st_size if p.exists() else 0, 95, 5, "Seed"))
    # seed report
    rp = REPORTS_DIR / "report_seed.csv"
    with rp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["date","channel","spend","impressions","clicks","conversions","revenue"])
        w.writerow([today.isoformat(),"IG",120.5,25000,430,38,1420.0])
        w.writerow([(today - timedelta(days=1)).isoformat(),"TikTok",80.0,18000,220,12,420.0])
    con.commit(); con.close()
    return jsonify({"ok": True, "seeded": {"posts": 7, "asset": "seed_sample.png", "report": "report_seed.csv"}})

@app.get("/admin/reset_db")
def admin_reset_db():
    try:
        if DB_PATH.exists():
            DB_BACKUP.write_bytes(DB_PATH.read_bytes())
            DB_PATH.unlink()
        init_db()
        return jsonify({"ok": True, "message": "DB reset. Now hit /admin/seed."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/debug/check")
def debug_check():
    info = {
        "base_dir": str(BASE_DIR),
        "exists": {
            "assets_dir": ASSETS_DIR.exists(),
            "uploads_dir": UPLOADS_DIR.exists(),
            "reports_dir": REPORTS_DIR.exists(),
            "db": DB_PATH.exists(),
        },
        "assets_files": [p.name for p in ASSETS_DIR.glob("*")][:10],
        "reports_files": [p.name for p in REPORTS_DIR.glob("*")][:10],
        "schema": {}
    }
    try:
        con = db()
        for t in ("assets","posts","performance_reports"):
            try:
                info["schema"][t] = list(table_columns(con, t))
            except Exception as e:
                info["schema"][t] = f"error: {e}"
        con.close()
    except Exception as e:
        info["schema_error"] = str(e)
    return jsonify(info)

# ---------- Health ----------
@app.get("/healthz")
def healthz(): return {"ok": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8080")))
