from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=5000, 
        description="The chat message input from the user"
    )
    language: Optional[str] = Field(
        "en", 
        description="Optional preferred language code (en, te, hi, ur)"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Optional session tracking ID for maintaining conversation history"
    )

class ChatResponse(BaseModel):
    success: bool = Field(True, description="Indicates whether the request was successful")
    message: Optional[str] = Field(None, description="Status or info message (e.g. when AI service is disabled)")
    reply: Optional[str] = Field(None, description="The response reply text from HYBO Assistant")
    detected_language: Optional[str] = Field(None, description="The language code detected from the user message")
    timestamp: Optional[str] = Field(None, description="The ISO formatted response timestamp")
    session_id: Optional[str] = Field(None, description="The session tracking ID associated with the response")
    sources: Optional[List[str]] = Field(None, description="Source URLs retrieved for this answer")

# --- RAG / URL Knowledge Schemas ---

class URLIngestRequest(BaseModel):
    url: str = Field(..., description="The website URL to process and ingest")

class URLSourceStatus(BaseModel):
    url: str = Field(..., description="The ingested website URL")
    status: str = Field(..., description="Status of processing (processing, success, failed)")
    message: Optional[str] = Field(None, description="Detailed error message if processing failed")
    pages_count: int = Field(0, description="Number of pages crawled and indexed for this domain")
    updated_at: str = Field(..., description="Timestamp of when the source was last processed")

class URLSourceListResponse(BaseModel):
    success: bool = Field(True, description="Whether the request was successful")
    sources: List[URLSourceStatus] = Field([], description="List of registered website knowledge sources")


# --- Auth Schemas ---

class SendOTPRequest(BaseModel):
    phone_number: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="User mobile phone number with country code (e.g. +919876543210 or 9876543210)",
        examples=["+919876543210"]
    )
    name: Optional[str] = Field(None, description="Optional user name during signup/login")

class SendOTPResponse(BaseModel):
    success: bool = Field(True, description="Whether the OTP was generated/sent successfully")
    message: str = Field(..., description="Status message")
    phone_number: Optional[str] = Field(None, description="Normalized E.164 phone number")
    dev_mode: bool = Field(False, description="True if Twilio is unconfigured and running in local dev fallback")
    dev_otp: Optional[str] = Field(None, description="Only provided in dev fallback mode for testing")

class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=7, max_length=20, description="Mobile phone number")
    otp: str = Field(..., min_length=4, max_length=10, description="4-to-6 digit OTP code received")
    name: Optional[str] = Field(None, description="Optional name of the user to register/update")

class UserProfile(BaseModel):
    id: str = Field(..., description="Unique User ID")
    phone_number: str = Field(..., description="Registered Phone Number")
    name: Optional[str] = Field("Citizen User", description="Display name")
    role: str = Field("citizen", description="User role")
    created_at: str = Field(..., description="User creation timestamp")

class VerifyOTPResponse(BaseModel):
    success: bool = Field(True, description="Whether verification was successful")
    message: str = Field(..., description="Status message")
    access_token: Optional[str] = Field(None, description="JWT Bearer access token")
    token_type: str = Field("bearer", description="Token type")
    user: Optional[UserProfile] = Field(None, description="Authenticated user profile")

class AuthMeResponse(BaseModel):
    authenticated: bool = Field(True, description="Whether the session token is valid")
    user: Optional[UserProfile] = Field(None, description="Current authenticated user")

