"""Talabalarni K-Means orqali 5 ta segmentga ajratish.

Klasterlar:
🌟 Yulduzlar    — yuqori GPA, yuqori davomat
📚 Tirishqoq    — yuqori davomat, o'rta GPA
🎯 Ko'tarilayotgan — trend ijobiy
😴 Loqayd       — yuqori davomat, past GPA
⚠️ Xavf ostida  — past hammasi
"""
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.ml.dropout_predictor import extract_features

MODEL_DIR = Path(__file__).resolve().parents[2] / "ml_models"
MODEL_DIR.mkdir(exist_ok=True)
CLUSTER_PATH = MODEL_DIR / "student_kmeans.joblib"
SCALER_PATH = MODEL_DIR / "student_scaler.joblib"

CLUSTER_FEATURES = ["avg_gpa", "avg_attendance", "failed_count", "low_grade_ratio"]

# Klaster nomlari va emoji (cluster_id -> label)
CLUSTER_LABELS = {
    0: {"emoji": "🌟", "name": "Yulduzlar", "code": "stars", "color": "#fbbf24"},
    1: {"emoji": "📚", "name": "Tirishqoq", "code": "diligent", "color": "#3b82f6"},
    2: {"emoji": "🎯", "name": "Ko'tarilayotgan", "code": "rising", "color": "#10b981"},
    3: {"emoji": "😴", "name": "Loqayd", "code": "lazy", "color": "#f59e0b"},
    4: {"emoji": "⚠️", "name": "Xavf ostida", "code": "at_risk", "color": "#ef4444"},
}


def _assign_labels(centers: np.ndarray) -> dict[int, dict]:
    """Klaster markazlariga asoslangan holda 5 ta nomni mantiqan biriktirish.

    Markaz (avg_gpa, avg_attendance, failed_count, low_grade_ratio) bo'yicha.
    """
    # Eng yaxshi GPA va davomat — Yulduzlar
    quality_score = centers[:, 0] - centers[:, 2] * 0.5  # high gpa, low failed
    attendance_score = centers[:, 1]
    risk_score = centers[:, 3] + centers[:, 2] * 0.3  # low gpa, high failed

    order = np.argsort(-quality_score)  # eng yaxshidan eng yomonga

    mapping = {}
    used = set()

    # Yulduzlar — eng yaxshi quality
    mapping[int(order[0])] = CLUSTER_LABELS[0]
    used.add(int(order[0]))

    # Xavf ostida — eng yomon
    worst = int(np.argsort(quality_score)[0])
    if worst not in used:
        mapping[worst] = CLUSTER_LABELS[4]
        used.add(worst)

    # Tirishqoq — yuqori davomat, o'rta GPA
    remaining = [i for i in range(len(centers)) if i not in used]
    if remaining:
        best_att = max(remaining, key=lambda i: attendance_score[i])
        mapping[best_att] = CLUSTER_LABELS[1]
        used.add(best_att)

    # Loqayd — yuqori davomat, past GPA
    remaining = [i for i in range(len(centers)) if i not in used]
    if remaining:
        # Yuqori davomat + past GPA
        scores = [(i, attendance_score[i] - quality_score[i]) for i in remaining]
        scores.sort(key=lambda x: -x[1])
        if scores:
            mapping[scores[0][0]] = CLUSTER_LABELS[3]
            used.add(scores[0][0])

    # Qolgan — Ko'tarilayotgan
    for i in range(len(centers)):
        if i not in mapping:
            mapping[i] = CLUSTER_LABELS[2]

    return mapping


def train(db: Session, n_clusters: int = 5) -> dict[str, Any]:
    """K-Means modelini o'qitish."""
    df = extract_features(db)
    if df.empty or len(df) < n_clusters * 5:
        return {"error": f"Yetarli emas: {len(df)} talaba"}

    X = df[CLUSTER_FEATURES].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = model.fit_predict(X_scaled)

    # Klaster markazlarini real qiymatlarga aylantirish
    centers_real = scaler.inverse_transform(model.cluster_centers_)
    label_map = _assign_labels(centers_real)

    # Save
    bundle = {
        "model": model,
        "scaler": scaler,
        "features": CLUSTER_FEATURES,
        "label_map": label_map,
        "n_clusters": n_clusters,
        "centers_real": centers_real.tolist(),
    }
    joblib.dump(bundle, CLUSTER_PATH)

    # Cluster statistics
    counts = pd.Series(labels).value_counts().to_dict()
    stats = []
    for cid, info in label_map.items():
        stats.append({
            **info,
            "cluster_id": cid,
            "count": int(counts.get(cid, 0)),
            "center": {
                feat: round(float(centers_real[cid, i]), 2)
                for i, feat in enumerate(CLUSTER_FEATURES)
            },
        })

    logger.info("K-Means clustering: {} talaba, {} ta klaster", len(df), n_clusters)
    return {
        "n_students": len(df),
        "n_clusters": n_clusters,
        "inertia": float(model.inertia_),
        "clusters": stats,
    }


def predict_cluster(db: Session, student_code: str) -> dict[str, Any] | None:
    """Bitta talaba klasterini aniqlash."""
    if not CLUSTER_PATH.exists():
        return {"error": "Model o'qitilmagan"}

    bundle = joblib.load(CLUSTER_PATH)
    df = extract_features(db)
    row = df[df["student_id"] == student_code]
    if row.empty:
        return None

    X = bundle["scaler"].transform(row[CLUSTER_FEATURES].fillna(0).values)
    cluster_id = int(bundle["model"].predict(X)[0])
    info = bundle["label_map"][cluster_id]

    return {
        "student_id": student_code,
        "cluster_id": cluster_id,
        "cluster_name": info["name"],
        "emoji": info["emoji"],
        "code": info["code"],
        "color": info["color"],
    }


def list_all_clusters(db: Session) -> dict[str, Any]:
    """Barcha talabalarning klasterlari."""
    if not CLUSTER_PATH.exists():
        return {"error": "Model o'qitilmagan"}

    bundle = joblib.load(CLUSTER_PATH)
    df = extract_features(db)
    if df.empty:
        return {"items": []}

    X = bundle["scaler"].transform(df[CLUSTER_FEATURES].fillna(0).values)
    clusters = bundle["model"].predict(X)
    df["cluster_id"] = clusters

    # Statistika
    groups = []
    for cid, info in bundle["label_map"].items():
        members = df[df["cluster_id"] == cid]
        groups.append({
            **info,
            "cluster_id": cid,
            "count": len(members),
            "students": members["student_id"].tolist()[:10],  # birinchi 10 ta
            "avg_gpa": round(float(members["avg_gpa"].mean()), 2) if len(members) else 0,
            "avg_attendance": round(float(members["avg_attendance"].mean()), 2) if len(members) else 0,
        })
    return {"clusters": groups}
