from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Finance Tracker"
    secret_key: str = "dev-only-change-me"
    database_url: str = "sqlite:///./finance.db"
    access_token_minutes: int = 30
    refresh_token_days: int = 7
    frontend_origin: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
