from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, Complaint, ChatSession, Feedback
from ..auth import get_current_user, require_admin, require_official

router = APIRouter(prefix="/admin", tags=["admin"])

class FeedbackCreateSchema(BaseModel):
    rating: int  # 1 to 5
    comments: Optional[str] = None

class FeedbackResponseSchema(BaseModel):
    id: int
    user_id: Optional[int] = None
    rating: int
    comments: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

class UserUpdateRoleSchema(BaseModel):
    role: str  # admin, official, resident

class UserAdminResponseSchema(BaseModel):
    id: int
    email: Optional[str] = None
    mobile: Optional[str] = None
    role: str
    created_at: str

    class Config:
        from_attributes = True

def to_iso(dt):
    return dt.isoformat() + "Z" if dt else None

@router.post("/feedback", response_model=FeedbackResponseSchema, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )

    # Allow guest users as user_id=None
    uid = None if current_user.role == "guest" else current_user.id

    new_fb = Feedback(
        user_id=uid,
        rating=payload.rating,
        comments=payload.comments
    )
    db.add(new_fb)
    db.commit()
    db.refresh(new_fb)

    return {
        "id": new_fb.id,
        "user_id": new_fb.user_id,
        "rating": new_fb.rating,
        "comments": new_fb.comments,
        "created_at": to_iso(new_fb.created_at)
    }

@router.get("/feedback/all", response_model=List[FeedbackResponseSchema])
def get_all_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_official)
):
    feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    res = []
    for f in feedbacks:
        res.append({
            "id": f.id,
            "user_id": f.user_id,
            "rating": f.rating,
            "comments": f.comments,
            "created_at": to_iso(f.created_at)
        })
    return res

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_official)
):
    total_users = db.query(User).count()
    total_complaints = db.query(Complaint).count()
    pending_complaints = db.query(Complaint).filter(Complaint.status == "pending").count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == "resolved").count()
    in_progress_complaints = db.query(Complaint).filter(Complaint.status == "in_progress").count()
    
    total_chats = db.query(ChatSession).count()
    total_feedback = db.query(Feedback).count()
    
    # Calculate average feedback rating
    avg_rating = 0.0
    feedbacks = db.query(Feedback.rating).all()
    if feedbacks:
        avg_rating = sum([f[0] for f in feedbacks]) / len(feedbacks)

    return {
        "users": {
            "total": total_users,
            "admins": db.query(User).filter(User.role == "admin").count(),
            "officials": db.query(User).filter(User.role == "official").count(),
            "residents": db.query(User).filter(User.role == "resident").count()
        },
        "complaints": {
            "total": total_complaints,
            "pending": pending_complaints,
            "in_progress": in_progress_complaints,
            "resolved": resolved_complaints,
            "rejected": total_complaints - pending_complaints - resolved_complaints - in_progress_complaints
        },
        "chats": {
            "total": total_chats
        },
        "feedback": {
            "total": total_feedback,
            "average_rating": round(avg_rating, 2)
        },
        "system": {
            "status": "healthy",
            "db_provider": "sqlite" if "sqlite" in db.bind.url.drivername else "postgresql"
        }
    }

@router.get("/users", response_model=List[UserAdminResponseSchema])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    res = []
    for u in users:
        res.append({
            "id": u.id,
            "email": u.email,
            "mobile": u.mobile,
            "role": u.role,
            "created_at": to_iso(u.created_at)
        })
    return res

@router.post("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserUpdateRoleSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if payload.role not in ["admin", "official", "resident"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role value"
        )

    user.role = payload.role
    db.commit()
    return {"message": f"User {user_id} role updated to {payload.role}"}
