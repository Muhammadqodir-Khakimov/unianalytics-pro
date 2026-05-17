"""Fallback handler — noma'lum buyruq/matn uchun."""
from aiogram import Router
from aiogram.types import Message

router = Router(name="common")


@router.message()
async def fallback(message: Message, token: str | None) -> None:
    if not token:
        await message.answer(
            "🔒 Avval tizimga kiring: /login\n\n"
            "Buyruqlar ro'yxati uchun /help"
        )
    else:
        await message.answer(
            "Noma'lum buyruq. /help — buyruqlar ro'yxati"
        )
