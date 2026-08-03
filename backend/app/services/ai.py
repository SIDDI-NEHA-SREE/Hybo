import re
from datetime import datetime
from app.utils.logger import logger
from app.services.ai_client import BedrockClient

class AIService:
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detects language based on Unicode character ranges.
        Supports: te (Telugu), hi (Hindi), ur (Urdu), en (English/Default).
        """
        if re.search(r"[\u0c00-\u0c7f]", text):
            return "te"
        if re.search(r"[\u0900-\u097f]", text):
            return "hi"
        if re.search(r"[\u0600-\u06ff]", text):
            return "ur"
        return "en"

    @staticmethod
    def verify_local_scope(text: str) -> bool:
        """
        Verifies if the user's message is related to Hyderabad or Telangana.
        Returns True if in scope, False otherwise.
        """
        lower_text = text.lower()
        
        keywords = [
            "hyderabad", "telangana", "charminar", "biryani", "ghmc", "hmda",
            "kcr", "revanth", "cyberabad", "secunderabad", "tsrtc", "hospital",
            "scheme", "metro", "bus", "route", "district", "mandal", "village",
            "welfare", "tourism", "police", "circular", "goverment", "governance"
        ]
        
        telangana_terms = ["హైదరాబాద్", "తెలంగాణ", "చార్మినార్", "మెట్రో", "బస్సు", "ఆసుపత్రి", "పథకం"]
        hindi_terms = ["हैदराबाद", "तेलंगाना", "चारमीनार", "मेट्रो", "बस", "अस्पताल", "योजना"]
        urdu_terms = ["حیدرآباد", "تلنگانہ", "چارمینار"]

        all_keywords = keywords + telangana_terms + hindi_terms + urdu_terms
        return any(keyword in lower_text for keyword in all_keywords)

    @classmethod
    async def process_chat(cls, message: str, preferred_lang: str) -> tuple[str, str]:
        """
        Processes user chat message, checks scope, detects language, and delegates response.
        Returns a tuple of (reply_text, detected_language).
        """
        detected_lang = cls.detect_language(message)
        logger.info(f"Processing chat. Detected language: {detected_lang}, preferred: {preferred_lang}")

        # Check local boundary scope
        in_scope = cls.verify_local_scope(message)
        
        if not in_scope:
            # Rejection message translations
            rejections = {
                "en": "I specialize ONLY in Hyderabad and Telangana related topics. Please ask me about local welfare schemes, historical landmarks, transport routes, or emergency contacts within our state.",
                "te": "నేను కేవలం హైదరాబాద్ మరియు తెలంగాణకు సంబంధించిన అంశాలపై మాత్రమే సహాయపడగలను. దయచేసి స్థానిక సంక్షేమ పథకాలు, చారిత్రక ప్రదేశాలు, రవాణా మార్గాలు లేదా అత్యవసర సేవల గురించి అడగండి.",
                "hi": "मैं केवल हैदराबाद और तेलंगाना से संबंधित विषयों में विशेषज्ञता रखता हूँ। कृपया हमारे राज्य के कल्याणकारी योजनाओं, ऐतिहासिक स्थलों, परिवहन मार्गों या आपातकालीन संपर्कों के बारे में पूछें।",
                "ur": "میں صرف حیدرآباد اور تلنگانہ سے متعلقہ موضوعات پر ہی جواب دے سکتا ہوں۔ براہ کرم ہمارے صوبے کی فلاحی اسکیموں، تاریخی مقامات، ٹرانسپورٹ روٹس یا ہنگامی رابطوں کے بارے میں سوال کریں۔"
            }
            lang_to_use = detected_lang if detected_lang in rejections else (preferred_lang if preferred_lang in rejections else "en")
            return rejections[lang_to_use], detected_lang

        # Delegate execution to Bedrock client
        reply = await BedrockClient.invoke_model(
            prompt=message,
            preferred_lang=detected_lang
        )
        
        return reply, detected_lang
