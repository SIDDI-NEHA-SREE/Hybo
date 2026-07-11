from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, Announcement
from ..auth import get_current_user, require_official

router = APIRouter(prefix="/announcements", tags=["announcements"])

class AnnouncementCreateSchema(BaseModel):
    title: str
    content: str
    department: str

class AnnouncementResponseSchema(BaseModel):
    id: int
    official_id: int
    title: str
    content: str
    department: str
    created_at: str

    class Config:
        from_attributes = True

def to_iso(dt):
    return dt.isoformat() + "Z" if dt else None

@router.post("/publish", response_model=AnnouncementResponseSchema, status_code=status.HTTP_201_CREATED)
def publish_announcement(
    payload: AnnouncementCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_official)
):
    if current_user.role not in ["official", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officials and admins can publish announcements."
        )

    new_announcement = Announcement(
        official_id=current_user.id,
        title=payload.title,
        content=payload.content,
        department=payload.department
    )

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    return {
        "id": new_announcement.id,
        "official_id": new_announcement.official_id,
        "title": new_announcement.title,
        "content": new_announcement.content,
        "department": new_announcement.department,
        "created_at": to_iso(new_announcement.created_at)
    }

@router.get("/all", response_model=List[AnnouncementResponseSchema])
def get_all_announcements(db: Session = Depends(get_db)):
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    
    res = []
    for a in announcements:
        res.append({
            "id": a.id,
            "official_id": a.official_id,
            "title": a.title,
            "content": a.content,
            "department": a.department,
            "created_at": to_iso(a.created_at)
        })
    return res
