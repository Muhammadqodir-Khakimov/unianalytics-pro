"""Ilova sozlamalari (Pydantic Settings)."""
import os
from functools import lru_cache
from typing import List
from urllib.parse import urlparse

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_pg_url(url: str) -> str:
    """Railway/Heroku 'postgres://' yoki 'postgresql://' ni psycopg2 driveriga moslashtirish."""
    if not url:
        return url
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


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
    app_debug: bool = False
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
    redis_password: str | None = None
    redis_url: str | None = None  # to'liq URL override (Railway/Render uchun)

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS — vergul bilan ajratilgan domenlar yoki '*'
    cors_origins: str = "http://localhost:3000,http://localhost"

    # Celery
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    @property
    def oltp_database_url(self) -> str:
        # 1. Aniq belgilangan override
        if self.oltp_db_url:
            return _normalize_pg_url(self.oltp_db_url)
        # 2. Railway/Heroku style: DATABASE_URL
        env_url = os.environ.get("DATABASE_URL") or os.environ.get("OLTP_DATABASE_URL")
        if env_url:
            return _normalize_pg_url(env_url)
        # 3. Komponentlardan yig'ish
        return (
            f"postgresql+psycopg2://{self.oltp_db_user}:{self.oltp_db_password}"
            f"@{self.oltp_db_host}:{self.oltp_db_port}/{self.oltp_db_name}"
        )

    @property
    def olap_database_url(self) -> str:
        if self.olap_db_url:
            return _normalize_pg_url(self.olap_db_url)
        env_url = os.environ.get("OLAP_DATABASE_URL") or os.environ.get("OLAP_DB_URL")
        if env_url:
            return _normalize_pg_url(env_url)
        # Agar alohida OLAP DB yo'q bo'lsa — OLTP bilan bitta DB ishlatamiz (Railway free plan)
        if os.environ.get("DATABASE_URL") and not os.environ.get("OLAP_DATABASE_URL"):
            return _normalize_pg_url(os.environ["DATABASE_URL"])
        return (
            f"postgresql+psycopg2://{self.olap_db_user}:{self.olap_db_password}"
            f"@{self.olap_db_host}:{self.olap_db_port}/{self.olap_db_name}"
        )

    @property
    def redis_dsn(self) -> str:
        """To'liq Redis URL — Celery va cache uchun."""
        if self.redis_url:
            return self.redis_url
        env_url = os.environ.get("REDIS_URL")
        if env_url:
            return env_url
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def celery_broker(self) -> str:
        if self.celery_broker_url:
            return self.celery_broker_url
        return self.redis_dsn

    @property
    def celery_backend(self) -> str:
        if self.celery_result_backend:
            return self.celery_result_backend
        # Result backend uchun /1 db
        base = self.redis_dsn
        if base.rstrip("/").split("/")[-1].isdigit():
            return "/".join(base.rstrip("/").split("/")[:-1]) + "/1"
        return base.rstrip("/") + "/1"

    @property
    def cors_origins_list(self) -> List[str]:
        raw = (os.environ.get("CORS_ORIGINS") or self.cors_origins).strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
