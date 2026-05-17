"""Click va Payme to'lov shlyuzlari (O'zbekiston).

Click API: https://docs.click.uz/
Payme: https://developer.help.paycom.uz/
"""
import hashlib
import os
from datetime import datetime
from typing import Any

import httpx
from loguru import logger


# ============================================================
# CLICK
# ============================================================


class ClickGateway:
    """Click.uz to'lov shlyuzi."""

    def __init__(self):
        self.merchant_id = os.environ.get("CLICK_MERCHANT_ID")
        self.service_id = os.environ.get("CLICK_SERVICE_ID")
        self.secret_key = os.environ.get("CLICK_SECRET_KEY")
        self.merchant_user_id = os.environ.get("CLICK_MERCHANT_USER_ID")

    def is_configured(self) -> bool:
        return bool(self.merchant_id and self.secret_key)

    def generate_payment_url(self, invoice_id: int, amount: float, return_url: str = "") -> str:
        """Foydalanuvchi yo'naltirilishi mumkin bo'lgan to'lov URL."""
        if not self.is_configured():
            return f"https://my.click.uz/services/pay?demo=1&invoice={invoice_id}&amount={amount}"
        # Real Click format
        return (
            f"https://my.click.uz/services/pay"
            f"?service_id={self.service_id}"
            f"&merchant_id={self.merchant_id}"
            f"&amount={amount}"
            f"&transaction_param={invoice_id}"
            f"&return_url={return_url}"
        )

    def verify_signature(self, payload: dict, sign_string: str) -> bool:
        """Click webhook signature tekshirish."""
        if not self.secret_key:
            return True  # demo
        # Click MD5 signature format
        # md5(click_trans_id + service_id + secret_key + merchant_trans_id + amount + action + sign_time)
        s = (
            f"{payload.get('click_trans_id')}"
            f"{payload.get('service_id')}"
            f"{self.secret_key}"
            f"{payload.get('merchant_trans_id')}"
            f"{payload.get('amount')}"
            f"{payload.get('action')}"
            f"{payload.get('sign_time')}"
        )
        expected = hashlib.md5(s.encode()).hexdigest()
        return expected == sign_string


# ============================================================
# PAYME
# ============================================================


class PaymeGateway:
    """Payme (paycom.uz) to'lov shlyuzi."""

    def __init__(self):
        self.merchant_id = os.environ.get("PAYME_MERCHANT_ID")
        self.test_key = os.environ.get("PAYME_TEST_KEY")
        self.production_key = os.environ.get("PAYME_PRODUCTION_KEY")
        self.is_test = os.environ.get("PAYME_TEST_MODE", "true").lower() == "true"

    def is_configured(self) -> bool:
        return bool(self.merchant_id and (self.test_key or self.production_key))

    def _get_key(self) -> str:
        return self.test_key if self.is_test else self.production_key

    def generate_checkout_url(self, invoice_id: int, amount: float) -> str:
        """Payme checkout URL (Payme Merchant docs)."""
        if not self.is_configured():
            return f"https://checkout.paycom.uz/?demo=1&invoice={invoice_id}&amount={amount}"
        # Payme amount tiyin da (so'm * 100)
        amount_tiyin = int(amount * 100)
        import base64
        params = f"m={self.merchant_id};ac.invoice_id={invoice_id};a={amount_tiyin}"
        encoded = base64.b64encode(params.encode()).decode()
        return f"https://checkout.paycom.uz/{encoded}"


click = ClickGateway()
payme = PaymeGateway()
