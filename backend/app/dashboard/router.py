# app/dashboard/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.dashboard import service
from app.dashboard.schemas import DashboardResponse, CompanyReadiness

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.get_dashboard(db, current_user)


@router.get("/company-readiness", response_model=CompanyReadiness)
def company_readiness(
    company: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.get_company_readiness(db, current_user, company)