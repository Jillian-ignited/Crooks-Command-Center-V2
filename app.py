#!/usr/bin/env python3
"""
CROOKS & CASTLES COMMAND CENTER - CLEAN BASE APP
"""

from flask import Flask, jsonify
from flask_cors import CORS
import datetime

# Create Flask app
app = Flask(__name__)
CORS(app)

# Health check
@app.route("/healthz")
def health():
    return jsonify({"status": "ok", "message": "🏰 Crooks Command Center is alive"})

# Simple calendar endpoint
@app.route("/api/calendar/7day")
def calendar_7day():
    today = datetime.date.today()
    data = []
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        data.append({
            "date": str(day),
            "day_name": day.strftime("%A"),
            "posts": [
                {
                    "title": f"Demo Post {i+1}",
                    "platform": "Instagram",
                    "time": "12:00 CT",
                    "content": f"Sample content for {day.strftime('%A')}"
                }
            ]
        })
    return jsonify({"success": True, "calendar_data": data})

# Simple assets endpoint
@app.route("/api/assets")
def assets():
    return jsonify({
        "success": True,
        "assets": [
            {"id": "1", "name": "demo_asset.png", "badge_score": 95},
            {"id": "2", "name": "demo_video.mp4", "badge_score": 85}
        ]
    })

# Simple deliverables endpoint
@app.route("/api/deliverables")
def deliverables():
    return jsonify({
        "success": True,
        "current_phase": {"name": "Foundation & Awareness", "period": "Sep-Oct 2025"},
        "overall_progress": 50,
        "progress": {
            "social_posts": {"current": 6, "target": 12},
            "ad_creatives": {"current": 2, "target": 4},
            "email_campaigns": {"current": 1, "target": 2}
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
