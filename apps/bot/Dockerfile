FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Tarmoq uchun zarur paketlar
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot /app/bot
COPY .env.example /app/.env.example

# Non-root user
RUN useradd -u 1000 -m botuser && chown -R botuser /app
USER botuser

CMD ["python", "-m", "bot.main"]
