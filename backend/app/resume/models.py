# app/resume/models.py
# Two tables:
# resume_analyses — every resume upload and its scores (history preserved)
# analysis_jobs — tracks async processing status for frontend polling

import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from app.database import Base

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=True)

    # Score components
    ats_score = Column(Float, nullable=True)          # 0-100 overall
    section_score = Column(Float, nullable=True)      # /20
    keyword_score = Column(Float, nullable=True)      # /30
    metrics_score = Column(Float, nullable=True)      # /20
    length_score = Column(Float, nullable=True)       # /10
    action_verb_score = Column(Float, nullable=True)  # /10
    contact_score = Column(Float, nullable=True)      # /10

    # JSON stored as text
    extracted_skills = Column(Text, default="[]")     # [{"name": "Python", "category": "..."}]
    missing_keywords = Column(Text, default="[]")     # skills target company wants but resume lacks
    suggestions = Column(Text, default="[]")          # top improvement actions

    created_at = Column(DateTime, default=datetime.utcnow)

    def get_extracted_skills(self) -> list:
        return json.loads(self.extracted_skills or "[]")

    def get_missing_keywords(self) -> list:
        return json.loads(self.missing_keywords or "[]")

    def get_suggestions(self) -> list:
        return json.loads(self.suggestions or "[]")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")   # pending / processing / complete / failed
    analysis_id = Column(String, nullable=True)       # links to ResumeAnalysis when complete
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)