# app/dashboard/service.py
# Aggregation logic. Pulls from twin + resume + skills_data
# and shapes it for the frontend dashboard.

from sqlalchemy.orm import Session
from app.auth.models import User
from app.career_twin.service import get_twin, get_readiness_status
from app.resume.models import ResumeAnalysis
from app.resume.skills_data import COMPANY_REQUIREMENTS, SKILL_TO_CATEGORY

# Radar axes — the 5 dimensions shown on the dashboard chart
RADAR_CATEGORIES = {
    "DSA & Algorithms": ["dsa", "data structures", "algorithms"],
    "System Design": ["system design", "microservices"],
    "Languages": ["python", "java", "javascript", "c++", "c", "typescript", "go", "sql"],
    "AI/ML": [],       # filled by category match below
    "Web & Cloud": [], # filled by category match below
}


def build_skill_radar(extracted_skills: list, skill_gaps: list) -> list:
    """Score each radar axis 0-100 based on skills present vs gaps."""
    skills_lower = [s.lower() for s in extracted_skills]
    gaps_lower = [g.lower() for g in skill_gaps]
    radar = []

    for axis, keywords in RADAR_CATEGORIES.items():
        if axis == "AI/ML":
            have = sum(1 for s in skills_lower if SKILL_TO_CATEGORY.get(s) == "AI/ML")
            score = min(100, have * 12)  # 8+ AI skills = full
        elif axis == "Web & Cloud":
            have = sum(1 for s in skills_lower
                       if SKILL_TO_CATEGORY.get(s) in ("Web Frameworks", "Cloud & DevOps"))
            score = min(100, have * 12)
        else:
            have = sum(1 for k in keywords if k in skills_lower)
            missing = sum(1 for k in keywords if k in gaps_lower)
            total = have + missing
            score = round((have / total) * 100, 0) if total > 0 else 50
        radar.append({"axis": axis, "value": float(score)})
    return radar


def build_priority_actions(twin, target_company: str) -> list:
    """Top 3 actions ranked by readiness impact."""
    actions = []
    gaps = twin.get_skill_gaps() if twin else []
    resume_score = twin.resume_score if twin else None

    if resume_score is None:
        actions.append({
            "rank": 1,
            "action": "Upload your resume for analysis",
            "reason": "Your Career Digital Twin has no resume data yet",
            "impact": "+30% of your readiness score unlocks"
        })
    elif gaps:
        actions.append({
            "rank": 1,
            "action": f"Start learning {gaps[0]}",
            "reason": f"Biggest skill gap for {target_company or 'your target'}",
            "impact": "+12.5% skill completeness per gap closed"
        })
        if len(gaps) > 1:
            actions.append({
                "rank": 2,
                "action": f"Add {gaps[1]} to a project and your resume",
                "reason": "Second-highest impact gap — projects prove skills better than listing them",
                "impact": "Keyword score +3 pts, skill completeness +12.5%"
            })
    if resume_score is not None and resume_score < 90:
        actions.append({
            "rank": len(actions) + 1,
            "action": "Apply your resume improvement suggestions",
            "reason": f"Resume scores {resume_score}/100 — the suggestions list shows exactly what to fix",
            "impact": f"Up to +{round(90 - resume_score)} ATS points available"
        })
    while len(actions) < 3:
        actions.append({
            "rank": len(actions) + 1,
            "action": "Ask the AI Mentor for a weekly study plan",
            "reason": "Consistent structured prep beats cramming",
            "impact": "Compounding readiness gains"
        })
    return actions[:3]


def get_dashboard(db: Session, user: User) -> dict:
    twin = get_twin(db, user.id)
    latest = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == user.id
    ).order_by(ResumeAnalysis.created_at.desc()).first()

    extracted = twin.get_extracted_skills() if twin else []
    gaps = twin.get_skill_gaps() if twin else []
    target = (twin.target_company if twin else None) or user.target_company

    return {
        "student_name": user.full_name,
        "target_company": target,
        "overall_readiness": twin.overall_readiness if twin else 0.0,
        "readiness_status": get_readiness_status(twin.overall_readiness if twin else 0.0),
        "resume_score": twin.resume_score if twin else None,
        "ats_score": twin.ats_score if twin else None,
        "skills_found": len(extracted),
        "gaps_remaining": len(gaps),
        "last_resume_upload": latest.created_at if latest else None,
        "skill_radar": build_skill_radar(extracted, gaps),
        "priority_actions": build_priority_actions(twin, target),
    }


def get_company_readiness(db: Session, user: User, company: str = None) -> dict:
    twin = get_twin(db, user.id)
    target = company or (twin.target_company if twin else None) or user.target_company or "default"
    required = COMPANY_REQUIREMENTS.get(target, COMPANY_REQUIREMENTS["default"])
    extracted = [s.lower() for s in (twin.get_extracted_skills() if twin else [])]

    matched = [r for r in required if r.lower() in extracted]
    missing = [r for r in required if r.lower() not in extracted]

    return {
        "company": target,
        "readiness_pct": round((len(matched) / len(required)) * 100, 1),
        "matched_skills": matched,
        "missing_skills": missing,
    }