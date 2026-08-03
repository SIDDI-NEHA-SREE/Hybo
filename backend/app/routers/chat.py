from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.schemas import ChatRequest, ChatResponse
from app.services.ai import AIService
from app.utils.logger import logger

router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)

@router.post(
    "/chat", 
    response_model=ChatResponse, 
    status_code=status.HTTP_200_OK,
    summary="Process user query and return local Hyderabad/Telangana response"
)
async def chat_interaction(payload: ChatRequest):
    logger.info(f"Incoming chat request: {payload.message[:50]}...")
    try:
        reply, detected_lang = await AIService.process_chat(
            message=payload.message, 
            preferred_lang=payload.language
        )
        
        return ChatResponse(
            reply=reply,
            detected_language=detected_lang,
            timestamp=datetime.utcnow().isoformat() + "Z",
            session_id=payload.session_id
        )
    except Exception as e:
        logger.error(f"Error processing chat response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing chatbot interaction"
        )
