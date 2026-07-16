# app/chat/service.py
# The AI Mentor brain. Three responsibilities:
# 1. Fetch the user's Career Digital Twin and format it as context
# 2. Build the Gemini prompt: system context + history + new message
# 3. Generate suggested questions from the user's actual skill gaps

from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.career_twin.service import get_twin
from app.auth.models import User
from app.chat.models import ChatSession, ChatMessage

# Gemini 2.5 Flash — free tier, fast, more than capable for career mentoring
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.7,
    google_api_key=settings.GOOGLE_API_KEY,
)

SYSTEM_TEMPLATE = """You are PrepPath — an AI career mentor for engineering students preparing for campus placements at Indian tech companies.

You ONLY answer questions about: placement preparation, technical skills, DSA, system design, resume improvement, interview preparation, and career guidance. If asked anything unrelated, politely redirect to placement topics.

CURRENT STUDENT PROFILE (from their Career Digital Twin):
- Name: {name}
- Target Company: {target_company}
- Resume ATS Score: {resume_score}/100
- Overall Placement Readiness: {readiness}%
- Skills found on their resume: {skills}
- Skill gaps for their target company: {gaps}

CRITICAL RULES:
1. Always personalize advice using THIS student's actual data above.
2. If they ask "what should I study" — answer based on their specific gaps, not generic advice.
3. Reference their actual numbers when relevant ("your resume scores 82, but...").
4. Be direct, specific, and actionable. Indian placement context (campus drives, CGPA cutoffs, service vs product companies).
5. Keep responses focused — under 250 words unless they ask for depth.
6. If their data shows 'Not analyzed yet', encourage them to upload their resume first."""


def build_twin_context(db: Session, user: User) -> dict:
    twin = get_twin(db, user.id)
    if not twin:
        return {
            "name": user.full_name,
            "target_company": user.target_company or "Not set",
            "resume_score": "Not analyzed yet",
            "readiness": "0",
            "skills": "Not analyzed yet",
            "gaps": "Not analyzed yet",
        }
    return {
        "name": user.full_name,
        "target_company": twin.target_company or user.target_company or "Not set",
        "resume_score": str(twin.resume_score) if twin.resume_score else "Not analyzed yet",
        "readiness": str(twin.overall_readiness),
        "skills": ", ".join(twin.get_extracted_skills()) or "Not analyzed yet",
        "gaps": ", ".join(twin.get_skill_gaps()) or "Not analyzed yet",
    }


def get_or_create_session(db: Session, user_id: str, session_id: str = None) -> ChatSession:
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        if session:
            return session
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_history(db: Session, session_id: str, limit: int = 10) -> list:
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    return list(reversed(messages))


def send_message(db: Session, user: User, message: str, session_id: str = None) -> dict:
    session = get_or_create_session(db, user.id, session_id)
    context = build_twin_context(db, user)

    # Build the message chain: system + history + new message
    chain = [SystemMessage(content=SYSTEM_TEMPLATE.format(**context))]
    for msg in get_history(db, session.id):
        if msg.role == "user":
            chain.append(HumanMessage(content=msg.content))
        else:
            chain.append(AIMessage(content=msg.content))
    chain.append(HumanMessage(content=message))

    # Call Gemini
    response = llm.invoke(chain)
    # Newer Gemini models return content as a list of blocks;
    # older ones return a plain string. Handle both.
    if isinstance(response.content, list):
        reply = "".join(
            block.get("text", "") for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        reply = response.content

    # Persist both messages
    db.add(ChatMessage(session_id=session.id, role="user", content=message))
    db.add(ChatMessage(session_id=session.id, role="assistant", content=reply))
    session.message_count += 2
    # First message becomes the session title
    if session.message_count == 2:
        session.title = message[:60]
    db.commit()

    return {"session_id": session.id, "reply": reply}


def get_suggestions(db: Session, user: User) -> list:
    twin = get_twin(db, user.id)
    company = (twin.target_company if twin else None) or user.target_company or "your target company"
    gaps = twin.get_skill_gaps() if twin else []

    if not gaps:
        return [
            f"How should I prepare for {company} placements?",
            "What should my resume include for AI/ML roles?",
            "How do I build a 30-day placement prep plan?",
            "What are the most common interview mistakes freshers make?",
        ]
    suggestions = [
        f"How do I close my {gaps[0]} gap for {company}?",
        f"What's a 2-week plan to learn {gaps[1] if len(gaps) > 1 else gaps[0]}?",
        f"How important is {gaps[-1]} in {company} interviews?",
        "Based on my resume score, what should I fix first?",
    ]
    return suggestions[:4]