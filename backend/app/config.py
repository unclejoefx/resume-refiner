"""Application configuration."""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    CLAUDE_API_KEY: str = ""

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./resume_refiner.db"

    # CORS Configuration
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000"]

    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: Union[List[str], str] = [".pdf", ".docx"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated ALLOWED_ORIGINS string from .env file."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Parse comma-separated ALLOWED_EXTENSIONS string from .env file."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
