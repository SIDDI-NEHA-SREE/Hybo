from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
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
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Process user query and return local Hyderabad/Telangana response"
)
async def chat_interaction(payload: ChatRequest):
    logger.info(f"Incoming chat request: {payload.message[:50]}...")
    try:
        reply, detected_lang, is_available = await AIService.process_chat(
            message=payload.message, 
            preferred_lang=payload.language
        )
        
        if not is_available or reply is None:
            return ChatResponse(
                success=False,
                message="AI service is currently disabled."
            )

        return ChatResponse(
            success=True,
            reply=reply,
            detected_language=detected_lang,
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=payload.session_id
        )
    except Exception as e:
        logger.error(f"Error processing chat response: {str(e)}")
        return ChatResponse(
            success=False,
            message="AI service is currently disabled."
        )

