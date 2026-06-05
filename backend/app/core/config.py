from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Azure Inventory SaaS"
    environment: str = "dev"
    frontend_origin: str = "http://localhost:3000"
    public_base_url: str = "http://localhost"

    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/azure_inventory"
    redis_url: str = "redis://redis:6379/0"

    microsoft_client_id: str
    microsoft_client_secret: str
    microsoft_authority: str = "https://login.microsoftonline.com/common"
    microsoft_redirect_uri: str = "http://localhost/api/auth/callback"
    microsoft_audience: str
    microsoft_allowed_issuers: list[str] = Field(default_factory=list)

    cookie_domain: str | None = None
    session_cookie_name: str = "azinv_session"
    cookie_secure: bool = False
    jwt_signing_key: str
    token_encryption_key: str

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    rate_limit_per_minute: int = 120

    graph_base_url: AnyHttpUrl = "https://graph.microsoft.com/v1.0"
    arm_base_url: AnyHttpUrl = "https://management.azure.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
