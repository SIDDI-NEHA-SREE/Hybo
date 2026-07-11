from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, Complaint
from ..auth import get_current_user, require_official, require_resident

router = APIRouter(prefix="/complaints", tags=["complaints"])

class ComplaintCreateSchema(BaseModel):
    title: str
    description: str
    category: str
    department: str

class ComplaintUpdateStatusSchema(BaseModel):
    status: str  # pending, in_progress, resolved, rejected
    official_response: str

class ComplaintRateSchema(BaseModel):
    rating: int  # 1 to 5

class ComplaintResponseSchema(BaseModel):
    id: int
    resident_id: int
    title: str
    description: str
    category: str
    status: str
    department: str
    rating: Optional[int] = None
    official_response: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

def to_iso(dt):
    return dt.isoformat() + "Z" if dt else None

@router.post("/submit", response_model=ComplaintResponseSchema, status_code=status.HTTP_201_CREATED)
def submit_complaint(
    payload: ComplaintCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_resident)
):
    if current_user.role == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guests cannot submit complaints."
        )

    new_complaint = Complaint(
        resident_id=current_user.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        department=payload.department,
        status="pending"
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    # Format return
    return {
        "id": new_complaint.id,
        "resident_id": new_complaint.resident_id,
        "title": new_complaint.title,
        "description": new_complaint.description,
        "category": new_complaint.category,
        "status": new_complaint.status,
        "department": new_complaint.department,
        "rating": new_complaint.rating,
        "official_response": new_complaint.official_response,
        "created_at": to_iso(new_complaint.created_at)
    }

@router.get("/my", response_model=List[ComplaintResponseSchema])
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_resident)
):
    complaints = db.query(Complaint).filter(
        Complaint.resident_id == current_user.id
    ).order_by(Complaint.created_at.desc()).all()

    res = []
    for c in complaints:
        res.append({
            "id": c.id,
            "resident_id": c.resident_id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "status": c.status,
            "department": c.department,
            "rating": c.rating,
            "official_response": c.official_response,
            "created_at": to_iso(c.created_at)
        })
    return res

@router.get("/all", response_model=List[ComplaintResponseSchema])
def get_all_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_official)
):
    complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()

    res = []
    for c in complaints:
        res.append({
            "id": c.id,
            "resident_id": c.resident_id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "status": c.status,
            "department": c.department,
            "rating": c.rating,
            "official_response": c.official_response,
            "created_at": to_iso(c.created_at)
        })
    return res

@router.post("/{complaint_id}/respond", response_model=ComplaintResponseSchema)
def respond_to_complaint(
    complaint_id: int,
    payload: ComplaintUpdateStatusSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_official)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )

    if payload.status not in ["pending", "in_progress", "resolved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value"
        )

    complaint.status = payload.status
    complaint.official_response = payload.official_response
    db.commit()
    db.refresh(complaint)

    return {
        "id": complaint.id,
        "resident_id": complaint.resident_id,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "status": complaint.status,
        "department": complaint.department,
        "rating": complaint.rating,
        "official_response": complaint.official_response,
        "created_at": to_iso(complaint.created_at)
    }

@router.post("/{complaint_id}/rate", response_model=ComplaintResponseSchema)
def rate_complaint(
    complaint_id: int,
    payload: ComplaintRateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_resident)
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id,
        Complaint.resident_id == current_user.id
    ).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found or does not belong to you"
        )

    if complaint.status != "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only rate resolved complaints"
        )

    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )

    complaint.rating = payload.rating
    db.commit()
    db.refresh(complaint)

    return {
        "id": complaint.id,
        "resident_id": complaint.resident_id,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "status": complaint.status,
        "department": complaint.department,
        "rating": complaint.rating,
        "official_response": complaint.official_response,
        "created_at": to_iso(complaint.created_at)
    }
