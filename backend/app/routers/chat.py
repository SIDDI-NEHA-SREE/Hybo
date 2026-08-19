from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from app.schemas import ChatRequest, ChatResponse
from app.services.ai import AIService
from app.services.vector_store import VectorStore
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
        # Search local vector database for matching website chunks
        relevant_chunks = []
        retrieved_context = ""
        sources = []
        
        try:
            relevant_chunks = await VectorStore.query_similarity(payload.message, top_k=3)
            if relevant_chunks:
                logger.info(f"RAG: Found {len(relevant_chunks)} matching chunks in vector index")
                chunks_text = []
                for chunk in relevant_chunks:
                    chunks_text.append(
                        f"Source URL: {chunk['source_url']}\n"
                        f"Page Title: {chunk['page_title']}\n"
                        f"Content: {chunk['text']}"
                    )
                    if chunk['source_url'] not in sources:
                        sources.append(chunk['source_url'])
                retrieved_context = "\n\n---\n\n".join(chunks_text)
        except Exception as ve:
            logger.error(f"Error querying vector store: {str(ve)}")

        reply, detected_lang, is_available = await AIService.process_chat(
            message=payload.message, 
            preferred_lang=payload.language,
            retrieved_context=retrieved_context
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
            session_id=payload.session_id,
            sources=sources if sources else None
        )
    except Exception as e:
        logger.error(f"Error processing chat response: {str(e)}")
        return ChatResponse(
            success=False,
            message="AI service is currently disabled."
        )

