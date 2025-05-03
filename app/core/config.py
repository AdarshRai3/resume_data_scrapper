from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume Analyzer API"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # File upload settings
    UPLOAD_DIR: str = "uploads"

    # Allowed file types
    ALLOWED_FILE_TYPES: tuple = (".pdf",)

    class Config:
        env_file = ".env"  # Load environment variables from .env file (optional)

# Global settings instance
settings = Settings()
