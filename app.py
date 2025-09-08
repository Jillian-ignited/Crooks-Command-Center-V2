#!/usr/bin/env python3
import os, json, uuid, datetime
from dateutil import tz
from flask import Flask, jsonify, send_file, send_from_directory, redirect, request, abort
from flask_cors import CORS
from db import init_db, conn
import os
import psycopg2
from flask import Flask

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn
APP_ROOT   = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_ROOT, "src", "static")
ASSET_DIR  = os.path.join(STATIC_DIR, "assets")
DATA_DIR   = os.path.join(APP_ROOT, "src", "data")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(ASSET_DIR,  exist_ok=True)
os.makedirs(DATA_DIR,   exist_ok=True)

ADMIN_KEY = os.getenv("ADMIN_KEY", "")  # set this in Render → Environment

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)

# ---------- helpers ----------
def ui_path():
    for p in [
        os.path.join(STATIC_DIR, "index_enhanced_planning.html"),
        os.path.join(APP_ROOT, "static", "index_enhanced_planning.html"),
        os.path.join(APP_ROOT, "index_enhanced_planning.html"),
    ]:
        if os.path.exists(p): return p
    return None

def load_json(name, default):
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def require_admin():
    if not ADMIN_KEY or request.headers.get("X-Admin-Key") != ADMIN_KEY:
        abort(401)

def today_ct():
    return datetime.datetime.now(tz.gettz("America/Chicago")).date()

# ---------- demo seeds (used only if no DB rows) ----------
_today = today_ct()
DEMO_7 = [
  {
    "date": str(_today + datetime.timedelta(days=i)),
    "day_name": (_today + datetime.timedelta(days=i)).strftime("%A"),
    "formatted_date": (_today + datetime.timedelta(days=i)).strftime("%b %d"),
    "posts": [
      {
        "title": "NFL Season Kickoff Street Style" if i==1 else "Monday Night Football Prep" if i==2 else f"Planned Content D{i+1}",
        "platform": "Instagram Story" if i==1 else "TikTok",
        "time_slot": "00:00 CT",
        "code_name": "Code 29: Story",
        "badge_score": 95 if i in (1,2) else 85,
        "hashtags": "#crooksandcastles #street #culture",
        "content": "Game day drip different when you rep the castle 🏈" if i==1 else "Primetime prep — crown bright ✨" if i==2 else "Strategic slot."
      }
    ] if i in (1,2) else []
  } for i in range(7)
]
DEMO_30 = {"calendar_data": DEMO_7}
DEMO_60 = {"opportunities":[
  {"date":"2025-10-01","event":"Hip Hop History Month","type":"Cultural Heritage","priority":"High",
   "suggested_codes":["11: Culture","1: Hustle Into Heritage"],"content_ideas":["Community spotlights","Legends tribute","Street history"]}
]}
DEMO_90 = {"long_range":[
  {"date":"2026-01-15","milestone":"TikTok Shop Launch","type":"Platform Expansion",
   "preparation_needed":["Content strategy","Video assets","Influencers","Ecom integration"],
   "success_metrics":["Shop CVR","Video engagement","Follower growth"]}
]}
DEMO_ASSETS = [
  {"id":"asset-1","original_name":"real_instagram_story_rebel_rooftop.png","file_type":"image/png",
   "badge_score":95,"assigned_code":"Code 29: Story","created_at":str(_today),
   "file_url":"/static/assets/real_instagram_story_rebel_rooftop.png"}
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

# ---------- boot ----------
init_db()  # no-op if DATABASE_URL not set

# ---------- routes: UI ----------
@app.get("/")
def root(): return redirect("/ui", code=302)

@app.get("/ui")
def serve_ui():
    p = ui_path()
    if not p:
        return jsonify({"error":"UI not found","expected":"src/static/index_enhanced_planning.html"}), 404
    return send_file(p)

@app.get("/healthz")
def healthz(): return jsonify({"ok": True})

@app.get("/debug/whereis-ui")
def where_ui(): return jsonify({"found": bool(ui_path()), "path": ui_path()})

# ---------- routes: data (DB first; fallback to seeds) ----------
def posts_between(d1:datetime.date, d2:datetime.date):
    # inclusive range [d1, d2]
    if not conn(): return None
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
          SELECT id, title, content, platform, scheduled_at, code_name, badge_score, hashtags, asset_id, status
          FROM posts
          WHERE date(scheduled_at AT TIME ZONE 'America/Chicago') BETWEEN %s AND %s
          ORDER BY scheduled_at ASC NULLS LAST
        """, (d1, d2))
        return cur.fetchall()

def db_assets():
    if not conn(): return None
    with conn() as c:
        cur = c.cursor()
        cur.execute("""SELECT id, original_name, file_type, file_url, badge_score, assigned_code, created_at, usage_count
                       FROM assets ORDER BY created_at DESC""")
        return cur.fetchall()

def db_deliverables_for_month(yyyy_mm:str):
    if not conn(): return None
    with conn() as c:
        cur = c.cursor()
        cur.execute("""SELECT * FROM deliverables WHERE id=%s""", (yyyy_mm,))
        row = cur.fetchone()
        return row

# ---- Calendar APIs ----
@app.get("/api/calendar/7day")
def cal_7():
    start = today_ct()
    end = start + datetime.timedelta(days=6)
    rows = posts_between(start, end)
    if rows is None or len(rows)==0:
        return jsonify({"success": True, "view_type":"7day", "calendar_data": load_json("seed_calendar_7day.json", DEMO_7)})
    # group by day
    days = []
    cur = start
    while cur <= end:
        day_posts = []
        for r in rows:
            if r["scheduled_at"]:
                dt = r["scheduled_at"].astimezone(tz.gettz("America/Chicago"))
                if dt.date()==cur:
                    day_posts.append({
                        "title": r["title"],
                        "platform": r["platform"] or "",
                        "time_slot": dt.strftime("%H:%M CT"),
                        "code_name": r["code_name"] or "",
                        "badge_score": r["badge_score"] or 0,
                        "hashtags": r["hashtags"] or "",
                        "content": (r["content"] or "")
                    })
        days.append({
            "date": str(cur),
            "day_name": cur.strftime("%A"),
            "formatted_date": cur.strftime("%b %d"),
            "posts": day_posts
        })
        cur += datetime.timedelta(days=1)
    return jsonify({"success": True, "view_type":"7day", "calendar_data": days})

@app.get("/api/calendar/30day")
def cal_30():
    start = today_ct()
    end = start + datetime.timedelta(days=29)
    rows = posts_between(start, end)
    if rows is None or len(rows)==0:
        data = load_json("seed_calendar_30day.json", DEMO_30)
        data = data.get("calendar_data") if isinstance(data, dict) else data
        return jsonify({"success": True, "view_type":"30day", "calendar_data": data})
    # only days with posts
    by_day = {}
    for r in rows:
        if not r["scheduled_at"]: continue
        dt = r["scheduled_at"].astimezone(tz.gettz("America/Chicago"))
        d = dt.date()
        by_day.setdefault(d, [])
        by_day[d].append({
            "title": r["title"],
            "platform": r["platform"] or "",
            "time_slot": dt.strftime("%H:%M CT"),
            "code_name": r["code_name"] or "",
            "badge_score": r["badge_score"] or 0,
            "hashtags": r["hashtags"] or "",
            "content": (r["content"] or "")
        })
    calendar_data = [{
        "date": str(d),
        "day_name": d.strftime("%A"),
        "formatted_date": d.strftime("%b %d"),
        "posts": posts
    } for d, posts in sorted(by_day.items())]
    return jsonify({"success": True, "view_type":"30day", "calendar_data": calendar_data})

@app.get("/api/calendar/60day")
def cal_60():
    if conn():
        # You can later store opportunities in a table; for now read seeds if present
        pass
    return jsonify({"success": True, "view_type":"60day",
                    **load_json("seed_opportunities_60day.json", DEMO_60)})

@app.get("/api/calendar/90day")
def cal_90():
    if conn():
        pass
    return jsonify({"success": True, "view_type":"90day",
                    **load_json("seed_longrange_90day.json", DEMO_90)})

# ---- Assets ----
@app.get("/api/assets")
def api_assets():
    rows = db_assets()
    if rows is None or len(rows)==0:
        return jsonify({"success": True, "assets": load_json("seed_assets.json", DEMO_ASSETS)})
    return jsonify({"success": True, "assets": rows})

@app.get("/api/download/<asset_id>")
def download(asset_id):
    # works for local files under /static/assets
    rows = db_assets()
    items = rows if rows else load_json("seed_assets.json", DEMO_ASSETS)
    a = next((x for x in items if str(x.get("id"))==str(asset_id)), None)
    if not a: abort(404)
    url = a.get("file_url","")
    if url.startswith("/static/assets/"):
        rel = url.replace("/static/assets/","")
        p = os.path.join(ASSET_DIR, rel)
        if os.path.exists(p):
            return send_from_directory(ASSET_DIR, rel, as_attachment=True)
    abort(404)

# ---- Deliverables ----
@app.get("/api/deliverables")
def api_deliverables():
    yyyy_mm = today_ct().strftime("%Y-%m")
    row = db_deliverables_for_month(yyyy_mm)
    if not row:
        return jsonify({"success": True, **load_json("seed_deliverables.json", DEMO_DELV)})
    # compute progress helpers
    def pct(cur, tgt): return min(100, round((cur/tgt)*100,1)) if tgt else 0
    resp = {
        "success": True,
        "current_phase": {"name": row["phase"], "period": yyyy_mm, "budget": row["budget"]},
        "current_progress": {
            "social_posts":   {"current": row["social_current"], "target": row["social_target"],   "progress": pct(row["social_current"], row["social_target"]), "outstanding": max(0,(row["social_target"]-row["social_current"])), "status": "on_track"},
            "ad_creatives":   {"current": row["creative_current"], "target": row["creative_target"],"progress": pct(row["creative_current"], row["creative_target"]), "outstanding": max(0,(row["creative_target"]-row["creative_current"])), "status": "on_track"},
            "email_campaigns":{"current": row["email_current"], "target": row["email_target"],     "progress": pct(row["email_current"], row["email_target"]), "outstanding": max(0,(row["email_target"]-row["email_current"])), "status": "on_track"}
        },
        "overall_progress": round((pct(row["social_current"], row["social_target"])+pct(row["creative_current"], row["creative_target"])+pct(row["email_current"], row["email_target"]))/3,1)
    }
    return jsonify(resp)

# ---------- Minimal write APIs (with admin key) ----------
@app.post("/api/posts")
def create_post():
    require_admin()
    b = request.get_json(force=True)
    if not conn(): abort(503, description="DB not configured")
    with conn() as c:
        cur = c.cursor()
        pid = b.get("id") or str(uuid.uuid4())
        cur.execute("""
          INSERT INTO posts (id,title,content,platform,scheduled_at,code_name,badge_score,hashtags,asset_id,status,owner,due_date)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
          ON CONFLICT (id) DO NOTHING
        """,(pid,b.get("title"),b.get("content"),b.get("platform"),b.get("scheduled_at"),
             b.get("code_name"),b.get("badge_score") or 0,b.get("hashtags"),b.get("asset_id"),
             b.get("status","draft"),b.get("owner"),b.get("due_date")))
        c.commit()
        return jsonify({"success": True, "id": pid})

@app.put("/api/posts/<id>")
def update_post(id):
    require_admin()
    if not conn(): abort(503)
    b = request.get_json(force=True)
    fields = ["title","content","platform","scheduled_at","code_name","badge_score","hashtags","asset_id","status","owner","due_date"]
    sets   = [f"{k}=%s" for k in fields if k in b]
    vals   = [b[k] for k in b if k in fields]
    if not sets: return jsonify({"success": True})
    with conn() as c:
        cur = c.cursor()
        cur.execute(f"UPDATE posts SET {', '.join(sets)}, updated_at=now() WHERE id=%s", (*vals, id))
        c.commit()
        return jsonify({"success": True})

@app.post("/api/assets")
def create_asset():
    require_admin()
    b = request.get_json(force=True)
    if not conn(): abort(503)
    with conn() as c:
        cur = c.cursor()
        aid = b.get("id") or str(uuid.uuid4())
        cur.execute("""INSERT INTO assets (id,original_name,file_type,file_url,badge_score,assigned_code)
                       VALUES (%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (id) DO NOTHING""",
                       (aid,b.get("original_name"),b.get("file_type"),b.get("file_url"),
                        b.get("badge_score") or 0,b.get("assigned_code")))
        c.commit()
        return jsonify({"success": True, "id": aid})

@app.put("/api/deliverables/<yyyy_mm>")
def update_deliverables(yyyy_mm):
    require_admin()
    b = request.get_json(force=True)
    if not conn(): abort(503)
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
          INSERT INTO deliverables (id,phase,budget,social_target,social_current,creative_target,creative_current,email_target,email_current,notes)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
          ON CONFLICT (id) DO UPDATE SET
            phase=EXCLUDED.phase, budget=EXCLUDED.budget,
            social_target=EXCLUDED.social_target, social_current=EXCLUDED.social_current,
            creative_target=EXCLUDED.creative_target, creative_current=EXCLUDED.creative_current,
            email_target=EXCLUDED.email_target, email_current=EXCLUDED.email_current,
            notes=EXCLUDED.notes, updated_at=now()
        """,(yyyy_mm,b.get("phase"),b.get("budget"),b.get("social_target"),b.get("social_current"),
             b.get("creative_target"),b.get("creative_current"),b.get("email_target"),b.get("email_current"),b.get("notes")))
        c.commit()
        return jsonify({"success": True})
