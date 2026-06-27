"""
Application settings loaded from environment variables and .env file.
"""

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration (Laravel config/*.php equivalent)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./app.db"
    api_key: str = "dev-key-123"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins from settings."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
