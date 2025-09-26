import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crooks Command Center API", version="1.0.0")

# ----- CORS -----
_origins_env = os.getenv("ALLOWED_ORIGINS", "https://crooks-command-center-v2.onrender.com")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Healthcheck -----
@app.get("/health")
def health():
    return {"ok": True}

# ----- Include your existing routers if available -----
# These are optional and safe: adjust names to your project structure.
try:
    from routers import intelligence  # type: ignore
    app.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])  # type: ignore
except Exception:
    pass

try:
    from routers import calendar  # type: ignore
    app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])  # type: ignore
except Exception:
    pass

try:
    from routers import agency  # type: ignore
    app.include_router(agency.router, prefix="/agency", tags=["agency"])  # type: ignore
except Exception:
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
