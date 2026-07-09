# app/database.py
# This file does three things:
# 1. Creates the connection to SQLite database
# 2. Creates a session factory for database operations
# 3. Provides a Base class that all models inherit from

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# create_engine opens the connection to the database file
# check_same_thread=False is required for SQLite with FastAPI
# because FastAPI handles multiple threads simultaneously
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory that creates new database sessions
# autocommit=False means changes aren't saved until you call db.commit()
# autoflush=False means SQLAlchemy won't auto-sync before queries
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base is the parent class all SQLAlchemy models inherit from
# When you define class User(Base), SQLAlchemy knows to create
# a 'users' table from that class
Base = declarative_base()

# get_db is a FastAPI dependency
# Every route that needs database access uses this
# It opens a session, gives it to the route, then ALWAYS closes it
# The try/finally ensures the session closes even if an error occurs
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()