# app/resume/service.py
# The resume intelligence engine. Pipeline:
# 1. extract_text_from_pdf — PyMuPDF pulls raw text from the PDF
# 2. extract_skills — spaCy PhraseMatcher finds known skills
# 3. calculate_ats_score — 6-component rule-based scoring
# 4. find_missing_keywords — compares against target company needs
# 5. generate_suggestions — actionable improvements ranked by impact
# 6. run_full_analysis — orchestrates everything + updates the twin

import re
import json
from datetime import datetime
import fitz  # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher
from sqlalchemy.orm import Session

from app.resume.models import ResumeAnalysis, AnalysisJob
from app.resume.skills_data import (
    ALL_SKILLS, SKILL_TO_CATEGORY, COMPANY_REQUIREMENTS
)
from app.career_twin.service import update_twin

# Load spaCy once at module import — loading takes ~1s,
# doing it per-request would make every analysis slow
nlp = spacy.load("en_core_web_sm")

# Build the PhraseMatcher once with all 200+ skill patterns
# attr="LOWER" makes matching case-insensitive:
# "python", "Python", "PYTHON" all match
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in ALL_SKILLS]
matcher.add("SKILLS", patterns)


# ─── STEP 1: PDF TEXT EXTRACTION ─────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    doc.close()
    return full_text.strip()


# ─── STEP 2: SKILL EXTRACTION ────────────────────────────

def extract_skills(text: str) -> list:
    doc = nlp(text)
    matches = matcher(doc)
    found = {}
    for match_id, start, end in matches:
        skill_text = doc[start:end].text
        # Normalize to the canonical name from our dictionary
        key = skill_text.lower()
        if key in SKILL_TO_CATEGORY and key not in found:
            # Find canonical casing from ALL_SKILLS
            canonical = next(
                (s for s in ALL_SKILLS if s.lower() == key), skill_text
            )
            found[key] = {
                "name": canonical,
                "category": SKILL_TO_CATEGORY[key]
            }
    return list(found.values())


# ─── STEP 3: ATS SCORING (6 components = 100 points) ─────

def calculate_ats_score(text: str, skills: list, target_company: str) -> dict:
    text_lower = text.lower()
    scores = {}

    # Component 1 — Sections present (20 pts, 5 each)
    sections = {
        "education": ["education", "academic"],
        "experience": ["experience", "internship", "work history"],
        "skills": ["skills", "technical skills", "technologies"],
        "projects": ["projects", "personal projects"]
    }
    section_pts = 0
    for section, keywords in sections.items():
        if any(k in text_lower for k in keywords):
            section_pts += 5
    scores["section_score"] = section_pts

    # Component 2 — Keyword match vs target company (30 pts)
    required = COMPANY_REQUIREMENTS.get(
        target_company, COMPANY_REQUIREMENTS["default"]
    )
    skill_names_lower = {s["name"].lower() for s in skills}
    matched = sum(1 for req in required if req.lower() in skill_names_lower)
    scores["keyword_score"] = round((matched / len(required)) * 30, 1)

    # Component 3 — Measurable metrics in bullets (20 pts)
    # Looks for numbers, percentages, quantities: "reduced by 40%", "500 users"
    metric_patterns = re.findall(
        r'\d+%|\d+x|\d+\+|(?:reduced|improved|increased|achieved|scored)\s+\S*\s*\d+',
        text_lower
    )
    metric_count = len(metric_patterns)
    scores["metrics_score"] = min(20, metric_count * 4)  # 5 metrics = full marks

    # Component 4 — Length appropriate for fresher (10 pts)
    word_count = len(text.split())
    if 350 <= word_count <= 900:
        scores["length_score"] = 10
    elif 250 <= word_count < 350 or 900 < word_count <= 1100:
        scores["length_score"] = 6
    else:
        scores["length_score"] = 3

    # Component 5 — Action verbs starting bullets (10 pts)
    action_verbs = ["built", "developed", "implemented", "designed",
                    "created", "led", "improved", "optimized", "engineered",
                    "architected", "deployed", "automated", "integrated"]
    verb_count = sum(text_lower.count(v) for v in action_verbs)
    scores["action_verb_score"] = min(10, verb_count * 2)  # 5 verbs = full

    # Component 6 — Contact info present (10 pts)
    contact_pts = 0
    if re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text):     # email
        contact_pts += 4
    if "linkedin" in text_lower:
        contact_pts += 3
    if "github" in text_lower:
        contact_pts += 3
    scores["contact_score"] = contact_pts

    scores["ats_score"] = round(sum(scores.values()), 1)
    return scores


# ─── STEP 4: MISSING KEYWORDS ────────────────────────────

def find_missing_keywords(skills: list, target_company: str) -> list:
    required = COMPANY_REQUIREMENTS.get(
        target_company, COMPANY_REQUIREMENTS["default"]
    )
    skill_names_lower = {s["name"].lower() for s in skills}
    return [req for req in required if req.lower() not in skill_names_lower]


# ─── STEP 5: SUGGESTIONS (ranked by point impact) ────────

def generate_suggestions(scores: dict, missing: list, target_company: str) -> list:
    suggestions = []

    if scores["keyword_score"] < 20 and missing:
        top_missing = ", ".join(missing[:4])
        suggestions.append(
            f"Add these {target_company or 'target company'} keywords to your skills/projects: {top_missing} (+{30 - scores['keyword_score']:.0f} pts potential)"
        )
    if scores["metrics_score"] < 12:
        suggestions.append(
            "Add measurable outcomes to project bullets — numbers, percentages, scale. Example: 'Reduced load time by 40%' instead of 'Improved performance' (+8 pts)"
        )
    if scores["section_score"] < 20:
        suggestions.append(
            "Add missing standard sections — ATS systems look for Education, Experience, Skills, and Projects headers (+5 pts each)"
        )
    if scores["action_verb_score"] < 8:
        suggestions.append(
            "Start every bullet with a strong action verb: Built, Developed, Implemented, Designed, Optimized (+2 pts each)"
        )
    if scores["contact_score"] < 10:
        suggestions.append(
            "Add missing contact links — email, LinkedIn, and GitHub are all checked by recruiters (+3-4 pts each)"
        )
    if scores["length_score"] < 10:
        suggestions.append(
            "Adjust resume length to 350-900 words — the sweet spot for a fresher single-page resume"
        )

    return suggestions[:5]


# ─── STEP 6: FULL PIPELINE ───────────────────────────────

def run_full_analysis(db: Session, job_id: str, user_id: str,
                      filename: str, file_bytes: bytes, target_company: str):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    try:
        job.status = "processing"
        db.commit()

        # Pipeline
        text = extract_text_from_pdf(file_bytes)
        skills = extract_skills(text)
        scores = calculate_ats_score(text, skills, target_company)
        missing = find_missing_keywords(skills, target_company)
        suggestions = generate_suggestions(scores, missing, target_company)

        # Save analysis
        analysis = ResumeAnalysis(
            user_id=user_id,
            filename=filename,
            raw_text=text,
            ats_score=scores["ats_score"],
            section_score=scores["section_score"],
            keyword_score=scores["keyword_score"],
            metrics_score=scores["metrics_score"],
            length_score=scores["length_score"],
            action_verb_score=scores["action_verb_score"],
            contact_score=scores["contact_score"],
            extracted_skills=json.dumps(skills),
            missing_keywords=json.dumps(missing),
            suggestions=json.dumps(suggestions),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # THE KEY MOMENT: update the Career Digital Twin
        # This is what connects resume analysis to everything else
        update_twin(
            db, user_id,
            resume_score=scores["ats_score"],
            ats_score=scores["ats_score"],
            skill_gaps=missing,
            keyword_gaps=missing,
            extracted_skills=[s["name"] for s in skills],
        )

        job.status = "complete"
        job.analysis_id = analysis.id
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()