from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Trace"
    DEBUG: bool = False

    DATABASE_URL: str
    REDIS_URL: str

    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    VISION_MODEL: str = "google/gemini-2.0-flash-exp"
    EMBEDDING_MODEL: str = "openai/text-embedding-3-small"

    VISION_CALLS_PER_DAY: int = 1000
    SEARCH_CALLS_PER_DAY: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()