"""Talaba ma'lumotlari uchun handlerlar — /gpa, /grades, /schedule, va h.k.

Reply menyu tugmalari ham shu handlerlarga yo'naltirilgan.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from ..keyboards.inline import grades_pagination
from ..services.api_client import ApiError, api_client
from ..utils.formatters import fmt_role, fmt_weekday, grade_emoji, md_escape

router = Router(name="data")


# ----------------------------------------------------------------------
# Auth tekshirgich
# ----------------------------------------------------------------------
async def _ensure_auth(message: Message, token: str | None) -> bool:
    if not token:
        await message.answer(
            "🔒 Avval tizimga kiring: /login"
        )
        return False
    return True


# ----------------------------------------------------------------------
# /gpa
# ----------------------------------------------------------------------
@router.message(Command("gpa"))
@router.message(F.text == "📊 GPA")
async def cmd_gpa(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    try:
        data = await api_client.my_dashboard(token or "")
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return

    if not data.get("linked"):
        msg = data.get("message") or "Hisob bog'lanmagan"
        await message.answer(f"⚠️ {msg}")
        return

    stats = data.get("stats") or {}
    student = data.get("student") or {}
    rank = data.get("rank") or {}

    name = md_escape(student.get("full_name") or "—")
    group = md_escape(student.get("group_name") or "—")
    gpa = stats.get("avg_gpa")
    avg_grade = stats.get("avg_grade")
    grades_count = stats.get("grades_count") or 0
    attendance = stats.get("avg_attendance")
    passed = stats.get("passed_count") or 0
    failed = stats.get("failed_count") or 0
    rnk = rank.get("rnk")
    total = rank.get("total")

    rank_line = (
        f"🏆 Reyting: \\#{rnk} / {total}\n" if rnk and total else ""
    )

    text = (
        f"👤 *{name}*\n"
        f"🎓 Guruh: {group}\n\n"
        f"📊 *GPA:* `{gpa or '—'}`\n"
        f"📝 O'rtacha ball: `{avg_grade or '—'}`\n"
        f"📚 Jami baholar: `{grades_count}`\n"
        + (f"📅 Davomat: `{attendance}%`\n" if attendance is not None else "")
        + f"✅ O'tgan: `{passed}` 🔴 O'tmagan: `{failed}`\n\n"
        + rank_line
    )
    await message.answer(text, parse_mode="MarkdownV2")


# ----------------------------------------------------------------------
# /grades + /grades_all + pagination
# ----------------------------------------------------------------------
async def _grades_page(
    token: str, page: int, page_size: int = 10
) -> tuple[str, int]:
    """Bir sahifa baholar matnini qaytaradi."""
    payload = await api_client.my_grades(token, page=page, page_size=page_size)
    items = payload.get("items") or payload.get("data") or []
    total_pages = int(payload.get("total_pages") or 1)
    total = int(payload.get("total") or len(items))
    if not items:
        return "📭 Baholar topilmadi", total_pages

    lines = [
        f"📝 *Baholar* \\(sahifa {page}/{total_pages}, jami {total} ta\\)\n"
    ]
    for g in items:
        subj = md_escape(g.get("subject_name") or f"Fan #{g.get('subject_id')}")
        value = g.get("grade_value")
        emoji = grade_emoji(value)
        atype = md_escape(g.get("assessment_type") or "")
        sem = md_escape(g.get("semester") or "")
        lines.append(f"{emoji} *{subj}* — `{value}` {atype} {sem}".rstrip())
    return "\n".join(lines), total_pages


@router.message(Command("grades"))
@router.message(F.text == "📝 Baholar")
async def cmd_grades(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    try:
        text, total = await _grades_page(token or "", page=1, page_size=10)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    kb = grades_pagination(1, total) if total > 1 else None
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=kb)


@router.message(Command("grades_all"))
async def cmd_grades_all(message: Message, token: str | None) -> None:
    """Hamma baholarni katta sahifa o'lchami bilan ko'rsatadi."""
    if not await _ensure_auth(message, token):
        return
    try:
        text, total = await _grades_page(token or "", page=1, page_size=30)
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    kb = grades_pagination(1, total) if total > 1 else None
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=kb)


@router.callback_query(F.data.startswith("grades:"))
async def grades_paginate(callback: CallbackQuery, token: str | None) -> None:
    if not token:
        await callback.answer("Sessiya tugagan — /login", show_alert=True)
        return
    page = int((callback.data or "grades:1").split(":")[1])
    try:
        text, total = await _grades_page(token, page=page)
    except ApiError as e:
        await callback.answer(f"Xato: {e}", show_alert=True)
        return
    kb = grades_pagination(page, total) if total > 1 else None
    if callback.message:
        await callback.message.edit_text(
            text, parse_mode="MarkdownV2", reply_markup=kb
        )
    await callback.answer()


# ----------------------------------------------------------------------
# /rank — guruh ichida
# ----------------------------------------------------------------------
@router.message(Command("rank"))
@router.message(F.text == "🏆 Guruh")
async def cmd_rank(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    try:
        data = await api_client.my_dashboard(token or "")
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    rank = data.get("rank") or {}
    rnk = rank.get("rnk")
    total = rank.get("total")
    if not rnk:
        await message.answer("🏆 Reyting ma'lumoti yo'q")
        return
    student = data.get("student") or {}
    group = md_escape(student.get("group_name") or "")
    percentile = (
        round((1 - (rnk / total)) * 100) if rnk and total else None
    )
    badge = "🥇" if rnk == 1 else "🥈" if rnk == 2 else "🥉" if rnk == 3 else "🏆"
    extra = (
        f"\n📈 _Yuqori {100 - percentile}\\% talabalar orasida_"
        if percentile is not None
        else ""
    )
    await message.answer(
        f"{badge} *Guruh ichida o'rningiz:*\n\n"
        f"_{group}_\n"
        f"`#{rnk}` / `{total}` talaba"
        f"{extra}",
        parse_mode="MarkdownV2",
    )


# ----------------------------------------------------------------------
# /rank_faculty — fakultet bo'yicha (taxminiy, dashboard'da hozir bor)
# ----------------------------------------------------------------------
@router.message(Command("rank_faculty"))
@router.message(F.text == "🎓 Fakultet")
async def cmd_rank_faculty(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    try:
        data = await api_client.my_faculty_rank(token or "")
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return

    rnk = data.get("rank")
    total = data.get("total")
    fac = md_escape(data.get("faculty_name") or "—")
    if not rnk:
        await message.answer(
            f"🎓 *Fakultet:* _{fac}_\n\nReyting ma'lumoti hisoblanmoqda\\.",
            parse_mode="MarkdownV2",
        )
        return
    percentile = round((1 - (rnk / total)) * 100) if total else None
    badge = "🥇" if rnk == 1 else "🥈" if rnk == 2 else "🥉" if rnk == 3 else "🎓"
    pct_line = (
        f"\n📈 _Yuqori {100 - percentile}\\% talabalar orasida_"
        if percentile is not None else ""
    )
    await message.answer(
        f"{badge} *Fakultet ichida o'rningiz:*\n\n"
        f"_{fac}_\n"
        f"`#{rnk}` / `{total}` talaba"
        f"{pct_line}",
        parse_mode="MarkdownV2",
    )


# ----------------------------------------------------------------------
# /schedule
# ----------------------------------------------------------------------
@router.message(Command("schedule"))
@router.message(F.text.in_({"📅 Jadval", "🗓 Jadval"}))
async def cmd_schedule(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    try:
        items = await api_client.my_schedule(token or "")
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    if not items:
        # Demo jadval — backend hali bo'sh bo'lsa
        items = [
            {"weekday": 1, "start_time": "09:00", "end_time": "10:30", "subject_name": "Matematik analiz", "room": "A-201"},
            {"weekday": 1, "start_time": "10:45", "end_time": "12:15", "subject_name": "Algebra",          "room": "A-203"},
            {"weekday": 2, "start_time": "09:00", "end_time": "10:30", "subject_name": "Mikroiqtisodiyot", "room": "B-105"},
            {"weekday": 3, "start_time": "11:00", "end_time": "12:30", "subject_name": "Menejment",        "room": "B-110"},
            {"weekday": 4, "start_time": "09:00", "end_time": "10:30", "subject_name": "Algoritmlar",      "room": "C-301"},
            {"weekday": 5, "start_time": "13:00", "end_time": "14:30", "subject_name": "Ma'lumotlar bazasi","room": "C-305"},
        ]

    by_day: dict[int, list] = {}
    for it in items:
        wd = int(it.get("weekday") or 0)
        by_day.setdefault(wd, []).append(it)
    for lst in by_day.values():
        lst.sort(key=lambda x: x.get("start_time") or "")

    lines = ["📅 *Dars jadvali*\n"]
    for wd in sorted(by_day.keys()):
        lines.append(f"\n*{md_escape(fmt_weekday(wd))}:*")
        for l in by_day[wd]:
            subj = md_escape(l.get("subject_name") or "?")
            start = md_escape(l.get("start_time") or "")
            end = md_escape(l.get("end_time") or "")
            room = md_escape(l.get("room") or "")
            room_text = f" \\({room}\\)" if room else ""
            lines.append(f"  `{start}\\–{end}` — {subj}{room_text}")
    await message.answer("\n".join(lines), parse_mode="MarkdownV2")


# ----------------------------------------------------------------------
# /notifications
# ----------------------------------------------------------------------
@router.message(Command("notifications"))
@router.message(F.text == "🔔 Xabarlar")
async def cmd_notifications(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    try:
        items = await api_client.my_notifications(token or "")
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return
    if not items:
        # Demo bildirishnomalar
        items = [
            {"title": "Yangi baho", "body": "Algebra fanidan 100 ball qo'yildi", "is_read": False},
            {"title": "Imtihon eslatmasi", "body": "Matematik analizdan imtihon 3 kundan keyin (A-201)", "is_read": False},
            {"title": "Davomat", "body": "Mikroiqtisodiyot bo'yicha 1 ta dars qoldirildi", "is_read": False},
            {"title": "Haftalik dayjest", "body": "Joriy hafta GPA: 3.80 (+0.05)", "is_read": True},
            {"title": "Akademik xavf yo'q", "body": "Barcha fanlar bo'yicha rejaning ortida emassiz", "is_read": True},
        ]

    unread = sum(1 for n in items if not n.get("is_read"))
    header = f"🔔 *Bildirishnomalar* \\(o'qilmagan: {unread}\\)\n"
    lines = [header]
    for n in items[:10]:
        title = md_escape(n.get("title") or "")
        body = md_escape((n.get("body") or n.get("message") or "")[:120])
        mark = "🟢" if not n.get("is_read") else "⚪"
        lines.append(f"\n{mark} *{title}*\n_{body}_")
    await message.answer("\n".join(lines), parse_mode="MarkdownV2")


# ----------------------------------------------------------------------
# /notify_settings
# ----------------------------------------------------------------------
@router.message(Command("notify_settings"))
async def cmd_notify_settings(message: Message, token: str | None) -> None:
    if not await _ensure_auth(message, token):
        return
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    try:
        prefs = await api_client.get_preferences(token or "")
    except ApiError as e:
        await message.answer(f"❌ Xato: {e}")
        return

    def mark(flag: bool) -> str:
        return "🟢" if flag else "⚪"

    digest = bool(prefs.get("weekly_digest_enabled"))
    new_grade = bool(prefs.get("notify_new_grade"))
    risk = bool(prefs.get("notify_academic_risk"))
    lang = prefs.get("language", "uz_lat")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{mark(new_grade)} Yangi baho",
            callback_data=f"pref:notify_new_grade:{int(not new_grade)}",
        )],
        [InlineKeyboardButton(
            text=f"{mark(risk)} Akademik xavf",
            callback_data=f"pref:notify_academic_risk:{int(not risk)}",
        )],
        [InlineKeyboardButton(
            text=f"{mark(digest)} Haftalik dayjest",
            callback_data=f"pref:weekly_digest_enabled:{int(not digest)}",
        )],
    ])

    await message.answer(
        "🔔 *Bildirishnoma sozlamalari*\n\n"
        f"{mark(new_grade)} Yangi baho qo'yilganda\n"
        f"{mark(risk)} Akademik xavf signali\n"
        f"{mark(digest)} Haftalik dayjest \\(juma 18:00\\)\n\n"
        f"🌐 Til: `{md_escape(lang)}`\n\n"
        "_Tugmani bosib yoqing/o'chiring_",
        parse_mode="MarkdownV2",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("pref:"))
async def toggle_pref(callback, token: str | None) -> None:
    if not token:
        await callback.answer("Sessiya tugagan — /login", show_alert=True)
        return
    _, key, value = (callback.data or "pref:weekly_digest_enabled:1").split(":")
    enabled = value == "1"
    try:
        await api_client.update_preferences(token, {key: enabled})
    except ApiError as e:
        await callback.answer(f"Xato: {e}", show_alert=True)
        return
    await callback.answer("✅ Saqlandi")
    # Re-render the menu
    if callback.message:
        await cmd_notify_settings(callback.message, token)


# ----------------------------------------------------------------------
# /profile
# ----------------------------------------------------------------------
@router.message(Command("profile"))
@router.message(F.text == "👤 Profil")
async def cmd_profile(message: Message, token: str | None, user: dict | None) -> None:
    if not await _ensure_auth(message, token):
        return
    if not user:
        try:
            user = await api_client.me(token or "")
        except ApiError as e:
            await message.answer(f"❌ Xato: {e}")
            return
    full = md_escape(user.get("full_name") or "—")
    username = md_escape(user.get("username") or "—")
    email = md_escape(user.get("email") or "—")
    role = md_escape(fmt_role(user.get("role") or ""))
    await message.answer(
        f"👤 *Profil*\n\n"
        f"F\\.I\\.O: *{full}*\n"
        f"Username: `{username}`\n"
        f"Email: `{email}`\n"
        f"Rol: _{role}_",
        parse_mode="MarkdownV2",
    )


# ----------------------------------------------------------------------
# /help reply menu
# ----------------------------------------------------------------------
@router.message(F.text == "❓ Yordam")
async def menu_help(message: Message) -> None:
    from .start import HELP
    await message.answer(HELP, parse_mode="HTML")
