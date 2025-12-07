"""Application settings sourced from environment variables.

Using pydantic-settings keeps configuration explicit and testable.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised configuration for the FastAPI app and workers."""

    environment: str = Field(default="local", validation_alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    supabase_url: Optional[AnyHttpUrl] = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_service_role_key: Optional[str] = Field(
        default=None, validation_alias="SUPABASE_SERVICE_ROLE_KEY"
    )

    newsapi_key: Optional[str] = Field(default=None, validation_alias="NEWSAPI_KEY")
    unsplash_access_key: Optional[str] = Field(default=None, validation_alias="UNSPLASH_ACCESS_KEY")
    mailjet_api_key: Optional[str] = Field(default=None, validation_alias="MAILJET_API_KEY")
    mailjet_api_secret: Optional[str] = Field(default=None, validation_alias="MAILJET_API_SECRET")

    openrouter_api_key: Optional[str] = Field(default=None, validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: AnyHttpUrl = Field(
        default="https://openrouter.ai/api/v1", validation_alias="OPENROUTER_BASE_URL"
    )
    openrouter_model: str = Field(default="gpt-4o-mini", validation_alias="OPENROUTER_MODEL")

    firecrawl_server_url: Optional[AnyHttpUrl] = Field(
        default="https://api.firecrawl.dev", validation_alias="FIRECRAWL_SERVER_URL"
    )
    firecrawl_api_key: Optional[str] = Field(default=None, validation_alias="FIRECRAWL_API_KEY")

    redis_url: str = Field(default="redis://redis:6379/0", validation_alias="REDIS_URL")

    mailjet_sender_name: str = Field(default="Weekly Brief", validation_alias="MAILJET_SENDER_NAME")
    mailjet_sender_email: str = Field(
        default="no-reply@example.com", validation_alias="MAILJET_SENDER_EMAIL"
    )
    mailjet_contact_list_id: Optional[int] = Field(
        default=None, validation_alias="MAILJET_CONTACT_LIST_ID"
    )

    mjml_template_path: str = Field(
        default="backend/app/templates/newsletter.mjml",
        validation_alias="MJML_TEMPLATE_PATH",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance for the current process."""

    return Settings()  # type: ignore[call-arg]
