"""
Enhanced competitor analysis for Crooks & Castles.
Works on the same `posts` list used by /api/intelligence:
  - IG:  {"caption","hashtags","likesCount","commentsCount","timestamp","url"}
  - TikTok: {"description","viewCount","shareCount","timestamp","url"}
No extra dependencies. Pure stdlib.
"""
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Any, Iterable

_WORD = re.compile(r"[A-Za-z0-9_]{3,}")

def _text_of(p):
    return f"{p.get('caption','')} {p.get('description','')}"

def _tokens(text: str) -> List[str]:
    return [w.lower() for w in _WORD.findall(text or "")]

def _week_key(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
    except Exception:
        return "unknown"

def brand_aliases_map(primary: Iterable[str], competitors: Dict[str, Iterable[str]]) -> Dict[str, List[str]]:
    out = {"Crooks & Castles": [a.lower() for a in primary]}
    for brand, aliases in competitors.items():
        out[brand] = [a.lower() for a in aliases]
    return out

def share_of_voice(posts: List[Dict[str, Any]], aliases: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    counts = Counter()
    for p in posts:
        t = _text_of(p).lower()
        for brand, keys in aliases.items():
            if any(k in t for k in keys):
                counts[brand] += 1
    total = sum(counts.values()) or 1
    return [{"brand": b, "mentions": n, "share_pct": round(100.0 * n / total, 2)}
            for b, n in counts.most_common()]

def engagement_by_brand(posts: List[Dict[str, Any]], aliases: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    agg = defaultdict(lambda: {"likes":0,"comments":0,"shares":0,"views":0,"posts":0})
    for p in posts:
        t = _text_of(p).lower()
        # attribution: first matching brand wins to keep counts exclusive
        owner = None
        for brand, keys in aliases.items():
            if any(k in t for k in keys):
                owner = brand
                break
        if not owner:
            continue
        agg[owner]["likes"] += int(p.get("likesCount") or 0)
        agg[owner]["comments"] += int(p.get("commentsCount") or 0)
        agg[owner]["shares"] += int(p.get("shareCount") or 0)
        agg[owner]["views"] += int(p.get("viewCount") or 0)
        agg[owner]["posts"] += 1
    out = []
    for b, v in agg.items():
        posts_n = max(v["posts"], 1)
        out.append({
            "brand": b,
            "avg_engagement": round((v["likes"]+v["comments"]+v["shares"])/posts_n, 2),
            "avg_views": round(v["views"]/posts_n, 2),
            "posts": v["posts"]
        })
    return sorted(out, key=lambda x: (-x["avg_engagement"], -x["avg_views"]))

def trending_terms(posts: List[Dict[str, Any]], top_k: int = 25) -> List[Dict[str, Any]]:
    # very lightweight: term freq with hashtag boost
    counts = Counter()
    for p in posts:
        text = _text_of(p)
        toks = _tokens(text)
        counts.update(toks)
        # boost hashtags
        tags = p.get("hashtags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split() if t.strip().startswith('#')]
        for t in tags:
            counts[t.lower().lstrip("#")] += 3
    out = [{"term": t, "score": n} for t, n in counts.most_common(top_k)]
    return out

def weekly_trend(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    bucket = defaultdict(lambda: {"posts":0,"eng":0,"views":0})
    for p in posts:
        wk = _week_key(p.get("timestamp") or "")
        e = int(p.get("likesCount") or 0) + int(p.get("commentsCount") or 0) + int(p.get("shareCount") or 0)
        v = int(p.get("viewCount") or 0)
        bucket[wk]["posts"] += 1
        bucket[wk]["eng"] += e
        bucket[wk]["views"] += v
    out = []
    for wk, v in sorted(bucket.items()):
        posts_n = max(v["posts"],1)
        out.append({
            "week": wk,
            "avg_engagement": round(v["eng"]/posts_n, 2),
            "avg_views": round(v["views"]/posts_n, 2),
            "posts": v["posts"]
        })
    return out

def build_competitor_intel(
    posts: List[Dict[str, Any]],
    primary_aliases: Iterable[str] = ("crooks & castles","crooks and castles","crooks"),
    competitor_aliases: Dict[str, Iterable[str]] = None
) -> Dict[str, Any]:
    competitor_aliases = competitor_aliases or {
        "Supreme": ("supreme",),
        "BAPE": ("bape","a bathing ape"),
        "Kith": ("kith",),
        "Palace": ("palace skateboards","palace"),
        "Fear of God": ("fear of god","essentials"),
        "Off-White": ("off-white","off white"),
        "Stüssy": ("stussy","stüssy"),
        "BBC": ("billionaire boys club","bbc icecream","icecream"),
        "Purple Brand": ("purple brand","purpledenim"),
    }
    alias_map = brand_aliases_map(primary_aliases, competitor_aliases)
    return {
        "share_of_voice": share_of_voice(posts, alias_map),
        "brand_engagement": engagement_by_brand(posts, alias_map),
        "trending_terms": trending_terms(posts, top_k=30),
        "weekly_trend": weekly_trend(posts),
        "notes": "Counts derived from captions/descriptions; hashtags boosted in trending terms.",
    }
