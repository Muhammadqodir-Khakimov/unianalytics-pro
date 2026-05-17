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
        att = await api_client.my_attendance(token)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return

    avg = att.get("avg")
    if avg is None:
        # Fallback: dashboard'dan o'rtacha
        dash = await api_client.my_dashboard(token)
        avg = (dash.get("stats") or {}).get("avg_attendance")
        try:
            avg = float(avg) if avg is not None else None
        except (TypeError, ValueError):
            avg = None

    if avg is None:
        await message.answer("📅 Davomat ma'lumoti hali shakllanmadi.")
        return

    bar = "🟢" if avg >= 90 else "🟡" if avg >= 75 else "🔴"
    by_sub = att.get("by_subject") or []
    lines = [
        f"{bar} *Davomat:* `{avg:.1f}%`",
    ]
    if att.get("min") is not None:
        lines.append(f"📉 Eng past: `{att['min']:.1f}%`")
    if by_sub:
        lines.append("\n*Fan bo'yicha:*")
        for s in by_sub[:6]:
            ic = "🟢" if s['att'] >= 90 else "🟡" if s['att'] >= 75 else "🔴"
            lines.append(f"  {ic} {s['subject']} — `{s['att']:.1f}%`")
    lines.append(
        "\n_75% dan past davomat akademik xavf signaliga olib keladi._"
    )
    await message.answer("\n".join(lines), parse_mode="Markdown")


# ---------------------------------------------------------------------------
# /top — guruh ichida TOP klassmati (yangi)
# ---------------------------------------------------------------------------
@router.message(Command("top"))
async def cmd_top(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    try:
        data = await api_client.my_top_classmates(token, limit=10)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return

    items = data.get("items", [])
    group = md_escape(data.get("group_name") or "—")
    if not items:
        await message.answer(f"📊 Guruh `{group}` uchun ma'lumot tayyorlanmoqda.", parse_mode="Markdown")
        return

    lines = [f"🏆 *TOP talabalar — _{group}_*\n"]
    medals = ["🥇", "🥈", "🥉"] + ["🎓"] * 10
    for i, s in enumerate(items):
        m = medals[i] if i < len(medals) else "•"
        you = " ⬅️ *siz*" if s.get("is_me") else ""
        name = md_escape((s.get("name") or "")[:30])
        gpa = s.get("gpa") or 0
        lines.append(f"{m} `{gpa:.2f}`  {name}{you}")
    await message.answer("\n".join(lines), parse_mode="Markdown")


# ---------------------------------------------------------------------------
# /imtihon — yaqinlashayotgan imtihonlar (yangi)
# ---------------------------------------------------------------------------
@router.message(Command("imtihon"))
async def cmd_imtihon(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    try:
        data = await api_client.my_upcoming_exams(token, limit=10)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    items = data.get("items", [])
    if not items:
        await message.answer(
            "📚 *Yaqin 30 kun ichida imtihon belgilanmagan*\n\n"
            "_Jadval shakllangach bu yerda paydo bo'ladi._",
            parse_mode="Markdown",
        )
        return
    lines = ["📚 *Yaqinlashayotgan imtihonlar*\n"]
    for e in items:
        date = (e.get("exam_date") or "")[:16].replace("T", " ")
        room = md_escape(e.get("room") or "")
        etype = md_escape(e.get("exam_type") or "")
        lines.append(f"📅 `{date}`  {etype}  📍 {room}")
    await message.answer("\n".join(lines), parse_mode="Markdown")


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
    group = student.get("group_name") or "—"
    kurator = contacts.get("kurator") or {}
    dekan = contacts.get("dekan") or {}
    kafedra = contacts.get("kafedra_mudiri") or {}

    # Demo fallback — agar backend bo'sh qaytarsa, namuna kontaktlar
    if not kurator:
        kurator = {"fish": "Karimova Dilshoda Nuriddinovna", "phone": "+998 71 200-12-34", "email": "kurator@univ.uz"}
    if not dekan:
        dekan = {"fish": "Tursunov Bobur Olimovich", "phone": "+998 71 200-22-22", "email": "dean@univ.uz"}
    if not kafedra:
        kafedra = {"fish": "Sharipov Akram Rasulovich", "phone": "+998 71 200-33-33", "email": "head@univ.uz"}

    lines = [
        "📞 *Aloqa ma'lumotlari*",
        "",
        f"🎓 Guruh: `{group}`",
        "",
        f"👤 *Kurator*",
        f"  └ {kurator['fish']}",
        f"  └ 📱 {kurator['phone']}",
        f"  └ ✉️ {kurator['email']}",
        "",
        f"🏛 *Kafedra mudiri*",
        f"  └ {kafedra['fish']}",
        f"  └ 📱 {kafedra['phone']}",
        f"  └ ✉️ {kafedra['email']}",
        "",
        f"🎓 *Dekan*",
        f"  └ {dekan['fish']}",
        f"  └ 📱 {dekan['phone']}",
        f"  └ ✉️ {dekan['email']}",
        "",
        "_Shoshilinch holatda qo'ng'iroq qiling._",
    ]
    await message.answer("\n".join(lines), parse_mode="Markdown")


# ---------------------------------------------------------------------------
# /sozlamalar — til + xabarnoma sozlamalari (TZ 4.2.4)
# ---------------------------------------------------------------------------
@router.message(Command("sozlamalar"))
async def cmd_sozlamalar(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("🔒 Avval tizimga kiring: /login")
        return
    # /sozlamalar interaktiv panelni /notify_settings tarzida ko'rsatadi.
    from .data import cmd_notify_settings
    await cmd_notify_settings(message, token)


# ---------------------------------------------------------------------------
# /chiqish — sessiyani yopish (cmd_logout aliasi)
# ---------------------------------------------------------------------------
@router.message(Command("chiqish"))
async def cmd_chiqish(message: Message, state: FSMContext, token: str | None) -> None:
    await cmd_logout(message, state, token)
