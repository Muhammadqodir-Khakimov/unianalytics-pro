"""Ilova sozlamalari (Pydantic Settings)."""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Markazlashgan sozlamalar — barcha env o'zgaruvchilarini saqlaydi."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Student Rating OLAP System"
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000

    # OLTP Database
    oltp_db_host: str = "postgres-oltp"
    oltp_db_port: int = 5432
    oltp_db_user: str = "oltp_user"
    oltp_db_password: str = "oltp_pass"
    oltp_db_name: str = "student_oltp"
    oltp_db_url: str | None = None  # to'liq URL override (SQLite local dev uchun)

    # OLAP Database
    olap_db_host: str = "postgres-olap"
    olap_db_port: int = 5432
    olap_db_user: str = "olap_user"
    olap_db_password: str = "olap_pass"
    olap_db_name: str = "student_olap"
    olap_db_url: str | None = None  # to'liq URL override

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    @property
    def oltp_database_url(self) -> str:
        if self.oltp_db_url:
            return self.oltp_db_url
        return (
            f"postgresql+psycopg2://{self.oltp_db_user}:{self.oltp_db_password}"
            f"@{self.oltp_db_host}:{self.oltp_db_port}/{self.oltp_db_name}"
        )

    @property
    def olap_database_url(self) -> str:
        if self.olap_db_url:
            return self.olap_db_url
        return (
            f"postgresql+psycopg2://{self.olap_db_user}:{self.olap_db_password}"
            f"@{self.olap_db_host}:{self.olap_db_port}/{self.olap_db_name}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
