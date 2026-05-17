"""Monitoring va observability — Sentry + Prometheus."""
import os
from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from loguru import logger


def _scrub_sensitive(event: dict[str, Any], hint: dict) -> dict[str, Any] | None:
    """Sentry'ga yuborishdan oldin sensitive ma'lumotlarni tozalash."""
    SENSITIVE_KEYS = {"password", "token", "secret", "authorization", "api_key", "totp", "totp_secret"}

    def scrub(obj):
        if isinstance(obj, dict):
            return {k: ("***" if k.lower() in SENSITIVE_KEYS else scrub(v)) for k, v in obj.items()}
        if isinstance(obj, list):
            return [scrub(x) for x in obj]
        return obj

    if "request" in event and "data" in event["request"]:
        event["request"]["data"] = scrub(event["request"]["data"])
    if "extra" in event:
        event["extra"] = scrub(event["extra"])
    return event


def setup_sentry(app: FastAPI) -> None:
    """Sentry error tracking ni ulash (agar DSN bo'lsa)."""
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        logger.info("SENTRY_DSN topilmadi — Sentry o'chirilgan")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        release = os.environ.get("APP_VERSION") or os.environ.get("GIT_SHA", "unknown")
        sentry_sdk.init(
            dsn=dsn,
            release=f"unianalytics-backend@{release}",
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_RATE", "0.1")),
            profiles_sample_rate=float(os.environ.get("SENTRY_PROFILES_RATE", "0.1")),
            environment=os.environ.get("APP_ENV", "production"),
            send_default_pii=False,
            # Don't send DB query content (PII risk)
            before_send=_scrub_sensitive,
            attach_stacktrace=True,
            max_breadcrumbs=50,
        )
        logger.info("Sentry ulandi (release={})", release)
    except ImportError:
        logger.warning("sentry-sdk o'rnatilmagan — pip install sentry-sdk[fastapi]")


def setup_prometheus(app: FastAPI) -> None:
    """Prometheus metrics endpoint qo'shish."""
    try:
        from prometheus_client import (
            CONTENT_TYPE_LATEST,
            Counter,
            Histogram,
            generate_latest,
        )

        # Metrics
        REQ_COUNT = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
        )
        REQ_LATENCY = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency",
            ["method", "endpoint"],
        )

        @app.middleware("http")
        async def metrics_middleware(request: Request, call_next: Callable):
            import time
            start = time.time()
            response = await call_next(request)
            duration = time.time() - start

            endpoint = request.url.path
            REQ_COUNT.labels(request.method, endpoint, response.status_code).inc()
            REQ_LATENCY.labels(request.method, endpoint).observe(duration)
            return response

        @app.get("/metrics", include_in_schema=False)
        def metrics() -> Response:
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

        logger.info("Prometheus metrics /metrics da mavjud")
    except ImportError:
        logger.warning("prometheus-client o'rnatilmagan")
