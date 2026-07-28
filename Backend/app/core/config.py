"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root: Document Assistant/
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Central configuration for the backend API."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI Engineering Document Assistant"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = False

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # External services (used in later phases)
    gemini_api_key: str | None = None

    # Upload limits
    max_upload_size_mb: int = Field(default=10, description="Maximum PDF upload size in MB")

    # Data paths
    data_dir: Path = Field(default=PROJECT_ROOT / "Data")
    uploads_dir: Path = Field(default=PROJECT_ROOT / "Data" / "uploads")
    chroma_dir: Path = Field(default=PROJECT_ROOT / "Data" / "chroma")

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in {"development", "dev", "local"}


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
