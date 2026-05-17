"""Telegram bot integratsiyasi.

Ishlatish:
1. @BotFather dan token oling, .env ga `TELEGRAM_BOT_TOKEN` qo'ying
2. Talaba botga /link <STUDENT_ID> yuborib o'z hisobini bog'laydi
3. Bundan keyin: /balls, /gpa, /jadval, /ogohlantirishlar buyruqlari ishlaydi
4. Backend periodik ravishda yangi xabarlarni botga jo'natadi

Ishga tushirish (alohida process):
    py -m app.services.telegram_bot
"""
import asyncio
import json
import os
from typing import Any

import httpx
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import OLTPSession, OLAPSession
from app.models.oltp.student import Student
from app.models.oltp.user import User


TG_API = "https://api.telegram.org/bot{token}/{method}"


def _token() -> str | None:
    return os.environ.get("TELEGRAM_BOT_TOKEN") or getattr(settings, "telegram_bot_token", None)


# Linking storage — student_id -> telegram_chat_id (oddiy DB sifatida file)
LINK_FILE = "telegram_links.json"


def _load_links() -> dict[str, int]:
    if not os.path.exists(LINK_FILE):
        return {}
    try:
        with open(LINK_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_links(links: dict[str, int]) -> None:
    with open(LINK_FILE, "w") as f:
        json.dump(links, f)


async def send_message(chat_id: int, text_msg: str, parse_mode: str = "Markdown") -> bool:
    """Telegram orqali xabar yuborish."""
    token = _token()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
        return False
    url = TG_API.format(token=token, method="sendMessage")
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, json={
                "chat_id": chat_id,
                "text": text_msg,
                "parse_mode": parse_mode,
            })
            return r.status_code == 200
        except Exception as e:
            logger.error("TG send error: {}", e)
            return False


def get_student_summary(student_id: str) -> str:
    """Talabaning umumiy holatini matn ko'rinishida tayyorlash."""
    oltp = OLTPSession()
    olap = OLAPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return "❌ Talaba topilmadi"

        stats = olap.execute(
            text(
                """
                SELECT ROUND(AVG(grade_value), 2) AS avg_grade,
                       ROUND(AVG(gpa_points), 3) AS avg_gpa,
                       COUNT(*) AS grades_count
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                WHERE ds.student_id = :sid
                """
            ),
            {"sid": student_id},
        ).mappings().first() or {}

        return (
            f"👤 *{student.full_name}*\n"
            f"📋 ID: `{student.student_id}`\n"
            f"🎓 Guruh: {student.group.name if student.group else '-'}\n"
            f"📊 GPA: *{stats.get('avg_gpa') or '-'}*\n"
            f"📝 O'rtacha ball: {stats.get('avg_grade') or '-'}\n"
            f"📚 Jami baholar: {stats.get('grades_count') or 0}"
        )
    finally:
        oltp.close()
        olap.close()


def get_student_grades(student_id: str, limit: int = 10) -> str:
    """So'nggi baholarni ko'rsatish."""
    olap = OLAPSession()
    try:
        rows = olap.execute(
            text(
                """
                SELECT s.subject_name, f.grade_value, t.academic_year, t.semester
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                JOIN dim_subject s ON f.subject_key = s.subject_key
                JOIN dim_time t ON f.time_key = t.time_key
                WHERE ds.student_id = :sid
                ORDER BY t.full_date DESC
                LIMIT :lim
                """
            ),
            {"sid": student_id, "lim": limit},
        ).mappings().all()
        if not rows:
            return "Baholar yo'q"
        lines = ["📝 *So'nggi baholar:*\n"]
        for r in rows:
            emoji = "🟢" if r["grade_value"] >= 85 else "🔵" if r["grade_value"] >= 70 else "🟡" if r["grade_value"] >= 55 else "🔴"
            lines.append(f"{emoji} *{r['subject_name']}*: {r['grade_value']} ({r['academic_year']} {r['semester']})")
        return "\n".join(lines)
    finally:
        olap.close()


async def handle_update(update: dict) -> None:
    """Bitta Telegram update ni qayta ishlash."""
    msg = update.get("message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    text_in = (msg.get("text") or "").strip()
    links = _load_links()

    if text_in.startswith("/start"):
        await send_message(
            chat_id,
            "👋 *Student Rating OLAP* botiga xush kelibsiz!\n\n"
            "Hisobingizni bog'lash uchun:\n"
            "`/link STUDENT_ID`\n\n"
            "Misol: `/link ST202500001`\n\n"
            "Bog'langandan keyin:\n"
            "/balls — so'nggi baholaringiz\n"
            "/gpa — GPA va statistika\n"
            "/help — yordam",
        )
        return

    if text_in.startswith("/link"):
        parts = text_in.split(maxsplit=1)
        if len(parts) < 2:
            await send_message(chat_id, "Format: `/link STUDENT_ID`")
            return
        sid = parts[1].strip()
        # Tekshirish
        oltp = OLTPSession()
        try:
            student = oltp.query(Student).filter(Student.student_id == sid).first()
            if not student:
                await send_message(chat_id, f"❌ Bunday talaba topilmadi: `{sid}`")
                return
            links[str(chat_id)] = sid
            _save_links(links)
            await send_message(chat_id, f"✅ Hisob bog'landi: *{student.full_name}*\n\n/help — buyruqlar ro'yxati")
        finally:
            oltp.close()
        return

    if text_in.startswith("/help"):
        await send_message(
            chat_id,
            "*📚 Asosiy buyruqlar:*\n"
            "/balls — so'nggi baholar\n"
            "/gpa — GPA va umumiy statistika\n"
            "/jadval — bu hafta jadval\n"
            "/imtihon — yaqin imtihonlar\n"
            "/tolovlar — to'lov holati\n"
            "/elonlar — so'nggi e'lonlar\n"
            "/kutubxona — ijara olgan kitoblarim\n"
            "/yotoqxona — yotoqxona ma'lumoti\n"
            "/profil — shaxsiy ma'lumot\n"
            "/tavsiya — AI fan tavsiyalari\n"
            "\n*Boshqaruv:*\n"
            "/link ID — hisobni qayta bog'lash\n"
            "/unlink — hisobni o'chirish",
        )
        return

    if text_in.startswith("/unlink"):
        if str(chat_id) in links:
            del links[str(chat_id)]
            _save_links(links)
            await send_message(chat_id, "Hisob o'chirildi")
        return

    sid = links.get(str(chat_id))
    if not sid:
        await send_message(chat_id, "Avval hisobingizni bog'lang: `/link STUDENT_ID`")
        return

    if text_in.startswith("/gpa"):
        await send_message(chat_id, get_student_summary(sid))
        return

    if text_in.startswith("/balls"):
        await send_message(chat_id, get_student_grades(sid))
        return

    if text_in.startswith("/jadval"):
        await send_message(chat_id, get_student_schedule(sid))
        return

    if text_in.startswith("/imtihon"):
        await send_message(chat_id, get_student_exams(sid))
        return

    if text_in.startswith("/tolovlar"):
        await send_message(chat_id, get_student_payments(sid))
        return

    if text_in.startswith("/elonlar") or text_in.startswith("/e'lonlar"):
        await send_message(chat_id, get_latest_announcements())
        return

    if text_in.startswith("/kutubxona"):
        await send_message(chat_id, get_student_library(sid))
        return

    if text_in.startswith("/yotoqxona"):
        await send_message(chat_id, get_student_dormitory(sid))
        return

    if text_in.startswith("/profil"):
        await send_message(chat_id, get_student_profile(sid))
        return

    if text_in.startswith("/tavsiya"):
        await send_message(chat_id, get_student_recommendations(sid))
        return

    await send_message(chat_id, "Noma'lum buyruq. /help ni bosing")


# ============================================================
# QO'SHIMCHA HANDLER LAR
# ============================================================


def get_student_schedule(student_id: str) -> str:
    """Hozirgi haftalik jadval."""
    from app.models.oltp.schedule import ScheduleEntry
    from app.models.oltp.subject import Subject as Subj

    oltp = OLTPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student or not student.group_id:
            return "Jadval topilmadi"

        entries = (
            oltp.query(ScheduleEntry)
            .filter(ScheduleEntry.group_id == student.group_id, ScheduleEntry.is_active == True)  # noqa: E712
            .order_by(ScheduleEntry.weekday, ScheduleEntry.start_time)
            .limit(20)
            .all()
        )
        if not entries:
            return "📅 Hozircha jadval kiritilmagan"

        days = ["", "Dush", "Sesh", "Chor", "Pay", "Juma", "Shan", "Yak"]
        lines = ["📅 *Haftalik jadval:*\n"]
        current_day = None
        for e in entries:
            if e.weekday != current_day:
                current_day = e.weekday
                lines.append(f"\n*{days[e.weekday]}:*")
            subj = oltp.query(Subj).filter(Subj.id == e.subject_id).first()
            lines.append(
                f"  {e.start_time.strftime('%H:%M')} — {subj.name if subj else '?'} ({e.room or '-'})"
            )
        return "\n".join(lines)
    finally:
        oltp.close()


def get_student_exams(student_id: str) -> str:
    """Yaqin imtihonlar."""
    from datetime import date
    from app.models.oltp.hemis import ExamSchedule
    from app.models.oltp.subject import Subject as Subj

    oltp = OLTPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student or not student.group_id:
            return "Imtihon ma'lumotlari yo'q"
        exams = (
            oltp.query(ExamSchedule)
            .filter(ExamSchedule.group_id == student.group_id, ExamSchedule.exam_date >= date.today())
            .order_by(ExamSchedule.exam_date)
            .limit(10)
            .all()
        )
        if not exams:
            return "📝 Yaqin imtihonlar yo'q"
        lines = ["📝 *Yaqin imtihonlar:*\n"]
        for e in exams:
            subj = oltp.query(Subj).filter(Subj.id == e.subject_id).first()
            lines.append(
                f"*{e.exam_date.strftime('%d.%m')}* {e.start_time.strftime('%H:%M')} — {subj.name if subj else '?'} ({e.room or '-'})"
            )
        return "\n".join(lines)
    finally:
        oltp.close()


def get_student_payments(student_id: str) -> str:
    """To'lov holati."""
    from app.models.oltp.hemis import Payment, PaymentStatus

    oltp = OLTPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return "Topilmadi"
        payments = oltp.query(Payment).filter(Payment.student_id == student.id).order_by(Payment.due_date.desc()).all()
        if not payments:
            return "💰 To'lov yozuvlari yo'q"
        total_due = sum(float(p.amount) - float(p.paid_amount) for p in payments if p.status != PaymentStatus.PAID)
        lines = [f"💰 *To'lov holati:*\n\nJami qarz: *{total_due:,.0f}* so'm\n"]
        for p in payments[:5]:
            remaining = float(p.amount) - float(p.paid_amount)
            emoji = "✅" if p.status == PaymentStatus.PAID else "🟡"
            lines.append(f"{emoji} {p.academic_year}: {remaining:,.0f} so'm ({p.status.value})")
        return "\n".join(lines)
    finally:
        oltp.close()


def get_latest_announcements() -> str:
    """So'nggi e'lonlar."""
    from app.models.oltp.hemis import Announcement

    oltp = OLTPSession()
    try:
        anns = oltp.query(Announcement).order_by(Announcement.published_at.desc()).limit(5).all()
        if not anns:
            return "📢 E'lonlar yo'q"
        lines = ["📢 *So'nggi e'lonlar:*\n"]
        for a in anns:
            emoji = "🚨" if a.priority.value == "urgent" else "⚠️" if a.priority.value == "high" else "📌"
            lines.append(f"\n{emoji} *{a.title}*\n_{a.body[:100]}_")
        return "\n".join(lines)
    finally:
        oltp.close()


def get_student_library(student_id: str) -> str:
    """Ijara olgan kitoblar."""
    from app.models.oltp.hemis import Book, BookLoan, BookLoanStatus

    oltp = OLTPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return "Topilmadi"
        loans = (
            oltp.query(BookLoan)
            .filter(BookLoan.student_id == student.id, BookLoan.status == BookLoanStatus.ACTIVE)
            .all()
        )
        if not loans:
            return "📚 Ijaraga olingan kitoblar yo'q"
        lines = ["📚 *Mening kitoblarim:*\n"]
        for l in loans:
            book = oltp.query(Book).filter(Book.id == l.book_id).first()
            lines.append(f"📖 {book.title if book else '?'}\n  Qaytarish: *{l.due_date}*")
        return "\n".join(lines)
    finally:
        oltp.close()


def get_student_dormitory(student_id: str) -> str:
    """Yotoqxona ma'lumoti."""
    from app.models.oltp.hemis import DormitoryAssignment, DormitoryBuilding, DormitoryRoom

    oltp = OLTPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return "Topilmadi"
        a = (
            oltp.query(DormitoryAssignment)
            .filter(DormitoryAssignment.student_id == student.id, DormitoryAssignment.is_active == True)  # noqa: E712
            .first()
        )
        if not a:
            return "🏠 Yotoqxonaga biriktirilmagansiz"
        room = oltp.query(DormitoryRoom).filter(DormitoryRoom.id == a.room_id).first()
        building = oltp.query(DormitoryBuilding).filter(DormitoryBuilding.id == room.building_id).first() if room else None
        return (
            f"🏠 *Yotoqxona:*\n\n"
            f"Bino: *{building.name if building else '?'}*\n"
            f"Xona: *{room.room_number if room else '?'}*\n"
            f"Qavat: {room.floor if room else '-'}\n"
            f"Oylik to'lov: *{float(room.monthly_fee) if room else 0:,.0f}* so'm"
        )
    finally:
        oltp.close()


def get_student_profile(student_id: str) -> str:
    """Shaxsiy ma'lumot."""
    oltp = OLTPSession()
    try:
        student = oltp.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return "Topilmadi"
        return (
            f"👤 *Profil:*\n\n"
            f"F.I.Sh.: *{student.full_name}*\n"
            f"ID: `{student.student_id}`\n"
            f"Guruh: {student.group.name if student.group else '-'}\n"
            f"Kurs: {student.group.course if student.group else '-'}\n"
            f"Yo'nalish: {student.group.specialty.name if student.group else '-'}\n"
            f"Status: {student.status.value}\n"
            f"Kirgan yili: {student.enrollment_year}"
        )
    finally:
        oltp.close()


def get_student_recommendations(student_id: str) -> str:
    """AI fan tavsiyalari."""
    olap = OLAPSession()
    try:
        rows = olap.execute(
            text(
                """
                SELECT s.subject_name, ROUND(AVG(f.grade_value), 2) AS avg_grade
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                JOIN dim_subject s ON f.subject_key = s.subject_key
                WHERE ds.student_id = :sid
                GROUP BY s.subject_name
                HAVING AVG(f.grade_value) < 70
                ORDER BY AVG(f.grade_value) ASC
                LIMIT 3
                """
            ),
            {"sid": student_id},
        ).mappings().all()
        if not rows:
            return "🌟 Tabriklaymiz! Barcha fanlarda yaxshi natijalar"
        lines = ["🤖 *AI tavsiyalari:*\n\nE'tibor talab qiluvchi fanlar:"]
        for r in rows:
            lines.append(f"⚠️ *{r['subject_name']}* — ball: {r['avg_grade']}")
        lines.append("\n💡 Repititor olish yoki kafedraga murojaat qiling")
        return "\n".join(lines)
    finally:
        olap.close()


async def poll_loop() -> None:
    """Long-polling bilan Telegram dan update larni olish."""
    token = _token()
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN sozlanmagan — bot ishga tushmaydi")
        return

    offset = 0
    logger.info("Telegram bot ishga tushdi")
    async with httpx.AsyncClient(timeout=35) as client:
        while True:
            try:
                url = TG_API.format(token=token, method="getUpdates")
                r = await client.get(url, params={"offset": offset, "timeout": 30})
                data = r.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    asyncio.create_task(handle_update(update))
            except Exception as e:
                logger.error("Poll error: {}", e)
                await asyncio.sleep(5)


def get_chat_id_for_student(student_id: str) -> int | None:
    """Student id bo'yicha Telegram chat id ni topish (notification yuborish uchun)."""
    links = _load_links()
    for chat_id, linked_sid in links.items():
        if linked_sid == student_id:
            return int(chat_id)
    return None


async def send_grade_notification(student_id: str, subject: str, grade: float) -> bool:
    """Telegram orqali baho bildirgisi."""
    chat_id = get_chat_id_for_student(student_id)
    if not chat_id:
        return False
    emoji = "🟢" if grade >= 85 else "🔵" if grade >= 70 else "🟡" if grade >= 55 else "🔴"
    return await send_message(
        chat_id,
        f"{emoji} *Yangi baho*\n\n*Fan:* {subject}\n*Ball:* {grade}",
    )


if __name__ == "__main__":
    asyncio.run(poll_loop())
