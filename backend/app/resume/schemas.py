# app/resume/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SkillItem(BaseModel):
    name: str
    category: str

class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    analysis_id: Optional[str] = None
    error_message: Optional[str] = None

class ScoreBreakdown(BaseModel):
    section_score: float
    keyword_score: float
    metrics_score: float
    length_score: float
    action_verb_score: float
    contact_score: float

class AnalysisResponse(BaseModel):
    id: str
    filename: str
    ats_score: float
    breakdown: ScoreBreakdown
    extracted_skills: List[SkillItem]
    missing_keywords: List[str]
    suggestions: List[str]
    created_at: datetime