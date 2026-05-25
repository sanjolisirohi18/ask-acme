"""Application configuration loaded from environment variables.

Values are read from environment variables and/or a `.env` file at startup.
Validation happens once — if anything is missing or malformed, the app fails
fast rather than crashing later on first use.

Usage:
    from ask_acme.config import settings
    print(settings.database_url)
"""

from functools import cached_property
from typing import Literal

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # silently ignore unrelated env vars
        case_sensitive=False,    # POSTGRES_USER == postgres_user
    )

    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------
    env: Literal["development", "staging", "production"] = Field(
        default="development", alias="ASK_ACME_ENV"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", alias="ASK_ACME_LOG_LEVEL"
    )
    debug: bool = Field(default=False, alias="ASK_ACME_DEBUG")

    # -----------------------------------------------------------------------
    # Server
    # -----------------------------------------------------------------------
    host: str = Field(default="0.0.0.0", alias="ASK_ACME_HOST")
    port: int = Field(default=8000, alias="ASK_ACME_PORT")

    # -----------------------------------------------------------------------
    # Postgres
    # -----------------------------------------------------------------------
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def database_url(self) -> str:
        """SQLAlchemy-style DSN for synchronous drivers (psycopg).

        Used by Alembic migrations and any sync code path.
        """
        pw = self.postgres_password.get_secret_value()
        return (
            f"postgresql+psycopg://{self.postgres_user}:{pw}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def database_url_async(self) -> str:
        """DSN for asyncpg — used by the app's async data path."""
        pw = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{pw}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # -----------------------------------------------------------------------
    # Qdrant
    # -----------------------------------------------------------------------
    qdrant_host: str = Field(default="qdrant", alias="QDRANT_HOST")
    qdrant_http_port: int = Field(default=6333, alias="QDRANT_HTTP_PORT")
    qdrant_grpc_port: int = Field(default=6334, alias="QDRANT_GRPC_PORT")
    qdrant_api_key: SecretStr | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(alias="QDRANT_COLLECTION")

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def qdrant_http_url(self) -> str:
        """Full HTTP URL for the Qdrant REST API and dashboard."""
        return f"http://{self.qdrant_host}:{self.qdrant_http_port}"

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def qdrant_grpc_url(self) -> str:
        """Full gRPC URL for high-throughput Qdrant operations."""
        return f"http://{self.qdrant_host}:{self.qdrant_grpc_port}"

    # -----------------------------------------------------------------------
    # External APIs
    # -----------------------------------------------------------------------
    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")


# Single shared instance — import this everywhere rather than constructing
# new Settings() objects, so the .env file is only parsed once.
settings = Settings()  # type: ignore[call-arg]