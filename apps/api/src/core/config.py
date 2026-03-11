"""API config from environment."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://app:app@localhost:5433/multi_asset_invest"
    redis_url: str = "redis://localhost:6380/0"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    class Config:
        env_prefix = ""


settings = Settings()
