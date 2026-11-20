from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Основное подключение
    database_url: str | None = None
    test_database_url: str | None = None

    # Переменные PostgreSQL от LMS
    postgres_connection_string: str | None = None
    postgres_host: str | None = None
    postgres_port: int = 5432
    postgres_database_name: str | None = None
    postgres_username: str | None = None
    postgres_password: str | None = None

    # Внешний API
    external_api_url: str = "https://events-provider.dev-2.python-labs.ru"
    external_api_key: str | None = None

    # Синхронизация и кэш
    sync_interval_minutes: int = Field(default=1440, ge=1)
    seats_cache_ttl_seconds: int = Field(default=30, ge=1)

    @model_validator(mode="after")
    def configure_database_url(self) -> "Settings":
        if self.database_url:
            self.database_url = self._normalize_database_url(self.database_url)
            return self

        if self.postgres_connection_string:
            self.database_url = self._normalize_database_url(
                self.postgres_connection_string
            )
            return self

        if all(
            (
                self.postgres_host,
                self.postgres_database_name,
                self.postgres_username,
                self.postgres_password,
            )
        ):
            self.database_url = (
                "postgresql+asyncpg://"
                f"{quote_plus(self.postgres_username)}:"
                f"{quote_plus(self.postgres_password)}@"
                f"{self.postgres_host}:{self.postgres_port}/"
                f"{quote_plus(self.postgres_database_name)}"
            )
            return self

        raise ValueError(
            "Set DATABASE_URL, POSTGRES_CONNECTION_STRING "
            "or all PostgreSQL connection parameters"
        )

    @staticmethod
    def _normalize_database_url(url: str) -> str:
        if url.startswith("postgres://"):
            return url.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        if url.startswith("postgresql://"):
            return url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return url


settings = Settings()
