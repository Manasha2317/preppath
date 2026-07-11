# app/career_twin/router.py
# API endpoints for the Career Digital Twin.
# GET /twin — full twin data (dashboard's primary data source)
# GET /twin/readiness — readiness score with component breakdown

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.career_twin import service
from app.career_twin.schemas import TwinResponse, ReadinessBreakdown

router = APIRouter(prefix="/twin", tags=["Career Digital Twin"])

@router.get("", response_model=TwinResponse)
def get_my_twin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    twin = service.get_twin(db, current_user.id)
    if not twin:
        # Auto-create if missing (users registered before twin existed)
        twin = service.initialize_twin(db, current_user.id, current_user.target_company)
    return TwinResponse(
        id=twin.id,
        user_id=twin.user_id,
        resume_score=twin.resume_score,
        ats_score=twin.ats_score,
        overall_readiness=twin.overall_readiness,
        skill_gaps=twin.get_skill_gaps(),
        keyword_gaps=twin.get_keyword_gaps(),
        extracted_skills=twin.get_extracted_skills(),
        target_company=twin.target_company,
        last_updated=twin.last_updated
    )

@router.get("/readiness", response_model=ReadinessBreakdown)
def get_readiness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    twin = service.get_twin(db, current_user.id)
    if not twin:
        twin = service.initialize_twin(db, current_user.id, current_user.target_company)

    score = service.calculate_readiness(db, twin)
    gaps = len(twin.get_skill_gaps())
    skill_completeness = max(0, 100 - (gaps * 12.5))

    from app.auth.models import User as UserModel
    user = db.query(UserModel).filter(UserModel.id == twin.user_id).first()
    fields = [user.college, user.department, user.cgpa,
              user.graduation_year, user.target_role, user.target_company]
    filled = sum(1 for f in fields if f)
    profile_completeness = (filled / len(fields)) * 100

    return ReadinessBreakdown(
        overall_readiness=score,
        resume_component=round((twin.resume_score or 0) * 0.30, 1),
        skill_component=round(skill_completeness * 0.40, 1),
        profile_component=round(profile_completeness * 0.30, 1),
        status=service.get_readiness_status(score)
    )