"""Bot sozlamalari — pydantic-settings orqali .env dan o'qiladi."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str
    backend_api_url: str = "http://localhost:8000/api/v1"
    # Bo'sh qoldirilsa — in-memory storage (dev rejim, prod'da Redis kerak)
    redis_url: str = ""

    # Webhook (ixtiyoriy)
    webhook_url: str | None = None
    webhook_secret: str | None = None
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8080

    bot_mode: str = "polling"  # polling | webhook
    rate_limit_per_min: int = 20


settings = Settings()  # type: ignore[call-arg]
