import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "HYBO-Assistant"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    # AWS Credentials
    AWS_ACCESS_KEY_ID: str = "mock-key"
    AWS_SECRET_ACCESS_KEY: str = "mock-secret"
    AWS_REGION: str = "us-east-1"

    # AI Configurations
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.2

    # Allow custom .env file locations
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
