import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost", "http://localhost:3000", "http://localhost:8000"]

    # Database Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "podcast_chunks")

    # External Services
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # File Storage
    UPLOAD_DIR: str = "app/static/uploads"
    AUDIO_DIR: str = "app/static/audio"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
