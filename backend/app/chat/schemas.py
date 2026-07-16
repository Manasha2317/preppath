# app/chat/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SendMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None   # None = start new session

class MessageResponse(BaseModel):
    session_id: str
    reply: str

class SessionSummary(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: datetime

class MessageItem(BaseModel):
    role: str
    content: str
    created_at: datetime

class SessionDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageItem]

class SuggestionsResponse(BaseModel):
    suggestions: List[str]