# app/career_twin/models.py
# The Career Digital Twin — the single most important table in PrepPath.
# One record per student. Every AI feature reads from and writes to this.
# Resume analyzer updates it. Chat reads it. Dashboard displays it.

import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from app.database import Base

class CareerDigitalTwin(Base):
    __tablename__ = "career_digital_twins"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    # One-to-one with users table
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Scores — populated by resume analyzer and readiness engine
    resume_score = Column(Float, nullable=True)       # 0-100
    ats_score = Column(Float, nullable=True)          # 0-100
    overall_readiness = Column(Float, default=0.0)    # 0-100

    # JSON stored as text — SQLite doesn't have a native JSON type
    # skill_gaps example: ["System Design", "DSA", "Docker"]
    skill_gaps = Column(Text, default="[]")
    # keyword_gaps example: ["microservices", "CI/CD", "Kubernetes"]
    keyword_gaps = Column(Text, default="[]")
    # extracted_skills example: ["Python", "React", "FastAPI"]
    extracted_skills = Column(Text, default="[]")

    target_company = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Helper methods to read/write JSON fields cleanly
    def get_skill_gaps(self) -> list:
        return json.loads(self.skill_gaps or "[]")

    def set_skill_gaps(self, gaps: list):
        self.skill_gaps = json.dumps(gaps)

    def get_keyword_gaps(self) -> list:
        return json.loads(self.keyword_gaps or "[]")

    def set_keyword_gaps(self, gaps: list):
        self.keyword_gaps = json.dumps(gaps)

    def get_extracted_skills(self) -> list:
        return json.loads(self.extracted_skills or "[]")

    def set_extracted_skills(self, skills: list):
        self.extracted_skills = json.dumps(skills)