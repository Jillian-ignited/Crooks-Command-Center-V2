# backend/services/shopify_importer.py
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from . import intelligence_store as store

# ---------- utilities ----------

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _strip_num(s: str | None) -> Optional[str]:
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    # remove currency symbols, commas, and percent signs; keep minus and dot
    out = []
    for ch in s:
        if ch.isdigit() or ch in ".-":
            out.append(ch)
    return "".join(out) if out else None

def _parse_date_maybe(s: str | None) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass
    # Shopify often uses "Aug 27, 2025"
    try:
        return dt.datetime.strptime(s, "%b %d, %Y").date().isoformat()
    except Exception:
        return None

def _header_map(headers: List[str]) -> Dict[str, str]:
    """
    Build a quick lookup dict from normalized headers to original header text.
    """
    m = {}
    for h in headers:
        m[_norm(h)] = h
    return m

def _collect(reader: csv.DictReader) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    rows = list(reader)
    hdr = _header_map(reader.fieldnames or [])
    return rows, hdr

# ---------- import handlers ----------

def _import_orders_over_time(csv_path: Path, brand: str) -> Dict[str, Any]:
    store.ensure_brand(brand)
    inserted = 0
    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        rows, hdr = _collect(rdr)

    # likely columns
    col_date = hdr.get("date") or hdr.get("day") or "Date"
    col_orders = None
    for key in ("orders", "total orders", "number of orders"):
        if key in hdr:
            col_orders = hdr[key]; break
    if not col_orders:
        # find any header containing "order"
        for k, v in hdr.items():
            if "order" in k:
                col_orders = v; break

    bms = []
    for r in rows:
        when = _parse_date_maybe(r.get(col_date))
        if not when:
            continue
        orders = _strip_num(r.get(col_orders)) if col_orders else None
        if orders:
            bms.append({"metric": "Orders (Shopify)", "subject": brand, "value": orders, "as_of": when})

    inserted += store.insert_benchmarks(bms)
    return {"brands": [brand], "competitors": [], "benchmark_count": inserted}

def _import_total_sales_over_time(csv_path: Path, brand: str) -> Dict[str, Any]:
    store.ensure_brand(brand)
    inserted = 0
    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        rows, hdr = _collect(rdr)

    col_date = hdr.get("date") or hdr.get("day") or "Date"

    def pick(*candidates: str) -> Optional[str]:
        for c in candidates:
            if c in hdr:
                return hdr[c]
        return None

    col_gross  = pick("gross sales", "gross sales (shop currency)", "gross sales (store currency)")
    col_net    = pick("net sales", "net sales (shop currency)", "net sales (store currency)")
    col_discts = pick("discounts", "discount amount", "total discounts")

    bms = []
    for r in rows:
        when = _parse_date_maybe(r.get(col_date))
        if not when:
            continue
        if col_gross:
            v = _strip_num(r.get(col_gross))
            if v: bms.append({"metric": "Gross sales (Shopify)", "subject": brand, "value": v, "as_of": when})
        if col_net:
            v = _strip_num(r.get(col_net))
            if v: bms.append({"metric": "Net sales (Shopify)", "subject": brand, "value": v, "as_of": when})
        if col_discts:
            v = _strip_num(r.get(col_discts))
            if v: bms.append({"metric": "Discounts (Shopify)", "subject": brand, "value": v, "as_of": when})

    inserted += store.insert_benchmarks(bms)
    return {"brands": [brand], "competitors": [], "benchmark_count": inserted}

def _import_conversion_rate_over_time(csv_path: Path, brand: str) -> Dict[str, Any]:
    store.ensure_brand(brand)
    inserted = 0
    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        rows, hdr = _collect(rdr)

    col_date = hdr.get("date") or hdr.get("day") or "Date"

    # common fields in Shopify conversion report
    col_sessions = None
    for k, v in hdr.items():
        if "session" in k:
            col_sessions = v; break

    col_conv = None
    for k, v in hdr.items():
        if "conversion" in k and "%" in v.lower() or "rate" in k:
            col_conv = v; break
    # fallback: any header containing "conversion"
    if not col_conv:
        for k, v in hdr.items():
            if "conversion" in k:
                col_conv = v; break

    bms = []
    for r in rows:
        when = _parse_date_maybe(r.get(col_date))
        if not when:
            continue
        if col_sessions:
            v = _strip_num(r.get(col_sessions))
            if v: bms.append({"metric": "Sessions (Shopify)", "subject": brand, "value": v, "as_of": when})
        if col_conv:
            raw = r.get(col_conv)
            # keep one decimal place for percent if present
            pct = None
            if raw:
                # extract numeric including dot
                pct = _strip_num(raw)
            if pct:
                bms.append({"metric": "Conversion rate % (Shopify)", "subject": brand, "value": pct, "as_of": when})

    inserted += store.insert_benchmarks(bms)
    return {"brands": [brand], "competitors": [], "benchmark_count": inserted}

def _import_total_sales_by_product(csv_path: Path, brand: str) -> Dict[str, Any]:
    store.ensure_brand(brand)
    inserted = 0
    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        rows, hdr = _collect(rdr)

    # guess columns
    col_product = None
    for k, v in hdr.items():
        if "product" in k and ("title" in k or k == "product" or "name" in k):
            col_product = v; break
    if not col_product:
        col_product = hdr.get("product title") or hdr.get("title") or "Product"

    # monetary columns
    col_net    = None
    for k, v in hdr.items():
        if "net sales" in k:
            col_net = v; break
    if not col_net:
        col_net = hdr.get("sales") or hdr.get("total sales")

    col_units  = None
    for k, v in hdr.items():
        if "units" in k or "quantity" in k or "sold" in k:
            col_units = v; break

    # per-row benchmarks (no date in this report; use 'as_of' today)
    when = dt.date.today().isoformat()
    bms = []
    for r in rows:
        prod = (r.get(col_product) or "").strip()
        if not prod:
            continue
        subj = f"{brand} · {prod}"
        if col_net:
            v = _strip_num(r.get(col_net))
            if v: bms.append({"metric": "Product sales (Shopify)", "subject": subj, "value": v, "as_of": when})
        if col_units:
            v = _strip_num(r.get(col_units))
            if v: bms.append({"metric": "Product units (Shopify)", "subject": subj, "value": v, "as_of": when})

    inserted += store.insert_benchmarks(bms)
    return {"brands": [brand], "competitors": [], "benchmark_count": inserted}

# ---------- dispatch ----------

def detect_kind(filename: str, headers: List[str]) -> str:
    name = filename.lower()
    hnorm = [_norm(h) for h in headers]
    # filename heuristics
    if "orders over time" in name:
        return "orders_over_time"
    if "total sales over time" in name:
        return "total_sales_over_time"
    if "conversion rate over time" in name:
        return "conversion_rate_over_time"
    if "total sales by product" in name or "sales by product" in name:
        return "total_sales_by_product"
    # header heuristics
    if any("orders" in h for h in hnorm) and any(h in ("date", "day") for h in hnorm):
        return "orders_over_time"
    if any("gross sales" in h or "net sales" in h for h in hnorm) and any(h in ("date", "day") for h in hnorm):
        return "total_sales_over_time"
    if any("conversion" in h for h in hnorm):
        return "conversion_rate_over_time"
    if any("product" in h for h in hnorm) and any("sales" in h for h in hnorm):
        return "total_sales_by_product"
    return "unknown"

def import_csv(csv_path: Path, brand: str) -> Dict[str, Any]:
    """
    Main entry for Shopify CSVs. Returns summary with benchmark_count.
    """
    # read headers only once
    with csv_path.open("r", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        headers = rdr.fieldnames or []

    kind = detect_kind(csv_path.name, headers)
    if kind == "orders_over_time":
        return _import_orders_over_time(csv_path, brand)
    if kind == "total_sales_over_time":
        return _import_total_sales_over_time(csv_path, brand)
    if kind == "conversion_rate_over_time":
        return _import_conversion_rate_over_time(csv_path, brand)
    if kind == "total_sales_by_product":
        return _import_total_sales_by_product(csv_path, brand)

    # fallback: treat like sales over time if date+amount present; else do nothing
    return _import_total_sales_over_time(csv_path, brand)
