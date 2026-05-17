"""Telegram bot boshqaruv endpointlari."""
from fastapi import APIRouter, Depends

from app.core.dependencies import require_admin

router = APIRouter(prefix="/telegram", tags=["Telegram"], dependencies=[Depends(require_admin)])


@router.get("/status")
def bot_status():
    """Telegram bot konfiguratsiya holatini ko'rish."""
    import os
    token_exists = bool(os.environ.get("TELEGRAM_BOT_TOKEN"))
    try:
        from app.services.telegram_bot import _load_links
        links_count = len(_load_links())
    except Exception:
        links_count = 0
    return {
        "configured": token_exists,
        "linked_users": links_count,
        "instructions": (
            "1. @BotFather dan token oling\n"
            "2. .env ga TELEGRAM_BOT_TOKEN=xxx qo'ying\n"
            "3. Alohida process: py -m app.services.telegram_bot"
        ),
    }


@router.get("/linked-users")
def linked_users():
    """Qaysi talabalar Telegram bilan bog'langan."""
    from app.services.telegram_bot import _load_links
    links = _load_links()
    return [{"chat_id": int(cid), "student_id": sid} for cid, sid in links.items()]
