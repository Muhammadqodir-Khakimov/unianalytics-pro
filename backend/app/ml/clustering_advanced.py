"""DBSCAN va Random Forest baseline (Sprint 3.2 + 3.1 to'liq).

K-Means dan tashqari DBSCAN bilan outlier detection.
Drop-out uchun Random Forest baseline (XGBoost bilan solishtirish).
"""
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session


def dbscan_anomalies(db: Session, eps: float = 0.8, min_samples: int = 5) -> dict[str, Any]:
    """DBSCAN bilan outlier (label = -1) talabalarni topish."""
    from app.ml.dropout_predictor import extract_features

    df = extract_features(db)
    if df.empty or len(df) < 20:
        return {"error": "Yetarli ma'lumot yo'q"}

    features = ["avg_gpa", "avg_attendance", "failed_count", "low_grade_ratio"]
    X = StandardScaler().fit_transform(df[features].fillna(0).values)

    db_scan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db_scan.fit_predict(X)
    df["dbscan_label"] = labels

    outliers = df[df["dbscan_label"] == -1]
    clusters = sorted(set(labels) - {-1})

    return {
        "total": len(df),
        "outliers_count": len(outliers),
        "outlier_percentage": round(len(outliers) * 100 / len(df), 2),
        "cluster_count": len(clusters),
        "outliers": [
            {"student_id": r["student_id"], "avg_gpa": float(r["avg_gpa"])}
            for _, r in outliers.head(20).iterrows()
        ],
    }


def random_forest_baseline(db: Session) -> dict[str, Any]:
    """Random Forest drop-out baseline (XGBoost bilan solishtirish)."""
    from app.ml.dropout_predictor import extract_features, FEATURE_NAMES, _generate_labels

    df = extract_features(db)
    if df.empty or len(df) < 50:
        return {"error": f"Yetarli emas: {len(df)} ta yozuv"}

    X = df[FEATURE_NAMES].values
    y = _generate_labels(df)
    if y.sum() < 5 or y.sum() > len(y) - 5:
        return {"error": "Class balance yomon"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    return {
        "model": "RandomForest",
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if len(set(y_test)) > 1 else None,
        "n_samples": len(df),
        "feature_importance": [
            {"feature": fname, "importance": float(imp)}
            for fname, imp in sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1])
        ],
        "note": "XGBoost bilan solishtirish uchun baseline (Sprint 3.1 talabi)",
    }


def what_if_analysis(db: Session, student_code: str, hypothetical_grade: float, subject_name: str) -> dict:
    """Talaba uchun "what-if" tahlili.

    Hozirgi GPA ga gipotetik baho ta'sirini hisoblash.
    """
    from sqlalchemy import text
    current = db.execute(
        text("""
            SELECT AVG(grade_value) AS current_avg, COUNT(*) AS n
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid
        """),
        {"sid": student_code},
    ).mappings().first()

    if not current or not current["current_avg"]:
        return {"error": "Ma'lumot yo'q"}

    n = int(current["n"])
    current_avg = float(current["current_avg"])
    # Yangi baho qo'shilsa, o'rtacha qancha bo'ladi
    new_avg = (current_avg * n + hypothetical_grade) / (n + 1)
    delta = new_avg - current_avg

    return {
        "student_id": student_code,
        "current_avg_grade": round(current_avg, 2),
        "hypothetical_subject": subject_name,
        "hypothetical_grade": hypothetical_grade,
        "new_avg_grade": round(new_avg, 2),
        "impact": round(delta, 3),
        "trend": "improves" if delta > 0.1 else "worsens" if delta < -0.1 else "neutral",
        "message": f"Agar siz {subject_name} dan {hypothetical_grade} ball olsangiz, o'rtacha balli {current_avg:.2f} dan {new_avg:.2f} ga {'oshadi' if delta > 0 else 'tushadi'}",
    }
