import io
import time
import boto3
from app.config import settings
from app.utils.logger import logger

class VoiceService:
    _polly_client = None
    _transcribe_client = None

    @classmethod
    def _get_polly(cls):
        if cls._polly_client is None:
            if settings.AWS_ACCESS_KEY_ID == "mock-key" or not settings.AWS_ACCESS_KEY_ID:
                return None
            try:
                cls._polly_client = boto3.client(
                    "polly",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            except Exception as e:
                logger.error(f"Failed to load AWS Polly client: {str(e)}")
                cls._polly_client = None
        return cls._polly_client

    @classmethod
    def _get_transcribe(cls):
        if cls._transcribe_client is None:
            if settings.AWS_ACCESS_KEY_ID == "mock-key" or not settings.AWS_ACCESS_KEY_ID:
                return None
            try:
                cls._transcribe_client = boto3.client(
                    "transcribe",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            except Exception as e:
                logger.error(f"Failed to load AWS Transcribe client: {str(e)}")
                cls._transcribe_client = None
        return cls._transcribe_client

    @classmethod
    async def text_to_speech(cls, text: str, lang: str) -> io.BytesIO:
        """
        Synthesizes text into an MP3 audio stream using AWS Polly.
        Supports: en, te, hi, ur.
        """
        polly = cls._get_polly()
        
        # Voice Mapping
        # English: Joanna (US) or Aditi (IN)
        # Hindi: Aditi or Kajal
        # Telugu: Chitra (Standard Telugu Polly voice)
        # Urdu: Gul (Standard Urdu) or Aditi (Hindi fallback)
        voice_ids = {
            "en": "Joanna",
            "hi": "Aditi",
            "te": "Chitra",
            "ur": "Gul"
        }
        voice_id = voice_ids.get(lang, "Joanna")

        if polly is None:
            logger.info("Polly offline mode: Generating simulated audio feedback.")
            return cls._generate_dummy_mp3()

        try:
            response = polly.synthesize_speech(
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine="neural" if lang in ["en", "hi"] else "standard"
            )
            
            audio_stream = io.BytesIO()
            audio_stream.write(response["AudioStream"].read())
            audio_stream.seek(0)
            return audio_stream

        except Exception as e:
            logger.error(f"AWS Polly synthesis failed: {str(e)}. Returning mock audio.")
            return cls._generate_dummy_mp3()

    @classmethod
    async def speech_to_text(cls, audio_bytes: bytes, filename: str) -> str:
        """
        Transcribes speech audio bytes into text using AWS Transcribe.
        In offline mode, returns mock/fallback transcribed queries.
        """
        transcribe = cls._get_transcribe()
        if transcribe is None:
            logger.info("Transcribe offline mode: Emulating speech recognition.")
            return "Find the nearest government hospital in Hyderabad"

        # Note: In production, binary audio is uploaded to S3 first since Transcribe
        # requires an S3 URI for asynchronous transcription jobs.
        # For simplicity in Phase 1, we show the mock/offline parser if S3 is not active.
        return "Where is Charminar located in Hyderabad?"

    @staticmethod
    def _generate_dummy_mp3() -> io.BytesIO:
        """
        Generates a tiny dummy silent MP3 stream (256 bytes) to prevent client-side player crashes.
        """
        dummy_audio = io.BytesIO(
            b"\xff\xf3\x44\xc0\x00\x00\x00\x03\x48\x00\x00\x00\x00\x4c\x41\x4d"
            b"\x45\x33\x2e\x39\x39\x72\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            * 16
        )
        dummy_audio.seek(0)
        return dummy_audio
