from typing import List, Dict, Any
import pandas as pd
import numpy as np
import re
from collections import Counter
from services.scraper import load_all_uploaded_frames

def _keyword_extract(texts: List[str], top_k=10) -> List[str]:
    bag = []
    for t in texts:
        if not isinstance(t, str): 
            continue
        t = t.lower()
        t = re.sub(r"[^a-z0-9#@\s]", " ", t)
        words = [w for w in t.split() if len(w) >= 3 and w not in {"the","and","for","with","this","that","from","your","you","are","has","was","have","our","out"}]
        bag.extend(words)
    return [w for w,_ in Counter(bag).most_common(top_k)]

def brand_intelligence(brands: List[str], lookback_days: int = 7) -> Dict[str, Any]:
    df = load_all_uploaded_frames()
    if df.empty:
        return {
            "timeframe_days": lookback_days,
            "metrics": [],
            "highlights": ["No uploaded data found. Upload CSV/JSON first."],
            "prioritized_actions": [
                "Upload fresh scraped files for Crooks and competitors.",
                "Ensure fields include brand, platform, date, likes, comments, shares, text, url."
            ]
        }

    # Filter by lookback if date exists
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=lookback_days)
        df = df[df["date"] >= cutoff]

    if brands:
        df = df[df["brand"].str.lower().isin([b.lower() for b in brands])]

    if df.empty:
        return {
            "timeframe_days": lookback_days,
            "metrics": [],
            "highlights": ["No rows after filters. Check brand names or date range."],
            "prioritized_actions": ["Adjust brand filters or extend timeframe."]
        }

    # Group metrics
    metrics = []
    for brand, g in df.groupby(df["brand"].str.strip()):
        posts = len(g)
        avg_likes = float(np.mean(g.get("likes", 0))) if posts else 0.0
        avg_comments = float(np.mean(g.get("comments", 0))) if posts else 0.0
        # engagement_rate heuristic: (likes+comments+shares)/posts
        eng = float(np.mean((g.get("likes",0) + g.get("comments",0) + g.get("shares",0)).fillna(0))) if posts else 0.0

        # top posts by likes+comments
        g["_score"] = (g.get("likes",0).fillna(0) + g.get("comments",0).fillna(0))
        top_posts = g.sort_values("_score", ascending=False).head(5)[["platform","date","likes","comments","text","url"]].fillna("").to_dict(orient="records")
        top_keywords = _keyword_extract(g.get("text", []).tolist(), top_k=10)

        metrics.append({
            "brand": brand,
            "posts": int(posts),
            "avg_likes": round(avg_likes,2),
            "avg_comments": round(avg_comments,2),
            "engagement_rate": round(eng,2),
            "top_posts": top_posts,
            "top_keywords": top_keywords
        })

    # Highlights: rank by engagement
    metrics_sorted = sorted(metrics, key=lambda m: m["engagement_rate"], reverse=True)
    highlights = []
    if metrics_sorted:
        leader = metrics_sorted[0]["brand"]
        highlights.append(f"{leader} leads on engagement in the last {lookback_days} days.")
        laggard = metrics_sorted[-1]["brand"]
        if laggard != leader:
            highlights.append(f"{laggard} trails; review content cadence and hooks.")

    # Actions: simple rules
    actions = [
        "Double down on post formats driving top-5 engagement this week (reuse hooks, angles).",
        "Ship 3 tests: creator collab, archive graphic story, and giveaway/pin with comment CTA.",
        "Audit underperforming platforms; pause low-ROI posts and reallocate to winning channel."
    ]

    return {
        "timeframe_days": lookback_days,
        "metrics": metrics_sorted,
        "highlights": highlights or ["No standouts detected."],
        "prioritized_actions": actions
    }

def weekly_summary(brands: List[str], lookback_days: int = 7) -> Dict[str, Any]:
    rep = brand_intelligence(brands, lookback_days)
    if not rep["metrics"]:
        return {
            "timeframe_days": lookback_days,
            "narrative": "No data available to summarize. Upload new files.",
            "key_moves": ["Upload scraped data", "Re-run weekly summary"],
            "risks": ["Zero signal -> zero insight"]
        }
    leader = rep["metrics"][0]["brand"]
    narrative = (
        f"{leader} set the pace this week. Focus on replicating their winning content mechanics. "
        f"Overall, engagement clustered around top 5 posts per brand; expand those storylines."
    )
    key_moves = [
        "Spin 2 archive-driven posts with updated styling and trend audio.",
        "Run a micro-collab with one mid-tier creator per brand.",
        "Deploy a comment-to-unlock CTA on the next drop teaser."
    ]
    risks = [
        "Over-reliance on one platform; diversify to hedge algorithm swings.",
        "Inconsistent posting cadence versus competitors."
    ]
    return {
        "timeframe_days": lookback_days,
        "narrative": narrative,
        "key_moves": key_moves,
        "risks": risks
    }
