"""ML uchun Celery tasklar — retrain, alerts."""
from loguru import logger

from app.database import oltp_session, olap_session
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.ml_tasks.retrain_all_models")
def retrain_all_models() -> dict:
    """Barcha ML modellarni qayta o'qitish (har hafta)."""
    from app.ml import dropout_predictor, student_clusterer

    results = {}
    with olap_session() as db:
        try:
            r = dropout_predictor.train(db)
            results["dropout_xgb"] = r
        except Exception as e:
            results["dropout_xgb"] = {"error": str(e)}

        try:
            r = student_clusterer.train(db, n_clusters=5)
            results["kmeans"] = r
        except Exception as e:
            results["kmeans"] = {"error": str(e)}

    logger.info("ML retrain: {}", results)
    return results


@celery_app.task(name="app.tasks.ml_tasks.send_dropout_alerts")
def send_dropout_alerts() -> dict:
    """Kritik xavf zonasidagi talabalarga va dekanlarga ogohlantirish yuborish."""
    from app.ml import dropout_predictor
    from app.models.oltp.user import User, UserRole
    from app.services import notification_service

    with olap_session() as olap, oltp_session() as oltp:
        at_risk = dropout_predictor.predict_all(olap, top_n=20)
        critical = [s for s in at_risk if s.get("risk_code") == "critical"]

        if not critical:
            return {"alerts_sent": 0}

        # Dekanlarga xabar
        deans = oltp.query(User).filter(User.role.in_([UserRole.DEKAN, UserRole.RECTOR])).all()
        for dean in deans:
            notification_service.create_notification(
                oltp,
                user_id=dean.id,
                title="Drop-out kritik xavfi",
                message=f"Bu hafta {len(critical)} ta talaba kritik holatda. Tezkor choralar ko'rish kerak.",
                notification_type="error",
                link="/ml-insights",
                send_email=True,
            )

    return {"critical_count": len(critical), "deans_notified": len(deans)}
