from pydantic import BaseModel, Field
from typing import Optional

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
    reply: str = Field(..., description="The response reply text from HYBO Assistant")
    detected_language: str = Field(..., description="The language code detected from the user message")
    timestamp: str = Field(..., description="The ISO formatted response timestamp")
    session_id: Optional[str] = Field(None, description="The session tracking ID associated with the response")
