# backend/services/intelligence_store.py
from __future__ import annotations
import csv, json, sqlite3, os, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DB   = ROOT / "storage" / "intelligence.db"
DB.parent.mkdir(parents=True, exist_ok=True)

def _cx() -> sqlite3.Connection:
    cx = sqlite3.connect(DB)
    cx.row_factory = sqlite3.Row
    return cx

def init():
    with _cx() as cx:
        cx.execute("""
        CREATE TABLE IF NOT EXISTS meta (
          key TEXT PRIMARY KEY,
          value TEXT
        )""")
        cx.execute("""
        CREATE TABLE IF NOT EXISTS brands (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          category TEXT,
          notes TEXT
        )""")
        cx.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          notes TEXT
        )""")
        cx.execute("""
        CREATE TABLE IF NOT EXISTS benchmarks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          metric TEXT,       -- e.g., "IG Followers", "AOV"
          subject TEXT,      -- brand or competitor name
          value TEXT,
          as_of TEXT
        )""")

def set_meta(key: str, value: Any):
    with _cx() as cx:
        cx.execute("INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                   (key, json.dumps(value)))

def get_meta(key: str, default=None):
    with _cx() as cx:
        r = cx.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

def list_brands() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM brands ORDER BY name").fetchall()]

def list_competitors() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM competitors ORDER BY name").fetchall()]

def list_benchmarks() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM benchmarks ORDER BY metric, subject").fetchall()]

def import_csv(file_path: Path):
    """
    Try to parse a generic CSV with columns such as:
    Brand, Competitor, Metric, Value, Category, Notes
    This is tolerant; it will populate the three tables and store a snapshot.
    """
    init()
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    def pick(row: dict, *names: str) -> str:
        for n in names:
            for k in row.keys():
                if k.strip().lower() == n.lower():
                    return (row[k] or "").strip()
        return ""

    brands, competitors, benchmarks = {}, {}, []
    with file_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            b = pick(row, "Brand")
            c = pick(row, "Competitor")
            metric = pick(row, "Metric")
            value  = pick(row, "Value")
            cat    = pick(row, "Category")
            notes  = pick(row, "Notes")

            if b:
                brands.setdefault(b, {"name": b, "category": cat, "notes": notes})
            if c:
                competitors.setdefault(c, {"name": c, "notes": notes})

            if metric and (b or c) and value:
                subject = b or c
                benchmarks.append({"metric": metric, "subject": subject, "value": value, "as_of": datetime.date.today().isoformat()})

    # write to DB
    with _cx() as cx:
        for v in brands.values():
            cx.execute("INSERT INTO brands(name,category,notes) VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET category=excluded.category, notes=excluded.notes",
                       (v["name"], v.get("category",""), v.get("notes","")))
        for v in competitors.values():
            cx.execute("INSERT INTO competitors(name,notes) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET notes=excluded.notes",
                       (v["name"], v.get("notes","")))
        for bm in benchmarks:
            cx.execute("INSERT INTO benchmarks(metric,subject,value,as_of) VALUES(?,?,?,?)",
                       (bm["metric"], bm["subject"], bm["value"], bm["as_of"]))

    # store a light snapshot for executive overview
    snapshot = {
        "brands": list(brands.keys()),
        "competitors": list(competitors.keys()),
        "benchmark_count": len(benchmarks),
        "last_import": datetime.datetime.utcnow().isoformat()
    }
    set_meta("executive_snapshot", snapshot)
    return snapshot

def executive_overview() -> Dict[str,Any]:
    init()
    snap = get_meta("executive_snapshot", default={"brands": [], "competitors": [], "benchmark_count": 0})
    return {
        "snapshot": snap,
        "brands": list_brands(),
        "competitors": list_competitors(),
        "benchmarks": list_benchmarks(),
    }
