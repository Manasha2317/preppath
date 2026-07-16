# app/main.py
# This is the single entry point of the entire PrepPath backend.
# Every router (auth, resume, chat, dashboard) plugs into this one app object.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.auth.router import router as auth_router
from app.career_twin.router import router as twin_router
from app.resume.router import router as resume_router
from app.chat.router import router as chat_router
from app.dashboard.router import router as dashboard_router

app = FastAPI(
    title="PrepPath API",
    description="AI Career Intelligence Platform for Engineering Students",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc"      # ReDoc UI at /redoc
)

# CORS middleware — without this, your React frontend
# (running on localhost:5173) cannot call this API.
# The browser blocks cross-origin requests by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # React dev server
        "http://localhost:3000",    # alternate React port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(twin_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")

# Health check — first endpoint we test.
# If this works, the server is running correctly.
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "PrepPath API",
        "version": "1.0.0"
    }

# Routers registered here as we build them — commented for now
# from app.auth.router import router as auth_router
# app.include_router(auth_router, prefix="/api/v1")