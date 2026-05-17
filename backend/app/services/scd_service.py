"""SCD Type 2 (Slowly Changing Dimensions) — talaba ma'lumotlari tarixini saqlash.

OLAP DB da dim_student ga history saqlash uchun:
- valid_from / valid_to / is_current ustunlar
- Ma'lumot o'zgarganda — yangi yozuv yaratiladi, eski yozuv yopiladi.
"""
from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session


def upsert_scd2(db: Session, table: str, key_field: str, key_value: Any, attrs: dict) -> int:
    """SCD Type 2 upsert.

    1. Joriy yozuvni topish (is_current=true)
    2. Agar attributelar o'zgargan bo'lsa:
       - Eski yozuvni yopish (valid_to = today, is_current=false)
       - Yangi yozuv qo'shish (valid_from=today, is_current=true)
    3. Agar mavjud emas bo'lsa — yangi yozuv qo'shish
    """
    # Joriy yozuvni topish
    current = db.execute(
        text(f"SELECT * FROM {table} WHERE {key_field} = :v AND is_current = TRUE"),
        {"v": key_value},
    ).mappings().first()

    if current:
        # Tekshirish — biron-bir attribute o'zgarganmi
        changed = any(
            current.get(k) != v for k, v in attrs.items() if k in current
        )
        if not changed:
            return current[f"{table.replace('dim_', '')}_key"] if f"{table.replace('dim_', '')}_key" in current else 0

        # Eski yozuvni yopish
        db.execute(
            text(f"UPDATE {table} SET valid_to = :t, is_current = FALSE WHERE {key_field} = :v AND is_current = TRUE"),
            {"t": date.today().isoformat(), "v": key_value},
        )

    # Yangi yozuv qo'shish
    cols = list(attrs.keys()) + [key_field, "valid_from", "is_current"]
    vals = list(attrs.values()) + [key_value, date.today().isoformat(), True]
    placeholders = ", ".join([f":{c}" for c in cols])

    db.execute(
        text(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"),
        dict(zip(cols, vals)),
    )
    db.commit()
    logger.debug("SCD2 upsert: {}={}", key_field, key_value)
    return 0  # ID returning required separate logic


def get_history(db: Session, table: str, key_field: str, key_value: Any) -> list[dict]:
    """Talaba ma'lumotlari tarixini olish (oldingi versiyalar)."""
    rows = db.execute(
        text(f"SELECT * FROM {table} WHERE {key_field} = :v ORDER BY valid_from"),
        {"v": key_value},
    ).mappings().all()
    return [dict(r) for r in rows]
