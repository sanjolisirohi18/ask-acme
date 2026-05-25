"""Application configuration loaded from environment variables.

Values are read from environment variables and/or a `.env` file. Validation
happens the first time `get_settings()` is called and the result is cached, so
the app fails fast at startup — not at import time, which would break tooling
(pytest, CI, `python -c "import ask_acme"`) in environments without a `.env`.

Usage:
    from ask_acme.config import get_settings
    print(get_settings().database_url)
"""

from functools import cached_property, lru_cache
from typing import Literal

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # ignore unrelated process-env vars (PATH, HOME, etc.) we don't care about — forbid would crash on every import
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
    # Defaults to localhost so host-machine runs (pytest, alembic, ad-hoc
    # scripts) work against the published compose ports with zero overrides.
    # Inside the compose network the app service sets POSTGRES_HOST=postgres
    # explicitly, so this default never applies there.
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
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
    # See postgres_host above: localhost for host-machine runs; the compose app
    # service overrides this to QDRANT_HOST=qdrant inside the network.
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_http_port: int = Field(default=6333, alias="QDRANT_HTTP_PORT")
    qdrant_grpc_port: int = Field(default=6334, alias="QDRANT_GRPC_PORT")
    qdrant_api_key: SecretStr | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(alias="QDRANT_COLLECTION")

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def qdrant_http_url(self) -> str:
        """Full HTTP URL for the Qdrant REST API and dashboard."""
        return f"http://{self.qdrant_host}:{self.qdrant_http_port}"

    # No qdrant_grpc_url on purpose: gRPC isn't HTTP, so a "http://host:6334"
    # string is misleading, and qdrant-client doesn't take a gRPC URL anyway —
    # it wants host + grpc_port separately, e.g.
    #   QdrantClient(host=settings.qdrant_host,
    #                grpc_port=settings.qdrant_grpc_port, prefer_grpc=True)
    # Use those fields directly; add a typed accessor only when a caller needs it.

    # -----------------------------------------------------------------------
    # External APIs
    # -----------------------------------------------------------------------
    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    """Return the shared Settings instance, constructing it on first call.

    Cached so the `.env` file is parsed and validated only once. Call this
    everywhere rather than constructing `Settings()` directly. Lazy by design:
    a missing/malformed env only raises when the app actually needs config,
    not when a module merely imports it.
    """
    return Settings()  # type: ignore[call-arg]