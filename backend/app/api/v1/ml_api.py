"""ML/AI endpointlari — XGBoost, K-Means, forecasting, anomaly, AI Tutor."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_any, require_dekan
from app.database import get_olap_db, get_oltp_db
from app.ml import ai_tutor, anomaly_detector, dropout_predictor, gpa_forecaster, student_clusterer
from app.models.oltp.student import Student
from app.models.oltp.user import User

router = APIRouter(prefix="/ml", tags=["ML / AI"])


# ============================================================
# DROP-OUT PREDICTION (XGBoost + SHAP)
# ============================================================


@router.post("/dropout/train", dependencies=[Depends(require_dekan)])
def train_dropout_model(db: Session = Depends(get_olap_db)):
    """XGBoost drop-out modelini qayta o'qitish."""
    return dropout_predictor.train(db)


@router.get("/dropout/status", dependencies=[Depends(require_any)])
def dropout_status():
    return dropout_predictor.model_status()


@router.get("/dropout/student/{student_id}", dependencies=[Depends(require_any)])
def dropout_predict_one(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Bitta talaba uchun XGBoost prognoz + SHAP."""
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)
    result = dropout_predictor.predict_one(olap, student.student_id)
    return result or {"error": "Topilmadi"}


@router.get("/dropout/at-risk", dependencies=[Depends(require_dekan)])
def dropout_at_risk(top_n: int = 50, db: Session = Depends(get_olap_db)):
    return {"items": dropout_predictor.predict_all(db, top_n)}


# ============================================================
# CLUSTERING (K-Means)
# ============================================================


@router.post("/clustering/train", dependencies=[Depends(require_dekan)])
def train_clusters(n_clusters: int = 5, db: Session = Depends(get_olap_db)):
    return student_clusterer.train(db, n_clusters)


@router.get("/clustering/student/{student_id}", dependencies=[Depends(require_any)])
def cluster_predict(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)
    return student_clusterer.predict_cluster(olap, student.student_id) or {}


@router.get("/clustering/all", dependencies=[Depends(require_dekan)])
def clusters_all(db: Session = Depends(get_olap_db)):
    return student_clusterer.list_all_clusters(db)


# ============================================================
# FORECASTING
# ============================================================


@router.get("/forecast/student/{student_id}", dependencies=[Depends(require_any)])
def forecast_student(
    student_id: int,
    horizon: int = 3,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)
    return gpa_forecaster.forecast_student(olap, student.student_id, horizon)


@router.get("/forecast/faculty/{faculty_name}", dependencies=[Depends(require_dekan)])
def forecast_faculty(faculty_name: str, db: Session = Depends(get_olap_db)):
    return gpa_forecaster.forecast_faculty(db, faculty_name)


@router.get("/forecast/enrollment", dependencies=[Depends(require_dekan)])
def forecast_enrollment(db: Session = Depends(get_olap_db)):
    return gpa_forecaster.enrollment_forecast(db)


# ============================================================
# ANOMALY DETECTION (Isolation Forest)
# ============================================================


@router.get("/anomalies/students", dependencies=[Depends(require_dekan)])
def anomalies_students(db: Session = Depends(get_olap_db)):
    return {"items": anomaly_detector.detect_student_anomalies(db)}


@router.get("/anomalies/teachers", dependencies=[Depends(require_dekan)])
def anomalies_teachers(db: Session = Depends(get_olap_db)):
    return {"items": anomaly_detector.detect_teacher_anomalies(db)}


@router.get("/anomalies/subjects", dependencies=[Depends(require_dekan)])
def subject_difficulty(db: Session = Depends(get_olap_db)):
    return {"items": anomaly_detector.detect_subject_difficulty(db)}


# ============================================================
# AI TUTOR (Claude/OpenAI)
# ============================================================


class ChatMessage(BaseModel):
    role: str
    content: str


class TutorChat(BaseModel):
    message: str
    history: list[ChatMessage] = []


@router.post("/tutor/chat", dependencies=[Depends(require_any)])
def tutor_chat(
    payload: TutorChat,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
    user: User = Depends(get_current_user),
):
    """AI Tutor — talaba bilan suhbat."""
    # Joriy talabani topish
    student = (
        oltp.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )
    if not student and user.username == "student":
        student = oltp.query(Student).first()
    if not student:
        raise HTTPException(404, "Talaba hisobi yo'q")

    history = [{"role": m.role, "content": m.content} for m in payload.history]
    return ai_tutor.chat(olap, student.student_id, payload.message, history)
