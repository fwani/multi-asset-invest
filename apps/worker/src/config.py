"""Worker config. Load from env and .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WORKER_",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://app:app@localhost:5433/multi_asset_invest"
    redis_url: str = "redis://localhost:6380/0"
    log_level: str = "INFO"


settings = Settings()
