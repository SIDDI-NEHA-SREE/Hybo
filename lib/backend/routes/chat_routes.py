from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, ChatSession, ChatMessage
from ..auth import get_current_user
from ..rag import rag_manager

router = APIRouter(prefix="/chat", tags=["chat"])

class MessageSendSchema(BaseModel):
    session_id: Optional[int] = None
    content: str
    language: str = "en"  # en, te, hi

class MessageResponseSchema(BaseModel):
    id: int
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    language: str
    created_at: str

    class Config:
        from_attributes = True

class SessionResponseSchema(BaseModel):
    id: int
    title: str
    created_at: str

    class Config:
        from_attributes = True

class ChatResponseSchema(BaseModel):
    session_id: int
    session_title: str
    user_message: MessageResponseSchema
    assistant_message: MessageResponseSchema

@router.post("/send", response_model=ChatResponseSchema)
def send_message(
    payload: MessageSendSchema, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not payload.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    # 1. Resolve or create chat session
    session = None
    if payload.session_id:
        # If user, verify it belongs to them
        if current_user.role != "guest":
            session = db.query(ChatSession).filter(
                ChatSession.id == payload.session_id,
                ChatSession.user_id == current_user.id
            ).first()
        else:
            session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
            
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found."
            )
    else:
        # Create new session
        title = payload.content[:30] + ("..." if len(payload.content) > 30 else "")
        session = ChatSession(
            user_id=None if current_user.role == "guest" else current_user.id,
            title=title
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Retrieve context from FAISS RAG
    search_results = rag_manager.search(payload.content, k=4)
    
    if search_results:
        context_parts = []
        for r in search_results:
            context_parts.append(f"Source: {r['source']} | Title: {r['title']} | Content: {r['text']}")
        context_str = "\n\n".join(context_parts)
    else:
        context_str = "No relevant local database records found."

    # 3. Retrieve conversation history for memory
    history_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).all()

    history_list = []
    for msg in history_messages:
        history_list.append({
            "role": msg.role,
            "content": msg.content
        })

    # 4. Generate answer using Gemini (or fallback mock)
    answer = rag_manager.ask_gemini(
        query=payload.content,
        context=context_str,
        conversation_history=history_list
    )

    # Clean up citations formatting for DB
    citations_data = []
    for res in search_results:
        citations_data.append({
            "title": res["title"],
            "source": res["source"],
            "category": res["category"]
        })

    # 5. Save user and assistant messages to database
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=payload.content,
        language=payload.language
    )
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
        citations=citations_data,
        language=payload.language
    )

    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    # Helper function to format datetime to ISO string
    def to_iso(dt):
        return dt.isoformat() + "Z"

    return {
        "session_id": session.id,
        "session_title": session.title,
        "user_message": {
            "id": user_msg.id,
            "role": user_msg.role,
            "content": user_msg.content,
            "citations": None,
            "language": user_msg.language,
            "created_at": to_iso(user_msg.created_at)
        },
        "assistant_message": {
            "id": assistant_msg.id,
            "role": assistant_msg.role,
            "content": assistant_msg.content,
            "citations": assistant_msg.citations,
            "language": assistant_msg.language,
            "created_at": to_iso(assistant_msg.created_at)
        }
    }

@router.get("/sessions", response_model=List[SessionResponseSchema])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "guest":
        return []
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()

    # Format output dates to ISO string
    res = []
    for s in sessions:
        res.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat() + "Z"
        })
    return res

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponseSchema])
def get_session_messages(
    session_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )

    # Security check: verify ownership if not guest
    if current_user.role != "guest" and session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session."
        )

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

    res = []
    for m in messages:
        res.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "citations": m.citations,
            "language": m.language,
            "created_at": m.created_at.isoformat() + "Z"
        })
    return res

@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )

    if current_user.role != "guest" and session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this session."
        )

    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully."}
