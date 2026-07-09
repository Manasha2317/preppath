# app/auth/models.py
# This defines the 'users' table in the database.
# SQLAlchemy reads this class and creates the table automatically.
# We never write CREATE TABLE SQL — SQLAlchemy handles it.

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    # UUID primary key — better than auto-increment integers for APIs
    # because IDs are not guessable (1, 2, 3 is guessable, UUID is not)
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="student")
    college = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    cgpa = Column(String(10), nullable=True)
    graduation_year = Column(String(4), nullable=True)
    target_role = Column(String(100), nullable=True)
    target_company = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)