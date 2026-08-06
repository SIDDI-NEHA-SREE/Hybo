from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from app.config import settings
from app.services.voice import VoiceService
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"]
)

@router.post(
    "/transcribe",
    summary="Transcribe uploaded speech audio file to text using AWS Transcribe"
)
async def transcribe_audio(file: UploadFile = File(...)):
    logger.info(f"Incoming audio transcription request: {file.filename}")
    if not settings.is_aws_configured:
        return {
            "success": False,
            "message": "AI service is currently disabled."
        }
    try:
        audio_content = await file.read()
        transcription = await VoiceService.speech_to_text(audio_content, file.filename)
        return {
            "success": True,
            "transcription": transcription
        }
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return {
            "success": False,
            "message": "AI service is currently disabled."
        }

@router.post(
    "/synthesize",
    summary="Synthesize input text into speech audio streams using AWS Polly"
)
async def synthesize_speech(
    text: str = Form(...),
    language: str = Form("en")
):
    logger.info(f"Incoming speech synthesis request for: {text[:50]}...")
    if not settings.is_aws_configured:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": False,
                "message": "AI service is currently disabled."
            }
        )
    try:
        audio_stream = await VoiceService.text_to_speech(text, language)
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": False,
                "message": "AI service is currently disabled."
            }
        )

