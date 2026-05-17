"""MeiliSearch — tez full-text qidiruv.

Local: docker-compose'da MeiliSearch service yoki tashqi server.
Env:
    MEILI_URL=http://meilisearch:7700
    MEILI_KEY=master-key

Indekslar:
- students (id, student_id, full_name, group_name)
- teachers (id, teacher_id, full_name, department)
- subjects (id, code, name, department)

API: PostgreSQL bo'lsa fallback SQL search ishlatadi (graceful degradation).
"""
import os
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.orm import Session


class MeiliClient:
    def __init__(self):
        self.url = os.environ.get("MEILI_URL", "http://localhost:7700")
        self.key = os.environ.get("MEILI_KEY")

    def is_configured(self) -> bool:
        if not self.key:
            return False
        try:
            with httpx.Client(timeout=3) as client:
                r = client.get(f"{self.url}/health", headers=self._headers())
                return r.status_code == 200
        except Exception:
            return False

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.key:
            h["Authorization"] = f"Bearer {self.key}"
        return h

    def index(self, index_name: str, documents: list[dict]) -> bool:
        """Indekslarga hujjatlar qo'shish."""
        if not self.is_configured():
            return False
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{self.url}/indexes/{index_name}/documents",
                headers=self._headers(),
                json=documents,
            )
            return r.status_code in (200, 201, 202)

    def search(self, index_name: str, query: str, limit: int = 10) -> list[dict]:
        """Qidiruv."""
        if not self.is_configured():
            return []
        with httpx.Client(timeout=10) as client:
            r = client.post(
                f"{self.url}/indexes/{index_name}/search",
                headers=self._headers(),
                json={"q": query, "limit": limit},
            )
            if r.status_code == 200:
                return r.json().get("hits", [])
            return []

    def reindex_all(self, db: Session) -> dict:
        """Hamma jadvallarni MeiliSearchga yuklash."""
        from app.models.oltp.student import Student
        from app.models.oltp.teacher import Teacher
        from app.models.oltp.subject import Subject

        if not self.is_configured():
            return {"error": "MeiliSearch sozlanmagan", "fallback": "PostgreSQL ILIKE"}

        students = [
            {"id": s.id, "student_id": s.student_id, "full_name": s.full_name, "group_name": s.group.name if s.group else ""}
            for s in db.query(Student).limit(10000).all()
        ]
        teachers = [
            {"id": t.id, "teacher_id": t.teacher_id, "full_name": t.full_name, "department": t.department or ""}
            for t in db.query(Teacher).all()
        ]
        subjects = [
            {"id": s.id, "code": s.code, "name": s.name, "department": s.department or ""}
            for s in db.query(Subject).all()
        ]

        self.index("students", students)
        self.index("teachers", teachers)
        self.index("subjects", subjects)

        return {
            "indexed": {"students": len(students), "teachers": len(teachers), "subjects": len(subjects)},
            "success": True,
        }


meili = MeiliClient()
