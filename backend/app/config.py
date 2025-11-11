"""Application configuration."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    CLAUDE_API_KEY: str = ""

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./resume_refiner.db"

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
