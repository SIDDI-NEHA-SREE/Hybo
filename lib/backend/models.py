import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    mobile = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="resident")  # admin, official, resident, guest
    remember_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="resident", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="official", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for guests
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # Store list of sources/URLs
    language = Column(String, default="en")  # en, te, hi
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # e.g., Sanitation, Water Supply, Electricity, Roads
    status = Column(String, default="pending")  # pending, in_progress, resolved, rejected
    department = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)  # resident's satisfaction rating
    official_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resident = relationship("User", back_populates="complaints")

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    official_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    department = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    official = relationship("User", back_populates="announcements")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
