from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    supabase_key: str
    redis_url: str = "redis://localhost:6379/0"
    processing_delay_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
