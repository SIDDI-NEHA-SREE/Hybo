from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegisterSchema(BaseModel):
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    password: str
    role: str = "resident"  # resident, official, admin

class UserLoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    password: str
    remember_me: bool = False

class UserResponseSchema(BaseModel):
    id: int
    email: Optional[str] = None
    mobile: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema

class PasswordResetSchema(BaseModel):
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    new_password: str

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    if not user_data.email and not user_data.mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or mobile number must be provided."
        )

    # Check email duplicate
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

    # Check mobile duplicate
    if user_data.mobile:
        existing_user = db.query(User).filter(User.mobile == user_data.mobile).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number is already registered."
            )

    # Validate role
    if user_data.role not in ["resident", "official", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role selected."
        )

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        mobile=user_data.mobile,
        password_hash=hashed_pw,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponseSchema)
def login(login_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = None
    if login_data.email:
        user = db.query(User).filter(User.email == login_data.email).first()
    elif login_data.mobile:
        user = db.query(User).filter(User.mobile == login_data.mobile).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/mobile or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires = timedelta(days=30) if login_data.remember_me else timedelta(days=1)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponseSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/reset-password")
def reset_password(data: PasswordResetSchema, db: Session = Depends(get_db)):
    user = None
    if data.email:
        user = db.query(User).filter(User.email == data.email).first()
    elif data.mobile:
        user = db.query(User).filter(User.mobile == data.mobile).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated successfully."}
