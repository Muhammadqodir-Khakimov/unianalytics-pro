"""GPA forecasting — sklearn LinearRegression va PolynomialFeatures.

Prophet o'rniga sklearn ishlatildi (Python 3.14 mosligi uchun).
Polynomial regression + confidence interval bilan.
"""
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sqlalchemy import text
from sqlalchemy.orm import Session


def _student_history(db: Session, student_code: str) -> pd.DataFrame:
    """Talabaning semestrlar bo'yicha GPA tarixi."""
    rows = db.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   AVG(f.gpa_points) AS gpa,
                   AVG(f.grade_value) AS avg_grade
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE ds.student_id = :sid
            GROUP BY t.academic_year, t.semester
            ORDER BY t.academic_year, t.semester
            """
        ),
        {"sid": student_code},
    ).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])


def forecast_student(db: Session, student_code: str, horizon: int = 3) -> dict[str, Any]:
    """Bitta talaba uchun GPA prognozi."""
    df = _student_history(db, student_code)
    if len(df) < 2:
        return {"error": "Tarix yetarli emas (kamida 2 ta semester kerak)"}

    n = len(df)
    x = np.arange(n).reshape(-1, 1)
    y = df["gpa"].astype(float).values

    # Polynomial regression (degree 2 - kvadratik trend)
    degree = min(2, n - 1)
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    x_poly = poly.fit_transform(x)
    model = LinearRegression()
    model.fit(x_poly, y)

    # Confidence — residual std
    y_pred_train = model.predict(x_poly)
    residual_std = float(np.std(y - y_pred_train))

    # Bashorat
    future_x = np.arange(n, n + horizon).reshape(-1, 1)
    future_poly = poly.transform(future_x)
    future_gpa = model.predict(future_poly)

    # Trend
    slope = float(model.coef_[0])
    trend = "barqaror"
    if slope > 0.1:
        trend = "o'sayotgan"
    elif slope < -0.1:
        trend = "pasayayotgan"

    predictions = []
    for i, gpa in enumerate(future_gpa):
        gpa_clamped = max(0.0, min(4.0, float(gpa)))
        predictions.append({
            "period": f"prognoz +{i + 1}",
            "gpa": round(gpa_clamped, 3),
            "ci_low": round(max(0, gpa_clamped - 1.96 * residual_std), 3),
            "ci_high": round(min(4, gpa_clamped + 1.96 * residual_std), 3),
        })

    return {
        "student_id": student_code,
        "history": [
            {"period": f"{r['academic_year']} {r['semester']}", "gpa": round(float(r["gpa"]), 3)}
            for _, r in df.iterrows()
        ],
        "predictions": predictions,
        "trend": trend,
        "slope": round(slope, 4),
        "residual_std": round(residual_std, 3),
        "method": f"polynomial_regression_degree_{degree}",
    }


def forecast_faculty(db: Session, faculty_name: str, horizon: int = 2) -> dict[str, Any]:
    """Fakultet uchun o'rtacha GPA prognozi."""
    rows = db.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   AVG(f.gpa_points) AS gpa
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE fac.faculty_name = :fname
            GROUP BY t.academic_year, t.semester
            ORDER BY t.academic_year, t.semester
            """
        ),
        {"fname": faculty_name},
    ).mappings().all()

    df = pd.DataFrame([dict(r) for r in rows])
    if len(df) < 2:
        return {"error": "Yetarli emas"}

    x = np.arange(len(df)).reshape(-1, 1)
    y = df["gpa"].astype(float).values
    model = LinearRegression()
    model.fit(x, y)

    future_x = np.arange(len(df), len(df) + horizon).reshape(-1, 1)
    future_gpa = model.predict(future_x)

    return {
        "faculty_name": faculty_name,
        "history": [
            {"period": f"{r['academic_year']} {r['semester']}", "gpa": round(float(r["gpa"]), 3)}
            for _, r in df.iterrows()
        ],
        "predictions": [
            {"period": f"+{i + 1}", "gpa": round(max(0, min(4, float(g))), 3)}
            for i, g in enumerate(future_gpa)
        ],
        "slope": float(model.coef_[0]),
    }


def enrollment_forecast(db: Session) -> dict[str, Any]:
    """Yangi talabalar prognozi (asosiy daromad ko'rsatkichi)."""
    rows = db.execute(
        text(
            """
            SELECT enrollment_year, COUNT(*) AS count
            FROM dim_student
            GROUP BY enrollment_year
            ORDER BY enrollment_year
            """
        )
    ).mappings().all()

    df = pd.DataFrame([dict(r) for r in rows])
    if len(df) < 2:
        return {"error": "Yetarli emas"}

    x = df["enrollment_year"].values.reshape(-1, 1)
    y = df["count"].astype(float).values
    model = LinearRegression()
    model.fit(x, y)

    last_year = int(x.max())
    future_years = np.arange(last_year + 1, last_year + 4).reshape(-1, 1)
    future_counts = model.predict(future_years)

    return {
        "history": [
            {"year": int(r["enrollment_year"]), "count": int(r["count"])}
            for _, r in df.iterrows()
        ],
        "predictions": [
            {"year": int(y), "count": max(0, int(c))}
            for y, c in zip(future_years.flatten(), future_counts)
        ],
        "trend_per_year": round(float(model.coef_[0]), 1),
    }
