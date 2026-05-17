"""Isolation Forest bilan anomaliya aniqlash.

3 turdagi anomaliya:
1. Talaba xulq-atvori (g'ayrioddiy yaxshi yoki yomon)
2. O'qituvchi baholash patterni (juda yumshoq yoki qattiq)
3. Fan natijasi (juda oson yoki qiyin)
"""
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from sqlalchemy.orm import Session


def detect_student_anomalies(db: Session, contamination: float = 0.05) -> list[dict]:
    """Talabalar orasidagi anomaliyalar."""
    rows = db.execute(
        text(
            """
            SELECT ds.student_id, ds.full_name, ds.group_name,
                   AVG(f.grade_value) AS avg_grade,
                   0.0 AS std_grade,
                   AVG(f.attendance_percentage) AS avg_attendance,
                   COUNT(*) AS grades_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            GROUP BY ds.student_id, ds.full_name, ds.group_name
            HAVING COUNT(*) >= 5
            """
        )
    ).mappings().all()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty or len(df) < 20:
        return []

    features = ["avg_grade", "avg_attendance", "grades_count"]
    df = df.fillna(0)
    X = StandardScaler().fit_transform(df[features].values)

    iso = IsolationForest(contamination=contamination, random_state=42)
    iso.fit(X)
    df["score"] = iso.score_samples(X)
    df["is_anomaly"] = iso.predict(X) == -1

    anomalies = df[df["is_anomaly"]].copy()
    anomalies = anomalies.sort_values("score")

    result = []
    for _, r in anomalies.iterrows():
        avg_g = float(r["avg_grade"])
        avg_a = float(r["avg_attendance"])
        anomaly_type = "g'ayrioddiy past" if avg_g < 50 else "g'ayrioddiy yuqori" if avg_g > 95 else "g'ayrioddiy pattern"
        result.append({
            "student_id": r["student_id"],
            "full_name": r["full_name"],
            "group_name": r["group_name"],
            "avg_grade": round(avg_g, 2),
            "avg_attendance": round(avg_a, 2),
            "grades_count": int(r["grades_count"]),
            "anomaly_score": round(float(r["score"]), 3),
            "type": anomaly_type,
        })
    return result


def detect_teacher_anomalies(db: Session, contamination: float = 0.1) -> list[dict]:
    """O'qituvchilar baholash anomaliyalari.

    Aniqlanadi:
    - Juda yumshoq baholash (avg > 90)
    - Juda qattiq (avg < 50)
    - Past o'zgaruvchanlik (std < 5 — barchasiga bir xil baho)
    """
    rows = db.execute(
        text(
            """
            SELECT dt.teacher_id, dt.full_name,
                   AVG(f.grade_value) AS avg_grade,
                   0.0 AS std_grade,
                   COUNT(*) AS grades_count,
                   COUNT(DISTINCT f.student_key) AS students_count
            FROM fact_student_grades f
            JOIN dim_teacher dt ON f.teacher_key = dt.teacher_key
            GROUP BY dt.teacher_id, dt.full_name
            HAVING COUNT(*) >= 10
            """
        )
    ).mappings().all()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty or len(df) < 10:
        return []

    df = df.fillna(0)
    features = ["avg_grade", "std_grade"]
    X = StandardScaler().fit_transform(df[features].values)

    iso = IsolationForest(contamination=contamination, random_state=42)
    iso.fit(X)
    df["score"] = iso.score_samples(X)
    df["is_anomaly"] = iso.predict(X) == -1

    anomalies = df[df["is_anomaly"]].sort_values("score")

    result = []
    for _, r in anomalies.iterrows():
        avg = float(r["avg_grade"])
        std = float(r["std_grade"])
        if avg > 88:
            atype = "juda yumshoq (grade inflation)"
        elif avg < 55:
            atype = "juda qattiq"
        elif std < 5:
            atype = "past o'zgaruvchanlik (bir xil baholar)"
        else:
            atype = "boshqa pattern"
        result.append({
            "teacher_id": r["teacher_id"],
            "full_name": r["full_name"],
            "avg_grade": round(avg, 2),
            "std_grade": round(std, 2),
            "grades_count": int(r["grades_count"]),
            "students_count": int(r["students_count"]),
            "anomaly_score": round(float(r["score"]), 3),
            "type": atype,
        })
    return result


def detect_subject_difficulty(db: Session) -> list[dict]:
    """Fanlar qiyinligi va trendi."""
    rows = db.execute(
        text(
            """
            SELECT s.subject_name,
                   AVG(f.grade_value) AS avg_grade,
                   0.0 AS std_grade,
                   COUNT(*) AS grades_count,
                   SUM(CASE WHEN f.is_passed THEN 0 ELSE 1 END) * 100.0 / COUNT(*) AS fail_rate
            FROM fact_student_grades f
            JOIN dim_subject s ON f.subject_key = s.subject_key
            GROUP BY s.subject_name
            HAVING COUNT(*) >= 20
            """
        )
    ).mappings().all()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return []

    df = df.fillna(0).sort_values("avg_grade")

    result = []
    for _, r in df.iterrows():
        avg = float(r["avg_grade"])
        fail_rate = float(r["fail_rate"])
        if avg < 60 or fail_rate > 30:
            difficulty = "🔴 Juda qiyin"
        elif avg < 70 or fail_rate > 15:
            difficulty = "🟠 Qiyin"
        elif avg > 90:
            difficulty = "🟢 Oson"
        else:
            difficulty = "🔵 O'rta"
        result.append({
            "subject_name": r["subject_name"],
            "avg_grade": round(avg, 2),
            "std_grade": round(float(r["std_grade"]), 2),
            "fail_rate": round(fail_rate, 2),
            "grades_count": int(r["grades_count"]),
            "difficulty": difficulty,
        })
    return result
