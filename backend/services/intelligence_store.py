# backend/services/intelligence_store.py
from __future__ import annotations

import csv
import json
import os
import sqlite3
import datetime as dt
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# --------------------------------------------------------------------------------------
# Paths / DB
# --------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DB   = ROOT / "storage" / "intelligence.db"
DB.parent.mkdir(parents=True, exist_ok=True)

# Default brand (used for Shopify + general rollups)
DEFAULT_BRAND = os.getenv("DEFAULT_BRAND", "Crooks & Castles")

# --------------------------------------------------------------------------------------
# DB helpers / schema
# --------------------------------------------------------------------------------------
def _cx() -> sqlite3.Connection:
    cx = sqlite3.connect(DB)
    cx.row_factory = sqlite3.Row
    return cx

def init():
    with _cx() as cx:
        cx.execute("""
        CREATE TABLE IF NOT EXISTS meta (
          key   TEXT PRIMARY KEY,
          value TEXT
        )""")
        cx.execute("""
        CREATE TABLE IF NOT EXISTS brands (
          id       INTEGER PRIMARY KEY AUTOINCREMENT,
          name     TEXT UNIQUE,
          category TEXT,
          notes    TEXT
        )""")
        cx.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
          id    INTEGER PRIMARY KEY AUTOINCREMENT,
          name  TEXT UNIQUE,
          notes TEXT
        )""")
        cx.execute("""
        CREATE TABLE IF NOT EXISTS benchmarks (
          id      INTEGER PRIMARY KEY AUTOINCREMENT,
          metric  TEXT,
          subject TEXT,
          value   TEXT,
          as_of   TEXT
        )""")

# --------------------------------------------------------------------------------------
# Meta
# --------------------------------------------------------------------------------------
def set_meta(key: str, value: Any):
    with _cx() as cx:
        cx.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value))
        )

def get_meta(key: str, default=None):
    with _cx() as cx:
        r = cx.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

# --------------------------------------------------------------------------------------
# Lists
# --------------------------------------------------------------------------------------
def list_brands() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM brands ORDER BY name").fetchall()]

def list_competitors() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM competitors ORDER BY name").fetchall()]

def list_benchmarks() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute(
            "SELECT * FROM benchmarks ORDER BY as_of, metric, subject"
        ).fetchall()]

# --------------------------------------------------------------------------------------
# Helpers used by importers
# --------------------------------------------------------------------------------------
def ensure_brand(name: str, category: str = "", notes: str = ""):
    if not name:
        return
    with _cx() as cx:
        cx.execute(
            "INSERT INTO brands(name,category,notes) VALUES(?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET category=excluded.category, notes=excluded.notes",
            (name, category, notes)
        )

def insert_benchmarks(rows: Iterable[Dict[str,Any]]) -> int:
    count = 0
    with _cx() as cx:
        for bm in rows:
            cx.execute(
                "INSERT INTO benchmarks(metric,subject,value,as_of) VALUES(?,?,?,?)",
                (bm["metric"], bm["subject"], str(bm["value"]), bm["as_of"])
            )
            count += 1
    return count

# --------------------------------------------------------------------------------------
# Generic CSV importer (Brand / Competitor / Metric / Value / Date)
# --------------------------------------------------------------------------------------
def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _parse_date_maybe(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass
    try:
        return dt.date.fromisoformat(s).isoformat()
    except Exception:
        return None

def _import_generic(csv_path: Path) -> Dict[str,Any]:
    brands, competitors, bms = {}, {}, []

    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)

        def pick(row: dict, *names: str) -> str:
            for n in names:
                for k in row.keys():
                    if _norm(k) == _norm(n):
                        return (row[k] or "").strip()
            return ""

        for row in rdr:
            b      = pick(row, "Brand")
            c      = pick(row, "Competitor")
            metric = pick(row, "Metric")
            value  = pick(row, "Value")
            asof   = pick(row, "AsOf", "Date", "as_of", "date")
            cat    = pick(row, "Category")
            notes  = pick(row, "Notes")

            if b:
                brands.setdefault(b, {"name": b, "category": cat, "notes": notes})
            if c:
                competitors.setdefault(c, {"name": c, "notes": notes})

            if metric and (b or c) and value:
                when = _parse_date_maybe(asof) or dt.date.today().isoformat()
                bms.append({"metric": metric, "subject": b or c, "value": value, "as_of": when})

    with _cx() as cx:
        for v in brands.values():
            cx.execute(
                "INSERT INTO brands(name,category,notes) VALUES(?,?,?) "
                "ON CONFLICT(name) DO UPDATE SET category=excluded.category, notes=excluded.notes",
                (v["name"], v.get("category",""), v.get("notes",""))
            )
        for v in competitors.values():
            cx.execute(
                "INSERT INTO competitors(name,notes) VALUES(?,?) "
                "ON CONFLICT(name) DO UPDATE SET notes=excluded.notes",
                (v["name"], v.get("notes",""))
            )

    inserted = insert_benchmarks(bms)
    return {
        "brands": list(brands.keys()),
        "competitors": list(competitors.keys()),
        "benchmark_count": inserted
    }

# --------------------------------------------------------------------------------------
# Shopify dispatcher
# --------------------------------------------------------------------------------------
def import_csv(csv_path: Path, source: Optional[str] = None, brand: Optional[str] = None) -> Dict[str,Any]:
    init()
    name = csv_path.name.lower()

    if (source or "").lower() == "shopify":
        from . import shopify_importer
        resolved_brand = (brand or DEFAULT_BRAND).strip() or DEFAULT_BRAND
        summary = shopify_importer.import_csv(csv_path, resolved_brand)
    else:
        if any(k in name for k in [
            "orders over time",
            "total sales over time",
            "conversion rate over time",
            "total sales by product"
        ]):
            from . import shopify_importer
            resolved_brand = (brand or DEFAULT_BRAND).strip() or DEFAULT_BRAND
            summary = shopify_importer.import_csv(csv_path, resolved_brand)
        else:
            summary = _import_generic(csv_path)

    snapshot = {
        "brands": summary.get("brands", []),
        "competitors": summary.get("competitors", []),
        "benchmark_count": summary.get("benchmark_count", 0),
        "last_import": dt.datetime.utcnow().isoformat()
    }
    set_meta("executive_snapshot", snapshot)
    return snapshot

# --------------------------------------------------------------------------------------
# Metrics + recaps
# --------------------------------------------------------------------------------------
# Commerce metrics
_METRIC_ORDERS       = "Orders (Shopify)"
_METRIC_NET_SALES    = "Net sales (Shopify)"
_METRIC_GROSS_SALES  = "Gross sales (Shopify)"
_METRIC_DISCOUNTS    = "Discounts (Shopify)"
_METRIC_SESSIONS     = "Sessions (Shopify)"
_METRIC_CONV_PCT     = "Conversion rate % (Shopify)"  # store as e.g. 2.45

# Social metrics
_METRIC_TT_PLAYS   = "TT Plays"
_METRIC_TT_LIKES   = "TT Likes"
_METRIC_TT_SHARES  = "TT Shares"
_METRIC_TT_COMMS   = "TT Comments"
_METRIC_TT_SAVES   = "TT Saves"
_METRIC_IG_PLAYS   = "IG Plays"
_METRIC_IG_LIKES   = "IG Likes"
_METRIC_IG_COMMS   = "IG Comments"
_METRIC_IG_SAVES   = "IG Saves"
_METRIC_TT_TAGS    = "TT Hashtag Mentions"
_METRIC_IG_TAGS    = "IG Hashtag Mentions"

def _window_rows(days: int, brand: Optional[str] = None, offset_days: int = 0) -> List[sqlite3.Row]:
    """
    Return rows within [today-(offset_days+days), today-offset_days)
    If offset_days=0 and days=7 -> last 7 days (including today as end-exclusive).
    """
    end = dt.date.today() - dt.timedelta(days=offset_days)
    start = end - dt.timedelta(days=days)
    start_iso, end_iso = start.isoformat(), end.isoformat()
    with _cx() as cx:
        if brand:
            return cx.execute("""
                SELECT metric, subject, value, as_of FROM benchmarks
                WHERE as_of >= ? AND as_of < ? AND subject LIKE ?
            """, (start_iso, end_iso, f"{brand}%")).fetchall()
        else:
            return cx.execute("""
                SELECT metric, subject, value, as_of FROM benchmarks
                WHERE as_of >= ? AND as_of < ?
            """, (start_iso, end_iso)).fetchall()

def _to_float(s: Any) -> Optional[float]:
    try:
        if s is None: return None
        if isinstance(s, (int,float)): return float(s)
        s = str(s).strip()
        if not s: return None
        return float(s)
    except Exception:
        return None

def _aggregate(rows: List[sqlite3.Row]) -> Tuple[Dict[str,float], Optional[str]]:
    totals: Dict[str,float] = {}
    last_date: Optional[str] = None
    for r in rows:
        v = _to_float(r["value"])
        if v is None:
            continue
        totals[r["metric"]] = totals.get(r["metric"], 0.0) + v
        d = r["as_of"]
        if d and (last_date is None or d > last_date):
            last_date = d
    return totals, last_date

def _derive_aov_and_conversion(rows: List[sqlite3.Row]) -> Dict[str, float]:
    totals, _ = _aggregate(rows)
    orders   = totals.get(_METRIC_ORDERS, 0.0)
    net      = totals.get(_METRIC_NET_SALES, 0.0)
    sessions = totals.get(_METRIC_SESSIONS, 0.0)

    conv_pct_sum = 0.0
    conv_pct_cnt = 0
    for r in rows:
        if r["metric"] == _METRIC_CONV_PCT:
            v = _to_float(r["value"])
            if v is not None:
                conv_pct_sum += v
                conv_pct_cnt += 1

    aov = (net / orders) if orders > 0 else 0.0
    if sessions > 0:
        conv_pct = 100.0 * (orders / sessions)
    else:
        conv_pct = (conv_pct_sum / conv_pct_cnt) if conv_pct_cnt > 0 else 0.0

    return {"aov": aov, "conversion_pct": conv_pct}

def _recap_base(rows: List[sqlite3.Row]) -> Dict[str, Any]:
    totals, last_date = _aggregate(rows)
    derived = _derive_aov_and_conversion(rows)
    return {
        "last_date": last_date,
        "orders": totals.get(_METRIC_ORDERS, 0.0),
        "net_sales": totals.get(_METRIC_NET_SALES, 0.0),
        "gross_sales": totals.get(_METRIC_GROSS_SALES, 0.0),
        "discounts": totals.get(_METRIC_DISCOUNTS, 0.0),
        "sessions": totals.get(_METRIC_SESSIONS, 0.0),
        "aov": derived["aov"],
        "conversion_pct": derived["conversion_pct"],
    }

def _wow(curr: float, prev: float) -> Dict[str, float]:
    delta = curr - prev
    pct = (delta / prev * 100.0) if prev else (100.0 if curr > 0 else 0.0)
    return {"delta": delta, "pct": pct}

def _recap_with_wow(days: int, brand: Optional[str]) -> Dict[str, Any]:
    rows_curr = _window_rows(days, brand=brand, offset_days=0)
    rows_prev = _window_rows(days, brand=brand, offset_days=days)

    curr = _recap_base(rows_curr)
    prev = _recap_base(rows_prev)

    recap = {
        "days": days,
        **curr,
        "current": True,
        "refreshed_at": dt.datetime.utcnow().isoformat(),
        "wow": {
            "orders": _wow(curr["orders"], prev["orders"]),
            "net_sales": _wow(curr["net_sales"], prev["net_sales"]),
            "gross_sales": _wow(curr["gross_sales"], prev["gross_sales"]),
            "discounts": _wow(curr["discounts"], prev["discounts"]),
            "sessions": _wow(curr["sessions"], prev["sessions"]),
            "aov": _wow(curr["aov"], prev["aov"]),
            "conversion_pct": _wow(curr["conversion_pct"], prev["conversion_pct"]),
        }
    }
    return recap

# --------------------------------- Social -------------------------------------------
def _sum_metrics(rows: List[sqlite3.Row], names: List[str]) -> float:
    tot = 0.0
    for r in rows:
        if r["metric"] in names:
            v = _to_float(r["value"])
            if v is not None:
                tot += v
    return tot

def _top_hashtags(days: int, brand: Optional[str]) -> Dict[str, List[Dict[str, Any]]]:
    rows = _window_rows(days, brand=brand, offset_days=0)
    rows_prev = _window_rows(days, brand=brand, offset_days=days)

    def top_from(rows: List[sqlite3.Row], metrics: List[str]) -> List[Dict[str, Any]]:
        agg: Dict[str, float] = {}
        for r in rows:
            if r["metric"] in metrics:
                tag = r["subject"]
                val = _to_float(r["value"]) or 0.0
                agg[tag] = agg.get(tag, 0.0) + val
        items = sorted(agg.items(), key=lambda x: x[1], reverse=True)[:10]
        return [{"tag": k, "count": v} for k, v in items]

    top_tt = top_from(rows, [_METRIC_TT_TAGS])
    top_ig = top_from(rows, [_METRIC_IG_TAGS])

    # WoW for combined tags (match by tag)
    combined_curr: Dict[str, float] = {}
    for item in top_from(rows, [_METRIC_TT_TAGS, _METRIC_IG_TAGS]):
        combined_curr[item["tag"]] = item["count"]
    combined_prev: Dict[str, float] = {}
    for item in top_from(rows_prev, [_METRIC_TT_TAGS, _METRIC_IG_TAGS]):
        combined_prev[item["tag"]] = item["count"]

    combined = []
    for tag, cnt in sorted(combined_curr.items(), key=lambda x: x[1], reverse=True)[:10]:
        prev = combined_prev.get(tag, 0.0)
        combined.append({
            "tag": tag,
            "count": cnt,
            "wow": _wow(cnt, prev)
        })

    return {"tiktok": top_tt, "instagram": top_ig, "combined": combined}

def _recap_social_with_wow(days: int, brand: Optional[str]) -> Dict[str, Any]:
    rows_curr = _window_rows(days, brand=brand, offset_days=0)
    rows_prev = _window_rows(days, brand=brand, offset_days=days)

    def roll(rows: List[sqlite3.Row]) -> Dict[str, float]:
        return {
            "plays": _sum_metrics(rows, [_METRIC_TT_PLAYS, _METRIC_IG_PLAYS]),
            "likes": _sum_metrics(rows, [_METRIC_TT_LIKES, _METRIC_IG_LIKES]),
            "comments": _sum_metrics(rows, [_METRIC_TT_COMMS, _METRIC_IG_COMMS]),
            "shares": _sum_metrics(rows, [_METRIC_TT_SHARES]),   # IG shares often unavailable
            "saves": _sum_metrics(rows, [_METRIC_TT_SAVES, _METRIC_IG_SAVES]),
        }

    cur = roll(rows_curr)
    prv = roll(rows_prev)

    last_date = None
    for r in rows_curr:
        d = r["as_of"]
        if d and (last_date is None or d > last_date):
            last_date = d

    recap = {
        "days": days,
        "last_date": last_date,
        **cur,
        "current": True,
        "refreshed_at": dt.datetime.utcnow().isoformat(),
        "wow": {
            "plays": _wow(cur["plays"], prv["plays"]),
            "likes": _wow(cur["likes"], prv["likes"]),
            "comments": _wow(cur["comments"], prv["comments"]),
            "shares": _wow(cur["shares"], prv["shares"]),
            "saves": _wow(cur["saves"], prv["saves"]),
        },
        "top_hashtags": _top_hashtags(days, brand)
    }
    return recap

# --------------------------------------------------------------------------------------
# Executive Overview
# --------------------------------------------------------------------------------------
def executive_overview(brand: Optional[str] = DEFAULT_BRAND) -> Dict[str,Any]:
    init()
    snap = get_meta("executive_snapshot", default={"brands": [], "competitors": [], "benchmark_count": 0})

    return {
        "snapshot": snap,
        "brands": list_brands(),
        "competitors": list_competitors(),
        "benchmarks": list_benchmarks(),
        "recaps": {
            "7d": _recap_with_wow(7, brand),
            "30d": _recap_with_wow(30, brand),
            "social": {
                "7d": _recap_social_with_wow(7, brand),
                "30d": _recap_social_with_wow(30, brand)
            }
        }
    }
