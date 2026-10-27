"""Configuration module for VidyaSetu using Pydantic Settings."""
import os
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application identity
    APP_NAME: str = "VidyaSetu"
    APP_VERSION: str = "0.1.0-alpha"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # Server Bindings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # Database URLs
    # By default, use local SQLite file for immediate zero-config testing if PostgreSQL is not specified
    DATABASE_URL: str = "sqlite+aiosqlite:///./vidyasetu.db"
    SYNC_DATABASE_URL: str = "sqlite:///./vidyasetu.db"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Security (Synthetic demo secret)
    SECRET_KEY: str = "vidyasetu-demo-secret-key-32-chars-minimum-token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Structured Logging
    LOG_LEVEL: str = "INFO"

    # Simulation / Mock Controls
    ENABLE_MOCK_APAAR: bool = True
    APAAR_MOCK_LATENCY_MS: int = 250
    AICTE_COUNCIL_REGISTRY_MOCK: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Any) -> str:
        if not v or not isinstance(v, str):
            return "sqlite+aiosqlite:///./vidyasetu.db"
        val = v.strip()
        if val.startswith("postgres://"):
            return val.replace("postgres://", "postgresql+asyncpg://", 1)
        if val.startswith("postgresql://") and not val.startswith("postgresql+"):
            return val.replace("postgresql://", "postgresql+asyncpg://", 1)
        return val

    @field_validator("SYNC_DATABASE_URL", mode="before")
    @classmethod
    def normalize_sync_database_url(cls, v: Any) -> str:
        if not v or not isinstance(v, str):
            return "sqlite:///./vidyasetu.db"
        val = v.strip()
        if val.startswith("postgres://"):
            return val.replace("postgres://", "postgresql+psycopg2://", 1)
        if val.startswith("postgresql://") and not val.startswith("postgresql+"):
            return val.replace("postgresql://", "postgresql+psycopg2://", 1)
        return val

    @field_validator("BACKEND_PORT", mode="before")
    @classmethod
    def resolve_backend_port(cls, v: Any) -> int:
        port_env = os.environ.get("PORT")
        if port_env:
            try:
                return int(port_env)
            except ValueError:
                pass
        return int(v) if v is not None else 8000

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return []


settings = Settings()
