# backend/services/agency_store.py
from __future__ import annotations
import csv, sqlite3, os, datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR   = Path(__file__).resolve().parents[1]
DB_PATH    = BASE_DIR / "storage" / "agency.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

STATUS_VALUES = [
    "Not Started", "In Progress", "Blocked", "Waiting Approval", "Approved", "Done"
]

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema():
    with _conn() as cx:
        cx.execute("""
        CREATE TABLE IF NOT EXISTS deliverables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase TEXT,
            task TEXT,
            owner TEXT,
            channel TEXT,
            assets TEXT,
            dependencies TEXT,
            notes TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Not Started',
            priority INTEGER DEFAULT 3,
            last_updated TEXT
        )
        """)
        cx.execute("CREATE INDEX IF NOT EXISTS idx_deliverables_phase ON deliverables(phase)")
        cx.execute("CREATE INDEX IF NOT EXISTS idx_deliverables_status ON deliverables(status)")

def _normalize(row: Dict[str, Any]) -> Dict[str, Any]:
    # Map CSV headers → DB columns (adjust to your CSV header names)
    # Expected headers (case-insensitive): Phase, Task, Owner, Channel, Assets, Dependencies, Notes, Due Date, Priority
    def g(keys, default=""):
        for k in keys:
            for cand in row.keys():
                if cand.strip().lower() == k.lower():
                    return (row[cand] or "").strip()
        return default

    due = g(["Due Date","DueDate"])
    try:
        # Normalize to YYYY-MM-DD
        if due:
            dt = datetime.datetime.fromisoformat(due.replace("/", "-"))
            due = dt.date().isoformat()
    except Exception:
        pass

    pri = g(["Priority"])
    try:
        pri = int(pri) if str(pri).strip() else 3
    except Exception:
        pri = 3

    return {
        "phase": g(["Phase"]),
        "task": g(["Task","Deliverable","Title"]),
        "owner": g(["Owner","Assignee"]),
        "channel": g(["Channel","Platform"]),
        "assets": g(["Assets","Asset Links","Links"]),
        "dependencies": g(["Dependencies","Depends On"]),
        "notes": g(["Notes","Description"]),
        "due_date": due,
        "priority": pri,
    }

def import_csv(csv_path: Path, truncate: bool = True) -> int:
    init_schema()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig") as f, _conn() as cx:
        rdr = csv.DictReader(f)
        if truncate:
            cx.execute("DELETE FROM deliverables")
        count = 0
        for raw in rdr:
            d = _normalize(raw)
            cx.execute("""
            INSERT INTO deliverables (phase, task, owner, channel, assets, dependencies, notes, due_date, status, priority, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Not Started', ?, ?)
            """, (
                d["phase"], d["task"], d["owner"], d["channel"], d["assets"], d["dependencies"], d["notes"], d["due_date"],
                d["priority"], datetime.datetime.utcnow().isoformat()
            ))
            count += 1
        return count

def list_deliverables(phase: Optional[str]=None, status: Optional[str]=None, q: Optional[str]=None) -> List[Dict[str,Any]]:
    init_schema()
    sql = "SELECT * FROM deliverables WHERE 1=1"
    args: List[Any] = []
    if phase:
        sql += " AND phase = ?"
        args.append(phase)
    if status:
        sql += " AND status = ?"
        args.append(status)
    if q:
        like = f"%{q}%"
        sql += " AND (task LIKE ? OR owner LIKE ? OR channel LIKE ? OR notes LIKE ?)"
        args.extend([like, like, like, like])
    sql += " ORDER BY priority ASC, COALESCE(due_date, '9999-12-31') ASC, id ASC"
    with _conn() as cx:
        rows = [dict(r) for r in cx.execute(sql, args).fetchall()]
    return rows

def get_one(item_id: int) -> Optional[Dict[str,Any]]:
    with _conn() as cx:
        r = cx.execute("SELECT * FROM deliverables WHERE id = ?", (item_id,)).fetchone()
        return dict(r) if r else None

def update_one(item_id: int, fields: Dict[str,Any]) -> Optional[Dict[str,Any]]:
    allowed = {"phase","task","owner","channel","assets","dependencies","notes","due_date","status","priority"}
    set_parts = []
    args: List[Any] = []
    for k,v in fields.items():
        if k in allowed:
            set_parts.append(f"{k} = ?")
            args.append(v)
    if not set_parts:
        return get_one(item_id)
    set_parts.append("last_updated = ?")
    args.append(datetime.datetime.utcnow().isoformat())
    args.append(item_id)
    with _conn() as cx:
        cx.execute(f"UPDATE deliverables SET {', '.join(set_parts)} WHERE id = ?", args)
    return get_one(item_id)

def phases() -> List[str]:
    with _conn() as cx:
        rows = cx.execute("SELECT DISTINCT phase FROM deliverables ORDER BY phase").fetchall()
    return [r[0] for r in rows if r[0]]

def stats() -> Dict[str,Any]:
    with _conn() as cx:
        total = cx.execute("SELECT COUNT(*) FROM deliverables").fetchone()[0]
        by_status = {s: cx.execute("SELECT COUNT(*) FROM deliverables WHERE status = ?", (s,)).fetchone()[0] for s in STATUS_VALUES}
        overdue = cx.execute("SELECT COUNT(*) FROM deliverables WHERE due_date IS NOT NULL AND due_date < date('now') AND status NOT IN ('Approved','Done')").fetchone()[0]
    return {"total": total, "by_status": by_status, "overdue": overdue, "statuses": STATUS_VALUES}
