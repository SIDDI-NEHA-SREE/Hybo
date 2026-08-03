import json
import boto3
from app.config import settings
from app.utils.logger import logger

class BedrockClient:
    _client = None

    @classmethod
    def get_client(cls):
        """
        Initializes and returns the boto3 Bedrock client.
        Fallbacks to None if mock values or invalid credentials are used.
        """
        if cls._client is None:
            if settings.AWS_ACCESS_KEY_ID == "mock-key" or not settings.AWS_ACCESS_KEY_ID:
                logger.warning("AWS credentials are set to mock values. Running in offline/fallback mode.")
                return None
            try:
                cls._client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                logger.info("Successfully initialized AWS Bedrock runtime client.")
            except Exception as e:
                logger.error(f"Failed to initialize AWS Bedrock client: {str(e)}. Falling back to mock model.")
                cls._client = None
        return cls._client

    @staticmethod
    def get_system_prompt() -> str:
        """
        Returns the system prompt enforcing specialized boundaries, safety guidelines, and multilingual support.
        """
        return (
            "You are HYBO, a specialized AI assistant dedicated ONLY to Hyderabad and Telangana state. "
            "Your main role is to act as an authoritative guide for public services, government schemes, "
            "municipal orders (GHMC, HMDA), local transit, history, landmarks, and emergencies. "
            "\n\n"
            "CRITICAL RULES:\n"
            "1. ONLY answer questions related to Hyderabad and Telangana. "
            "2. If a query is unrelated to Hyderabad or Telangana, you MUST politely reject it. State that "
            "you specialize strictly in Hyderabad and Telangana, and invite them to ask a relevant question. "
            "Reject unrelated queries in the same language as the query.\n"
            "3. NEVER fabricate or make up government information, rules, or schemes. "
            "4. If you are unsure or do not have authentic data, state clearly that the information could "
            "not be verified and suggest checking the official government portal (e.g. telangana.gov.in, ghmc.gov.in).\n"
            "5. Automatically detect the user's language (English, Telugu, Hindi, Urdu) and respond in that same language.\n"
            "6. Support future RAG context injections. Analyze any provided context under '<context>' XML tags first before answering."
        )

    @classmethod
    async def invoke_model(cls, prompt: str, retrieved_context: str = "", preferred_lang: str = "en") -> str:
        """
        Invokes Claude on Bedrock. If offline, runs simulated response.
        """
        client = cls.get_client()
        system_prompt = cls.get_system_prompt()
        
        # Inject RAG context if present
        user_message = prompt
        if retrieved_context:
            user_message = f"<context>\n{retrieved_context}\n</context>\n\nQuery: {prompt}"

        # If offline/mock state
        if client is None:
            logger.info("Executing mock AI response (offline mode).")
            return cls._simulate_offline_response(prompt, preferred_lang)

        try:
            # Bedrock Claude 3 Messages API Payload
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": settings.MAX_TOKENS,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": settings.TEMPERATURE
            }

            response = client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps(payload)
            )

            response_body = json.loads(response.get("body").read())
            reply = response_body["content"][0]["text"]
            return reply

        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {str(e)}. Falling back to offline simulator.")
            return cls._simulate_offline_response(prompt, preferred_lang)

    @staticmethod
    def _simulate_offline_response(prompt: str, lang: str) -> str:
        """
        Generates simulated high-quality offline responses based on query content and language.
        """
        lower_prompt = prompt.lower()
        
        # Scope verification logic
        keywords = ["hyderabad", "telangana", "charminar", "biryani", "ghmc", "hmda", "metro", "scheme", "hospital"]
        is_in_scope = any(k in lower_prompt for k in keywords) or any(ord(c) > 127 for c in prompt)

        if not is_in_scope:
            rejections = {
                "en": "I am HYBO. I specialize ONLY in Hyderabad and Telangana topics. Please ask me about local welfare schemes, historical landmarks, transport routes, or emergency contacts.",
                "te": "నేను కేవలం హైదరాబాద్ మరియు తెలంగాణకు సంబంధించిన అంశాలపై మాత్రమే సహాయపడగలను. దయచేసి స్థానిక సంక్షేమ పథకాలు, చారిత్రక ప్రదేశాలు, రవాణా మార్గాలు లేదా అత్యవసర సేవల గురించి అడగండి.",
                "hi": "मैं केवल हैदराबाद और तेलंगाना से संबंधित विषयों में विशेषज्ञता रखता हूँ। कृपया हमारे राज्य के कल्याणकारी योजनाओं, ऐतिहासिक स्थलों, परिवहन मार्गों या आपातकालीन संपर्कों के बारे में पूछें।",
                "ur": "میں صرف حیدرآباد اور تلنگانہ سے متعلقہ موضوعات پر ہی جواب دے سکتا ہوں۔ براہ کرم ہمارے صوبے کی فلاحی اسکیموں، تاریخی مقامات، ٹرانسپورٹ روٹس یا ہنگامی رابطوں کے بارے میں سوال کریں۔"
            }
            return rejections.get(lang, rejections["en"])

        # In-scope offline responses
        if "scheme" in lower_prompt or "పథకం" in lower_prompt:
            return (
                "[HYBO Offline Mode]: Telangana state runs several major welfare programs, including: "
                "1. Rythu Bandhu (Investment support for farmers)\n"
                "2. Kalyana Lakshmi / Shaadi Mubarak (Financial assistance for marriages)\n"
                "3. Arogyasri (Healthcare coverage)\n"
                "For active application links and live status checks, please visit the official Telangana portal."
            )
        elif "hospital" in lower_prompt or "ఆసుపత్రి" in lower_prompt:
            return (
                "[HYBO Offline Mode]: Major public emergency centers in Hyderabad include:\n"
                "- Osmania General Hospital (Afzal Gunj)\n"
                "- Gandhi Hospital (Secunderabad)\n"
                "- Niloufer Hospital for Women and Children (Red Hills)\n"
                "For ambulance services, call toll-free: 108."
            )
        else:
            return (
                f"[HYBO Offline Mode]: Thank you for asking about '{prompt}' in Hyderabad/Telangana. "
                "Once AWS Bedrock credentials are fully configured, live replies will be streamed here."
            )
