from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    test_database_url: str | None = None

    external_api_url: str = "https://example.com"
    external_api_key: str | None = None

    sync_interval_minutes: int = Field(default=10, ge=1)


settings = Settings()
