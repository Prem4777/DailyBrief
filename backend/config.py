"""
config.py — Application configuration via pydantic-settings.

All settings are loaded from environment variables (or .env file).
Access settings anywhere via the exported `settings` singleton.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for DailyBrief backend.

    All fields map 1:1 to environment variables defined in .env.example.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Gemini AI ---
    gemini_api_key: str = ""

    # --- Google OAuth ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # --- JWT ---
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # --- Encryption ---
    credential_encryption_key: str = ""
    """Fernet key used to encrypt/decrypt stored OAuth tokens."""

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./dailybrief.db"

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Google Calendar ---
    google_calendar_id: str = "primary"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Allow comma-separated string or a JSON list from the env var."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


# Singleton instance — import this everywhere.
settings = Settings()
