import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import intelligence, summary, calendar, agency
from routers import ingest_ENHANCED


os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/cache", exist_ok=True)

app = FastAPI(title="Crooks Command Center API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
app.include_router(summary.router, prefix="/summary", tags=["summary"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(agency.router, prefix="/agency", tags=["agency"])
app.include_router(ingest_ENHANCED.router, prefix="/ingest", tags=["ingest"])
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

STATIC_DIR = "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

@app.get("/")
@app.head("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
