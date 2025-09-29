# backend/routers/intelligence.py
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request
from typing import Dict, Any, List, Optional
from datetime import datetime

router = APIRouter(tags=["intelligence"])

# --- Canonical brand list (includes your 11 + the broader set) ---
ALL_BRANDS: List[str] = [
    # Core / requested must-haves
    "LRG",
    "Hellstar",
    "Godspeed",
    "Smoke Rise",
    "Reason Clothing",
    "Supreme",
    "Stüssy",
    "Ed Hardy",
    "Von Dutch",
    "Diamond Supply Co.",
    "Essentials by Fear of God",

    # Your brand + additional set
    "Crooks & Castles",
    "Memory Lane",
    "Purple Brand",
    "Amiri",
    "Aimé Leon Dore",
    "Kith",
    "Fear of God",
    "Off-White",
    "BAPE",
    "Palace",

    "Ecko Unlimited",
    "Sean John",
    "Rocawear",

    "Nike Sportswear",
    "Jordan",
    "Adidas Originals",
    "Puma",
    "New Balance Lifestyle",

    "H&M",
    "Zara",
    "BoohooMAN",
    "Shein",
    "PacSun Private Label",
    "Zumiez Private Label",
]

# --- Aliases → canonical name (input normalization) ---
ALIASES: Dict[str, str] = {
    # required set aliases
    "reason clothing": "Reason Clothing",
    "stussy": "Stüssy",
    "stüssy": "Stüssy",
    "diamond supply": "Diamond Supply Co.",
    "diamond supply co": "Diamond Supply Co.",
    "essentials": "Essentials by Fear of God",
    "fear of god essentials": "Essentials by Fear of God",
    "essentials by fog": "Essentials by Fear of God",

    # general aliases / casing
    "crooks & castles": "Crooks & Castles",
    "memory lane": "Memory Lane",
    "purple brand": "Purple Brand",
    "aimé leon dore": "Aimé Leon Dore",
    "aime leon dore": "Aimé Leon Dore",
    "ald": "Aimé Leon Dore",
    "off white": "Off-White",
    "bape": "BAPE",
    "ecko": "Ecko Unlimited",
    "nike": "Nike Sportswear",
    "adidas": "Adidas Originals",
    "new balance": "New Balance Lifestyle",
    "boohooman": "BoohooMAN",
    "pacsun": "PacSun Private Label",
    "zumiez": "Zumiez Private Label",
}

def canonize(name: str) -> str:
    key = (name or "").strip().lower()
    if not key:
        return ""
    if key in ALIASES:
        return ALIASES[key]
    # match exact canonical (case-insensitive)
    for b in ALL_BRANDS:
        if b.lower() == key:
            return b
    # fallback: title-cased unknown (still allowed)
    return " ".join(w.capitalize() for w in key.split())

def pick_brands(param: Optional[str]) -> List[str]:
    """brands query may be: missing | 'all' | 'comma,separated'."""
    if not param or param.strip().lower() == "all":
        # ensure required brands are present (already included above)
        return ALL_BRANDS[:]
    chosen: List[str] = []
    seen = set()
    for raw in param.split(","):
        c = canonize(raw)
        if not c:
            continue
        if c not in seen:
            chosen.append(c); seen.add(c)
    return chosen or ALL_BRANDS[:]

def summary_payload(brands_q: Optional[str], days: int) -> Dict[str, Any]:
    brands = pick_brands(brands_q)
    metrics = {
        b: {
            "posts": 0,
            "avg_engagement": 0,
            "total_engagement": 0,
            "avg_likes": 0,
            "status": "no_data"
        } for b in brands
    }
    return {
        "ok": True,
        "window_days": days,
        "brands_used": brands,
        "metrics": metrics,
        "last_updated": datetime.utcnow().isoformat(),
    }

# -------- Routes --------

@router.api_route("", methods=["GET", "POST"])
@router.api_route("/", methods=["GET", "POST"])
def root(brands: Optional[str] = Query(None), days: int = Query(30, ge=1, le=365)):
    return summary_payload(brands, days)

@router.api_route("/summary", methods=["GET", "POST"])
@router.api_route("/summary/", methods=["GET", "POST"])
def summary(brands: Optional[str] = Query(None), days: int = Query(30, ge=1, le=365)):
    return summary_payload(brands, days)

@router.get("/brands")
def brands():
    """Expose canonical brand list (handy for UI pickers)."""
    return {"ok": True, "brands": ALL_BRANDS}

@router.api_route("/report", methods=["GET", "POST"])
@router.api_route("/report/", methods=["GET", "POST"])
async def report(request: Request):
    """
    Accepts:
    - GET: use query params ?brands=...&days=...
    - POST JSON: {"brands": "csv|string|or 'all'", "days": 30}
    - POST multipart: treated as stub (ack)
    """
    ctype = (request.headers.get("content-type") or "").lower()
    if "application/json" in ctype:
        body = await request.json()
        brands_q = body.get("brands")
        days = int(body.get("days", 30))
        return {"ok": True, "type": "report", "summary": summary_payload(brands_q, days)}
    if "multipart/form-data" in ctype:
        return {"ok": True, "type": "report", "received": "multipart"}
    # GET fallback (or unknown types)
    q = dict(request.query_params)
    return {"ok": True, "type": "report", "summary": summary_payload(q.get("brands"), int(q.get("days", 30)))}

@router.post("/upload")
async def upload(request: Request, file: Optional[UploadFile] = File(None), kind: Optional[str] = Form(None)):
    """
    - multipart/form-data: file upload
    - application/json: {"content": "...", "filename": "...", "kind": "..."}
    """
    ctype = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" in ctype:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")
        return {
            "ok": True,
            "mode": "multipart",
            "filename": file.filename,
            "size": len(data),
            "mime": file.content_type or "application/octet-stream",
            "kind": kind or "unknown",
        }
    if "application/json" in ctype:
        body = await request.json()
        content = body.get("content")
        if not isinstance(content, str) or not content:
            raise HTTPException(status_code=400, detail="Missing/invalid 'content'")
        return {
            "ok": True,
            "mode": "json",
            "filename": body.get("filename", "payload.txt"),
            "size": len(content.encode()),
            "mime": "text/plain",
            "kind": body.get("kind") or "unknown",
        }
    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {ctype}")
