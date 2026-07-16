# app/chat/router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.chat import service
from app.chat.models import ChatSession, ChatMessage
from app.chat.schemas import (
    SendMessageRequest, MessageResponse, SessionSummary,
    SessionDetail, MessageItem, SuggestionsResponse
)

router = APIRouter(prefix="/chat", tags=["AI Mentor Chat"])


@router.post("/message", response_model=MessageResponse)
def send_message(
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        result = service.send_message(db, current_user, data.message, data.session_id)
        return MessageResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


@router.get("/suggestions", response_model=SuggestionsResponse)
def get_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return SuggestionsResponse(suggestions=service.get_suggestions(db, current_user))


@router.get("/sessions", response_model=list[SessionSummary])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    return SessionDetail(
        id=session.id,
        title=session.title,
        messages=[MessageItem(role=m.role, content=m.content, created_at=m.created_at) for m in messages]
    )