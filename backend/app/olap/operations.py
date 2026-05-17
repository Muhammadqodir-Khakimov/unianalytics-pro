"""OLAP operatsiyalari — slice, dice, drill-down, roll-up, pivot.

Bu modul yuqori darajadagi API: foydalanuvchi operatsiya parametrlarini beradi,
ichkarida OLAPQueryBuilder ishlatiladi.
"""
from typing import Any, List

from sqlalchemy.orm import Session

from app.olap.cube import CubeDefinition, get_cube
from app.olap.query_builder import FilterClause, OLAPQuery, OLAPQueryBuilder


def execute_query(
    db: Session,
    cube_name: str,
    dimensions: List[dict],
    measures: List[str],
    filters: List[dict] | None = None,
    order_by: List[str] | None = None,
    limit: int | None = None,
    grouping_mode: str = "GROUP BY",
) -> List[dict[str, Any]]:
    """Universal OLAP query."""
    cube = get_cube(cube_name)
    query = OLAPQuery(
        cube_name=cube_name,
        dimensions=dimensions,
        measures=measures,
        filters=[FilterClause(**f) for f in (filters or [])],
        order_by=order_by or [],
        limit=limit,
        grouping_mode=grouping_mode,
    )
    return OLAPQueryBuilder(cube).execute(db, query)


def slice_operation(
    db: Session,
    dimension: str,
    attribute: str,
    value: Any,
    group_by_dimensions: List[dict],
    measures: List[str],
    cube_name: str = "student_grades",
) -> List[dict]:
    """SLICE: bitta o'lchov bo'yicha bitta qiymatga filtrlash.

    Misol: faqat 2024-2025 o'quv yili bo'yicha fakultet kesimida o'rtacha ball.
    """
    filters = [{"dimension": dimension, "attribute": attribute, "operator": "=", "value": value}]
    return execute_query(db, cube_name, group_by_dimensions, measures, filters)


def dice_operation(
    db: Session,
    filters: List[dict],
    group_by_dimensions: List[dict],
    measures: List[str],
    cube_name: str = "student_grades",
) -> List[dict]:
    """DICE: bir nechta o'lchov bo'yicha filtrlash (Slice ning umumlashgan ko'rinishi)."""
    return execute_query(db, cube_name, group_by_dimensions, measures, filters)


def drill_down(
    db: Session,
    dimension: str,
    from_level: str,
    to_level: str,
    parent_filter: dict | None,
    measures: List[str],
    cube_name: str = "student_grades",
) -> dict:
    """DRILL-DOWN: yuqori darajadan past darajaga tushish.

    Misol: faculty_name -> specialty -> group_name.
    Agar parent_filter berilsa (masalan, "Informatika fakulteti"), faqat shu fakultet
    ichidagi yo'nalishlar/guruhlar qaytariladi.
    """
    cube = get_cube(cube_name)
    dim = cube.dimension_by_name(dimension)

    # Ierarxiyalarni topish
    hierarchy = None
    for h in dim.hierarchies:
        if from_level in h.levels and to_level in h.levels:
            hierarchy = h
            break
    if not hierarchy:
        raise ValueError(f"Ierarxiya topilmadi: {from_level} -> {to_level}")

    if hierarchy.levels.index(to_level) <= hierarchy.levels.index(from_level):
        raise ValueError("Drill-down faqat yuqoridan pastga ishlaydi")

    filters = []
    if parent_filter:
        filters.append(parent_filter)

    dimensions = [{"dimension": dimension, "attribute": to_level}]
    rows = execute_query(db, cube_name, dimensions, measures, filters, limit=1000)
    return {
        "operation": "drill_down",
        "from_level": from_level,
        "to_level": to_level,
        "parent_filter": parent_filter,
        "rows": rows,
    }


def roll_up(
    db: Session,
    dimension: str,
    from_level: str,
    to_level: str,
    measures: List[str],
    cube_name: str = "student_grades",
) -> dict:
    """ROLL-UP: past darajadan yuqori darajaga ko'tarilish (drill-down ning teskarisi)."""
    cube = get_cube(cube_name)
    dim = cube.dimension_by_name(dimension)

    hierarchy = None
    for h in dim.hierarchies:
        if from_level in h.levels and to_level in h.levels:
            hierarchy = h
            break
    if not hierarchy:
        raise ValueError(f"Ierarxiya topilmadi")

    if hierarchy.levels.index(to_level) >= hierarchy.levels.index(from_level):
        raise ValueError("Roll-up faqat pastdan yuqoriga ishlaydi")

    dimensions = [{"dimension": dimension, "attribute": to_level}]
    rows = execute_query(db, cube_name, dimensions, measures, limit=1000)
    return {
        "operation": "roll_up",
        "from_level": from_level,
        "to_level": to_level,
        "rows": rows,
    }


def pivot_operation(
    db: Session,
    row_dimension: dict,
    column_dimension: dict,
    measure: str,
    filters: List[dict] | None = None,
    cube_name: str = "student_grades",
) -> dict:
    """PIVOT: qator va ustun o'lchovlari bilan jadval ko'rinishida.

    Natija: { rows: [...], columns: [...], matrix: { row_value: { col_value: measure } } }
    """
    dimensions = [row_dimension, column_dimension]
    raw_rows = execute_query(db, cube_name, dimensions, [measure], filters, limit=10000)

    row_alias = f"{row_dimension['dimension']}_{row_dimension['attribute']}"
    col_alias = f"{column_dimension['dimension']}_{column_dimension['attribute']}"

    rows: set = set()
    cols: set = set()
    matrix: dict[Any, dict[Any, Any]] = {}

    for r in raw_rows:
        row_v = r.get(row_alias)
        col_v = r.get(col_alias)
        val = r.get(measure)
        rows.add(row_v)
        cols.add(col_v)
        matrix.setdefault(row_v, {})[col_v] = val

    return {
        "operation": "pivot",
        "row_dimension": row_alias,
        "column_dimension": col_alias,
        "measure": measure,
        "rows": sorted(rows, key=lambda x: (x is None, x)),
        "columns": sorted(cols, key=lambda x: (x is None, x)),
        "matrix": matrix,
    }


def cube_aggregate(
    db: Session,
    dimensions: List[dict],
    measures: List[str],
    filters: List[dict] | None = None,
    grouping_mode: str = "CUBE",
    cube_name: str = "student_grades",
) -> List[dict]:
    """CUBE / ROLLUP / GROUPING SETS — barcha mumkin kombinatsiyalar uchun agregatsiya."""
    return execute_query(
        db,
        cube_name,
        dimensions,
        measures,
        filters,
        grouping_mode=grouping_mode,
        limit=10000,
    )


def list_dimensions(cube_name: str = "student_grades") -> List[dict]:
    cube = get_cube(cube_name)
    return [
        {
            "name": d.name,
            "label": d.label,
            "table": d.table,
            "attributes": d.attributes,
            "hierarchies": [{"name": h.name, "levels": h.levels} for h in d.hierarchies],
        }
        for d in cube.dimensions
    ]


def list_measures(cube_name: str = "student_grades") -> List[dict]:
    cube = get_cube(cube_name)
    return [
        {
            "name": m.name,
            "label": m.label,
            "aggregation": m.aggregation,
            "format": m.format,
        }
        for m in cube.measures
    ]
