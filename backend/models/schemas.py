from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UploadAck(BaseModel):
    saved_files: List[str]

class IntelligenceRequest(BaseModel):
    brands: List[str]
    lookback_days: int = 7

class IntelligenceMetric(BaseModel):
    brand: str
    posts: int
    avg_likes: float
    avg_comments: float
    engagement_rate: float
    top_posts: List[Dict[str, Any]]
    top_keywords: List[str]

class IntelligenceReport(BaseModel):
    timeframe_days: int
    metrics: List[IntelligenceMetric]
    highlights: List[str]
    prioritized_actions: List[str]

class SummaryReport(BaseModel):
    timeframe_days: int
    narrative: str
    key_moves: List[str]
    risks: List[str]

class CalendarEvent(BaseModel):
    date: str  # ISO YYYY-MM-DD
    title: str
    category: str  # drop, collab, holiday, culture
    notes: Optional[str] = None

class CalendarResponse(BaseModel):
    range_days: int
    events: List[CalendarEvent]

class Deliverable(BaseModel):
    title: str
    status: str  # planned, in-progress, done
    owner: Optional[str] = None
    due: Optional[str] = None

class AgencyResponse(BaseModel):
    week_of: str
    deliverables: List[Deliverable]
