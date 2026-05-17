"""Moodle LMS integration.

Konfiguratsiya:
    MOODLE_URL=https://moodle.university.uz
    MOODLE_TOKEN=your_webservice_token

Moodle Web Services API ishlatadi.
"""
import os
from typing import Any

import httpx
from loguru import logger


class MoodleClient:
    def __init__(self):
        self.base_url = os.environ.get("MOODLE_URL", "https://moodle.example.uz")
        self.token = os.environ.get("MOODLE_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.token)

    def _call(self, function: str, **params) -> Any:
        if not self.is_configured():
            return self._mock_response(function)
        url = f"{self.base_url}/webservice/rest/server.php"
        data = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json",
            **params,
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(url, data=data)
            r.raise_for_status()
            return r.json()

    def get_courses(self) -> list[dict]:
        return self._call("core_course_get_courses")

    def get_user_courses(self, user_id: int) -> list[dict]:
        return self._call("core_enrol_get_users_courses", userid=user_id)

    def get_quiz_grades(self, quiz_id: int) -> list[dict]:
        return self._call("mod_quiz_get_user_attempts", quizid=quiz_id)

    def _mock_response(self, function: str) -> Any:
        mocks = {
            "core_course_get_courses": [
                {"id": 1, "shortname": "INF101", "fullname": "Dasturlash asoslari", "_mock": True},
                {"id": 2, "shortname": "MAT201", "fullname": "Matematik analiz", "_mock": True},
            ],
            "core_enrol_get_users_courses": [
                {"id": 1, "shortname": "INF101", "fullname": "Dasturlash asoslari", "_mock": True},
            ],
        }
        return mocks.get(function, {"_mock": True})


moodle = MoodleClient()
