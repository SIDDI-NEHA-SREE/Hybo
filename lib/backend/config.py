import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hybo.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "hybo_secret_key_change_me_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Application directories
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    VECTOR_DIR: str = os.getenv("VECTOR_DIR", "vector_store")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_DIR, exist_ok=True)
