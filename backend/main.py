# backend/main.py
import os, importlib
from typing import Any, Dict, List
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crooks Command Center", version="1.0.0")

# -------- Health & routes ----------
@app.get("/health")
@app.get("/api/health")
def health() -> Dict[str, bool]:
    return {"ok": True}

@app.get("/routes")
@app.get("/api/routes")
def routes() -> Dict[str, Any]:
    out = []
    for r in app.routes:
        methods = sorted(list((getattr(r, "methods", set()) or set()) - {"HEAD", "OPTIONS"}))
        out.append({"path": getattr(r, "path", ""), "methods": methods, "name": getattr(r, "name", "")})
    return {"routes": out}

# -------- Router auto-mount ----------
MODULE_PREFIXES = ["backend.routers", "routers"]
ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "routers")

PREFIX_RULES: Dict[str, str] = {
    "content_creation": "/content",
    "ingest_ENHANCED_MULTI_FORMAT": "/ingest",
    "upload_sidecar": "/intelligence",
}

def _import_router(modname: str) -> APIRouter:
    last_err = None
    for base in MODULE_PREFIXES:
        try:
            mod = importlib.import_module(f"{base}.{modname}")
            router = getattr(mod, "router")
            if not isinstance(router, APIRouter):
                raise TypeError("router must be fastapi.APIRouter")
            return router
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Unable to import router '{modname}': {last_err}")

def _segment_for(modname: str) -> str:
    return PREFIX_RULES.get(modname) or ("/" + modname.replace("__", "/").replace("_", "-").lower())

try:
    files = [f for f in os.listdir(ROUTERS_DIR) if f.endswith(".py") and f not in ("__init__.py",)]
except FileNotFoundError:
    files = []

MOUNTED_SEGMENTS: List[str] = []
for file in sorted(files):
    modname = file[:-3]
    try:
        router = _import_router(modname)
        seg = _segment_for(modname)
        async def _probe(segname=seg):
            return {"ok": True, "router": segname.lstrip("/")}
        app.get("/api" + seg)(_probe)
        app.include_router(router, prefix="/api" + seg, tags=[modname])
        MOUNTED_SEGMENTS.append(seg.lstrip("/"))
        print(f"[main] Mounted '{modname}' at /api{seg}")
    except Exception as e:
        print(f"[main] SKIP {modname}: {e}")

# -------- Static export ----------
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

STATIC_PREFIXES = ("/_next/", "/static/", "/assets/", "/favicon.ico", "/robots.txt", "/sitemap.xml")
def _is_static(path: str) -> bool:
    if path == "/": return True
    if path.startswith(STATIC_PREFIXES): return True
    return "." in path.rsplit("/", 1)[-1]

def _collapse(p: str) -> str:
    while "//" in p: p = p.replace("//", "/")
    return p if p.startswith("/") else "/" + p

# -------- Middleware ----------
@app.middleware("http")
async def forward_xhr_to_api(request: Request, call_next):
    raw = request.url.path
    if raw.startswith("/api/") or _is_static(raw):
        return await call_next(request)
    path = _collapse(raw)
    if path != raw:
        return RedirectResponse(url=path, status_code=307)
    parts = [p for p in path.split("/") if p]
    if parts:
        seg = parts[0]
        if seg in MOUNTED_SEGMENTS:
            accept = (request.headers.get("accept") or "").lower()
            sec_dest = (request.headers.get("sec-fetch-dest") or "").lower()
            is_api_like = ("application/json" in accept) or (sec_dest and sec_dest != "document")
            if is_api_like:
                return RedirectResponse(url="/api" + path, status_code=307)
    return await call_next(request)

@app.middleware("http")
async def spa_fallback(request: Request, call_next):
    if request.url.path.startswith("/api/") or _is_static(request.url.path):
        return await call_next(request)
    response = await call_next(request)
    if response.status_code != 404: return response
    accept = (request.headers.get("accept") or "").lower()
    idx = os.path.join(static_dir, "index.html")
    if "text/html" in accept and os.path.exists(idx):
        return FileResponse(idx)
    return response
