# backend/services/agency_store.py
from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

# If you're using SQLAlchemy Core/Engine:
from sqlalchemy import text
from sqlalchemy.engine import Connection

# If you prefer to keep parsing in a helper module, uncomment this and use parse_due_date below:
# from ._date_utils import parse_due_date as _parse_due_date


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def parse_due_date(raw: Optional[str]) -> Optional[str]:
    """
    Normalize various date strings to ISO (YYYY-MM-DD).
    Returns None if parsing fails (do not persist raw TEXT dates).
    """
    if not raw:
        return None
    s = raw.strip()
    # Common formats to support:
    formats = (
        "%Y-%m-%d",  # ISO
        "%Y/%m/%d",  # ISO with slashes
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m-%d-%Y",
        "%m-%d-%y",
    )
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    logger.warning("Unparsable due date %r; dropping value", raw)
    return None

# If you imported helper module, swap to:
# def parse_due_date(raw: Optional[str]) -> Optional[str]:
#     return _parse_due_date(raw)


def safe_execute(conn: Connection, sql: str, params: Optional[Dict[str, Any]] = None):
    """
    Execute parameterized SQL safely (prevents SQL injection).
    Usage:
      safe_execute(conn, "SELECT * FROM t WHERE brand = :brand", {"brand": brand})
    """
    return conn.execute(text(sql), params or {})


# -----------------------------------------------------------------------------
# Core ingestion/path you already have
# -----------------------------------------------------------------------------
def ingest_row(row: Dict[str, Any], *, conn: Connection) -> None:
    """
    Example ingestion entry point. Adjust field names to your schema.
    Assumes you were previously doing something like g([...]) to fetch values.
    """
    def g(keys: Iterable[str]) -> Optional[str]:
        for k in keys:
            if k in row and row[k] is not None:
                v = str(row[k]).strip()
                if v != "":
                    return v
        return None

    # --- FIXED: robust due-date normalization (no blind except/pass) ---
    due = parse_due_date(g(["Due Date", "DueDate"]))

    # Example: parameterized insert/update — replace with your real table/columns
    sql = """
    INSERT INTO agencies (brand, title, due)
    VALUES (:brand, :title, :due)
    ON CONFLICT (brand, title)
    DO UPDATE SET due = COALESCE(EXCLUDED.due, agencies.due)
    """
    params = {
        "brand": g(["Brand", "brand"]),
        "title": g(["Title", "Task", "Name"]),
        "due": due,  # None or ISO date string
    }

    # --- FIXED: no f-strings in SQL; use parameters ---
    try:
        safe_execute(conn, sql, params)
    except Exception as e:
        # Narrow/handle by expected exceptions if you know them (IntegrityError, etc.)
        logger.error("ingest_row failed for %s: %s", params.get("title"), e)
        raise  # do not silently pass


def list_deliverables(*, conn: Connection, brand: Optional[str] = None) -> Sequence[Tuple]:
    """
    Example query using parameterization; sorts by date correctly because 'due'
    is stored as ISO text or NULL (no raw '12/20/2026' strings).
    """
    base = """
    SELECT id, brand, title, due
    FROM agencies
    WHERE (:brand IS NULL OR brand = :brand)
    ORDER BY due NULLS LAST, id DESC
    """
    rows = safe_execute(conn, base, {"brand": brand}).fetchall()
    return rows


def stats(*, conn: Connection, today: Optional[datetime.date] = None) -> Dict[str, Any]:
    """
    Example stats calculation comparing ISO dates lexicographically works,
    but to be explicit we cast to DATE where needed.
    """
    today = today or datetime.date.today()
    params = {"today": today.isoformat()}

    sql = """
    SELECT
      COUNT(*) FILTER (WHERE due IS NOT NULL AND DATE(due) < DATE(:today)) AS overdue,
      COUNT(*) FILTER (WHERE due IS NOT NULL AND DATE(due) = DATE(:today)) AS due_today,
      COUNT(*) FILTER (WHERE due IS NOT NULL AND DATE(due) > DATE(:today)) AS upcoming,
      COUNT(*) AS total
    FROM agencies
    """
    row = safe_execute(conn, sql, params).mappings().first() or {}
    return {
        "overdue": row.get("overdue", 0),
        "due_today": row.get("due_today", 0),
        "upcoming": row.get("upcoming", 0),
        "total": row.get("total", 0),
    }


# -----------------------------------------------------------------------------
# Public API your routers probably call
# -----------------------------------------------------------------------------
def ingest_many(rows: Iterable[Dict[str, Any]], *, conn: Connection) -> int:
    """
    Bulk ingest with proper error handling (no try/except/pass).
    """
    count = 0
    for r in rows:
        ingest_row(r, conn=conn)
        count += 1
    return count