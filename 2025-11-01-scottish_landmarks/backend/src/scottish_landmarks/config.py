"""Configuration settings for the Scottish Landmarks application."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "Scottish Landmarks Travel Planner"
    api_version: str = "0.1.0"
    debug: bool = False

    # LLM Configuration
    gemini_token: str  # GEMINI_TOKEN from environment
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 2048

    # Google Search Configuration (for photo and review links)
    google_search_api_key: str = ""
    google_search_engine_id: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
