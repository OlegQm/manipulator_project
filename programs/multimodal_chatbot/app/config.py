"""
Application configuration via Pydantic BaseSettings.

All environment variables are read automatically from the .env file
or from the system environment. No manual dotenv loading required.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the multimodal chatbot application."""

    # --- OpenAI ---
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # --- Redis ---
    redis_url: str = "redis://redis:6379/0"

    # --- Session management ---
    session_ttl_seconds: int = 3600  # 1 hour of inactivity before auto-cleanup
    cleanup_interval_seconds: int = 600  # run cleanup every 10 minutes
    max_context_tokens: int = 100_000  # model context window limit

    # --- Basic Auth (used by Nginx, also readable by the app if needed) ---
    basic_auth_user: str = "admin"
    basic_auth_password: str = "changeme"

    # --- Logging ---
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
