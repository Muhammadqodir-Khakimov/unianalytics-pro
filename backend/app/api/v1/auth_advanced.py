"""Advanced auth: 2FA TOTP, Google OAuth, email verification.

OAuth Google flow: hozir mock — real GOOGLE_CLIENT_ID env bilan ulanadi.
2FA: pyotp library — QR code orqali Google Authenticator/Authy bilan ishlaydi.
"""
import base64
import io
import os
import secrets
from typing import Any

import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import CredentialsException
from app.database import get_oltp_db
from app.models.oltp.user import User

router = APIRouter(prefix="/auth/advanced", tags=["Advanced Auth"])


# ============================================================
# 2FA TOTP
# ============================================================


@router.post("/2fa/setup")
def setup_2fa(db: Session = Depends(get_oltp_db), user: User = Depends(get_current_user)):
    """2FA ni sozlash — QR code va secret qaytaradi."""
    if user.totp_enabled:
        raise HTTPException(400, "2FA allaqachon yoqilgan")

    secret = pyotp.random_base32()
    user.totp_secret = secret
    db.commit()

    # QR code uchun TOTP URI
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="UniAnalytics PRO")

    # QR code rasmga aylantirish
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_b64}",
        "uri": uri,
        "instructions": "1. Google Authenticator yoki Authy ni o'rnating. 2. QR kodni skanerlang. 3. 6-raqamli kodni /2fa/verify ga yuboring.",
    }


class TOTPVerify(BaseModel):
    code: str


@router.post("/2fa/verify")
def verify_2fa(payload: TOTPVerify, db: Session = Depends(get_oltp_db), user: User = Depends(get_current_user)):
    """2FA ni yoqish — kodni tasdiqlash."""
    if not user.totp_secret:
        raise HTTPException(400, "Avval /2fa/setup chaqiring")
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(400, "Noto'g'ri kod")
    user.totp_enabled = True
    db.commit()
    return {"success": True, "message": "2FA yoqildi"}


@router.post("/2fa/disable")
def disable_2fa(payload: TOTPVerify, db: Session = Depends(get_oltp_db), user: User = Depends(get_current_user)):
    """2FA ni o'chirish — kod orqali."""
    if not user.totp_enabled:
        return {"success": True, "message": "2FA allaqachon o'chirilgan"}
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(400, "Noto'g'ri kod")
    user.totp_enabled = False
    user.totp_secret = None
    db.commit()
    return {"success": True}


@router.post("/2fa/login")
def login_with_2fa(payload: TOTPVerify, db: Session = Depends(get_oltp_db), user: User = Depends(get_current_user)):
    """Login dan keyin 2FA kod tasdiqlash."""
    if not user.totp_enabled:
        return {"success": True, "message": "2FA o'chirilgan"}
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise CredentialsException("Noto'g'ri 2FA kod")
    return {"success": True}


# ============================================================
# GOOGLE OAUTH (mock + real-ready)
# ============================================================


@router.get("/google/url")
def google_oauth_url():
    """Google OAuth boshlash URLi."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id:
        return {
            "configured": False,
            "url": None,
            "instructions": "GOOGLE_CLIENT_ID va GOOGLE_CLIENT_SECRET ni .env ga qo'shing. https://console.cloud.google.com/apis/credentials",
        }
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "https://unianalytics.uz/auth/google/callback")
    scope = "openid email profile"
    state = secrets.token_urlsafe(16)
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&redirect_uri={redirect_uri}"
        f"&response_type=code&scope={scope}&state={state}"
    )
    return {"configured": True, "url": url, "state": state}


class OAuthCallback(BaseModel):
    code: str
    state: str | None = None


@router.post("/google/callback")
def google_oauth_callback(payload: OAuthCallback, db: Session = Depends(get_oltp_db)):
    """Google OAuth callback — code dan token olib user yaratish/topish."""
    import httpx

    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise HTTPException(503, "Google OAuth sozlanmagan")

    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "https://unianalytics.uz/auth/google/callback")

    # Exchange code for token
    with httpx.Client(timeout=15) as client:
        token_resp = client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": payload.code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_resp.json()
        if "access_token" not in token_data:
            raise HTTPException(400, f"Google token error: {token_data}")

        # Get user info
        user_resp = client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        info = user_resp.json()

    # Find or create user
    user = db.query(User).filter(User.google_id == info["id"]).first()
    if not user:
        user = db.query(User).filter(User.email == info["email"]).first()
        if user:
            user.google_id = info["id"]
        else:
            from app.core.security import hash_password
            from app.models.oltp.user import UserRole
            user = User(
                username=info["email"].split("@")[0],
                email=info["email"],
                full_name=info.get("name", "Google User"),
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                google_id=info["id"],
                avatar_url=info.get("picture"),
                role=UserRole.STUDENT,
                is_verified=True,
                is_active=True,
            )
            db.add(user)
    db.commit()
    db.refresh(user)

    # Issue JWT
    from app.services import auth_service
    return auth_service.build_tokens(user)


# ============================================================
# EMAIL VERIFICATION
# ============================================================


@router.post("/email/send-verification")
def send_verification_email(db: Session = Depends(get_oltp_db), user: User = Depends(get_current_user)):
    """Email tasdiqlash xatini yuborish."""
    if user.is_verified:
        return {"success": True, "message": "Email allaqachon tasdiqlangan"}

    token = secrets.token_urlsafe(32)
    user.email_verification_token = token
    db.commit()

    from app.services import notification_service
    verification_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"

    notification_service.create_notification(
        db,
        user_id=user.id,
        title="Email tasdiqlash",
        message=f"Email manzilingizni tasdiqlash uchun havolaga o'ting: {verification_url}",
        notification_type="info",
        link=verification_url,
        send_email=True,
    )
    return {"success": True, "message": "Tasdiqlash xati yuborildi", "_dev_token": token}


class EmailVerify(BaseModel):
    token: str


@router.post("/email/verify")
def verify_email(payload: EmailVerify, db: Session = Depends(get_oltp_db)):
    """Email tokenni tasdiqlash."""
    user = db.query(User).filter(User.email_verification_token == payload.token).first()
    if not user:
        raise HTTPException(400, "Yaroqsiz token")
    user.is_verified = True
    user.email_verification_token = None
    db.commit()
    return {"success": True, "message": "Email tasdiqlandi"}


# ============================================================
# Session list (active devices)
# ============================================================


@router.get("/sessions/active")
def list_sessions(user: User = Depends(get_current_user)):
    """Joriy active session lar (placeholder — Redis bilan kengaytirsa bo'ladi)."""
    return {
        "current_session": {
            "user_id": user.id,
            "login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        },
        "note": "Multi-device session tracking kelajakda Redis bilan kengaytiriladi",
    }
