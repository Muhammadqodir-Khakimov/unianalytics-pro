"""Drop-out (chetlashtirish) bashorat qiluvchi XGBoost modeli.

Pipeline:
1. Feature engineering: GPA dinamikasi, davomat, qarz, ijtimoiy
2. XGBoost Classifier o'qitish
3. SHAP bilan explainability
4. Risk kategoriyalari va tavsiyalar
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

MODEL_DIR = Path(__file__).resolve().parents[2] / "ml_models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "dropout_xgb.joblib"
SHAP_PATH = MODEL_DIR / "dropout_shap.joblib"

FEATURE_NAMES = [
    "avg_gpa",
    "gpa_trend",  # so'nggi 2 semester farqi
    "avg_attendance",
    "failed_count",
    "total_grades",
    "subject_count",
    "low_grade_ratio",  # 55 dan past baholar foizi
    "age",
    "enrollment_years",  # nechinchi yil
    "gender_male",  # binary
]

RISK_CATEGORIES = [
    (0.0, 0.20, "🟢 Xavfsiz (Safe)", "safe"),
    (0.20, 0.50, "🟡 Kuzatuv (Watch)", "watch"),
    (0.50, 0.75, "🟠 Xavfli (Risk)", "risk"),
    (0.75, 1.01, "🔴 Kritik (Critical)", "critical"),
]


def extract_features(db: Session) -> pd.DataFrame:
    """OLAP DB dan barcha talabalarning xususiyatlarini olish."""
    sql = text(
        """
        WITH stats AS (
            SELECT
                ds.student_id,
                ds.gender,
                ds.enrollment_year,
                AVG(f.grade_value) AS avg_grade,
                AVG(f.gpa_points) AS avg_gpa,
                AVG(f.attendance_percentage) AS avg_attendance,
                COUNT(*) AS total_grades,
                COUNT(DISTINCT f.subject_key) AS subject_count,
                SUM(CASE WHEN f.is_passed THEN 0 ELSE 1 END) AS failed_count,
                SUM(CASE WHEN f.grade_value < 55 THEN 1 ELSE 0 END) AS low_grade_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            GROUP BY ds.student_id, ds.gender, ds.enrollment_year
        )
        SELECT
            student_id,
            avg_grade,
            avg_gpa,
            avg_attendance,
            total_grades,
            subject_count,
            failed_count,
            CAST(low_grade_count AS FLOAT) / NULLIF(total_grades, 0) AS low_grade_ratio,
            gender,
            enrollment_year
        FROM stats
        WHERE total_grades >= 5
        """
    )
    rows = db.execute(sql).mappings().all()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return df

    current_year = datetime.now().year
    df["age"] = 18 + (current_year - df["enrollment_year"])
    df["enrollment_years"] = current_year - df["enrollment_year"]
    df["gender_male"] = (df["gender"] == "M").astype(int)
    df["gpa_trend"] = 0.0  # placeholder — keyinroq real trend
    df["avg_gpa"] = df["avg_gpa"].astype(float)
    df["avg_attendance"] = df["avg_attendance"].astype(float)
    df["low_grade_ratio"] = df["low_grade_ratio"].astype(float).fillna(0)

    return df[["student_id"] + FEATURE_NAMES]


def _generate_labels(df: pd.DataFrame) -> np.ndarray:
    """Drop-out yorlig'ini hosil qilish (real ma'lumot yo'qligi sababli synthetic).

    Real holatda bu o'tgan yillardan kelgan ma'lumot bo'lardi (talaba chetlashtirilganmi).
    Hozir esa GPA<2 yoki failed>5 bo'lsa droplout deb hisoblaymiz.
    """
    return ((df["avg_gpa"] < 2.0) | (df["failed_count"] > 5) | (df["avg_attendance"] < 60)).astype(int).values


def train(db: Session) -> dict[str, Any]:
    """XGBoost modelini o'qitish."""
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
    from xgboost import XGBClassifier
    import shap

    df = extract_features(db)
    if df.empty or len(df) < 50:
        return {"error": f"Yetarli emas: faqat {len(df)} ta yozuv"}

    X = df[FEATURE_NAMES].values
    y = _generate_labels(df)

    # Class balance
    if y.sum() < 5 or y.sum() > len(y) - 5:
        return {"error": f"Class balance yomon: {y.sum()} positive / {len(y)} total"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if len(set(y_test)) > 1 else None,
        "n_samples": len(df),
        "positive_ratio": float(y.mean()),
        "trained_at": datetime.utcnow().isoformat(),
    }

    # SHAP explainer
    explainer = shap.TreeExplainer(model)

    joblib.dump({"model": model, "feature_names": FEATURE_NAMES, "metrics": metrics}, MODEL_PATH)
    joblib.dump(explainer, SHAP_PATH)

    logger.info("Drop-out model o'qitildi: accuracy={:.3f}, AUC={}",
                metrics["accuracy"], metrics["roc_auc"])
    return metrics


def _load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def _load_shap():
    if not SHAP_PATH.exists():
        return None
    return joblib.load(SHAP_PATH)


def predict_one(db: Session, student_code: str) -> dict[str, Any] | None:
    """Bitta talaba uchun bashorat va SHAP tushuntirishi."""
    bundle = _load_model()
    if not bundle:
        return {"error": "Model o'qitilmagan. /api/v1/ml/dropout/train ni chaqiring"}

    model = bundle["model"]
    df = extract_features(db)
    if df.empty:
        return None

    row = df[df["student_id"] == student_code]
    if row.empty:
        return None

    X = row[FEATURE_NAMES].values
    proba = float(model.predict_proba(X)[0, 1])

    # Risk kategoriyasi
    risk_label = "?"
    risk_code = "unknown"
    for lo, hi, label, code in RISK_CATEGORIES:
        if lo <= proba < hi:
            risk_label = label
            risk_code = code
            break

    # SHAP
    explanation: list[dict] = []
    try:
        explainer = _load_shap()
        if explainer is not None:
            shap_values = explainer.shap_values(X)
            shap_arr = shap_values[0] if hasattr(shap_values, "__len__") else shap_values
            for i, fname in enumerate(FEATURE_NAMES):
                explanation.append({
                    "feature": fname,
                    "value": float(X[0, i]),
                    "shap_value": float(shap_arr[i]),
                    "impact": "increases_risk" if shap_arr[i] > 0 else "decreases_risk",
                })
            explanation.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    except Exception as e:
        logger.warning("SHAP error: {}", e)

    return {
        "student_id": student_code,
        "dropout_probability": round(proba, 3),
        "risk_category": risk_label,
        "risk_code": risk_code,
        "explanation": explanation[:5],  # eng kuchli 5 ta omil
        "recommendation": _recommend(risk_code, explanation[:3]),
    }


def predict_all(db: Session, top_n: int = 50) -> list[dict]:
    """Barcha talabalar uchun bashorat — eng yuqori xavf yuqorida."""
    bundle = _load_model()
    if not bundle:
        return []

    model = bundle["model"]
    df = extract_features(db)
    if df.empty:
        return []

    proba = model.predict_proba(df[FEATURE_NAMES].values)[:, 1]
    df["dropout_probability"] = proba

    df = df.sort_values("dropout_probability", ascending=False).head(top_n)

    out = []
    for _, r in df.iterrows():
        p = float(r["dropout_probability"])
        risk_label, risk_code = "?", "unknown"
        for lo, hi, label, code in RISK_CATEGORIES:
            if lo <= p < hi:
                risk_label, risk_code = label, code
                break
        out.append({
            "student_id": r["student_id"],
            "dropout_probability": round(p, 3),
            "risk_category": risk_label,
            "risk_code": risk_code,
            "avg_gpa": round(float(r["avg_gpa"]), 2),
            "avg_attendance": round(float(r["avg_attendance"]), 2),
            "failed_count": int(r["failed_count"]),
        })
    return out


def _recommend(risk_code: str, top_features: list[dict]) -> list[str]:
    """Risk va asosiy omillar asosida tavsiyalar."""
    recs = []
    if risk_code == "critical":
        recs.append("🚨 Kritik holat! Dekanat va ota-ona bilan tezda bog'lanish kerak.")
        recs.append("Akademik kurator biriktirish (har hafta 1 ta uchrashuv).")
    elif risk_code == "risk":
        recs.append("⚠️ Yuqori xavf. Psixolog va tutor bilan suhbat tavsiya etiladi.")
    elif risk_code == "watch":
        recs.append("📋 Kuzatuvga olinishi kerak.")

    for feat in top_features:
        if feat["feature"] == "avg_gpa" and feat["value"] < 2.5:
            recs.append("📚 GPA past — qo'shimcha mashg'ulotlar va repititor")
        elif feat["feature"] == "avg_attendance" and feat["value"] < 75:
            recs.append("📅 Davomat past — sabablari aniqlansin")
        elif feat["feature"] == "failed_count" and feat["value"] > 3:
            recs.append("❌ Ko'p o'tmaganlar — qayta topshirish jadvali")
        elif feat["feature"] == "low_grade_ratio" and feat["value"] > 0.3:
            recs.append("📉 Ko'p past baholar — fanlarni qayta o'rganish")

    if not recs:
        recs.append("✅ Hozir muammo yo'q, monitoringda davom eting")
    return recs


def model_status() -> dict[str, Any]:
    """Model holati va metrikalar."""
    bundle = _load_model()
    if not bundle:
        return {"trained": False}
    return {
        "trained": True,
        "metrics": bundle.get("metrics"),
        "features": bundle.get("feature_names"),
    }
