# app/auth/dependencies.py
# get_current_user is a FastAPI dependency.
# Add it to any route and FastAPI automatically:
# 1. Extracts the Bearer token from the Authorization header
# 2. Decodes and validates the JWT
# 3. Fetches the user from the database
# 4. Passes the user object to your route function
# If anything fails — invalid token, expired, user not found
# — it automatically returns 401 Unauthorized

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.auth.service import decode_token, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise credentials_exception
    return user