# app/dashboard/schemas.py
# Dashboard response shapes. No new tables — this module
# aggregates data from twin, resume, and user tables.

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SkillRadarItem(BaseModel):
    axis: str        # "DSA", "System Design", etc.
    value: float     # 0-100

class CompanyReadiness(BaseModel):
    company: str
    readiness_pct: float
    matched_skills: List[str]
    missing_skills: List[str]

class PriorityAction(BaseModel):
    rank: int
    action: str
    reason: str
    impact: str      # e.g. "+18 pts keyword score"

class DashboardResponse(BaseModel):
    student_name: str
    target_company: Optional[str]
    overall_readiness: float
    readiness_status: str
    resume_score: Optional[float]
    ats_score: Optional[float]
    skills_found: int
    gaps_remaining: int
    last_resume_upload: Optional[datetime]
    skill_radar: List[SkillRadarItem]
    priority_actions: List[PriorityAction]