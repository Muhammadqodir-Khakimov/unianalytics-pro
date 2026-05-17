"""Bot ishga tushirish — polling yoki webhook rejimida.

REDIS_URL berilgan bo'lsa — FSM/throttling/auth Redis'da; aks holda
in-memory (faqat dev/test rejim, restart'da yo'qoladi).
"""
from __future__ import annotations

import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from redis.asyncio import Redis

from .config import settings
from .handlers import auth, common, data, menu_callbacks, start, tz_commands
from .middlewares.auth import AuthMiddleware
from .middlewares.throttling import ThrottlingMiddleware
from .services.api_client import api_client
from .services.auth_store import auth_store


def _setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <7}</level> | "
            "<cyan>{name}</cyan> | <level>{message}</level>"
        ),
    )


def build_dispatcher(redis: Redis | None) -> Dispatcher:
    if redis is not None:
        from aiogram.fsm.storage.redis import RedisStorage
        storage = RedisStorage(redis=redis)
        logger.info("FSM: Redis storage")
    else:
        storage = MemoryStorage()
        logger.warning(
            "FSM: in-memory (dev rejim) — restart'da holatlar yo'qoladi. "
            "Production'da REDIS_URL ni .env'da bering."
        )
    dp = Dispatcher(storage=storage)

    dp.update.outer_middleware(AuthMiddleware())
    dp.update.outer_middleware(ThrottlingMiddleware(redis=redis))

    dp.include_routers(
        start.router,
        auth.router,
        data.router,
        tz_commands.router,
        menu_callbacks.router,
        common.router,
    )
    return dp


def _build_redis() -> Redis | None:
    if not settings.redis_url:
        return None
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def run_polling() -> None:
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    redis = _build_redis()
    dp = build_dispatcher(redis)

    try:
        me = await bot.get_me()
        logger.info("Bot @{} ishga tushdi (polling)", me.username)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        if redis is not None:
            await redis.aclose()
        await api_client.close()
        await auth_store.close()


async def run_webhook() -> None:
    """Webhook rejimi — production uchun."""
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import (
        SimpleRequestHandler,
        setup_application,
    )

    if not settings.webhook_url:
        raise RuntimeError("BOT_MODE=webhook lekin WEBHOOK_URL berilmagan")

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    redis = _build_redis()
    dp = build_dispatcher(redis)

    await bot.set_webhook(
        url=settings.webhook_url,
        secret_token=settings.webhook_secret,
        allowed_updates=dp.resolve_used_update_types(),
    )

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    ).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    logger.info("Webhook server: {}:{}", settings.webapp_host, settings.webapp_port)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.webapp_host, settings.webapp_port)
    await site.start()
    await asyncio.Event().wait()


async def amain() -> None:
    _setup_logging()
    if settings.bot_mode == "webhook":
        await run_webhook()
    else:
        await run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
