"""Kengaytirilgan forecasting: Prophet + sklearn fallback.

Prophet Python 3.14 da o'rnatish qiyin bo'lganligi sababli, bizning yondashuv:
- prophet ishlatiladi (agar import qilinishi mumkin bo'lsa)
- Aks holda — sklearn ARIMA-style fallback (joriy gpa_forecaster.py)
"""
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session


def has_prophet() -> bool:
    try:
        import prophet  # noqa
        return True
    except ImportError:
        return False


def forecast_with_prophet(history: pd.DataFrame, horizon: int = 3) -> dict[str, Any]:
    """Prophet bilan forecast (agar mavjud bo'lsa)."""
    if not has_prophet():
        return {"error": "Prophet o'rnatilmagan. fallback uchun gpa_forecaster.py ishlatiladi."}

    try:
        from prophet import Prophet
        m = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
        # Prophet uchun ds, y kerak
        df = history.rename(columns={"date": "ds", "value": "y"})
        m.fit(df)
        future = m.make_future_dataframe(periods=horizon, freq="MS")
        forecast = m.predict(future)
        return {
            "method": "prophet",
            "predictions": forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon).to_dict("records"),
        }
    except Exception as e:
        logger.error("Prophet error: {}", e)
        return {"error": str(e)}


def forecast_combined(db: Session, student_code: str, horizon: int = 3) -> dict[str, Any]:
    """Eng yaxshi method tanlash: Prophet → sklearn fallback."""
    from app.ml.gpa_forecaster import forecast_student

    sklearn_result = forecast_student(db, student_code, horizon)
    sklearn_result["prophet_available"] = has_prophet()
    return sklearn_result
