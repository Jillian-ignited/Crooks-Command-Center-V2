#!/usr/bin/env python3
import os, json, datetime
from flask import Flask, jsonify, send_file
from flask_cors import CORS

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CANDIDATE_UI = [
    os.path.join(APP_ROOT, "src", "static", "index_enhanced_planning.html"),
    os.path.join(APP_ROOT, "static", "index_enhanced_planning.html"),
    os.path.join(APP_ROOT, "index_enhanced_planning.html"),
]
DATA_DIR = os.path.join(APP_ROOT, "src", "data")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

def first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def load_json(name, default):
    p = os.path.join(DATA_DIR, name)
    if os.path.exists(p):
        try:
            with open(p, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return default

# ----------- demo fallbacks (used only if seed files absent) -----------
_today = datetime.date.today()
DEMO_CAL = [
    {
        "date": str(_today + datetime.timedelta(days=i)),
        "day_name": (_today + datetime.timedelta(days=i)).strftime("%A"),
        "formatted_date": (_today + datetime.timedelta(days=i)).strftime("%b %d"),
        "posts": [
            {
                "title": "NFL Season Kickoff Street Style" if i==1 else "Monday Night Football Prep" if i==2 else f"Planned Content D{i+1}",
                "platform": "Instagram Story" if i in (1,) else "TikTok",
                "time_slot": "00:00 CT",
                "code_name": "Code 29: Story",
                "badge_score": 95 if i in (1,2) else 85,
                "hashtags": "#crooksandcastles #street #culture",
                "content": "Game day drip. Street culture swagger." if i==1 else "Primetime prep — crown bright." if i==2 else "Strategic slot."
            }
        ] if i in (1,2) else []
    } for i in range(7)
]
DEMO_ASSETS = [
    {"id":"demo-1","original_name":"real_instagram_story_rebel_rooftop.png","file_type":"image/png","badge_score":95,"assigned_code":"Code 29: Story","created_date":str(_today)},
    {"id":"demo-2","original_name":"sept_16_cultural_fusion(3).png","file_type":"image/png","badge_score":92,"assigned_code":"Code 03: Global Throne","created_date":str(_today)}
]
DEMO_DELV = {
    "current_phase":{"name":"Foundation & Awareness","period":"Sep–Oct 2025","budget":"$4,000/month"},
    "current_progress":{
        "social_posts":{"current":6,"target":12,"progress":50,"outstanding":6,"status":"on_track"},
        "ad_creatives":{"current":2,"target":4,"progress":50,"outstanding":2,"status":"on_track"},
        "email_campaigns":{"current":1,"target":2,"progress":50,"outstanding":1,"status":"on_track"}
    },
    "overall_progress":50.0
}

# ----------- seeds (override demos if you add files) -----------
SEED_CAL = load_json("seed_calendar.json", DEMO_CAL)
SEED_ASSETS = load_json("seed_assets.json", DEMO_ASSETS)
SEED_DELV = load_json("seed_deliverables.json", DEMO_DELV)

@app.get("/healthz")
def health():
    return jsonify({"status":"ok","message":"🏰 Crooks Command Center alive"})

@app.get("/debug/whereis-ui")
def where_is_ui():
    found = first_existing(CANDIDATE_UI)
    return jsonify({"app_root": APP_ROOT, "candidates": CANDIDATE_UI, "found": found, "exists": bool(found)})

# ---------- serve the Manus UI ----------
@app.get("/ui")
def serve_ui():
    path = first_existing(CANDIDATE_UI)
    if not path:
        return jsonify({"error":"UI file not found", "expected_one_of": CANDIDATE_UI}), 404
    return send_file(path)

# ---------- APIs ----------
@app.get("/api/calendar/7day")
def api_calendar_7day():
    return jsonify({"success": True, "view_type":"7day", "calendar_data": SEED_CAL})

@app.get("/api/assets")
def api_assets():
    return jsonify({"success": True, "assets": SEED_ASSETS})

@app.get("/api/deliverables")
def api_deliverables():
    return jsonify({"success": True, **SEED_DELV})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
