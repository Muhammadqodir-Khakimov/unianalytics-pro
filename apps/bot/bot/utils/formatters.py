"""Telegram matn formatterlari.

MarkdownV2 talab qilgan belgilarni escape qilamiz va GPA/ball uchun emojilar.
"""
from __future__ import annotations

_MD_ESCAPE = r"_*[]()~`>#+-=|{}.!"


def md_escape(text: str | None) -> str:
    """MarkdownV2 uchun maxsus belgilarni escape qiladi."""
    if text is None:
        return ""
    out = []
    for ch in str(text):
        if ch in _MD_ESCAPE:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def grade_emoji(value: float | None) -> str:
    """Ball uchun rang emoji."""
    if value is None:
        return "⚪"
    if value >= 85:
        return "🟢"
    if value >= 70:
        return "🔵"
    if value >= 55:
        return "🟡"
    return "🔴"


def fmt_role(role: str) -> str:
    return {
        "admin": "Admin",
        "rector": "Rektor",
        "dean": "Dekan",
        "teacher": "O'qituvchi",
        "student": "Talaba",
    }.get(role, role.title())


def fmt_weekday(n: int) -> str:
    days = [
        "", "Dushanba", "Seshanba", "Chorshanba",
        "Payshanba", "Juma", "Shanba", "Yakshanba",
    ]
    return days[n] if 1 <= n <= 7 else f"Kun {n}"
