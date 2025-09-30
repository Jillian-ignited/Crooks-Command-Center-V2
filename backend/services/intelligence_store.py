# backend/services/intelligence_store.py
from __future__ import annotations
import csv, json, sqlite3, os, datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterable

ROOT = Path(__file__).resolve().parents[1]
DB   = ROOT / "storage" / "intelligence.db"
DB.parent.mkdir(parents=True, exist_ok=True)

# Default brand for Shopify data
DEFAULT_BRAND = os.getenv("DEFAULT_BRAND", "Crooks & Castles")

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
          metric TEXT,
          subject TEXT,
          value TEXT,
          as_of TEXT
        )""")

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

def list_brands() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM brands ORDER BY name").fetchall()]

def list_competitors() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM competitors ORDER BY name").fetchall()]

def list_benchmarks() -> List[Dict[str,Any]]:
    with _cx() as cx:
        return [dict(r) for r in cx.execute("SELECT * FROM benchmarks ORDER BY metric, subject, as_of").fetchall()]

# ---------- public helpers (used by shopify_importer) ----------
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
                (bm["metric"], bm["subject"], bm["value"], bm["as_of"])
            )
            count += 1
    return count

# ---------- generic importer (unchanged behavior) ----------
def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _parse_date_maybe(s: str) -> Optional[str]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime(s.strip(), fmt).date().isoformat()
        except Exception:
            continue
    try:
        return dt.date.fromisoformat(s.strip()).isoformat()
    except Exception:
        return None

def _import_generic(csv_path: Path) -> Dict[str,Any]:
    brands, competitors, benchmarks = {}, {}, []
    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)

        def pick(row: dict, *names: str) -> str:
            for n in names:
                for k in row.keys():
                    if _norm(k) == _norm(n):
                        return (row[k] or "").strip()
            return ""

        for row in rdr:
            b = pick(row, "Brand")
            c = pick(row, "Competitor")
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
                benchmarks.append({"metric": metric, "subject": b or c, "value": value, "as_of": when})

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

    inserted = insert_benchmarks(benchmarks)
    return {
        "brands": list(brands.keys()),
        "competitors": list(competitors.keys()),
        "benchmark_count": inserted
    }

# ---------- top-level dispatcher ----------
def import_csv(csv_path: Path, source: Optional[str] = None, brand: Optional[str] = None) -> Dict[str,Any]:
    """
    Dispatch CSV import by source. If 'shopify', use dedicated importer
    and default brand to Crooks & Castles unless overridden.
    """
    init()
    name = csv_path.name.lower()

    # Shopify path
    if (source or "").lower() == "shopify":
        from . import shopify_importer
        resolved_brand = (brand or DEFAULT_BRAND).strip() or DEFAULT_BRAND
        summary = shopify_importer.import_csv(csv_path, resolved_brand)
    else:
        # Auto-detect Shopify by filename keywords (so you can omit ?source=shopify)
        if any(k in name for k in ["orders over time", "total sales over time", "conversion rate over time", "total sales by product"]):
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

def executive_overview() -> Dict[str,Any]:
    init()
    snap = get_meta("executive_snapshot", default={"brands": [], "competitors": [], "benchmark_count": 0})
    return {
        "snapshot": snap,
        "brands": list_brands(),
        "competitors": list_competitors(),
        "benchmarks": list_benchmarks(),
    }
