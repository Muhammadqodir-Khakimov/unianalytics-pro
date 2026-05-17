"""TZ 4.2.4 talab qilgan o'zbekcha buyruqlar to'plami.

13 ta buyruq: /reyting, /fanlar, /davomat, /jadval, /bogla, /dayjest,
/yordam, /aloqa, /sozlamalar, /chiqish + start/login/menu (alohida fayllarda).

Bu handlerlar mavjud (ingliz nomli) buyruqlarning kontent qatlami ustida
yengil obyolg'ich rolini bajaradi — biznes-logika dublikatsiya qilinmaydi.
"""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..services.api_client import ApiError, api_client
from ..utils.formatters import md_escape
from .auth import cmd_logout
from .data import (
    cmd_gpa,
    cmd_grades,
    cmd_notifications,
    cmd_schedule,
)
from .start import HELP, cmd_help

router = Router(name="tz_commands")


# ---------------------------------------------------------------------------
# /reyting — GPA + guruh ichidagi o'rin (TZ 2.4.4)
# ---------------------------------------------------------------------------
@router.message(Command("reyting"))
async def cmd_reyting(message: Message, token: str | None) -> None:
    await cmd_gpa(message, token)


# ---------------------------------------------------------------------------
# /fanlar — fanlar bo'yicha baholar
# ---------------------------------------------------------------------------
@router.message(Command("fanlar"))
async def cmd_fanlar(message: Message, token: str | None) -> None:
    await cmd_grades(message, token)


# ---------------------------------------------------------------------------
# /davomat — darslarga qatnashish foizi (TZ 4.2.4)
# ---------------------------------------------------------------------------
@router.message(Command("davomat"))
async def cmd_davomat(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    try:
        data = await api_client.my_dashboard(token)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    stats = data.get("stats") or {}
    avg = stats.get("avg_attendance")
    if avg is None:
        await message.answer("📅 Davomat ma'lumoti hali kiritilmagan.")
        return
    bar = "🟢" if avg >= 90 else "🟡" if avg >= 75 else "🔴"
    await message.answer(
        f"{bar} *Davomat:* `{avg}%`\n\n"
        f"_Eslatma: 75% dan past davomat akademik xavf signaliga olib keladi._",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# /jadval — dars jadvali
# ---------------------------------------------------------------------------
@router.message(Command("jadval"))
async def cmd_jadval(message: Message, token: str | None) -> None:
    await cmd_schedule(message, token)


# ---------------------------------------------------------------------------
# /bogla — ota-onaning farzandiga bog'lanish so'rovi (TZ 4.2.4)
# ---------------------------------------------------------------------------
@router.message(Command("bogla"))
async def cmd_bogla(message: Message, command: Command, token: str | None) -> None:
    if not token:
        await message.answer(
            "🔒 Avval ota-ona sifatida ro'yxatdan o'ting: /login"
        )
        return
    args = (command.args or "").strip()
    if not args:
        await message.answer(
            "👨‍👩‍👧 *Farzandga bog'lanish*\n\n"
            "Foydalanish:\n"
            "`/bogla <farzandning HEMIS ID si>`\n\n"
            "Misol: `/bogla 11220194`\n\n"
            "_Talaba bog'lanish so'rovini tasdiqlashi shart._",
            parse_mode="Markdown",
        )
        return
    try:
        await api_client.request_parent_link(token, hemis_id=args)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    await message.answer(
        f"✅ So'rov yuborildi. *{md_escape(args)}* tasdiqlashi kutilmoqda.",
        parse_mode="MarkdownV2",
    )


# ---------------------------------------------------------------------------
# /dayjest — haftalik dayjest sozlash (TZ 4.2.4)
# ---------------------------------------------------------------------------
@router.message(Command("dayjest"))
async def cmd_dayjest(message: Message, command: Command, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    arg = (command.args or "").strip().lower()
    if arg not in {"yoq", "ochir", "on", "off", ""}:
        await message.answer(
            "📨 Foydalanish: `/dayjest yoq` yoki `/dayjest ochir`",
            parse_mode="Markdown",
        )
        return
    if not arg:
        await message.answer(
            "📨 *Haftalik dayjest*\n\n"
            "Har juma 18:00 da haftalik hisobot Telegram orqali yuboriladi.\n\n"
            "Yoqish:  `/dayjest yoq`\n"
            "O'chirish: `/dayjest ochir`",
            parse_mode="Markdown",
        )
        return
    enable = arg in {"yoq", "on"}
    try:
        await api_client.set_digest(token, enabled=enable)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    await message.answer(
        "✅ Haftalik dayjest YOQILDI" if enable else "🔕 Haftalik dayjest O'CHIRILDI"
    )


# ---------------------------------------------------------------------------
# /yordam — qo'llanma (cmd_help ning o'zbekcha aliasi)
# ---------------------------------------------------------------------------
@router.message(Command("yordam"))
async def cmd_yordam(message: Message) -> None:
    await cmd_help(message)


# ---------------------------------------------------------------------------
# /aloqa — dekanat / kurator bilan bog'lanish (TZ 4.2.4)
# ---------------------------------------------------------------------------
@router.message(Command("aloqa"))
async def cmd_aloqa(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    try:
        data = await api_client.my_dashboard(token)
        contacts = await api_client.my_contacts(token)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    student = data.get("student") or {}
    kurator = contacts.get("kurator") or {}
    dekan = contacts.get("dekan") or {}
    lines = [
        "📞 *Aloqa ma'lumotlari*\n",
        f"🎓 Guruh: {md_escape(student.get('group_name') or '—')}",
    ]
    if kurator:
        lines.append(
            f"\n👤 *Kurator:* {md_escape(kurator.get('fish') or '—')}\n"
            f"📱 `{md_escape(kurator.get('phone') or '—')}`"
        )
    if dekan:
        lines.append(
            f"\n🏛 *Dekan:* {md_escape(dekan.get('fish') or '—')}\n"
            f"📱 `{md_escape(dekan.get('phone') or '—')}`"
        )
    lines.append(
        "\n_Shoshilinch ish bo'lsa, ushbu raqamlarga qo'ng'iroq qiling._"
    )
    await message.answer("\n".join(lines), parse_mode="MarkdownV2")


# ---------------------------------------------------------------------------
# /sozlamalar — til + xabarnoma sozlamalari (TZ 4.2.4)
# ---------------------------------------------------------------------------
@router.message(Command("sozlamalar"))
async def cmd_sozlamalar(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    await message.answer(
        "⚙️ *Sozlamalar*\n\n"
        "🌐 Til: o'zbek (lotin) — `/til uz_lat` `/til uz_cyr` `/til ru`\n"
        "🔔 Bildirishnomalar: /notify\\_settings\n"
        "📨 Haftalik dayjest: /dayjest\n"
        "👨‍👩‍👧 Ota-ona bog'lash: /bogla\n",
        parse_mode="MarkdownV2",
    )


# ---------------------------------------------------------------------------
# /chiqish — sessiyani yopish (cmd_logout aliasi)
# ---------------------------------------------------------------------------
@router.message(Command("chiqish"))
async def cmd_chiqish(message: Message, state: FSMContext, token: str | None) -> None:
    await cmd_logout(message, state, token)
