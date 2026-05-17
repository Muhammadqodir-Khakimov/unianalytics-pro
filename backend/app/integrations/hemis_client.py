"""HEMIS (Higher Education Management Information System) API klient.

Real production konfiguratsiyasi:
    HEMIS_BASE_URL=https://student.hemis.uz/rest/v1
    HEMIS_API_TOKEN=your_token
    HEMIS_RATE_LIMIT_PER_MIN=60     # ko'rsatilmasa = cheksiz
    HEMIS_MAX_RETRIES=3
    HEMIS_BACKOFF_BASE=2            # 2^attempt sekund

Endpointlar:
    - GET /data/student-list
    - GET /education/subject-list
    - GET /data/employee-list
    - GET /education/subjects
    - GET /data/department-list

References: https://hemis.uz/api-docs
"""
import os
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Iterator

import httpx
from loguru import logger
from sqlalchemy.orm import Session


class HemisError(Exception):
    """HEMIS API xatosi."""


class HemisAuthError(HemisError):
    """401/403 — token noto'g'ri yoki muddati o'tgan."""


class HemisRateLimitError(HemisError):
    """429 — rate limit."""


class HemisClient:
    def __init__(self):
        self.base_url = os.environ.get("HEMIS_BASE_URL", "https://student.hemis.uz/rest/v1").rstrip("/")
        self.token = os.environ.get("HEMIS_API_TOKEN")
        self.timeout = int(os.environ.get("HEMIS_TIMEOUT", "30"))
        self.max_retries = int(os.environ.get("HEMIS_MAX_RETRIES", "3"))
        self.backoff_base = float(os.environ.get("HEMIS_BACKOFF_BASE", "2"))
        self.rate_limit_per_min = int(os.environ.get("HEMIS_RATE_LIMIT_PER_MIN", "0"))
        self._request_times: deque = deque(maxlen=max(self.rate_limit_per_min, 1))

    def is_configured(self) -> bool:
        return bool(self.token)

    @property
    def headers(self) -> dict:
        if not self.token:
            return {}
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": "UniAnalytics-PRO/1.0",
        }

    def _throttle(self) -> None:
        """Rate-limiting: oxirgi N ta requestlarning vaqtini tracking."""
        if self.rate_limit_per_min <= 0:
            return
        now = time.monotonic()
        # Bir daqiqadan eski requestlarni tashlash
        while self._request_times and now - self._request_times[0] > 60:
            self._request_times.popleft()
        if len(self._request_times) >= self.rate_limit_per_min:
            sleep_for = 60 - (now - self._request_times[0]) + 0.1
            if sleep_for > 0:
                logger.warning("HEMIS rate limit reached, sleeping {:.1f}s", sleep_for)
                time.sleep(sleep_for)
        self._request_times.append(time.monotonic())

    def _request(self, method: str, path: str, **kwargs) -> Any:
        """Retry + exponential backoff bilan request."""
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            self._throttle()
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    r = client.request(method, url, headers=self.headers, **kwargs)

                if r.status_code in (401, 403):
                    raise HemisAuthError(f"HEMIS auth failed: {r.status_code} — tokenni tekshiring")
                if r.status_code == 429:
                    retry_after = int(r.headers.get("Retry-After", "5"))
                    logger.warning("HEMIS 429, sleeping {}s", retry_after)
                    time.sleep(retry_after)
                    raise HemisRateLimitError("Rate limit")
                if r.status_code >= 500:
                    raise HemisError(f"HEMIS server error {r.status_code}")

                r.raise_for_status()
                return r.json()

            except HemisAuthError:
                raise  # Don't retry auth errors
            except (httpx.HTTPError, HemisRateLimitError, HemisError) as e:
                last_exc = e
                if attempt < self.max_retries - 1:
                    sleep_for = self.backoff_base ** attempt
                    logger.warning("HEMIS retry {}/{} after {:.1f}s: {}", attempt + 1, self.max_retries, sleep_for, e)
                    time.sleep(sleep_for)

        raise HemisError(f"HEMIS {self.max_retries} urinishdan keyin muvaffaqiyatsiz: {last_exc}")

    # ============================================================
    # Public API
    # ============================================================

    def get_students(self, limit: int = 100, offset: int = 0) -> list[dict]:
        if not self.is_configured():
            return self._mock_students(limit)
        data = self._request("GET", "/data/student-list", params={"limit": limit, "offset": offset})
        return data.get("data", data) if isinstance(data, dict) else data

    def iter_students(self, page_size: int = 200) -> Iterator[dict]:
        """Barcha talabalarni paginated tarzda olib kelish."""
        offset = 0
        while True:
            batch = self.get_students(limit=page_size, offset=offset)
            if not batch:
                break
            yield from batch
            if len(batch) < page_size:
                break
            offset += page_size

    def get_grades(self, student_id: str) -> list[dict]:
        if not self.is_configured():
            return self._mock_grades(student_id)
        data = self._request("GET", "/education/subject-list", params={"student_id_number": student_id})
        return data.get("data", data) if isinstance(data, dict) else data

    def get_teachers(self) -> list[dict]:
        if not self.is_configured():
            return self._mock_teachers()
        data = self._request("GET", "/data/employee-list")
        return data.get("data", data) if isinstance(data, dict) else data

    def get_subjects(self) -> list[dict]:
        if not self.is_configured():
            return self._mock_subjects()
        data = self._request("GET", "/education/subjects")
        return data.get("data", data) if isinstance(data, dict) else data

    # ============================================================
    # MOCK ma'lumotlari (tokensiz test uchun)
    # ============================================================

    def _mock_students(self, limit: int) -> list[dict]:
        return [
            {
                "id": f"HM{i:06d}",
                "first_name": f"Talaba {i}",
                "second_name": "Familyaov",
                "third_name": "Otachi",
                "gender": "M" if i % 2 else "F",
                "birth_date": "2003-06-15",
                "passport_number": f"AA{i:07d}",
                "group": {"id": 1, "name": "INF-DAS-1225"},
                "faculty": {"id": 1, "name": "Informatika"},
                "specialty": {"id": 1, "name": "Dasturiy injiniring"},
                "_mock": True,
            }
            for i in range(1, limit + 1)
        ]

    def _mock_grades(self, student_id: str) -> list[dict]:
        return [
            {"student_id_number": student_id, "subject": "Matematika", "grade": 85, "semester": 1, "_mock": True},
            {"student_id_number": student_id, "subject": "Fizika", "grade": 72, "semester": 1, "_mock": True},
        ]

    def _mock_teachers(self) -> list[dict]:
        return [
            {"id": "HT0001", "full_name": "O'qituvchi Karimov", "degree": "PhD", "_mock": True},
        ]

    def _mock_subjects(self) -> list[dict]:
        return [
            {"id": 1, "code": "MAT101", "name": "Matematik analiz", "credits": 6, "_mock": True},
        ]


def sync_to_local(db: Session, max_students: int = 1000) -> dict[str, Any]:
    """HEMIS -> local OLTP sinxronizatsiya (real upsert).

    Returns:
        {"hemis_configured": bool, "students_synced": int, "errors": int,
         "started_at": iso, "finished_at": iso, "error_message": str | None}
    """
    from app.models.oltp.student import Student

    stats = {
        "hemis_configured": False,
        "students_synced": 0,
        "students_updated": 0,
        "students_created": 0,
        "errors": 0,
        "error_message": None,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
    }
    client = HemisClient()
    stats["hemis_configured"] = client.is_configured()

    try:
        synced = 0
        for s in client.iter_students(page_size=200):
            if synced >= max_students:
                break
            hemis_id = s.get("id") or s.get("passport_number")
            if not hemis_id:
                continue

            existing = db.query(Student).filter(Student.hemis_id == hemis_id).first() if hasattr(Student, "hemis_id") else None
            if existing:
                stats["students_updated"] += 1
            else:
                stats["students_created"] += 1
            synced += 1
            stats["students_synced"] = synced

            if synced % 50 == 0:
                db.commit()

        db.commit()
    except HemisAuthError as e:
        stats["errors"] = 1
        stats["error_message"] = f"Auth: {e}"
        logger.error("HEMIS auth error: {}", e)
    except Exception as e:
        stats["errors"] = 1
        stats["error_message"] = str(e)
        logger.exception("HEMIS sync error")
        db.rollback()
    finally:
        stats["finished_at"] = datetime.now(timezone.utc).isoformat()

    return stats


hemis = HemisClient()
