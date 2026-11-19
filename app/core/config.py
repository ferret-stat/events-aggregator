from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DOTENV = BASE_DIR / ".env"


class Settings(BaseSettings):
    database_url: str
    test_database_url: str

    sync_interval_minutes: int = Field(default=10, ge=1)
    external_api_url: str
    external_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
