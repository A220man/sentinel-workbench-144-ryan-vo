"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = "Sentinel Workbench"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./sentinel.db"
    
    secret_key: str = Field(default="change-me-in-production-minimum-32-characters-long", min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OIDC / Keycloak
    oidc_enabled: bool = True
    oidc_issuer_url: str = "http://localhost:8080/realms/sentinel"
    oidc_client_id: str = "sentinel-workbench"
    oidc_client_secret: Optional[str] = None
    oidc_redirect_uri: str = "http://localhost:5173/callback"
    oidc_scopes: str = "openid profile email roles"
    
    # LLM Providers
    llm_api_key: Optional[str] = None
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None
    llm_timeout_seconds: int = 30
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Privacy mode
    privacy_enabled: bool = False
    privacy_mask_char: str = "█"
    privacy_rules: list[str] = ["secret", "email", "phone", "card", "iban", "ip"]
    privacy_allow_hosts: list[str] = ["github.com", "learn.microsoft.com"]
    
    # Agent settings
    agent_detect_seconds: int = 2
    agent_quiet_windows: list[str] = []


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()