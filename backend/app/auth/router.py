# app/auth/router.py
# These are the actual API endpoints for authentication.
# Routers are thin — they validate input, call service functions,
# and return responses. No business logic lives here.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth import schemas, service
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.career_twin.service import initialize_twin
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.TokenResponse, status_code=201)
def register(data: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    if service.get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    user = service.create_user(db, data)
    initialize_twin(db, user.id, user.target_company)
    token_data = {"sub": user.email, "user_id": user.id}
    return schemas.TokenResponse(
        access_token=service.create_access_token(token_data),
        refresh_token=service.create_refresh_token(token_data),
        user=schemas.UserResponse.model_validate(user)
    )

@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, data.email)
    if not user or not service.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    user.last_login = datetime.utcnow()
    db.commit()
    token_data = {"sub": user.email, "user_id": user.id}
    return schemas.TokenResponse(
        access_token=service.create_access_token(token_data),
        refresh_token=service.create_refresh_token(token_data),
        user=schemas.UserResponse.model_validate(user)
    )

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/login/form", response_model=schemas.TokenResponse, include_in_schema=False)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2 standard sends 'username' — we treat it as email
    user = service.get_user_by_email(db, form_data.username)
    if not user or not service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    user.last_login = datetime.utcnow()
    db.commit()
    token_data = {"sub": user.email, "user_id": user.id}
    return schemas.TokenResponse(
        access_token=service.create_access_token(token_data),
        refresh_token=service.create_refresh_token(token_data),
        user=schemas.UserResponse.model_validate(user)
    )