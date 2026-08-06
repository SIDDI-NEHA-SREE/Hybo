import json
from typing import Optional
import boto3
from app.config import settings
from app.utils.logger import logger

class BedrockClient:
    _client = None

    @classmethod
    def is_available(cls) -> bool:
        """
        Checks if AWS credentials are validly configured and client can be obtained.
        """
        if not settings.is_aws_configured:
            return False
        return cls.get_client() is not None

    @classmethod
    def get_client(cls):
        """
        Initializes and returns the boto3 Bedrock client.
        Returns None if AWS credentials are not configured or invalid.
        """
        if not settings.is_aws_configured:
            logger.info("AWS credentials not configured. Bedrock client is disabled.")
            cls._client = None
            return None

        if cls._client is None:
            try:
                cls._client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                logger.info("Successfully initialized AWS Bedrock runtime client.")
            except Exception as e:
                logger.error(f"Failed to initialize AWS Bedrock client: {str(e)}.")
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
    async def invoke_model(cls, prompt: str, retrieved_context: str = "", preferred_lang: str = "en") -> Optional[str]:
        """
        Invokes Claude on Bedrock. Returns response string, or None if Bedrock is unavailable/failed.
        """
        client = cls.get_client()
        if client is None:
            logger.info("Bedrock client is unavailable.")
            return None

        system_prompt = cls.get_system_prompt()
        
        # Inject RAG context if present
        user_message = prompt
        if retrieved_context:
            user_message = f"<context>\n{retrieved_context}\n</context>\n\nQuery: {prompt}"

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
            logger.error(f"Error invoking Bedrock model: {str(e)}.")
            return None

