"""/start, /menu, /help, fallback handlerlari."""
from __future__ import annotations

from aiogram import F, Router
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


# HTML formatda — Markdown'dan ishonchliroq (`[text]`, `*`, `_` xatosiz).
HELP = (
    "<b>📚 Bot buyruqlari:</b>\n\n"
    "<b>🔐 Auth</b>\n"
    "/login — tizimga kirish\n"
    "/chiqish (yoki /logout) — chiqish\n\n"
    "<b>📊 Akademik holat</b>\n"
    "/reyting — GPA va guruh ichidagi o'rin\n"
    "/rank_faculty — fakultet ichidagi o'rningiz\n"
    "/top — guruhda TOP-10 talabalar\n"
    "/trend — GPA dinamikasi (semestrlar)\n"
    "/maqsad — GPA bo'yicha maqsadlar\n"
    "/fanlar — baholar (sahifalanadi)\n"
    "/davomat — fan kesimida davomat foizi\n"
    "/imtihon — yaqinlashayotgan imtihonlar\n"
    "/jadval — dars jadvali\n"
    "/profile — shaxsiy ma'lumot\n\n"
    "<b>🎓 O'qituvchi / dekan / admin uchun</b>\n"
    "/xavf — akademik xavfdagi talabalar\n"
    "/top_fakultet — eng yaxshi fakultetlar\n\n"
    "<b>👨‍👩‍👧 Ota-ona / aloqa</b>\n"
    "/bogla 11220194 — farzandga bog'lanish (HEMIS ID bilan)\n"
    "/aloqa — kurator / dekan kontaktlari\n\n"
    "<b>⚙️ Sozlamalar va xabarlar</b>\n"
    "/sozlamalar — interaktiv panel\n"
    "/notify_settings — push sozlamalari\n"
    "/dayjest yoq — haftalik dayjest yoqish\n"
    "/notifications — bildirishnomalar\n\n"
    "<b>❓ Boshqa</b>\n"
    "/start — botni qayta ishga tushirish\n"
    "/menu — interaktiv menyu\n"
    "/yordam — ushbu qo'llanma"
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
@router.message(F.text == "❓ Yordam")
async def cmd_help(message: Message) -> None:
    # HELP endi HTML formatda — bot default parse_mode (HTML) bilan mos.
    await message.answer(HELP, parse_mode="HTML")


@router.message(Command("menu"))
@router.message(F.text == "📋 Menyu")
async def cmd_menu(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("Avval tizimga kiring: /login")
        return
    await message.answer(
        "📋 *Asosiy menyu*\n\nKerakli bo'limni tanlang:",
        reply_markup=main_menu_inline(),
        parse_mode="Markdown",
    )
