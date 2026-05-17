"""Monitoring va observability — Sentry + Prometheus."""
import os
from typing import Callable

from fastapi import FastAPI, Request, Response
from loguru import logger


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

        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% so'rovlar uchun performance tracking
            profiles_sample_rate=0.1,
            environment=os.environ.get("APP_ENV", "production"),
            send_default_pii=False,
        )
        logger.info("Sentry ulandi")
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
