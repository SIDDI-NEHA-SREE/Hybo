import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "HYBO-Assistant"
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = "0.0.0.0"

    # AWS Credentials (Optional for deployment without Bedrock)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # AI Configurations
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.2

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

    # Allow custom .env file locations
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

