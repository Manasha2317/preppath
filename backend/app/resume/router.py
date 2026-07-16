# app/resume/router.py
# Resume endpoints:
# POST /resume/upload — accepts PDF, starts async analysis, returns job_id
# GET /resume/status/{job_id} — poll processing status
# GET /resume/latest — full latest analysis with scores + suggestions

import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.resume.models import ResumeAnalysis, AnalysisJob
from app.resume import service
from app.resume.schemas import (
    UploadResponse, JobStatusResponse, AnalysisResponse,
    ScoreBreakdown, SkillItem
)

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])


def analyze_in_background(job_id: str, user_id: str, filename: str,
                          file_bytes: bytes, target_company: str):
    # Background tasks need their OWN db session —
    # the request's session closes when the response is sent
    db = SessionLocal()
    try:
        service.run_full_analysis(
            db, job_id, user_id, filename, file_bytes, target_company
        )
    finally:
        db.close()


@router.post("/upload", response_model=UploadResponse, status_code=202)
def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    file_bytes = file.file.read()

    # Validate size (10MB max)
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Create job record
    job = AnalysisJob(user_id=current_user.id, filename=file.filename)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue analysis — runs AFTER the response is sent
    background_tasks.add_task(
        analyze_in_background,
        job.id, current_user.id, file.filename,
        file_bytes, current_user.target_company
    )

    return UploadResponse(
        job_id=job.id,
        status="pending",
        message="Resume uploaded. Analysis in progress."
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        analysis_id=job.analysis_id,
        error_message=job.error_message
    )


@router.get("/latest", response_model=AnalysisResponse)
def get_latest_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == current_user.id
    ).order_by(ResumeAnalysis.created_at.desc()).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="No resume analyzed yet")

    return AnalysisResponse(
        id=analysis.id,
        filename=analysis.filename,
        ats_score=analysis.ats_score,
        breakdown=ScoreBreakdown(
            section_score=analysis.section_score,
            keyword_score=analysis.keyword_score,
            metrics_score=analysis.metrics_score,
            length_score=analysis.length_score,
            action_verb_score=analysis.action_verb_score,
            contact_score=analysis.contact_score,
        ),
        extracted_skills=[SkillItem(**s) for s in analysis.get_extracted_skills()],
        missing_keywords=analysis.get_missing_keywords(),
        suggestions=analysis.get_suggestions(),
        created_at=analysis.created_at
    )