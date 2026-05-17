"""/start, /menu, /help, fallback handlerlari."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from ..keyboards.inline import main_menu_inline
from ..keyboards.reply import main_menu

router = Router(name="start")


WELCOME_GUEST = (
    "👋 *UniAnalytics PRO* botiga xush kelibsiz\\!\n\n"
    "Bu bot orqali siz quyidagilarni ko'rishingiz mumkin:\n"
    "• GPA va o'rtacha ball\n"
    "• So'nggi baholaringiz\n"
    "• Guruhda o'rin \\(reyting\\)\n"
    "• Dars jadvali\n"
    "• Bildirishnomalar\n\n"
    "Boshlash uchun /login orqali tizimga kiring\\."
)


def welcome_authed(name: str) -> str:
    safe = name.replace("*", "").replace("_", "").replace("`", "")
    return (
        f"👋 Salom, *{safe}*!\n\n"
        "Pastdagi tugmalar yoki buyruqlar orqali ma'lumotlaringizni ko'ring."
    )


HELP = (
    "*📚 Bot buyruqlari:*\n\n"
    "🔐 *Auth:*\n"
    "/login — tizimga kirish\n"
    "/chiqish (yoki /logout) — chiqish\n\n"
    "📊 *Akademik holat:*\n"
    "/reyting — GPA, o'rtacha ball, guruh ichidagi o'rin\n"
    "/rank_faculty — fakultet ichidagi o'rningiz\n"
    "/top — guruhda TOP-10 talabalar\n"
    "/fanlar — fanlar bo'yicha baholar (sahifalanadi)\n"
    "/davomat — fan kesimida davomat foizi\n"
    "/imtihon — yaqinlashayotgan imtihonlar\n"
    "/jadval — dars jadvali\n"
    "/profile — shaxsiy ma'lumot\n\n"
    "👨‍👩‍👧 *Ota-ona / aloqa:*\n"
    "/bogla [HEMIS_ID] — farzandga bog'lanish so'rovi\n"
    "/aloqa — kurator/dekan kontaktlari\n\n"
    "⚙️ *Sozlamalar va xabarlar:*\n"
    "/sozlamalar — til + bildirishnomalar (interaktiv)\n"
    "/notify_settings — push sozlamalari\n"
    "/dayjest yoq|ochir — haftalik dayjest\n"
    "/notifications — bildirishnomalar ro'yxati\n\n"
    "❓ *Boshqa:*\n"
    "/start — botni qayta ishga tushirish\n"
    "/menu — interaktiv menyu\n"
    "/yordam (yoki /help) — ushbu qo'llanma"
)


@router.message(CommandStart())
async def cmd_start(
    message: Message, token: str | None, user: dict | None
) -> None:
    if token and user:
        name = user.get("full_name") or user.get("username") or "foydalanuvchi"
        await message.answer(
            welcome_authed(name),
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
    else:
        await message.answer(WELCOME_GUEST, parse_mode="MarkdownV2")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP, parse_mode="Markdown")


@router.message(Command("menu"))
async def cmd_menu(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("Avval tizimga kiring: /login")
        return
    await message.answer(
        "📋 *Asosiy menyu*\n\nKerakli bo'limni tanlang:",
        reply_markup=main_menu_inline(),
        parse_mode="Markdown",
    )
