# backend/services/apify_importer.py
from __future__ import annotations

import json, datetime as dt
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import intelligence_store as store

# ---------- helpers ----------
def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _to_float(x: Any) -> Optional[float]:
    try:
        if x is None: return None
        if isinstance(x, (int, float)): return float(x)
        s = str(x).replace(",", "").strip()
        if s.endswith("%"):
            s = s[:-1].strip()
        return float(s) if s else None
    except Exception:
        return None

def _parse_iso(s: Optional[str]) -> Optional[str]:
    if not s: return None
    try:
        # Apify scrapers usually emit ISO strings (e.g., 2025-09-28T03:25:46.000Z)
        return dt.datetime.fromisoformat(s.replace("Z","+00:00")).date().isoformat()
    except Exception:
        return None

def _read_jsonl(p: Path) -> Iterable[Dict[str, Any]]:
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            yield json.loads(line)

def _read_json_array(p: Path) -> Iterable[Dict[str, Any]]:
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict):
                yield it

def _iter_records(p: Path) -> Iterable[Dict[str, Any]]:
    name = p.name.lower()
    if name.endswith(".jsonl"):
        yield from _read_jsonl(p)
    elif name.endswith(".json"):
        yield from _read_json_array(p)
    else:
        # fallback: try jsonl first then json
        try:
            yield from _read_jsonl(p)
        except Exception:
            yield from _read_json_array(p)

def _hashtags(text: str) -> List[str]:
    out = []
    if not text: return out
    for token in text.replace("\n", " ").split():
        if token.startswith("#") and len(token) > 1:
            out.append(token.rstrip(",.!?;:").lower())
    return out

def _brand_for_text(text: str, default_brand: str) -> str:
    t = _norm(text)
    # Simple brand signal for Crooks & Castles
    if "crooks" in t or "crooksandcastles" in t or "crooks & castles" in t:
        return "Crooks & Castles"
    return default_brand

# ---------- TikTok ----------
def _import_tiktok(records: Iterable[Dict[str, Any]], brand: str) -> Dict[str, Any]:
    store.ensure_brand(brand)
    bms: List[Dict[str, Any]] = []
    tag_rows: List[Tuple[str, str]] = []  # (date, hashtag)

    for r in records:
        text   = (r.get("text") or r.get("caption") or "").strip()
        when   = _parse_iso(r.get("createTimeISO") or r.get("createTime") or r.get("timestamp"))
        plays  = _to_float(r.get("playCount") or r.get("plays"))
        likes  = _to_float(r.get("diggCount") or r.get("likes") or r.get("likesCount"))
        shares = _to_float(r.get("shareCount") or r.get("shares") or r.get("sharesCount"))
        comms  = _to_float(r.get("commentCount") or r.get("comments") or r.get("commentsCount"))
        saves  = _to_float(r.get("collectCount") or r.get("saves") or r.get("savesCount"))

        subj_brand = _brand_for_text(text, brand)
        subj = f"{subj_brand} · TikTok"

        if not when:
            # If missing timestamp, skip (we aggregate by date)
            continue

        def add(metric: str, val: Optional[float]):
            if val is None: return
            bms.append({"metric": metric, "subject": subj, "value": str(val), "as_of": when})

        add("TT Plays", plays)
        add("TT Likes", likes)
        add("TT Shares", shares)
        add("TT Comments", comms)
        add("TT Saves", saves)

        for h in _hashtags(text):
            tag_rows.append((when, h))

    inserted = store.insert_benchmarks(bms)

    # Optionally store hashtag counts as benchmarks (per day)
    if tag_rows:
        by_day: Dict[Tuple[str, str], int] = {}
        for d, h in tag_rows:
            by_day[(d, h)] = by_day.get((d, h), 0) + 1
        tag_bms = [
            {"metric": "TT Hashtag Mentions", "subject": tag, "value": str(cnt), "as_of": day}
            for (day, tag), cnt in by_day.items()
        ]
        inserted += store.insert_benchmarks(tag_bms)

    return {"brands": [brand], "competitors": [], "benchmark_count": inserted}

# ---------- Instagram ----------
def _import_instagram(records: Iterable[Dict[str, Any]], brand: str) -> Dict[str, Any]:
    store.ensure_brand(brand)
    bms: List[Dict[str, Any]] = []
    tag_rows: List[Tuple[str, str]] = []

    for r in records:
        text   = (r.get("caption") or r.get("text") or r.get("title") or "").strip()
        when   = _parse_iso(r.get("timestamp") or r.get("taken_at") or r.get("createTimeISO"))
        # Likes/comments/saves; reels often include play count via video_play_count or similar
        likes  = _to_float(r.get("likesCount") or r.get("likeCount") or r.get("edge_media_preview_like") or r.get("likes"))
        comms  = _to_float(r.get("commentsCount") or r.get("commentCount") or r.get("comments"))
        saves  = _to_float(r.get("saves") or r.get("saved") or r.get("saveCount"))
        plays  = _to_float(r.get("videoPlayCount") or r.get("plays") or r.get("reelsPlayCount") or r.get("viewCount"))

        subj_brand = _brand_for_text(text, brand)
        subj = f"{subj_brand} · Instagram"

        if not when:
            continue

        def add(metric: str, val: Optional[float]):
            if val is None: return
            bms.append({"metric": metric, "subject": subj, "value": str(val), "as_of": when})

        add("IG Plays", plays)
        add("IG Likes", likes)
        add("IG Comments", comms)
        add("IG Saves", saves)

        for h in _hashtags(text):
            tag_rows.append((when, h))

    inserted = store.insert_benchmarks(bms)

    if tag_rows:
        by_day: Dict[Tuple[str, str], int] = {}
        for d, h in tag_rows:
            by_day[(d, h)] = by_day.get((d, h), 0) + 1
        tag_bms = [
            {"metric": "IG Hashtag Mentions", "subject": tag, "value": str(cnt), "as_of": day}
            for (day, tag), cnt in by_day.items()
        ]
        inserted += store.insert_benchmarks(tag_bms)

    return {"brands": [brand], "competitors": [], "benchmark_count": inserted}

# ---------- main dispatch ----------
def import_file(path: Path, platform: Optional[str], brand: str) -> Dict[str, Any]:
    """
    platform: 'tiktok' | 'instagram' | None (auto-detect by keys)
    """
    # Select reader
    it = list(_iter_records(path))
    if not it:
        return {"brands": [brand], "competitors": [], "benchmark_count": 0}

    # Auto-detect if needed
    pl = (platform or "").lower()
    if not pl:
        # Very lightweight sniffing
        sample = it[0]
        keys = {k.lower() for k in sample.keys()}
        if any(k in keys for k in ("playcount", "diggcount", "sharecount", "collectcount", "videometa.duration", "createtimeiso")):
            pl = "tiktok"
        elif any(k in keys for k in ("likescoun", "commentscount", "reelsplaycount", "videoplaycount", "timestamp", "taken_at")):
            pl = "instagram"
        else:
            # default to instagram if unsure
            pl = "instagram"

    if pl == "tiktok":
        return _import_tiktok(it, brand)
    if pl == "instagram":
        return _import_instagram(it, brand)

    # Fallback
    return _import_tiktok(it, brand)
