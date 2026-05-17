"""AI Tutor — Claude/OpenAI API asosida talabaning shaxsiy yordamchisi.

Context-aware: talabaning baholarini, GPA, davomati va boshqa ma'lumotlarini
LLM ga kontekst sifatida beradi.

Use cases:
- "Mening eng kuchsiz fanim qaysi?"
- "Stipendiya olish uchun nima qilishim kerak?"
- "Algoritmlar fanidan o'qish uchun resurslar bering"

Provayder tanlash: ANTHROPIC_API_KEY yoki OPENAI_API_KEY env orqali.
"""
import os
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

SYSTEM_PROMPT = """Siz — universitet talabasi uchun AI yordamchi (Tutor) siz.
Talaba ismidan murojaat qiladigan, do'stona va aniq javob beradigan tutor sifatida ishlang.
Javoblarni O'zbek tilida bering (agar foydalanuvchi boshqa tilda yozsa, shu tilda).
Akademik nasihat berishda real ma'lumotga asoslaning (kontekstda berilgan)."""


def _get_student_context(db: Session, student_code: str) -> dict[str, Any]:
    """Talabaning to'liq akademik kontekstini olish."""
    summary = db.execute(
        text(
            """
            SELECT ds.full_name, ds.group_name,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
                   ROUND(AVG(f.attendance_percentage), 2) AS avg_attendance,
                   COUNT(*) AS grades_count,
                   COUNT(DISTINCT f.subject_key) AS subjects_count,
                   SUM(CASE WHEN f.is_passed THEN 0 ELSE 1 END) AS failed_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid
            GROUP BY ds.full_name, ds.group_name
            """
        ),
        {"sid": student_code},
    ).mappings().first()

    if not summary:
        return {}

    weak = db.execute(
        text(
            """
            SELECT s.subject_name, ROUND(AVG(f.grade_value), 2) AS avg_grade
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE ds.student_id = :sid
            GROUP BY s.subject_name
            ORDER BY AVG(f.grade_value) ASC
            LIMIT 3
            """
        ),
        {"sid": student_code},
    ).mappings().all()

    strong = db.execute(
        text(
            """
            SELECT s.subject_name, ROUND(AVG(f.grade_value), 2) AS avg_grade
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE ds.student_id = :sid
            GROUP BY s.subject_name
            ORDER BY AVG(f.grade_value) DESC
            LIMIT 3
            """
        ),
        {"sid": student_code},
    ).mappings().all()

    return {
        "name": summary["full_name"],
        "group": summary["group_name"],
        "avg_gpa": float(summary["avg_gpa"]) if summary["avg_gpa"] else 0,
        "avg_grade": float(summary["avg_grade"]) if summary["avg_grade"] else 0,
        "avg_attendance": float(summary["avg_attendance"]) if summary["avg_attendance"] else 0,
        "grades_count": int(summary["grades_count"]),
        "subjects_count": int(summary["subjects_count"]),
        "failed_count": int(summary["failed_count"]),
        "weak_subjects": [{"name": w["subject_name"], "avg": float(w["avg_grade"])} for w in weak],
        "strong_subjects": [{"name": s["subject_name"], "avg": float(s["avg_grade"])} for s in strong],
    }


def _build_context_message(ctx: dict) -> str:
    """Kontekst ma'lumotlarini matn ko'rinishida tayyorlash."""
    if not ctx:
        return "Talaba ma'lumotlari topilmadi."
    weak = "\n".join([f"  - {w['name']}: {w['avg']}" for w in ctx.get("weak_subjects", [])])
    strong = "\n".join([f"  - {s['name']}: {s['avg']}" for s in ctx.get("strong_subjects", [])])
    return f"""TALABA HAQIDA MA'LUMOT:
F.I.Sh.: {ctx['name']}
Guruh: {ctx['group']}
O'rtacha GPA: {ctx['avg_gpa']}
O'rtacha ball: {ctx['avg_grade']}
Davomat: {ctx['avg_attendance']}%
Jami baholar: {ctx['grades_count']}
Fanlar soni: {ctx['subjects_count']}
O'tmagan baholar: {ctx['failed_count']}

ENG KUCHSIZ FANLAR:
{weak}

ENG KUCHLI FANLAR:
{strong}
"""


def _provider() -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "demo"


def chat(db: Session, student_code: str, user_message: str, history: list[dict] | None = None) -> dict[str, Any]:
    """Talaba bilan AI chat — kontekst bilan boyitilgan.

    history: [{"role": "user|assistant", "content": "..."}, ...]
    """
    ctx = _get_student_context(db, student_code)
    context_msg = _build_context_message(ctx)

    provider = _provider()

    if provider == "demo":
        return {
            "response": _demo_response(user_message, ctx),
            "provider": "demo",
            "note": "AI Tutor demo rejimda ishlamoqda. Real AI uchun ANTHROPIC_API_KEY yoki OPENAI_API_KEY o'rnating.",
        }

    if provider == "anthropic":
        return _chat_anthropic(context_msg, user_message, history or [])
    return _chat_openai(context_msg, user_message, history or [])


def _chat_anthropic(context: str, user_message: str, history: list[dict]) -> dict[str, Any]:
    try:
        import anthropic
        client = anthropic.Anthropic()
        messages = list(history) + [{"role": "user", "content": user_message}]
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT + "\n\n" + context,
            messages=messages,
        )
        return {
            "response": resp.content[0].text,
            "provider": "anthropic",
            "model": resp.model,
            "usage": {"input": resp.usage.input_tokens, "output": resp.usage.output_tokens},
        }
    except Exception as e:
        logger.error("Anthropic AI Tutor error: {}", e)
        return {"response": f"AI xatolik: {e}", "provider": "anthropic", "error": True}


def _chat_openai(context: str, user_message: str, history: list[dict]) -> dict[str, Any]:
    try:
        from openai import OpenAI
        client = OpenAI()
        messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}] + list(history)
        messages.append({"role": "user", "content": user_message})
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1024,
        )
        return {
            "response": resp.choices[0].message.content,
            "provider": "openai",
            "model": resp.model,
            "usage": {"input": resp.usage.prompt_tokens, "output": resp.usage.completion_tokens},
        }
    except Exception as e:
        logger.error("OpenAI AI Tutor error: {}", e)
        return {"response": f"AI xatolik: {e}", "provider": "openai", "error": True}


def _demo_response(user_message: str, ctx: dict) -> str:
    """Demo rejimda javob (API key yo'q paytda)."""
    q = user_message.lower()
    if not ctx:
        return "Iltimos, hisobingizni bog'lang."

    name = ctx.get("name", "Talaba")

    if "kuchsiz" in q or "yomon" in q or "past" in q:
        weak = ctx.get("weak_subjects", [])
        if weak:
            return f"{name}, sizning eng kuchsiz fanlaringiz:\n" + "\n".join(
                [f"• {w['name']}: {w['avg']} ball" for w in weak]
            ) + "\n\nBu fanlarga qo'shimcha vaqt ajratishni tavsiya etaman."
        return "Hozircha kuchsiz fanlar yo'q!"

    if "kuchli" in q or "yaxshi" in q:
        strong = ctx.get("strong_subjects", [])
        if strong:
            return f"{name}, sizning eng kuchli fanlaringiz:\n" + "\n".join(
                [f"• {s['name']}: {s['avg']} ball" for s in strong]
            )
        return "Statistika hozircha yo'q."

    if "gpa" in q:
        gpa = ctx.get("avg_gpa", 0)
        msg = f"{name}, sizning GPA: *{gpa}*"
        if gpa >= 3.5:
            msg += "\n🌟 A'lo natija! Stipendiyaga tavsiya qilinasiz."
        elif gpa >= 3.0:
            msg += "\n👍 Yaxshi natija."
        elif gpa >= 2.5:
            msg += "\n📚 O'rta natija. Bir oz tirishish bilan oshirsa bo'ladi."
        else:
            msg += "\n⚠️ Past — akademik xavf zonasida. Dekanat bilan bog'laning."
        return msg

    if "stipendiya" in q:
        gpa = ctx.get("avg_gpa", 0)
        if gpa >= 3.5:
            return "Stipendiya olishingiz uchun: GPA yetarli (3.5+), qarz fanlar yo'qligini ko'rsating."
        return f"Stipendiya uchun GPA 3.0+ kerak. Hozir: {gpa}. {3.0 - gpa:.2f} oshirsangiz oddiy stipendiya olasiz."

    if "davomat" in q:
        att = ctx.get("avg_attendance", 0)
        return f"Davomat: {att}%. " + ("Yaxshi!" if att >= 80 else "Yaxshilash kerak (min 80%).")

    return (f"{name}, savolingizni tushundim, lekin hozir to'liq javob bera olmayman.\n\n"
            "Quyidagi savollar bilan murojaat qiling:\n"
            "• \"Mening eng kuchsiz fanim qaysi?\"\n"
            "• \"GPA ni qanday oshiraman?\"\n"
            "• \"Stipendiya uchun nima kerak?\"\n"
            "• \"Davomatim qancha?\"")
