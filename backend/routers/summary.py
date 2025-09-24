from fastapi import APIRouter
from models.schemas import SummaryReport, IntelligenceRequest
from services.analyzer import weekly_summary

router = APIRouter()

@router.post("", response_model=SummaryReport)
async def get_summary(req: IntelligenceRequest):
    return weekly_summary(req.brands, req.lookback_days)
