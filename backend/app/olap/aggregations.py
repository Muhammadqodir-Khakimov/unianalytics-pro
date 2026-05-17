"""Agregatsiya funksiyalari — SQL darajasida xavfsiz mapping."""
from typing import Final

ALLOWED_AGGREGATIONS: Final[set[str]] = {"AVG", "SUM", "COUNT", "MIN", "MAX", "COUNT_DISTINCT"}


def build_aggregation_expr(aggregation: str, column: str) -> str:
    """SQL agregatsiya ifodasini xavfsiz qurish.

    SQL injection oldini olish uchun aggregation va column nomi tekshiriladi.
    """
    agg = aggregation.upper().strip()
    if agg not in ALLOWED_AGGREGATIONS:
        raise ValueError(f"Yaroqsiz agregatsiya: {agg}")

    # Column nomi faqat harf, raqam va _ dan iborat bo'lishi mumkin
    if not column.replace("_", "").replace(".", "").isalnum():
        raise ValueError(f"Yaroqsiz ustun nomi: {column}")

    if agg == "COUNT_DISTINCT":
        return f"COUNT(DISTINCT {column})"
    if agg == "SUM" and "is_passed" in column.lower():
        return f"SUM(CASE WHEN {column} THEN 1 ELSE 0 END)"
    return f"{agg}({column})"
