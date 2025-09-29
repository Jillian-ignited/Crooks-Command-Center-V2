from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import random

router = APIRouter(tags=["intelligence"])

ALL_BRANDS: List[str] = [
    # Required 11
    "LRG","Hellstar","Godspeed","Smoke Rise","Reason Clothing","Supreme","Stüssy",
    "Ed Hardy","Von Dutch","Diamond Supply Co.","Essentials by Fear of God",
    # Rest
    "Crooks & Castles","Memory Lane","Purple Brand","Amiri","Aimé Leon Dore","Kith","Fear of God",
    "Off-White","BAPE","Palace","Ecko Unlimited","Sean John","Rocawear",
    "Nike Sportswear","Jordan","Adidas Originals","Puma","New Balance Lifestyle",
    "H&M","Zara","BoohooMAN","Shein","PacSun Private Label","Zumiez Private Label",
]

ALIASES: Dict[str, str] = {
    "reason clothing":"Reason Clothing",
    "stussy":"Stüssy","stüssy":"Stüssy",
    "diamond supply":"Diamond Supply Co.","diamond supply co":"Diamond Supply Co.",
    "essentials":"Essentials by Fear of God","fear of god essentials":"Essentials by Fear of God","essentials by fog":"Essentials by Fear of God",
    "crooks & castles":"Crooks & Castles","memory lane":"Memory Lane","purple brand":"Purple Brand",
    "aimé leon dore":"Aimé Leon Dore","aime leon dore":"Aimé Leon Dore","ald":"Aimé Leon Dore",
    "off white":"Off-White","bape":"BAPE","ecko":"Ecko Unlimited","nike":"Nike Sportswear","adidas":"Adidas Originals",
    "new balance":"New Balance Lifestyle","boohooman":"BoohooMAN","pacsun":"PacSun Private Label","zumiez":"Zumiez Private Label",
}

def canonize(name: str) -> str:
    k = (name or "").strip().lower()
    if not k: return ""
    if k in ALIASES: return ALIASES[k]
    for b in ALL_BRANDS:
        if b.lower() == k:
            return b
    return " ".join(w.capitalize() for w in k.split())

def pick_brands(param: Optional[str]) -> List[str]:
    if not param or param.strip().lower() == "all":
        return ALL_BRANDS[:]
    out, seen = [], set()
    for raw in param.split(","):
        c = canonize(raw)
        if c and c not in seen:
            out.append(c); seen.add(c)
    return out or ALL_BRANDS[:]

def seeded_metrics(brand: str, days: int) -> Dict[str, Any]:
    # deterministic seed per brand + window so values are stable
    seed = int(hashlib.sha256(f"{brand}|{days}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    posts = rng.randint(max(2, days//10), max(10, days//3))
    avg_like = rng.randint(80, 400)
    avg_cmt  = rng.randint(3, 40)
    avg_eng  = avg_like + avg_cmt*5
    total_eng = posts * avg_eng
    growth = round(rng.uniform(-0.05, 0.15), 3)  # -5%..+15%
    return {
        "posts": posts,
        "avg_likes": avg_like,
        "avg_comments": avg_cmt,
        "avg_engagement": avg_eng,
        "total_engagement": total_eng,
        "follower_growth_rate": growth,
    }

def summary_payload(brands_q: Optional[str], days: int) -> Dict[str, Any]:
    brands = pick_brands(brands_q)
    metrics = { b: seeded_metrics(b, days) for b in brands }
    # simple ranking by total_engagement
    ranking = sorted(
        [{"brand": b, "total_engagement": m["total_engagement"]} for b,m in metrics.items()],
        key=lambda x: x["total_engagement"], reverse=True
    )
    return {
        "ok": True,
        "window_days": days,
        "brands_used": brands,
        "metrics": metrics,
        "ranking": ranking[:10],
        "last_updated": datetime.utcnow().isoformat(),
    }

@router.api_route("", methods=["GET","POST"])
@router.api_route("/", methods=["GET","POST"])
def root(brands: Optional[str] = Query(None), days: int = Query(30, ge=1, le=365)):
    return summary_payload(brands, days)

@router.api_route("/summary", methods=["GET","POST"])
@router.api_route("/summary/", methods=["GET","POST"])
def summary(brands: Optional[str] = Query(None), days: int = Query(30, ge=1, le=365)):
    return summary_payload(brands, days)

@router.get("/brands")
def brands():
    return {"ok": True, "brands": ALL_BRANDS}

@router.api_route("/report", methods=["GET","POST"])
@router.api_route("/report/", methods=["GET","POST"])
async def report(request: Request):
    c = (request.headers.get("content-type") or "").lower()
    if "application/json" in c:
        body = await request.json()
        return {"ok": True, "type": "report",
                "summary": summary_payload(body.get("brands"), int(body.get("days",30)))}
    if "multipart/form-data" in c:
        return {"ok": True, "type": "report", "received": "multipart"}
    q = dict(request.query_params)
    return {"ok": True, "type": "report",
            "summary": summary_payload(q.get("brands"), int(q.get("days",30)))}

@router.post("/upload")
async def upload(request: Request, file: UploadFile | None = File(None), kind: str | None = Form(None)):
    c = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" in c:
        if not file or not file.filename: raise HTTPException(status_code=400, detail="Missing file")
        data = await file.read()
        if not data: raise HTTPException(status_code=400, detail="Empty file")
        return {"ok": True, "mode": "multipart", "filename": file.filename, "size": len(data),
                "mime": file.content_type or "application/octet-stream", "kind": kind or "unknown"}
    if "application/json" in c:
        body = await request.json()
        content = body.get("content")
        if not isinstance(content, str) or not content: raise HTTPException(status_code=400, detail="Missing/invalid 'content'")
        return {"ok": True, "mode": "json", "filename": body.get("filename","payload.txt"),
                "size": len(content.encode()), "mime": "text/plain", "kind": body.get("kind") or "unknown"}
    raise HTTPException(status_code=415, detail=f"Unsupported Content-Type: {c}")
