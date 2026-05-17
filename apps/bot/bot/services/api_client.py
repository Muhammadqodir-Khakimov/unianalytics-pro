"""Backend HTTP API klienti.

Bot DB ga to'g'ridan-to'g'ri kirmaydi — barcha ma'lumotlar backend orqali
olinadi. Bu bot va backendni decoupled qiladi.
"""
from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from ..config import settings


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    """Async backend klienti. Token har bir requestda yangilanishi mumkin."""

    def __init__(self, base_url: str | None = None, timeout: float = 15.0) -> None:
        self.base_url = (base_url or settings.backend_api_url).rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"User-Agent": "UniAnalytics-Bot/1.0"},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            r = await self._client.request(
                method, path,
                json=json, data=data, params=params, headers=headers,
            )
        except httpx.RequestError as e:
            logger.error("API tarmoq xatosi: {}", e)
            raise ApiError(f"Backend bilan bog'lanib bo'lmadi: {e}") from e

        if r.status_code == 401:
            raise ApiError("Sessiya tugagan — qayta kirish kerak", 401)
        if r.status_code >= 400:
            detail = self._extract_detail(r)
            logger.warning("API {} {} -> {} ({})", method, path, r.status_code, detail)
            raise ApiError(detail, r.status_code)
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        return r.text

    @staticmethod
    def _extract_detail(r: httpx.Response) -> str:
        try:
            data = r.json()
        except ValueError:
            return r.text or f"HTTP {r.status_code}"
        if isinstance(data, dict):
            d = data.get("detail")
            if isinstance(d, str):
                return d
            if isinstance(d, list) and d:
                first = d[0]
                if isinstance(first, dict) and "msg" in first:
                    return str(first["msg"])
        return r.text or f"HTTP {r.status_code}"

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    async def login(self, username: str, password: str) -> dict:
        # Backend OAuth2PasswordRequestForm ishlatadi — form-data, JSON emas.
        return await self._request(
            "POST", "/auth/login",
            data={"username": username, "password": password},
        )

    async def me(self, token: str) -> dict:
        return await self._request("GET", "/auth/me", token=token)

    # ------------------------------------------------------------------
    # Talaba ma'lumotlari
    # ------------------------------------------------------------------
    async def my_dashboard(self, token: str) -> dict:
        return await self._request("GET", "/my/dashboard", token=token)

    async def my_grades(
        self, token: str, page: int = 1, page_size: int = 10
    ) -> dict:
        # /my/grades — talabaga bog'langan baholar (bot uchun)
        return await self._request(
            "GET", "/my/grades",
            token=token,
            params={"page": page, "page_size": page_size},
        )

    async def my_schedule(self, token: str) -> list:
        data = await self._request("GET", "/schedule/my", token=token)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
        return []

    async def my_notifications(self, token: str) -> list:
        data = await self._request("GET", "/notifications", token=token)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
        return []

    # ------------------------------------------------------------------
    # TZ 4.2.4 — ota-ona / dayjest / aloqa
    # ------------------------------------------------------------------
    async def request_parent_link(self, token: str, hemis_id: str) -> dict:
        """TZ: /bogla — ota-onaning farzandiga bog'lanish so'rovi."""
        return await self._request(
            "POST", "/bot/link-parent",
            token=token,
            json={"talaba_hemis_id": hemis_id},
        )

    async def set_digest(self, token: str, enabled: bool) -> dict:
        """TZ: /dayjest — haftalik dayjest yoqish/o'chirish."""
        return await self._request(
            "PATCH", "/users/me/digest",
            token=token,
            json={"weekly_digest_enabled": enabled},
        )

    async def my_contacts(self, token: str) -> dict:
        """TZ: /aloqa — kurator/dekan kontaktlari."""
        try:
            return await self._request("GET", "/my/contacts", token=token)
        except ApiError:
            return {}

    # ------------------------------------------------------------------
    # Kengaytirilgan funksiyalar
    # ------------------------------------------------------------------
    async def my_faculty_rank(self, token: str) -> dict:
        return await self._request("GET", "/my/rank/faculty", token=token)

    async def my_attendance(self, token: str) -> dict:
        return await self._request("GET", "/my/attendance", token=token)

    async def my_top_classmates(self, token: str, limit: int = 10) -> dict:
        return await self._request(
            "GET", "/my/top-classmates", token=token, params={"limit": limit}
        )

    async def my_upcoming_exams(self, token: str, limit: int = 5) -> dict:
        return await self._request(
            "GET", "/my/exams/upcoming", token=token, params={"limit": limit}
        )

    async def get_preferences(self, token: str) -> dict:
        return await self._request("GET", "/users/me/preferences", token=token)

    async def update_preferences(self, token: str, patch: dict) -> dict:
        return await self._request(
            "PATCH", "/users/me/preferences", token=token, json=patch
        )


# Global singleton
api_client = ApiClient()
