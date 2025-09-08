#!/usr/bin/env python3
"""
Crooks & Castles — Command Center (Render + Postgres)
One-file Flask app with:
- UI at /ui (loads src/static/index_enhanced_planning.html if present)
- Calendar, Assets, Deliverables APIs
- Seed endpoint to import JSON from src/data/*
"""

import os
import json
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

# -----------------------------------------------------------------------------
# App & Config
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("command-center")

APP_ROOT = Path(__file__).resolve().parent
STATIC_DIR = APP_ROOT / "src" / "static"
DATA_DIR = APP_ROOT / "src" / "data"

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),         # serves /static/*
    static_url_path="/static"
)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
ADMIN_KEY = os.getenv("ADMIN_KEY", "").strip()

if not DATABASE_URL:
    log.warning("DATABASE_URL is not set. Set it in Render → Settings → Environment.")

# -----------------------------------------------------------------------------
# DB Helpers
# -----------------------------------------------------------------------------
def db() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db() -> None:
    with db() as conn:
        with conn.cursor() as cur:
            # posts
            cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                platform TEXT,
                scheduled_at TIMESTAMPTZ,
                code_name TEXT,
                badge_score INT,
                hashtags TEXT,
                status TEXT,
                owner TEXT,
                due_date DATE,
                asset_id TEXT
            );
            """)
            # assets
            cur.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                original_name TEXT NOT NULL,
                file_type TEXT,
                file_url TEXT,
                badge_score INT,
                assigned_code TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                usage_count INT DEFAULT 0
            );
            """)
            # deliverables (monthly)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS deliverables_monthly (
                year_month TEXT PRIMARY KEY,
                phase TEXT,
                budget TEXT,
                social_target INT,
                social_current INT,
                creative_target INT,
                creative_current INT,
                email_target INT,
                email_current INT,
                notes TEXT,
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """)
        conn.commit()

init_db()

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def require_admin() -> Optional[Response]:
    key = request.headers.get("X-Admin-Key", "")
    if not ADMIN_KEY or key != ADMIN_KEY:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    return None

def load_json(relpath: str) -> Optional[Any]:
    p = DATA_DIR / relpath
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def to_ct_label(dt: datetime) -> str:
    # Label only; assumes server UTC with CT label for display
    # (good enough for planning; adjust if you need true tz conversion)
    return dt.strftime("%H:%M CT")

def day_range(days: int = 7) -> List[date]:
    today = datetime.utcnow().date()
    return [today + timedelta(days=i) for i in range(days)]

# -----------------------------------------------------------------------------
# Health & UI
# -----------------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, "db": bool(DATABASE_URL)})

@app.get("/")
def root():
    base = request.host_url.rstrip("/")
    return (
        "🏰 Crooks & Castles — Command Center Live<br>"
        '<a href="/ui">Open UI</a><br><br>'
        f'APIs: <a href="/api/calendar/7day">/api/calendar/7day</a> '
        f'| <a href="/api/assets">/api/assets</a> '
        f'| <a href="/api/deliverables">/api/deliverables</a><br><br>'
        'Admin: POST /api/seed (with X-Admin-Key)'
    )

@app.get("/ui")
def ui():
    # Serve Manus-style UI file if present; else simple fallback
    target = STATIC_DIR / "index_enhanced_planning.html"
    if target.exists():
        return send_from_directory(str(STATIC_DIR), "index_enhanced_planning.html")
    # Fallback minimal UI
    html = f"""
    <!doctype html>
    <meta charset="utf-8">
    <title>Command Center</title>
    <body style="font-family: system-ui; padding: 24px;">
      <h1>🏰 Crooks & Castles — Command Center</h1>
      <p>Static UI not found. Add <code>src/static/index_enhanced_planning.html</code> for the full Manus UI.</p>
      <p><a href="/api/calendar/7day" target="_blank">/api/calendar/7day</a> •
         <a href="/api/assets" target="_blank">/api/assets</a> •
         <a href="/api/deliverables" target="_blank">/api/deliverables</a></p>
    </body>
    """
    return html

# -----------------------------------------------------------------------------
# Calendar APIs
# -----------------------------------------------------------------------------
@app.get("/api/calendar/7day")
def api_calendar_7day():
    # Build 7-day window from posts; if empty, try seed file
    days = day_range(7)
    by_date: Dict[str, Dict[str, Any]] = {}

    with db() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        start = datetime.combine(days[0], datetime.min.time())
        end = datetime.combine(days[-1], datetime.max.time())
        cur.execute("""
            SELECT * FROM posts
            WHERE scheduled_at >= %s AND scheduled_at <= %s
            ORDER BY scheduled_at ASC
        """, (start, end))
        rows = cur.fetchall()

    if not rows:
        seeded = load_json("seed_calendar_7day.json")
        if seeded:
            return jsonify({"success": True, "view_type": "7day", "calendar_data": seeded})

    for d in days:
        key = d.isoformat()
        by_date[key] = {
            "date": key,
            "day_name": d.strftime("%A"),
            "formatted_date": d.strftime("%b %d"),
            "posts": []
        }

    for r in rows:
        dt = (r.get("scheduled_at") or datetime.utcnow())
        dkey = dt.date().isoformat()
        by_date.setdefault(dkey, {
            "date": dkey,
            "day_name": dt.strftime("%A"),
            "formatted_date": dt.strftime("%b %d"),
            "posts": []
        })
        by_date[dkey]["posts"].append({
            "title": r.get("title"),
            "platform": r.get("platform") or "",
            "time_slot": to_ct_label(dt),
            "code_name": r.get("code_name") or "No Code",
            "badge_score": r.get("badge_score") or 85,
            "hashtags": r.get("hashtags") or "",
            "content": r.get("content") or ""
        })

    return jsonify({"success": True, "view_type": "7day", "calendar_data": list(by_date.values())})

@app.get("/api/calendar/30day")
def api_calendar_30day():
    # 30 days starting today; fallback to seed file
    days = day_range(30)
    with_db: List[Dict[str, Any]] = []

    with db() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        start = datetime.combine(days[0], datetime.min.time())
        end = datetime.combine(days[-1], datetime.max.time())
        cur.execute("""
            SELECT * FROM posts
            WHERE scheduled_at >= %s AND scheduled_at <= %s
            ORDER BY scheduled_at ASC
        """, (start, end))
        rows = cur.fetchall()

    if not rows:
        seed = load_json("seed_calendar_30day.json")
        if seed:
            return jsonify({"success": True, "view_type": "30day", **seed})

    # Group by date only for days with posts
    grouped: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        dt = r.get("scheduled_at") or datetime.utcnow()
        key = dt.date().isoformat()
        grouped.setdefault(key, {
            "date": key,
            "day_name": dt.strftime("%A"),
            "formatted_date": dt.strftime("%b %d"),
            "posts": []
        })
        grouped[key]["posts"].append({
            "title": r.get("title"),
            "platform": r.get("platform") or "",
            "time_slot": to_ct_label(dt),
            "code_name": r.get("code_name") or "No Code",
            "badge_score": r.get("badge_score") or 85,
            "hashtags": r.get("hashtags") or "",
            "content": r.get("content") or ""
        })

    return jsonify({"success": True, "view_type": "30day", "calendar_data": list(grouped.values())})

@app.get("/api/calendar/60day")
def api_calendar_60day():
    seed = load_json("seed_opportunities_60day.json")
    if seed:
        return jsonify({"success": True, "view_type": "60day", **seed})
    # Minimal fallback
    return jsonify({"success": True, "view_type": "60day", "opportunities": []})

@app.get("/api/calendar/90day")
def api_calendar_90day():
    seed = load_json("seed_longrange_90day.json")
    if seed:
        return jsonify({"success": True, "view_type": "90day", **seed})
    # Minimal fallback
    return jsonify({"success": True, "view_type": "90day", "long_range": []})

# -----------------------------------------------------------------------------
# Assets
# -----------------------------------------------------------------------------
@app.get("/api/assets")
def get_assets():
    with db() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM assets ORDER BY created_at DESC;")
        rows = cur.fetchall()

    if not rows:
        seed = load_json("seed_assets.json")
        if seed:
            rows = seed

    return jsonify({"success": True, "assets": rows})

@app.post("/api/assets")
def create_asset():
    # Admin-only
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    body = request.get_json(force=True)
    required = ["original_name", "file_type", "file_url"]
    for k in required:
        if not body.get(k):
            return jsonify({"success": False, "error": f"Missing '{k}'"}), 400

    asset = {
        "id": body.get("id") or f"asset-{int(datetime.utcnow().timestamp())}",
        "original_name": body["original_name"],
        "file_type": body["file_type"],
        "file_url": body["file_url"],
        "badge_score": int(body.get("badge_score", 85)),
        "assigned_code": body.get("assigned_code"),
        "created_at": datetime.utcnow(),
        "usage_count": int(body.get("usage_count", 0)),
    }

    with db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO assets (id, original_name, file_type, file_url, badge_score, assigned_code, created_at, usage_count)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
              original_name=EXCLUDED.original_name,
              file_type=EXCLUDED.file_type,
              file_url=EXCLUDED.file_url,
              badge_score=EXCLUDED.badge_score,
              assigned_code=EXCLUDED.assigned_code,
              created_at=EXCLUDED.created_at,
              usage_count=EXCLUDED.usage_count;
        """, (
            asset["id"], asset["original_name"], asset["file_type"], asset["file_url"],
            asset["badge_score"], asset["assigned_code"], asset["created_at"], asset["usage_count"]
        ))
        conn.commit()

    return jsonify({"success": True, "asset": asset})

# -----------------------------------------------------------------------------
# Deliverables
# -----------------------------------------------------------------------------
@app.get("/api/deliverables")
def get_deliverables():
    # Pull current month; if not found, fallback to seed_deliverables.json
    now = datetime.utcnow()
    ym = f"{now.year}-{str(now.month).zfill(2)}"

    with db() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM deliverables_monthly WHERE year_month=%s;", (ym,))
        row = cur.fetchone()

        # derive counts from posts & assets
        cur.execute("SELECT COUNT(*) FROM posts WHERE date_trunc('month', scheduled_at)=date_trunc('month', %s::timestamptz);", (now,))
        posts_cnt = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) FROM assets WHERE date_trunc('month', created_at)=date_trunc('month', %s::timestamptz);", (now,))
        assets_cnt = cur.fetchone()["count"]
        # emails = posts with platform='Email'
        cur.execute("SELECT COUNT(*) FROM posts WHERE platform='Email' AND date_trunc('month', scheduled_at)=date_trunc('month', %s::timestamptz);", (now,))
        emails_cnt = cur.fetchone()["count"]

    if not row:
        seed = load_json("seed_deliverables.json")
        if seed:
            return jsonify({"success": True, **seed})
        # default minimal
        row = dict(
            year_month=ym,
            phase="Foundation & Awareness",
            budget="$4,000/month",
            social_target=12, social_current=posts_cnt,
            creative_target=4, creative_current=assets_cnt,
            email_target=2, email_current=emails_cnt,
            notes="",
        )

    # compute progress
    def pct(cur, tgt): 
        return 0 if not tgt else min(100.0, (cur / float(tgt)) * 100.0)

    progress = {
        "social_posts": {
            "current": int(row.get("social_current", 0)),
            "target": int(row.get("social_target", 12)),
            "progress": round(pct(int(row.get("social_current", 0)), int(row.get("social_target", 12))), 1),
            "outstanding": max(0, int(row.get("social_target", 12)) - int(row.get("social_current", 0))),
            "status": "ahead" if int(row.get("social_current", 0)) > int(row.get("social_target", 12))
                               else "on_track" if pct(int(row.get("social_current", 0)), int(row.get("social_target", 12))) >= 80
                               else "behind"
        },
        "ad_creatives": {
            "current": int(row.get("creative_current", 0)),
            "target": int(row.get("creative_target", 4)),
            "progress": round(pct(int(row.get("creative_current", 0)), int(row.get("creative_target", 4))), 1),
            "outstanding": max(0, int(row.get("creative_target", 4)) - int(row.get("creative_current", 0))),
            "status": "ahead" if int(row.get("creative_current", 0)) > int(row.get("creative_target", 4))
                               else "on_track" if pct(int(row.get("creative_current", 0)), int(row.get("creative_target", 4))) >= 80
                               else "behind"
        },
        "email_campaigns": {
            "current": int(row.get("email_current", 0)),
            "target": int(row.get("email_target", 2)),
            "progress": round(pct(int(row.get("email_current", 0)), int(row.get("email_target", 2))), 1),
            "outstanding": max(0, int(row.get("email_target", 2)) - int(row.get("email_current", 0))),
            "status": "ahead" if int(row.get("email_current", 0)) > int(row.get("email_target", 2))
                               else "on_track" if pct(int(row.get("email_current", 0)), int(row.get("email_target", 2))) >= 80
                               else "behind"
        }
    }
    overall = round((progress["social_posts"]["progress"] +
                     progress["ad_creatives"]["progress"] +
                     progress["email_campaigns"]["progress"]) / 3.0, 1)

    return jsonify({
        "success": True,
        "current_phase": {
            "name": row.get("phase", "Foundation & Awareness"),
            "period": f"{date.today():%b %Y}",
            "budget": row.get("budget", "$4,000/month")
        },
        "current_progress": progress,
        "overall_progress": overall
    })

@app.put("/api/deliverables/<year_month>")
def put_deliverables(year_month: str):
    # Admin-only
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    body = request.get_json(force=True)
    fields = ("phase","budget","social_target","social_current","creative_target",
              "creative_current","email_target","email_current","notes")
    vals = [body.get(k) for k in fields]

    with db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO deliverables_monthly
              (year_month, phase, budget, social_target, social_current,
               creative_target, creative_current, email_target, email_current, notes, updated_at)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (year_month) DO UPDATE SET
              phase=EXCLUDED.phase,
              budget=EXCLUDED.budget,
              social_target=EXCLUDED.social_target,
              social_current=EXCLUDED.social_current,
              creative_target=EXCLUDED.creative_target,
              creative_current=EXCLUDED.creative_current,
              email_target=EXCLUDED.email_target,
              email_current=EXCLUDED.email_current,
              notes=EXCLUDED.notes,
              updated_at=NOW();
        """, (year_month, *vals))
        conn.commit()
    return jsonify({"success": True, "year_month": year_month})

# -----------------------------------------------------------------------------
# Posts (create)
# -----------------------------------------------------------------------------
@app.post("/api/posts")
def create_post():
    # Admin-only
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    b = request.get_json(force=True)
    required = ["title"]
    for k in required:
        if not b.get(k):
            return jsonify({"success": False, "error": f"Missing '{k}'"}), 400

    # Parse dates
    scheduled_at = b.get("scheduled_at")
    due_date_s = b.get("due_date")

    with db() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            INSERT INTO posts
            (title, content, platform, scheduled_at, code_name, badge_score, hashtags, status, owner, due_date, asset_id)
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING *;
        """, (
            b["title"],
            b.get("content"),
            b.get("platform"),
            scheduled_at,
            b.get("code_name"),
            b.get("badge_score"),
            b.get("hashtags"),
            b.get("status"),
            b.get("owner"),
            due_date_s,
            b.get("asset_id")
        ))
        row = cur.fetchone()
        conn.commit()

    return jsonify({"success": True, "post": row})

# -----------------------------------------------------------------------------
# Seed endpoint (loads JSON from src/data/*)
# -----------------------------------------------------------------------------
@app.post("/api/seed")
def seed_all():
    # Admin-only
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    # Seed assets
    assets = load_json("seed_assets.json") or []
    with db() as conn:
        cur = conn.cursor()
        for a in assets:
            cur.execute("""
                INSERT INTO assets (id, original_name, file_type, file_url, badge_score, assigned_code, created_at, usage_count)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                a.get("id") or f"asset-{int(datetime.utcnow().timestamp())}",
                a.get("original_name"),
                a.get("file_type"),
                a.get("file_url"),
                a.get("badge_score", 85),
                a.get("assigned_code"),
                a.get("created_at") or datetime.utcnow(),
                a.get("usage_count", 0),
            ))
        conn.commit()

    # Seed 7/30 day posts from seed files (if present)
    seeded_posts = 0
    cal7 = load_json("seed_calendar_7day.json") or []
    cal30 = (load_json("seed_calendar_30day.json") or {}).get("calendar_data", [])

    def add_posts_from_calendar(items: List[Dict[str, Any]]):
        nonlocal seeded_posts
        with db() as conn:
            cur = conn.cursor()
            for day in items:
                dstr = day.get("date")
                for p in day.get("posts", []):
                    # Compose scheduled_at from date + "time_slot" if present; default 10:00
                    tslot = p.get("time_slot") or "10:00 CT"
                    hhmm = (tslot.split(" ")[0] if tslot else "10:00")
                    scheduled_at = f"{dstr}T{hhmm}:00-05:00" if dstr else None
                    cur.execute("""
                        INSERT INTO posts
                        (title, content, platform, scheduled_at, code_name, badge_score, hashtags, status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        p.get("title"),
                        p.get("content"),
                        p.get("platform"),
                        scheduled_at,
                        p.get("code_name"),
                        p.get("badge_score", 85),
                        p.get("hashtags"),
                        "scheduled"
                    ))
                    seeded_posts += 1
            conn.commit()

    if cal7:
        add_posts_from_calendar(cal7)
    if cal30:
        add_posts_from_calendar(cal30)

    # Seed deliverables (optional)
    dseed = load_json("seed_deliverables.json")
    if dseed:
        now = datetime.utcnow()
        ym = f"{now.year}-{str(now.month).zfill(2)}"
        with db() as conn:
            cur = conn.cursor()
            cp = dseed.get("current_phase", {})
            prog = dseed.get("current_progress", {})
            cur.execute("""
                INSERT INTO deliverables_monthly
                (year_month, phase, budget,
                 social_target, social_current,
                 creative_target, creative_current,
                 email_target, email_current, notes, updated_at)
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                ON CONFLICT (year_month) DO UPDATE SET
                  phase=EXCLUDED.phase,
                  budget=EXCLUDED.budget,
                  social_target=EXCLUDED.social_target,
                  social_current=EXCLUDED.social_current,
                  creative_target=EXCLUDED.creative_target,
                  creative_current=EXCLUDED.creative_current,
                  email_target=EXCLUDED.email_target,
                  email_current=EXCLUDED.email_current,
                  notes=EXCLUDED.notes,
                  updated_at=NOW();
            """, (
                ym,
                cp.get("name", "Foundation & Awareness"),
                cp.get("period", "$4,000/month"),
                prog.get("social_posts", {}).get("target", 12),
                prog.get("social_posts", {}).get("current", 0),
                prog.get("ad_creatives", {}).get("target", 4),
                prog.get("ad_creatives", {}).get("current", 0),
                prog.get("email_campaigns", {}).get("target", 2),
                prog.get("email_campaigns", {}).get("current", 0),
                ""
            ))
            conn.commit()

    return jsonify({
        "success": True,
        "seeded_assets": len(assets),
        "seeded_posts": seeded_posts
    })

# -----------------------------------------------------------------------------
# Main (for local run; Render uses gunicorn)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5103"))
    log.info("Starting Crooks & Castles Command Center on port %s", port)
    app.run(host="0.0.0.0", port=port)
