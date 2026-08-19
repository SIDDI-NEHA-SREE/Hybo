import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "HYBO-Assistant"
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = "0.0.0.0"

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"

    # AWS Credentials (Optional for deployment without Bedrock)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # AI Configurations
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.2

    # Twilio Configurations
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    TWILIO_VERIFY_SERVICE_SID: Optional[str] = None

    # JWT Authentication
    JWT_SECRET_KEY: str = "hybo-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    OTP_EXPIRE_MINUTES: int = 5

    @property
    def is_aws_configured(self) -> bool:
        """
        Returns True only if all required AWS environment variables are set and non-dummy.
        """
        dummy_values = {"mock-key", "mock-secret", "your-aws-access-key", "your-aws-secret-key", "none", "null", ""}
        
        key = (self.AWS_ACCESS_KEY_ID or "").strip()
        secret = (self.AWS_SECRET_ACCESS_KEY or "").strip()
        region = (self.AWS_REGION or "").strip()
        
        if not key or key.lower() in dummy_values:
            return False
        if not secret or secret.lower() in dummy_values:
            return False
        if not region or region.lower() in dummy_values:
            return False
        return True

    @property
    def is_twilio_configured(self) -> bool:
        """
        Returns True only if Twilio Account SID and Auth Token are provided and non-dummy.
        """
        dummy_values = {"mock-sid", "mock-token", "your-twilio-account-sid", "your-twilio-auth-token", "none", "null", ""}
        sid = (self.TWILIO_ACCOUNT_SID or "").strip()
        token = (self.TWILIO_AUTH_TOKEN or "").strip()

        if not sid or sid.lower() in dummy_values:
            return False
        if not token or token.lower() in dummy_values:
            return False
        return True

    # Allow custom .env file locations
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

