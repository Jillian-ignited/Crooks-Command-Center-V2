#!/usr/bin/env python3
"""
CROOKS & CASTLES COMMAND CENTER — Render-stable
- Uses project-relative folders (no /home/ubuntu)
- Table schema and queries aligned
- Seeder endpoint to create 7-day calendar, demo assets, and a sample report
"""

import os, sys, uuid, json, sqlite3, logging, csv
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

try:
    from PIL import Image
except Exception:
    Image = None

# ---------------- Basics ----------------
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

app = Flask(__name__)
CORS(app)

# ---------------- DB ----------------
def db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    con = db(); cur = con.cursor()

    # Assets schema (names match code)
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
    )
    """)

    # Posts schema (names match code)
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
    )
    """)

    # Performance reports (for uploads)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS performance_reports (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        insights TEXT NOT NULL
    )
    """)
    con.commit(); con.close()

init_db()

# ---------------- Utilities ----------------
def safe_int(x, default=0):
    try: return int(x)
    except: return default

def calculate_post_badge_score(post_row):
    # Light-weight, deterministic
    score = 70
    content = (post_row["content"] or "")
    hashtags = (post_row["hashtags"] or "")
    platform = (post_row["platform"] or "").lower()
    if 100 <= len(content) <= 300: score += 10
    if hashtags and len(hashtags.split()) >= 3: score += 5
    if platform in ("instagram","instagram_reels","tiktok"): score += 5
    if post_row["assigned_code"]: score += 5
    return min(score, 100)

def calculate_asset_badge_score(filename, content_type):
    score = 75
    if str(content_type).startswith("image/"): score += 10
    if str(content_type).startswith("video/"): score += 15
    name = filename.lower()
    if any(k in name for k in ("crooks","castle","heritage","street")): score += 5
    return min(score, 100)

# ---------------- UI (kept your inline UI) ----------------
@app.route("/")
def index():
    return render_template_string("""
<!doctype html><html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Crooks & Castles Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
body{font-family:Inter,system-ui,Arial;background:#0a0a0a;color:#fff;margin:0}
.header{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;border-bottom:1px solid #222;background:#000}
.logo{font-weight:700;text-transform:uppercase;letter-spacing:2px}
.nav-tabs{display:flex;gap:12px}
.nav-tab{background:#111;border:1px solid #333;color:#fff;padding:10px 14px;border-radius:6px;cursor:pointer}
.nav-tab.active,.nav-tab:hover{background:#1a1a1a}
.main{max-width:1200px;margin:0 auto;padding:24px}
.section{display:none;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:20px}
.section.active{display:block}
.section-title{font-size:20px;font-weight:600;margin-bottom:14px}
.calendar-btn{margin-right:8px}
.day-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:12px;margin-bottom:10px}
.day-header{color:#22c55e;font-weight:600;margin-bottom:6px}
.post-item{background:rgba(0,0,0,.35);border-left:3px solid #22c55e;border-radius:6px;padding:10px;margin:6px 0}
.badge{display:inline-block;padding:2px 6px;border-radius:4px;font-size:12px;margin-left:8px}
.badge.ready{background:#22c55e}
.badge.review{background:#ef4444}
.asset-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-top:10px}
.asset-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:12px}
.asset-thumb{height:140px;background:#111;border-radius:6px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.asset-thumb img{max-width:100%;max-height:100%;object-fit:cover}
.upload-area{border:2px dashed rgba(255,255,255,.3);border-radius:8px;padding:18px;text-align:center;margin-bottom:12px}
.btn{background:#222;border:1px solid #555;color:#fff;border-radius:6px;padding:8px 12px;text-decoration:none}
.loading{opacity:.7}
</style>
</head><body>
<div class="header">
  <div class="logo">🏰 Crooks & Castles Command Center</div>
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="show('calendar', this)">Calendar</button>
    <button class="nav-tab" onclick="show('assets', this)">Assets</button>
    <button class="nav-tab" onclick="show('agency', this)">Agency</button>
  </div>
</div>
<div class="main">
  <div id="calendar" class="section active">
    <div class="section-title">Strategic Calendar Planning</div>
    <div>
      <button class="calendar-btn btn" onclick="setView('7day', this)">7-Day Tactical</button>
      <button class="calendar-btn btn" onclick="setView('30day', this)">30-Day Strategic</button>
      <button class="calendar-btn btn" onclick="setView('60day', this)">60-Day Opportunities</button>
      <button class="calendar-btn btn" onclick="setView('90day', this)">90-Day+ Vision</button>
    </div>
    <div id="cal" style="margin-top:10px"><div class="loading">Loading…</div></div>
  </div>

  <div id="assets" class="section">
    <div class="section-title">Asset Library</div>
    <div class="upload-area" onclick="document.getElementById('files').click()">📁 Click to upload</div>
    <input id="files" type="file" multiple accept="image/*,video/*" style="display:none" onchange="uploadAssets(this.files)">
    <div id="grid" class="asset-grid"><div class="loading">Loading…</div></div>
  </div>

  <div id="agency" class="section">
    <div class="section-title">High Voltage Digital — Deliverables</div>
    <div id="agencyBox"><div class="loading">Loading…</div></div>
  </div>
</div>

<script>
let view='7day';
function show(id, el){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  if(id==='calendar') loadCal();
  if(id==='assets') loadAssets();
  if(id==='agency') loadAgency();
}
function setView(v, el){ view=v; loadCal(); }
async function loadCal(){
  const box=document.getElementById('cal');
  try{
    const r=await fetch('/api/calendar/'+view);
    const d=await r.json();
    if(view==='7day'){
      let html='<h3>7-Day Tactical Execution</h3>';
      (d.calendar_data||[]).forEach(day=>{
        html+=`<div class="day-card">
          <div class="day-header">${day.day_name}, ${day.formatted_date}</div>`;
        if((day.posts||[]).length){
          day.posts.forEach(p=>{
            const cls=(p.badge_score||0)>=95?'ready':'review';
            html+=`<div class="post-item">
              <div><strong>${p.title}</strong><span class="badge ${cls}">${p.badge_score||0}%</span></div>
              <div style="opacity:.8">${p.platform} • ${p.time_slot} • ${p.code_name||'No Code'}</div>
              <div style="margin-top:6px;font-size:14px">${p.content||''}</div>
              <div style="margin-top:4px;font-size:12px;opacity:.8">${p.hashtags||''}</div>
            </div>`;
          });
        } else {
          html+='<div class="loading">No posts scheduled</div>';
        }
        html+='</div>';
      });
      box.innerHTML=html;
    } else {
      box.innerHTML='<pre style="white-space:pre-wrap">'+JSON.stringify(d,null,2)+'</pre>';
    }
  }catch(e){ box.innerHTML='<div class="loading">Error</div>'; }
}
async function loadAssets(){
  const box=document.getElementById('grid');
  try{
    const r=await fetch('/api/assets'); const d=await r.json();
    if(d.success && d.assets.length){
      box.innerHTML=d.assets.map(a=>`
      <div class="asset-card">
        <div class="asset-thumb"><img src="/api/thumbnail/${a.id}" onerror="this.style.display='none'"></div>
        <div><strong>${a.original_name||a.id}</strong></div>
        <div style="opacity:.8;font-size:12px">Code ${a.assigned_code||'—'} • ${a.badge_score||0}%</div>
        <div style="margin-top:8px"><a class="btn" href="/api/download/${a.id}">Download</a></div>
      </div>`).join('');
    } else {
      box.innerHTML='<div class="loading">No assets found</div>';
    }
  }catch(e){ box.innerHTML='<div class="loading">Error</div>'; }
}
async function loadAgency(){
  const box=document.getElementById('agencyBox');
  try{
    const r=await fetch('/api/deliverables'); const d=await r.json();
    if(!d.success){ box.innerHTML='<div class="loading">Error</div>'; return; }
    const p=d.current_progress;
    box.innerHTML = `
      <div style="display:grid;gap:12px">
        <div><strong>${d.current_phase.name}</strong> • ${d.current_phase.period} • ${d.current_phase.budget}</div>
        ${Object.entries(p).map(([k,v])=>`
          <div>
            <div style="display:flex;justify-content:space-between">
              <div>${k.replace('_',' ')}</div><div>${v.current}/${v.target} • ${v.progress}%</div>
            </div>
            <div style="height:8px;background:#222;border-radius:6px;overflow:hidden">
              <div style="height:8px;background:#22c55e;width:${v.progress}%"></div>
            </div>
          </div>
        `).join('')}
        <div><strong>Overall:</strong> ${d.overall_progress}%</div>
      </div>`;
  }catch(e){ box.innerHTML='<div class="loading">Error</div>'; }
}
async function uploadAssets(files){
  if(!files||!files.length) return;
  const fd=new FormData(); [...files].forEach(f=>fd.append('files',f));
  const r=await fetch('/api/upload-assets',{method:'POST',body:fd});
  const d=await r.json();
  if(d.success) loadAssets(); else alert(d.message||'Upload failed');
}
document.addEventListener('DOMContentLoaded', loadCal);
</script>
</body></html>
    """)

# ---------------- Calendar API ----------------
def _row_to_post(row):
    # Compute badge score if missing
    badge = row["badge_score"] if row["badge_score"] is not None else calculate_post_badge_score(row)
    # format time slot
    ts = "Not scheduled"
    if row["scheduled_date"]:
        try:
            ts = datetime.fromisoformat(row["scheduled_date"]).strftime("%H:%M CT")
        except:
            ts = row["scheduled_date"]
    # map code name
    code_name = f"Code {row['assigned_code']}" if row["assigned_code"] else "No Code"
    return {
        "id": row["id"],
        "title": row["title"],
        "content": (row["content"] or ""),
        "hashtags": (row["hashtags"] or ""),
        "platform": (row["platform"] or ""),
        "time_slot": ts,
        "assigned_code": row["assigned_code"],
        "code_name": code_name,
        "asset_name": row["mapped_asset_id"],
        "badge_score": badge,
        "status": "Castle Ready" if badge >= 95 else "Needs Review"
    }

@app.get("/api/calendar/<view_type>")
def api_calendar(view_type):
    con = db(); cur = con.cursor()
    today = datetime.utcnow().date()

    if view_type == "7day":
        out = []
        for i in range(7):
            d = today + timedelta(days=i)
            dstr = d.isoformat()
            cur.execute("""
                SELECT * FROM posts
                WHERE date(substr(scheduled_date,1,10)) = ?
                ORDER BY scheduled_date
            """, (dstr,))
            posts = [_row_to_post(r) for r in cur.fetchall()]
            out.append({
                "date": dstr,
                "day_name": d.strftime("%A"),
                "formatted_date": d.strftime("%b %d"),
                "posts": posts
            })
        con.close()
        return jsonify({"success": True, "view_type": "7day", "calendar_data": out})

    elif view_type == "30day":
        out = []
        for i in range(30):
            d = today + timedelta(days=i)
            dstr = d.isoformat()
            cur.execute("""
                SELECT * FROM posts
                WHERE date(substr(scheduled_date,1,10)) = ?
                ORDER BY scheduled_date
            """, (dstr,))
            posts = [_row_to_post(r) for r in cur.fetchall()]
            if posts:
                out.append({
                    "date": dstr,
                    "day_name": d.strftime("%A"),
                    "formatted_date": d.strftime("%b %d"),
                    "posts": posts
                })
        con.close()
        return jsonify({"success": True, "view_type": "30day", "calendar_data": out})

    elif view_type == "60day":
        con.close()
        opportunities = [
            {"date":"2025-10-15","event":"Hip Hop History Month","type":"Cultural Heritage","priority":"High"},
            {"date":"2025-11-01","event":"BFCM Prep Launch","type":"Commercial Campaign","priority":"Critical"}
        ]
        return jsonify({"success": True, "view_type":"60day", "opportunities": opportunities})

    elif view_type == "90day":
        con.close()
        long_range = [
            {"date":"2026-01-15","milestone":"TikTok Shop Launch","type":"Platform Expansion"},
            {"date":"2026-02-01","milestone":"Black History Month","type":"Cultural Heritage"}
        ]
        return jsonify({"success": True, "view_type":"90day", "long_range": long_range})

    con.close()
    return jsonify({"success": False, "message": "unknown view"}), 400

# ---------------- Assets API ----------------
@app.get("/api/assets")
def api_assets():
    con = db(); cur = con.cursor()
    cur.execute("SELECT * FROM assets ORDER BY created_date DESC")
    rows = cur.fetchall(); con.close()
    assets = [{
        "id": r["id"],
        "original_name": r["original_name"],
        "file_type": r["file_type"],
        "badge_score": r["badge_score"],
        "assigned_code": r["assigned_code"],
        "cultural_relevance": r["cultural_relevance"],
        "created_date": r["created_date"]
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
    uploaded = 0
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

# ---------------- Agency / Deliverables ----------------
@app.get("/api/deliverables")
def api_deliverables():
    con = db(); cur = con.cursor()
    now = datetime.utcnow()
    month = now.strftime("%Y-%m")

    # Count deliverables
    cur.execute("SELECT COUNT(*) c FROM posts WHERE substr(scheduled_date,1,7)=?", (month,))
    posts = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM assets WHERE substr(created_date,1,7)=?", (month,))
    creatives = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM posts WHERE substr(scheduled_date,1,7)=? AND lower(platform)='email'", (month,))
    emails = cur.fetchone()["c"]
    con.close()

    # Phase logic
    if now.year==2025 and now.month in (9,10):
        phase = ("phase1","Foundation & Awareness","Sep–Oct 2025","$4,000/month",12,4,2)
    elif now.year==2025 and now.month in (11,12):
        phase = ("phase2","Growth & Q4 Push","Nov–Dec 2025","$7,500/month",16,8,6)
    else:
        phase = ("phase3","Full Retainer + TikTok Shop","Jan 2026+","$10,000/month",20,12,8)

    pid, pname, pperiod, pbudget, tgt_posts, tgt_creatives, tgt_emails = phase
    prog_posts = min(100, round(posts / max(1,tgt_posts) * 100, 1))
    prog_creatives = min(100, round(creatives / max(1,tgt_creatives) * 100, 1))
    prog_emails = min(100, round(emails / max(1,tgt_emails) * 100, 1))
    overall = round((prog_posts + prog_creatives + prog_emails)/3, 1)

    def status(pct, cur, tgt):
        if cur > tgt: return "ahead"
        if pct >= 80: return "on_track"
        return "behind"

    return jsonify({
        "success": True,
        "current_phase": {"id": pid, "name": pname, "period": pperiod, "budget": pbudget},
        "current_progress": {
            "social_posts":{"current":posts,"target":tgt_posts,"progress":prog_posts,"outstanding":max(0,tgt_posts-posts),"status":status(prog_posts, posts, tgt_posts)},
            "ad_creatives":{"current":creatives,"target":tgt_creatives,"progress":prog_creatives,"outstanding":max(0,tgt_creatives-creatives),"status":status(prog_creatives, creatives, tgt_creatives)},
            "email_campaigns":{"current":emails,"target":tgt_emails,"progress":prog_emails,"outstanding":max(0,tgt_emails-emails),"status":status(prog_emails, emails, tgt_emails)}
        },
        "overall_progress": overall,
        "next_month_preview": {"scheduled_posts": 0, "month": (now + timedelta(days=32)).strftime("%B %Y")},
        "phase_transitions": {
            "next_phase": "phase2" if pid=="phase1" else "phase3" if pid=="phase2" else None,
            "transition_date": "2025-11-01" if pid=="phase1" else "2026-01-01" if pid=="phase2" else None
        }
    })

# ---------------- Seeder (one-click) ----------------
@app.get("/admin/seed")
def admin_seed():
    con = db(); cur = con.cursor()

    # Seed 7-day posts
    today = datetime.utcnow().date()
    titles = [
        "Drop Tease: Crown Logo Tee",
        "NFL Kickoff Street Style — No Code 75%",
        "Monday Night Prep — No Code 75%",
        "Warehouse BTS: Embroidery",
        "Street Interview: Who Runs the Castle?",
        "Fit Check Friday: Crown + Denim",
        "Weekend Offer: 15% Off Select"
    ]
    platforms = ["IG","Instagram","TikTok","IG Reel","TikTok","IG","Email"]
    times = ["09:00","00:00","00:00","09:00","12:00","09:00","10:00"]

    # clear existing demo rows (optional)
    cur.execute("DELETE FROM posts")

    for i in range(7):
        pid = uuid.uuid4().hex
        dt_iso = datetime.combine(today + timedelta(days=i), datetime.min.time()).strftime("%Y-%m-%dT")+times[i]+":00"
        cur.execute("""
            INSERT INTO posts (id, title, content, hashtags, platform, scheduled_date, assigned_code, mapped_asset_id, status, badge_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pid, titles[i],
            "Game day drip. Crown on. Street culture first.",
            "#crooksandcastles #street #culture",
            platforms[i],
            dt_iso, 5 if i%2==0 else 11, None, "planned", 90+i%5
        ))

    # Seed one image asset
    aid = uuid.uuid4().hex
    img_path = ASSETS_DIR / f"{aid}.png"
    if Image:
        img = Image.new("RGB",(800,450),(20,20,20))
        for x in range(0,800,10):
            img.putpixel((x,(x//10)%450),(240,240,240))
        img.save(img_path)
    cur.execute("""
        INSERT INTO assets (id, original_name, file_path, file_type, file_size, badge_score, assigned_code, cultural_relevance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (aid, "seed_sample.png", str(img_path), "image/png", img_path.stat().st_size if img_path.exists() else 0, 95, 5, "Seed"))

    # Seed a tiny CSV report (for your own analysis later if needed)
    REPORTS_DIR.mkdir(exist_ok=True, parents=True)
    rp = REPORTS_DIR / "report_seed.csv"
    with rp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date","channel","spend","impressions","clicks","conversions","revenue"])
        w.writerow([today.isoformat(),"IG",120.5,25000,430,38,1420.0])
        w.writerow([(today - timedelta(days=1)).isoformat(),"TikTok",80.0,18000,220,12,420.0])

    con.commit(); con.close()
    return jsonify({"ok": True, "seeded": {"posts": 7, "asset": "seed_sample.png", "report": "report_seed.csv"}})

# ---------------- Health ----------------
@app.get("/healthz")
def healthz(): return {"ok": True}, 200

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8080")))
