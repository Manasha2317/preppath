# app/career_twin/schemas.py
# API shapes for the Career Digital Twin.
# Note: JSON fields come out as lists here even though
# they're stored as text in SQLite.

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TwinResponse(BaseModel):
    id: str
    user_id: str
    resume_score: Optional[float] = None
    ats_score: Optional[float] = None
    overall_readiness: float = 0.0
    skill_gaps: List[str] = []
    keyword_gaps: List[str] = []
    extracted_skills: List[str] = []
    target_company: Optional[str] = None
    last_updated: datetime

class ReadinessBreakdown(BaseModel):
    overall_readiness: float
    resume_component: float      # resume_score × 0.30
    skill_component: float       # skill_completeness × 0.40
    profile_component: float     # profile_completeness × 0.30
    status: str                  # "Placement Ready" / "Almost Ready" / etc