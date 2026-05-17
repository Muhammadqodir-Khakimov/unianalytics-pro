"""HEMIS (Higher Education Management Information System) API klient.

Real production da: https://hemis.uz API documentation asosida tuziladi.
Hozir esa mock + real API-ready struktura.

Konfiguratsiya (.env):
    HEMIS_BASE_URL=https://student.hemis.uz/rest/v1
    HEMIS_API_TOKEN=your_token

Buyruqlar:
    sync_students()    — talabalar sinxronizatsiya
    sync_grades()      — baholar
    sync_teachers()    — o'qituvchilar
    sync_subjects()    — fanlar
"""
import os
from datetime import datetime
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.orm import Session


class HemisClient:
    def __init__(self):
        self.base_url = os.environ.get("HEMIS_BASE_URL", "https://student.hemis.uz/rest/v1")
        self.token = os.environ.get("HEMIS_API_TOKEN")
        self.timeout = 30

    def is_configured(self) -> bool:
        return bool(self.token)

    @property
    def headers(self) -> dict:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def _request(self, method: str, path: str, **kwargs) -> dict | list:
        url = f"{self.base_url.rstrip('/')}{path}"
        with httpx.Client(timeout=self.timeout) as client:
            r = client.request(method, url, headers=self.headers, **kwargs)
            r.raise_for_status()
            return r.json()

    def get_students(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Talabalar ro'yxati."""
        if not self.is_configured():
            return self._mock_students(limit)
        return self._request("GET", "/data/student-list", params={"limit": limit, "offset": offset})

    def get_grades(self, student_id: str) -> list[dict]:
        """Talabaning baholari."""
        if not self.is_configured():
            return self._mock_grades(student_id)
        return self._request("GET", f"/education/subject-list", params={"student_id_number": student_id})

    def get_teachers(self) -> list[dict]:
        if not self.is_configured():
            return self._mock_teachers()
        return self._request("GET", "/data/employee-list")

    def get_subjects(self) -> list[dict]:
        if not self.is_configured():
            return self._mock_subjects()
        return self._request("GET", "/education/subjects")

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


def sync_to_local(db: Session) -> dict[str, Any]:
    """HEMIS -> local OLTP sinxronizatsiya (mock yoki real)."""
    from app.models.oltp.faculty import Faculty
    from app.models.oltp.student import EducationForm, Gender, Student, StudentStatus

    client = HemisClient()
    stats = {"hemis_configured": client.is_configured(), "students_synced": 0, "errors": 0}

    try:
        students = client.get_students(limit=20)
        for s in students:
            # Production da real upsert logic kerak
            stats["students_synced"] += 1
        return stats
    except Exception as e:
        logger.error("HEMIS sync error: {}", e)
        stats["errors"] = 1
        stats["error_message"] = str(e)
        return stats


hemis = HemisClient()
