"""Email shablonlar — HTML + multi-til (uz/ru/en).

Ishlatish:
    from app.services.email_templates import render_template
    html = render_template("welcome", lang="uz", name="Alisher", login_url="...")
"""
from typing import Any


def _base_layout(title: str, body: str, primary_color: str = "#1677ff") -> str:
    """Modern email layout."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; color: #1f2937; }}
    .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
    .header {{ background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%); padding: 32px; color: white; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em; }}
    .header .logo {{ font-size: 36px; margin-bottom: 12px; }}
    .body {{ padding: 32px; font-size: 15px; line-height: 1.6; color: #374151; }}
    .button {{ display: inline-block; padding: 14px 28px; background: {primary_color}; color: white !important; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
    .button:hover {{ background: #1659d9; }}
    .footer {{ padding: 24px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; background: #fafafa; }}
    .footer a {{ color: {primary_color}; text-decoration: none; }}
    .alert-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px; margin: 16px 0; }}
    .stat {{ display: inline-block; padding: 12px 20px; background: #eff6ff; border-radius: 8px; margin: 4px; }}
    .stat strong {{ font-size: 20px; color: {primary_color}; }}
  </style>
</head>
<body>
  <div class="container">
    {body}
    <div class="footer">
      <strong>UniAnalytics PRO</strong> · O'zbekistondagi #1 ta'lim BI platforma<br>
      © 2026 UniAnalytics · <a href="https://unianalytics.uz">unianalytics.uz</a> · <a href="https://t.me/unianalytics">Telegram</a>
    </div>
  </div>
</body>
</html>"""


# ============================================================
# TEMPLATES (uz, ru, en)
# ============================================================


def welcome(lang: str = "uz", **ctx) -> tuple[str, str]:
    name = ctx.get("name", "Foydalanuvchi")
    login_url = ctx.get("login_url", "https://unianalytics.uz/login")
    if lang == "ru":
        subject = "Добро пожаловать в UniAnalytics!"
        body_html = f"""
        <div class="header">
          <div class="logo">🎓</div>
          <h1>Добро пожаловать!</h1>
        </div>
        <div class="body">
          <p>Здравствуйте, <strong>{name}</strong>!</p>
          <p>Вы успешно зарегистрированы в UniAnalytics PRO.</p>
          <p style="text-align: center;"><a href="{login_url}" class="button">Войти в систему</a></p>
          <p>Если у вас есть вопросы, ответьте на это письмо.</p>
        </div>"""
    elif lang == "en":
        subject = "Welcome to UniAnalytics!"
        body_html = f"""
        <div class="header">
          <div class="logo">🎓</div>
          <h1>Welcome!</h1>
        </div>
        <div class="body">
          <p>Hello, <strong>{name}</strong>!</p>
          <p>You have successfully registered to UniAnalytics PRO.</p>
          <p style="text-align: center;"><a href="{login_url}" class="button">Login to system</a></p>
        </div>"""
    else:
        subject = "UniAnalytics ga xush kelibsiz!"
        body_html = f"""
        <div class="header">
          <div class="logo">🎓</div>
          <h1>Xush kelibsiz!</h1>
        </div>
        <div class="body">
          <p>Salom, <strong>{name}</strong>!</p>
          <p>Siz UniAnalytics PRO platformasiga muvaffaqiyatli ro'yxatdan o'tdingiz.</p>
          <p style="text-align: center;"><a href="{login_url}" class="button">Tizimga kirish</a></p>
          <p>Savollar bo'lsa, javob bering yoki <a href="https://t.me/unianalytics">Telegram</a>da murojaat qiling.</p>
        </div>"""
    return subject, _base_layout(subject, body_html)


def password_reset(lang: str = "uz", **ctx) -> tuple[str, str]:
    reset_url = ctx.get("reset_url", "")
    token = ctx.get("token", "")
    if lang == "ru":
        subject = "Сброс пароля - UniAnalytics"
        body_html = f"""
        <div class="header"><div class="logo">🔐</div><h1>Сброс пароля</h1></div>
        <div class="body">
          <p>Запрос на сброс пароля получен.</p>
          <p style="text-align: center;"><a href="{reset_url}" class="button">Сбросить пароль</a></p>
          <div class="alert-box">Ссылка действительна 1 час. Если вы не запрашивали - игнорируйте это письмо.</div>
          <p><small>Токен: <code>{token}</code></small></p>
        </div>"""
    else:
        subject = "Parol tiklash - UniAnalytics"
        body_html = f"""
        <div class="header"><div class="logo">🔐</div><h1>Parol tiklash</h1></div>
        <div class="body">
          <p>Parolingizni tiklash so'rovi qabul qilindi.</p>
          <p style="text-align: center;"><a href="{reset_url}" class="button">Parolni tiklash</a></p>
          <div class="alert-box">⏰ Bu havola 1 soat davomida amal qiladi. Agar siz so'ramagan bo'lsangiz — bu xatni e'tibordan chetda qoldiring.</div>
          <p><small>Token: <code>{token}</code></small></p>
        </div>"""
    return subject, _base_layout(subject, body_html)


def low_gpa_warning(lang: str = "uz", **ctx) -> tuple[str, str]:
    name = ctx.get("name", "Talaba")
    gpa = ctx.get("gpa", 0)
    subject = "⚠️ Past GPA haqida ogohlantirish" if lang == "uz" else "⚠️ Low GPA warning"
    body_html = f"""
    <div class="header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
      <div class="logo">⚠️</div><h1>Diqqat!</h1>
    </div>
    <div class="body">
      <p>Hurmatli <strong>{name}</strong>,</p>
      <p>Sizning hozirgi GPA: <strong style="color: #ef4444; font-size: 24px;">{gpa}</strong></p>
      <div class="alert-box">
        GPA 2.5 dan past — akademik xavf zonasida. Quyidagilarni qiling:
        <ul>
          <li>O'qituvchilar bilan maslahatlashing</li>
          <li>Qo'shimcha mashg'ulotlarga qatnashing</li>
          <li>Dekanat bilan bog'laning</li>
        </ul>
      </div>
    </div>"""
    return subject, _base_layout(subject, body_html, "#f59e0b")


def grade_added(lang: str = "uz", **ctx) -> tuple[str, str]:
    subject_name = ctx.get("subject_name", "")
    grade = ctx.get("grade", 0)
    color = "#10b981" if grade >= 70 else "#f59e0b" if grade >= 55 else "#ef4444"
    subject = f"Yangi baho: {subject_name}"
    body_html = f"""
    <div class="header" style="background: linear-gradient(135deg, {color} 0%, #1659d9 100%);">
      <div class="logo">📝</div><h1>Yangi baho</h1>
    </div>
    <div class="body">
      <p>Yangi baho kiritildi:</p>
      <div style="text-align: center; padding: 24px; background: #f9fafb; border-radius: 12px;">
        <p style="color: #6b7280; margin: 0;">{subject_name}</p>
        <p style="font-size: 48px; font-weight: 700; color: {color}; margin: 8px 0;">{grade}</p>
      </div>
    </div>"""
    return subject, _base_layout(subject, body_html, color)


def invoice_created(lang: str = "uz", **ctx) -> tuple[str, str]:
    amount = ctx.get("amount", 0)
    invoice_num = ctx.get("invoice_number", "")
    pay_url = ctx.get("pay_url", "")
    subject = f"Hisob #{invoice_num} — {amount:,.0f} so'm"
    body_html = f"""
    <div class="header"><div class="logo">💳</div><h1>To'lov hisobi</h1></div>
    <div class="body">
      <p>Yangi hisob yaratildi.</p>
      <div class="stat"><strong>{invoice_num}</strong><br>Hisob raqami</div>
      <div class="stat"><strong>{amount:,.0f} so'm</strong><br>Summa</div>
      <p style="text-align: center;"><a href="{pay_url}" class="button">To'lash</a></p>
      <p>Click yoki Payme orqali to'lashingiz mumkin.</p>
    </div>"""
    return subject, _base_layout(subject, body_html)


def trial_expiring(lang: str = "uz", **ctx) -> tuple[str, str]:
    days = ctx.get("days_left", 7)
    upgrade_url = ctx.get("upgrade_url", "https://unianalytics.uz/pricing")
    subject = f"⏰ Sinov muddati {days} kunda tugaydi"
    body_html = f"""
    <div class="header" style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);">
      <div class="logo">⏰</div><h1>Sinov tugamoqda</h1>
    </div>
    <div class="body">
      <p>Sizning 30 kunlik bepul sinov muddatingiz <strong>{days} kunda</strong> tugaydi.</p>
      <p>Toplay etishni davom ettirish uchun PRO yoki Enterprise rejaga o'ting:</p>
      <p style="text-align: center;"><a href="{upgrade_url}" class="button">Plan tanlash</a></p>
      <ul>
        <li>PRO — 1.5M so'm/oy (2000 talaba)</li>
        <li>Enterprise — 9M so'm/oy (cheksiz)</li>
      </ul>
    </div>"""
    return subject, _base_layout(subject, body_html, "#f59e0b")


# ============================================================
# Registry
# ============================================================

TEMPLATES = {
    "welcome": welcome,
    "password_reset": password_reset,
    "low_gpa_warning": low_gpa_warning,
    "grade_added": grade_added,
    "invoice_created": invoice_created,
    "trial_expiring": trial_expiring,
}


def render_template(name: str, lang: str = "uz", **ctx: Any) -> tuple[str, str]:
    """Shablon nomi va kontekst bilan (subject, html) qaytaradi."""
    if name not in TEMPLATES:
        raise ValueError(f"Template not found: {name}")
    return TEMPLATES[name](lang=lang, **ctx)


def list_templates() -> list[dict]:
    return [
        {"name": "welcome", "description": "Welcome email yangi user uchun"},
        {"name": "password_reset", "description": "Parol tiklash"},
        {"name": "low_gpa_warning", "description": "Past GPA ogohlantirish"},
        {"name": "grade_added", "description": "Yangi baho kiritildi"},
        {"name": "invoice_created", "description": "Hisob yaratildi"},
        {"name": "trial_expiring", "description": "Trial tugayotganda"},
    ]
