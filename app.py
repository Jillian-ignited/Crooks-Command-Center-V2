#!/usr/bin/env python3
"""
Crooks & Castles Command Center — CLEAN API + UI WRAPPER
- Keeps simple demo APIs (/api/calendar/7day, /api/assets, /api/deliverables)
- Adds a shell front-end at '/' that calls those APIs
- Adds /ui route to serve Manus HTML if present at src/static/index_enhanced_planning.html
"""

import datetime
from flask import Flask, jsonify, send_from_directory, render_template_string
from flask_cors import CORS

# If you have your Manus HTML and assets, put them under src/static/
app = Flask(__name__, static_folder="src/static", static_url_path="/static")
CORS(app)

# ---------- HEALTH ----------
@app.get("/healthz")
def health():
    return jsonify({"status": "ok", "message": "🏰 Crooks Command Center is alive"})

# ---------- DEMO APIs (keep your real ones if you have them) ----------
@app.get("/api/calendar/7day")
def calendar_7day():
    today = datetime.date.today()
    data = []
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        data.append({
            "date": str(day),
            "day_name": day.strftime("%A"),
            "formatted_date": day.strftime("%b %d"),
            "posts": [{
                "title": f"Demo Post {i+1}",
                "platform": "Instagram",
                "time_slot": "12:00 CT",
                "code_name": "Code 05: Crooks Wear Crowns",
                "badge_score": 95,
                "hashtags": "#crooksandcastles #street #culture",
                "content": f"Sample content for {day.strftime('%A')}"
            }]
        })
    return jsonify({"success": True, "view_type": "7day", "calendar_data": data})

@app.get("/api/assets")
def assets():
    return jsonify({
        "success": True,
        "assets": [
            {"id": "1", "original_name": "demo_asset.png", "file_type": "image/png", "badge_score": 95, "assigned_code": 5, "created_date": str(datetime.date.today())},
            {"id": "2", "original_name": "demo_video.mp4", "file_type": "video/mp4", "badge_score": 85, "assigned_code": 11, "created_date": str(datetime.date.today())}
        ]
    })

@app.get("/api/deliverables")
def deliverables():
    return jsonify({
        "success": True,
        "current_phase": {"name": "Foundation & Awareness", "period": "Sep–Oct 2025", "budget": "$4,000/month"},
        "current_progress": {
            "social_posts": {"current": 6, "target": 12, "progress": 50, "outstanding": 6, "status": "on_track"},
            "ad_creatives": {"current": 2, "target": 4, "progress": 50, "outstanding": 2, "status": "on_track"},
            "email_campaigns": {"current": 1, "target": 2, "progress": 50, "outstanding": 1, "status": "on_track"},
        },
        "overall_progress": 50.0
    })

# ---------- UI: Manus HTML (if present) ----------
@app.get("/ui")
def serve_manus_ui():
    # If you committed src/static/index_enhanced_planning.html, this will serve it
    return send_from_directory("src/static", "index_enhanced_planning.html")

# ---------- UI: Shell Front-End ----------
@app.get("/")
def index():
    # Minimal self-contained UI that calls your APIs
    return render_template_string("""
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crooks & Castles Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
body{font-family:Inter,system-ui;background:#0a0a0a;color:#fff;margin:0}
.wrap{max-width:1200px;margin:0 auto;padding:20px}
h1{font-size:20px;margin:0 0 12px}
.card{background:#111;border:1px solid #222;border-radius:12px;padding:16px;margin:12px 0}
.btn{display:inline-block;background:#1d1d1d;border:1px solid #404040;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none;margin-right:8px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.item{background:#151515;border:1px solid #222;border-radius:10px;padding:12px}
.badge{display:inline-block;background:#22c55e;color:#000;padding:2px 6px;border-radius:6px;margin-left:6px}
.tabbar{display:flex;gap:8px;margin:8px 0 12px}
.tab{cursor:pointer;padding:8px 12px;border:1px solid #333;border-radius:8px;background:#101010}
.tab.active{border-color:#22c55e}
.mono{font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:12px; color:#cbd5e1}
hr{border:0;border-top:1px solid #222;margin:16px 0}
.small{opacity:.75;font-size:12px}
</style>
</head>
<body>
<div class="wrap">
  <h1>🏰 Crooks & Castles Command Center <span class="badge">Live</span></h1>
  <div class="card">
    <div class="tabbar">
      <div id="tab-cal" class="tab active" onclick="show('cal')">Calendar</div>
      <div id="tab-assets" class="tab" onclick="show('assets')">Assets</div>
      <div id="tab-agency" class="tab" onclick="show('agency')">Agency</div>
      <div id="tab-raw" class="tab" onclick="show('raw')">Raw API</div>
    </div>
    <div id="view-cal">
      <h3>7-Day Tactical</h3>
      <div id="cal" class="grid"></div>
    </div>
    <div id="view-assets" style="display:none">
      <h3>Asset Library</h3>
      <div id="assets" class="grid"></div>
    </div>
    <div id="view-agency" style="display:none">
      <h3>Agency Tracking</h3>
      <div id="agency" class="grid"></div>
    </div>
    <div id="view-raw" style="display:none">
      <p class="small">Quick links:</p>
      <a class="btn" href="/healthz">/healthz</a>
      <a class="btn" href="/api/calendar/7day">/api/calendar/7day</a>
      <a class="btn" href="/api/assets">/api/assets</a>
      <a class="btn" href="/api/deliverables">/api/deliverables</a>
      <hr/>
      <p class="small mono" id="raw"></p>
    </div>
  </div>
</div>
<script>
function show(which){
  const ids = ["cal","assets","agency","raw"];
  ids.forEach(id=>{
    document.getElementById("view-"+id).style.display = (id===which) ? "" : "none";
    document.getElementById("tab-"+id).classList.toggle("active", id===which);
  });
  if(which==="cal") loadCal();
  if(which==="assets") loadAssets();
  if(which==="agency") loadAgency();
  if(which==="raw") document.getElementById("raw").textContent =
    "Open the buttons above to view raw JSON in a new tab.";
}
async function loadCal(){
  const res = await fetch('/api/calendar/7day'); const j = await res.json();
  const el = document.getElementById('cal'); el.innerHTML = '';
  (j.calendar_data||[]).forEach(day=>{
    const posts = (day.posts||[]).map(p=>`
      <div class="item">
        <div><strong>${p.title}</strong></div>
        <div class="small">${p.platform} • ${p.time_slot} • ${p.code_name} • Badge ${p.badge_score}%</div>
        <div class="small" style="margin-top:6px">${p.content||''}</div>
        <div class="small" style="color:#22c55e">${p.hashtags||''}</div>
      </div>`).join('');
    el.insertAdjacentHTML('beforeend', `<div class="item"><div><strong>${day.day_name}</strong> — ${day.formatted_date}</div><hr/>${posts||'<div class="small">No posts</div>'}</div>`);
  });
}
async function loadAssets(){
  const res = await fetch('/api/assets'); const j = await res.json();
  const el = document.getElementById('assets'); el.innerHTML='';
  (j.assets||[]).forEach(a=>{
    el.insertAdjacentHTML('beforeend', `
      <div class="item">
        <div><strong>${a.original_name||a.name}</strong></div>
        <div class="small">${a.file_type||''}</div>
        <div class="small">Badge ${a.badge_score||0}% • Code ${a.assigned_code||'—'}</div>
        <div class="small">${a.created_date||''}</div>
      </div>`);
  });
}
async function loadAgency(){
  const res = await fetch('/api/deliverables'); const j = await res.json();
  const el = document.getElementById('agency'); el.innerHTML='';
  if(!j.success){ el.textContent='Error loading'; return; }
  const cp = j.current_progress||{};
  el.insertAdjacentHTML('beforeend', `
    <div class="item">
      <div><strong>${(j.current_phase||{}).name||'Phase'}</strong> — ${((j.current_phase||{}).period||'')}</div>
      <div class="small">${(j.current_phase||{}).budget||''}</div>
      <hr/>
      <div class="small">Social Posts: ${cp.social_posts?.current||0}/${cp.social_posts?.target||0} (${cp.social_posts?.progress||0}%)</div>
      <div class="small">Ad Creatives: ${cp.ad_creatives?.current||0}/${cp.ad_creatives?.target||0} (${cp.ad_creatives?.progress||0}%)</div>
      <div class="small">Email Campaigns: ${cp.email_campaigns?.current||0}/${cp.email_campaigns?.target||0} (${cp.email_campaigns?.progress||0}%)</div>
      <hr/>
      <div><strong>Overall:</strong> ${(j.overall_progress||0)}%</div>
    </div>`);
}
document.addEventListener('DOMContentLoaded', ()=>{ loadCal(); });
</script>
</body></html>
    """)

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000)
