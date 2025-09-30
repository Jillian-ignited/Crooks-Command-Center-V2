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

# Default brand for Shopify / general commerce (can override via Render env)
DEFAULT_BRAND = os.getenv("DEFAULT_BRAND", "Crooks & Castles")

# --------------------------------------------------------------------------------------
# Schema / DB helpers
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
# Public lists
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
# Public helpers (used by Shopify / Apify importers)
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
    """
    rows: [{'metric': str, 'subject': str, 'value': str|number, 'as_of': 'YYYY-MM-DD'}, ...]
    """
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
# Generic CSV importer (Brand, Competitor, Metric, Value, AsOf/Date)
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
    """
    Dispatch CSV import. If 'shopify', use dedicated importer.
    Otherwise try auto-detect by filename; else generic CSV.
    """
    init()
    name = csv_path.name.lower()

    if (source or "").lower() == "shopify":
        from . import shopify_importer
        resolved_brand = (brand or DEFAULT_BRAND).strip() or DEFAULT_BRAND
        summary = shopify_importer.import_csv(csv_path, resolved_brand)
    else:
        # Auto-detect common Shopify filenames so ?source=shopify is optional.
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
# Recaps (Commerce: 7d/30d with AOV & Conversion)
# --------------------------------------------------------------------------------------
_METRIC_ORDERS       = "Orders (Shopify)"
_METRIC_NET_SALES    = "Net sales (Shopify)"
_METRIC_GROSS_SALES  = "Gross sales (Shopify)"
_METRIC_DISCOUNTS    = "Discounts (Shopify)"
_METRIC_SESSIONS     = "Sessions (Shopify)"
_METRIC_CONV_PCT     = "Conversion rate % (Shopify)"  # raw percent like '2.45' (not 0.0245)

# Social metrics we aggregate when present
_METRIC_TT_PLAYS   = "TT Plays"
_METRIC_TT_LIKES   = "TT Likes"
_METRIC_TT_SHARES  = "TT Shares"
_METRIC_TT_COMMS   = "TT Comments"
_METRIC_TT_SAVES   = "TT Saves"
_METRIC_IG_PLAYS   = "IG Plays"
_METRIC_IG_LIKES   = "IG Likes"
_METRIC_IG_COMMS   = "IG Comments"
_METRIC_IG_SAVES   = "IG Saves"

def _window_rows(days: int, brand: Optional[str] = None) -> List[sqlite3.Row]:
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    with _cx() as cx:
        if brand:
            return cx.execute("""
                SELECT metric, subject, value, as_of FROM benchmarks
                WHERE as_of >= ? AND subject LIKE ?
            """, (since, f"{brand}%")).fetchall()
        else:
            return cx.execute("""
                SELECT metric, subject, value, as_of FROM benchmarks
                WHERE as_of >= ?
            """, (since,)).fetchall()

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

    # Average of daily % if sessions missing
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

def _recap(days: int, brand: Optional[str]) -> Dict[str, Any]:
    rows = _window_rows(days, brand=brand)
    totals, last_date = _aggregate(rows)
    derived = _derive_aov_and_conversion(rows)

    recap = {
        "days": days,
        "last_date": last_date,
        "orders": totals.get(_METRIC_ORDERS, 0.0),
        "net_sales": totals.get(_METRIC_NET_SALES, 0.0),
        "gross_sales": totals.get(_METRIC_GROSS_SALES, 0.0),
        "discounts": totals.get(_METRIC_DISCOUNTS, 0.0),
        "sessions": totals.get(_METRIC_SESSIONS, 0.0),
        "aov": derived["aov"],
        "conversion_pct": derived["conversion_pct"],
        "current": True,
        "refreshed_at": dt.datetime.utcnow().isoformat()
    }
    return recap

# --------------------------------------------------------------------------------------
# Social recaps (TikTok + Instagram)
# --------------------------------------------------------------------------------------
def _sum_metrics(rows: List[sqlite3.Row], names: List[str]) -> float:
    tot = 0.0
    for r in rows:
        if r["metric"] in names:
            v = _to_float(r["value"])
            if v is not None:
                tot += v
    return tot

def _recap_social(days: int, brand: Optional[str]) -> Dict[str, Any]:
    rows = _window_rows(days, brand=brand)
    plays    = _sum_metrics(rows, [_METRIC_TT_PLAYS, _METRIC_IG_PLAYS])
    likes    = _sum_metrics(rows, [_METRIC_TT_LIKES, _METRIC_IG_LIKES])
    comments = _sum_metrics(rows, [_METRIC_TT_COMMS, _METRIC_IG_COMMS])
    shares   = _sum_metrics(rows, [_METRIC_TT_SHARES])  # IG shares not always available
    saves    = _sum_metrics(rows, [_METRIC_TT_SAVES, _METRIC_IG_SAVES])

    last_date: Optional[str] = None
    for r in rows:
        d = r["as_of"]
        if d and (last_date is None or d > last_date):
            last_date = d

    return {
        "days": days,
        "last_date": last_date,
        "plays": plays,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "current": True,
        "refreshed_at": dt.datetime.utcnow().isoformat()
    }

# --------------------------------------------------------------------------------------
# Executive Overlook (cards/tables + recaps)
# --------------------------------------------------------------------------------------
def executive_overview(brand: Optional[str] = DEFAULT_BRAND) -> Dict[str,Any]:
    """
    Returns:
      snapshot: last import meta
      brands / competitors / benchmarks: raw lists
      recaps: {
        7d: {...commerce KPIs...},
        30d: {...commerce KPIs...},
        social: { 7d: {...}, 30d: {...} }
      }
    """
    init()
    snap = get_meta("executive_snapshot", default={"brands": [], "competitors": [], "benchmark_count": 0})

    return {
        "snapshot": snap,
        "brands": list_brands(),
        "competitors": list_competitors(),
        "benchmarks": list_benchmarks(),
        "recaps": {
            "7d": _recap(7, brand),
            "30d": _recap(30, brand),
            "social": {
                "7d": _recap_social(7, brand),
                "30d": _recap_social(30, brand)
            }
        }
    }
