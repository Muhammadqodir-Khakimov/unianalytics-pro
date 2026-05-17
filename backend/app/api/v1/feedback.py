"""Anonim feedback endpointlari (Sprint 6.2)."""
import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_dekan
from app.database import get_oltp_db
from app.models.oltp.feedback import TeacherFeedback
from app.models.oltp.teacher import Teacher
from app.models.oltp.user import User
from app.services import sentiment_service

router = APIRouter(prefix="/feedback", tags=["Feedback (Anonim)"])


class FeedbackSubmit(BaseModel):
    teacher_id: int
    subject_id: int | None = None
    semester: str = "kuzgi"
    academic_year: str = "2024-2025"
    rating_teaching: int = Field(..., ge=1, le=5)
    rating_knowledge: int = Field(..., ge=1, le=5)
    rating_attitude: int = Field(..., ge=1, le=5)
    rating_fairness: int = Field(..., ge=1, le=5)
    rating_availability: int = Field(..., ge=1, le=5)
    comment: str | None = None


def _anonymize(user_id: int, teacher_id: int, semester: str) -> str:
    """User ni anonim qilish (rate limiting uchun)."""
    raw = f"{user_id}-{teacher_id}-{semester}-secret-salt"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


@router.post("/submit")
def submit_feedback(
    payload: FeedbackSubmit,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Anonim feedback yuborish.

    User ID hash qilinadi — talaba ma'lumotlari saqlanmaydi.
    Bir user bir teacher uchun bir semestrda faqat 1 marta fikr bera oladi.
    """
    teacher = db.query(Teacher).filter(Teacher.id == payload.teacher_id).first()
    if not teacher:
        raise HTTPException(404, "O'qituvchi topilmadi")

    anon_id = _anonymize(user.id, payload.teacher_id, payload.semester)

    # Bir martadan ko'p emas
    existing = (
        db.query(TeacherFeedback)
        .filter(
            TeacherFeedback.anonymous_id == anon_id,
            TeacherFeedback.teacher_id == payload.teacher_id,
            TeacherFeedback.semester == payload.semester,
            TeacherFeedback.academic_year == payload.academic_year,
        )
        .first()
    )
    if existing:
        raise HTTPException(409, "Siz bu o'qituvchi uchun bu semesterda feedback yuborgansiz")

    overall = (
        payload.rating_teaching + payload.rating_knowledge + payload.rating_attitude
        + payload.rating_fairness + payload.rating_availability
    ) / 5.0

    # Sentiment analysis
    sent = sentiment_service.analyze_sentiment(payload.comment or "")

    fb = TeacherFeedback(
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        semester=payload.semester,
        academic_year=payload.academic_year,
        anonymous_id=anon_id,
        rating_teaching=payload.rating_teaching,
        rating_knowledge=payload.rating_knowledge,
        rating_attitude=payload.rating_attitude,
        rating_fairness=payload.rating_fairness,
        rating_availability=payload.rating_availability,
        rating_overall=overall,
        comment=payload.comment,
        sentiment_label=sent["label"],
        sentiment_score=sent["score"],
        toxicity_flag=sent.get("toxicity", False),
    )
    db.add(fb)
    db.commit()

    return {"success": True, "rating_overall": overall, "sentiment": sent}


@router.get("/teacher/{teacher_id}", dependencies=[Depends(require_dekan)])
def teacher_feedback_summary(teacher_id: int, db: Session = Depends(get_oltp_db)):
    """O'qituvchi haqida agregatsiyalangan feedback."""
    feedbacks = db.query(TeacherFeedback).filter(TeacherFeedback.teacher_id == teacher_id).all()
    if not feedbacks:
        return {"teacher_id": teacher_id, "total_feedbacks": 0}

    avg = {
        "teaching": sum(f.rating_teaching for f in feedbacks) / len(feedbacks),
        "knowledge": sum(f.rating_knowledge for f in feedbacks) / len(feedbacks),
        "attitude": sum(f.rating_attitude for f in feedbacks) / len(feedbacks),
        "fairness": sum(f.rating_fairness for f in feedbacks) / len(feedbacks),
        "availability": sum(f.rating_availability for f in feedbacks) / len(feedbacks),
        "overall": sum(float(f.rating_overall) for f in feedbacks) / len(feedbacks),
    }

    sentiments = {
        "positive": sum(1 for f in feedbacks if f.sentiment_label == "positive"),
        "negative": sum(1 for f in feedbacks if f.sentiment_label == "negative"),
        "neutral": sum(1 for f in feedbacks if f.sentiment_label == "neutral"),
    }

    word_cloud = sentiment_service.generate_word_cloud_data(
        [f.comment for f in feedbacks if f.comment]
    )

    return {
        "teacher_id": teacher_id,
        "total_feedbacks": len(feedbacks),
        "ratings_avg": {k: round(v, 2) for k, v in avg.items()},
        "sentiment_distribution": sentiments,
        "word_cloud": word_cloud,
        "toxicity_count": sum(1 for f in feedbacks if f.toxicity_flag),
        "recent_comments": [
            {
                "comment": f.comment,
                "sentiment": f.sentiment_label,
                "rating": float(f.rating_overall),
                "date": f.submitted_at.isoformat(),
            }
            for f in sorted(feedbacks, key=lambda x: x.submitted_at, reverse=True)[:10]
            if f.comment
        ],
    }


@router.get("/lowest-rated", dependencies=[Depends(require_dekan)])
def lowest_rated_teachers(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_oltp_db)):
    """Eng past reyting'li o'qituvchilar (rektor uchun)."""
    rows = (
        db.query(
            TeacherFeedback.teacher_id,
            func.avg(TeacherFeedback.rating_overall).label("avg_rating"),
            func.count(TeacherFeedback.id).label("count"),
        )
        .group_by(TeacherFeedback.teacher_id)
        .having(func.count(TeacherFeedback.id) >= 3)
        .order_by(func.avg(TeacherFeedback.rating_overall).asc())
        .limit(limit)
        .all()
    )

    out = []
    for r in rows:
        teacher = db.query(Teacher).filter(Teacher.id == r.teacher_id).first()
        if teacher:
            out.append({
                "teacher_id": teacher.id,
                "full_name": teacher.full_name,
                "department": teacher.department,
                "avg_rating": round(float(r.avg_rating), 2),
                "feedback_count": int(r.count),
            })
    return out


@router.get("/sentiment-trends", dependencies=[Depends(require_dekan)])
def sentiment_trends(db: Session = Depends(get_oltp_db)):
    """Sentiment trendlari vaqt bo'yicha."""
    feedbacks = db.query(TeacherFeedback).all()
    if not feedbacks:
        return {"trends": [], "summary": {}}

    by_month: dict = {}
    for f in feedbacks:
        ym = f.submitted_at.strftime("%Y-%m")
        if ym not in by_month:
            by_month[ym] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
        by_month[ym][f.sentiment_label or "neutral"] += 1
        by_month[ym]["total"] += 1

    trends = [
        {
            "month": ym,
            "positive_pct": round(d["positive"] * 100 / d["total"], 1),
            "negative_pct": round(d["negative"] * 100 / d["total"], 1),
            "total": d["total"],
        }
        for ym, d in sorted(by_month.items())
    ]

    return {
        "trends": trends,
        "summary": {
            "total_feedbacks": len(feedbacks),
            "positive": sum(1 for f in feedbacks if f.sentiment_label == "positive"),
            "negative": sum(1 for f in feedbacks if f.sentiment_label == "negative"),
            "neutral": sum(1 for f in feedbacks if f.sentiment_label == "neutral"),
        },
    }
