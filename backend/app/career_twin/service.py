# app/career_twin/service.py
# Business logic for the Career Digital Twin.
# initialize_twin: called once when a user registers
# get_twin: fetch the twin for any user
# update_twin: any module (resume, chat) calls this to update fields
# calculate_readiness: the weighted formula from the SRS

from sqlalchemy.orm import Session
from app.career_twin.models import CareerDigitalTwin
from app.auth.models import User

def initialize_twin(db: Session, user_id: str, target_company: str = None) -> CareerDigitalTwin:
    twin = CareerDigitalTwin(
        user_id=user_id,
        target_company=target_company
    )
    db.add(twin)
    db.commit()
    db.refresh(twin)
    return twin

def get_twin(db: Session, user_id: str) -> CareerDigitalTwin:
    return db.query(CareerDigitalTwin).filter(
        CareerDigitalTwin.user_id == user_id
    ).first()

def update_twin(db: Session, user_id: str, **kwargs) -> CareerDigitalTwin:
    twin = get_twin(db, user_id)
    if not twin:
        return None
    for key, value in kwargs.items():
        if key == "skill_gaps":
            twin.set_skill_gaps(value)
        elif key == "keyword_gaps":
            twin.set_keyword_gaps(value)
        elif key == "extracted_skills":
            twin.set_extracted_skills(value)
        elif hasattr(twin, key):
            setattr(twin, key, value)
    # Recalculate readiness after every update
    twin.overall_readiness = calculate_readiness(db, twin)
    db.commit()
    db.refresh(twin)
    return twin

def calculate_readiness(db: Session, twin: CareerDigitalTwin) -> float:
    # Formula from SRS Chapter 7:
    # overall = (resume_score × 0.30) + (skill_completeness × 0.40) + (profile_completeness × 0.30)

    resume_component = (twin.resume_score or 0) * 0.30

    # skill_completeness: how many required skills the student has
    # For v1 we approximate: fewer gaps = higher completeness
    # 0 gaps = 100%, each gap reduces by 12.5% (8 gaps = 0%)
    gaps = len(twin.get_skill_gaps())
    skill_completeness = max(0, 100 - (gaps * 12.5))
    skill_component = skill_completeness * 0.40

    # profile_completeness: how many profile fields are filled
    user = db.query(User).filter(User.id == twin.user_id).first()
    fields = [user.college, user.department, user.cgpa,
              user.graduation_year, user.target_role, user.target_company]
    filled = sum(1 for f in fields if f)
    profile_completeness = (filled / len(fields)) * 100
    profile_component = profile_completeness * 0.30

    return round(resume_component + skill_component + profile_component, 1)

def get_readiness_status(score: float) -> str:
    if score >= 90:
        return "Placement Ready"
    elif score >= 75:
        return "Almost Ready"
    elif score >= 60:
        return "Needs Improvement"
    return "Intensive Preparation Required"