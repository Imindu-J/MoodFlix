from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    database_url: str
    tmdb_read_access_token: SecretStr
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_request_timeout_seconds: float = 15.0
    tmdb_certification_country: str = "US"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
