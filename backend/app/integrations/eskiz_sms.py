"""Eskiz.uz SMS gateway integration.

API doc: https://documenter.getpostman.com/view/663428/RzfmES4z

Konfiguratsiya (.env):
    ESKIZ_EMAIL=your@email.com
    ESKIZ_PASSWORD=your_password
    ESKIZ_SENDER=4546   (default test)
"""
import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from loguru import logger


class EskizClient:
    BASE_URL = "https://notify.eskiz.uz/api"

    def __init__(self):
        self.email = os.environ.get("ESKIZ_EMAIL")
        self.password = os.environ.get("ESKIZ_PASSWORD")
        self.sender = os.environ.get("ESKIZ_SENDER", "4546")
        self._token: str | None = None
        self._token_expires: datetime | None = None

    def is_configured(self) -> bool:
        return bool(self.email and self.password)

    def _ensure_token(self) -> str:
        """Token oling (cached 25 kun)."""
        if self._token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._token

        if not self.is_configured():
            raise RuntimeError("Eskiz: ESKIZ_EMAIL va ESKIZ_PASSWORD kerak")

        with httpx.Client(timeout=10) as client:
            r = client.post(f"{self.BASE_URL}/auth/login", json={
                "email": self.email,
                "password": self.password,
            })
            r.raise_for_status()
            data = r.json()
            self._token = data["data"]["token"]
            self._token_expires = datetime.utcnow() + timedelta(days=25)
            return self._token

    def send_sms(self, phone: str, message: str) -> dict[str, Any]:
        """SMS yuborish.

        phone: 998901234567 ko'rinishida (faqat raqamlar, + siz)
        """
        if not self.is_configured():
            logger.warning("Eskiz sozlanmagan — SMS yuborilmadi. To: {}, msg: {}", phone, message[:50])
            return {"success": False, "demo_mode": True}

        phone = phone.lstrip("+").replace(" ", "")
        token = self._ensure_token()
        with httpx.Client(timeout=10) as client:
            r = client.post(
                f"{self.BASE_URL}/message/sms/send",
                headers={"Authorization": f"Bearer {token}"},
                data={"mobile_phone": phone, "message": message, "from": self.sender},
            )
            try:
                r.raise_for_status()
            except Exception as e:
                return {"success": False, "error": str(e), "detail": r.text}
            return {"success": True, "data": r.json()}

    def get_balance(self) -> float | None:
        if not self.is_configured():
            return None
        token = self._ensure_token()
        with httpx.Client(timeout=10) as client:
            r = client.get(f"{self.BASE_URL}/user/get-limit", headers={"Authorization": f"Bearer {token}"})
            try:
                r.raise_for_status()
                return float(r.json().get("data", {}).get("balance", 0))
            except Exception:
                return None


eskiz = EskizClient()
