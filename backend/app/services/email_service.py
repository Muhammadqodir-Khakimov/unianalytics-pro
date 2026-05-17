"""Email yuborish — SMTP yoki Resend API.

Konfiguratsiya (.env):
    # Resend (tavsiya — bepul 100 email/kun)
    RESEND_API_KEY=re_...
    EMAIL_FROM=noreply@unianalytics.uz

    # Yoki SMTP
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=...
    SMTP_PASSWORD=...
    SMTP_USE_TLS=true

Foydalanish:
    from app.services.email_service import send_email, send_template
    send_email("user@univ.uz", "Salom", "<h1>Xush kelibsiz</h1>")
    send_template("user@univ.uz", "verify_email", {"name": "Ali", "code": "1234"})
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import httpx
from loguru import logger


def send_email(to: str | list[str], subject: str, html: str, text: str | None = None) -> bool:
    """Email yuborish. Resend bo'lsa — Resend, aks holda SMTP. False qaytarsa — yuborilmadi."""
    recipients = [to] if isinstance(to, str) else to

    if os.environ.get("RESEND_API_KEY"):
        return _send_via_resend(recipients, subject, html, text)
    if os.environ.get("SMTP_HOST"):
        return _send_via_smtp(recipients, subject, html, text)

    logger.warning("Email service sozlanmagan — {} ga yuborilmadi: {}", recipients, subject)
    return False


def _send_via_resend(to: list[str], subject: str, html: str, text: str | None) -> bool:
    try:
        r = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "from": os.environ.get("EMAIL_FROM", "noreply@unianalytics.uz"),
                "to": to,
                "subject": subject,
                "html": html,
                **({"text": text} if text else {}),
            },
            timeout=10,
        )
        r.raise_for_status()
        logger.info("Email yuborildi (Resend): {} → {}", subject, to)
        return True
    except Exception as e:
        logger.error("Resend xato: {}", e)
        return False


def _send_via_smtp(to: list[str], subject: str, html: str, text: str | None) -> bool:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = os.environ.get("EMAIL_FROM", user)
    msg["To"] = ", ".join(to)

    if text:
        msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            if use_tls:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
        logger.info("Email yuborildi (SMTP): {} → {}", subject, to)
        return True
    except Exception as e:
        logger.error("SMTP xato: {}", e)
        return False


# ============================================================
# Templates
# ============================================================

TEMPLATES = {
    "verify_email": {
        "subject": "Email manzilingizni tasdiqlang",
        "html": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px;">
                <h2>Salom, {name}!</h2>
                <p>UniAnalytics PRO ga xush kelibsiz. Email manzilingizni tasdiqlash uchun:</p>
                <p style="text-align: center; margin: 24px 0;">
                    <a href="{verify_url}" style="background: #1677ff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                        Tasdiqlash
                    </a>
                </p>
                <p>Yoki kod: <b>{code}</b></p>
                <hr/>
                <small style="color: #888">Agar siz ro'yxatdan o'tmagan bo'lsangiz, bu emailni e'tiborsiz qoldiring.</small>
            </div>
        """,
    },
    "password_reset": {
        "subject": "Parolni tiklash",
        "html": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px;">
                <h2>Parol tiklash</h2>
                <p>Salom {name}, parolni tiklash uchun:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <small>Havola 1 soatdan keyin amal qilmaydi.</small>
            </div>
        """,
    },
    "weekly_report": {
        "subject": "Haftalik hisobot — {week}",
        "html": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px;">
                <h2>Haftalik hisobot</h2>
                <p>Salom {name}, sizning fakultet bo'yicha haftalik xulosa:</p>
                <ul>
                    <li>Jami baholar: <b>{total_grades}</b></li>
                    <li>O'rtacha GPA: <b>{avg_gpa}</b></li>
                    <li>Xavfli talabalar: <b>{at_risk}</b></li>
                </ul>
                <p><a href="{dashboard_url}">To'liq hisobotni ko'rish →</a></p>
            </div>
        """,
    },
    "trial_expiring": {
        "subject": "Trial muddati 3 kun ichida tugaydi",
        "html": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px;">
                <h2>Trial muddati tugamoqda</h2>
                <p>Salom {name}, sizning bepul sinov muddati {expires_at} sanasida tugaydi.</p>
                <p>Davom etish uchun PRO yoki Enterprise planni tanlang:</p>
                <p><a href="{billing_url}">Plan tanlash →</a></p>
            </div>
        """,
    },
}


def send_template(to: str | list[str], template: str, vars: dict[str, Any]) -> bool:
    """Tayyor shablon yuborish."""
    tpl = TEMPLATES.get(template)
    if not tpl:
        logger.error("Template topilmadi: {}", template)
        return False
    subject = tpl["subject"].format(**vars)
    html = tpl["html"].format(**vars)
    return send_email(to, subject, html)
