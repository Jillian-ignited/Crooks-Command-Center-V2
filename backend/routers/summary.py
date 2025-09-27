from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["summary"])

@router.get("/")
async def root():
    return {"ok": True, "message": "Summary root", "ts": datetime.now().isoformat()}
