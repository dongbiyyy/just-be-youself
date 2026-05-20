from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "GovernanceMonitor"
    app_env: str = "dev"

    secret_key: str = "change-me-please-use-a-long-random-string"
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"

    database_url: str = "sqlite:///./governance.db"

    init_admin_username: str = "admin"
    init_admin_password: str = "admin123"
    init_admin_email: str = "admin@example.com"

    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
