"""OLAP uchun dinamik SQL query builder.

Foydalanuvchi tanlagan dimension va measure-larga asoslanib xavfsiz SQL hosil qiladi.
Parameterlangan querylardan foydalanadi (SQL injection xavfini kamaytirish uchun).
"""
from dataclasses import dataclass, field
from typing import Any, List

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.olap.aggregations import build_aggregation_expr
from app.olap.cube import CubeDefinition


@dataclass
class FilterClause:
    """Slice/Dice uchun filter."""

    dimension: str
    attribute: str
    operator: str = "="  # =, !=, IN, NOT IN, >, <, >=, <=, BETWEEN, LIKE
    value: Any = None
    values: List[Any] | None = None  # IN, BETWEEN uchun


@dataclass
class OLAPQuery:
    """OLAP so'rovni tasvirlovchi struktura."""

    cube_name: str = "student_grades"
    dimensions: List[dict] = field(default_factory=list)  # [{"dimension": "faculty", "attribute": "faculty_name"}]
    measures: List[str] = field(default_factory=list)  # ["avg_grade", "total_grades"]
    filters: List[FilterClause] = field(default_factory=list)
    order_by: List[str] = field(default_factory=list)
    limit: int | None = None
    grouping_mode: str = "GROUP BY"  # GROUP BY, CUBE, ROLLUP, GROUPING SETS


class OLAPQueryBuilder:
    """Cube + OLAPQuery -> xavfsiz SQL.

    Misol:
        builder = OLAPQueryBuilder(cube)
        sql, params = builder.build(query)
        result = db.execute(text(sql), params).mappings().all()
    """

    def __init__(self, cube: CubeDefinition):
        self.cube = cube

    def build(self, query: OLAPQuery) -> tuple[str, dict[str, Any]]:
        """SQL stringini va parametrlarni qaytaradi."""
        select_parts: List[str] = []
        group_parts: List[str] = []
        join_parts: List[str] = []
        joined_dims: set[str] = set()
        params: dict[str, Any] = {}

        # 1. SELECT: dimension columns
        for i, d in enumerate(query.dimensions):
            dim = self.cube.dimension_by_name(d["dimension"])
            attr = d["attribute"]
            self._validate_attribute(dim, attr)
            col = f"{dim.table}.{attr}"
            alias = f"{dim.name}_{attr}"
            select_parts.append(f"{col} AS {alias}")
            group_parts.append(col)
            self._add_join(dim, joined_dims, join_parts)

        # 2. SELECT: measures
        if not query.measures:
            query.measures = ["avg_grade", "total_grades"]

        for m_name in query.measures:
            measure = self.cube.measure_by_name(m_name)
            column = f"{self.cube.fact_table}.{measure.column}"
            expr = build_aggregation_expr(measure.aggregation, column)
            select_parts.append(f"{expr} AS {measure.name}")

        # 3. JOIN: filter ishlatadigan dimensionlarni qo'shish
        for f in query.filters:
            dim = self.cube.dimension_by_name(f.dimension)
            self._add_join(dim, joined_dims, join_parts)

        # 4. WHERE
        where_parts: List[str] = []
        for idx, f in enumerate(query.filters):
            dim = self.cube.dimension_by_name(f.dimension)
            self._validate_attribute(dim, f.attribute)
            col = f"{dim.table}.{f.attribute}"
            clause, p = self._build_filter(col, f, idx)
            where_parts.append(clause)
            params.update(p)

        # 5. GROUP BY (yoki CUBE/ROLLUP)
        group_clause = ""
        if group_parts:
            if query.grouping_mode in ("CUBE", "ROLLUP"):
                group_clause = f"GROUP BY {query.grouping_mode}({', '.join(group_parts)})"
            elif query.grouping_mode == "GROUPING SETS":
                # default: ((all), (each)) — drilldown uchun foydali
                sets = ", ".join([f"({g})" for g in group_parts])
                group_clause = f"GROUP BY GROUPING SETS ({sets}, ())"
            else:
                group_clause = f"GROUP BY {', '.join(group_parts)}"

        # 6. ORDER BY
        order_clause = ""
        if query.order_by:
            safe_orders = []
            for o in query.order_by:
                direction = "ASC"
                col = o.strip()
                if col.upper().endswith(" DESC"):
                    direction = "DESC"
                    col = col[:-5].strip()
                elif col.upper().endswith(" ASC"):
                    col = col[:-4].strip()
                if not col.replace("_", "").isalnum():
                    continue
                safe_orders.append(f"{col} {direction}")
            if safe_orders:
                order_clause = f"ORDER BY {', '.join(safe_orders)}"

        # 7. LIMIT
        limit_clause = f"LIMIT {int(query.limit)}" if query.limit else ""

        sql = f"""
            SELECT {', '.join(select_parts)}
            FROM {self.cube.fact_table}
            {' '.join(join_parts)}
            {f"WHERE {' AND '.join(where_parts)}" if where_parts else ""}
            {group_clause}
            {order_clause}
            {limit_clause}
        """.strip()

        return sql, params

    def execute(self, db: Session, query: OLAPQuery) -> List[dict[str, Any]]:
        """Querini ishga tushiradi va natijani dict ko'rinishida qaytaradi."""
        sql, params = self.build(query)
        result = db.execute(text(sql), params).mappings().all()
        return [dict(row) for row in result]

    # Internal helpers
    def _add_join(self, dim, joined: set[str], join_parts: List[str]) -> None:
        if dim.name in joined:
            return
        join_parts.append(
            f"LEFT JOIN {dim.table} ON "
            f"{self.cube.fact_table}.{dim.fact_fk} = {dim.table}.{dim.key_column}"
        )
        joined.add(dim.name)

    def _validate_attribute(self, dim, attr: str) -> None:
        if attr not in dim.attributes:
            raise ValueError(f"'{attr}' atributi '{dim.name}' o'lchovida mavjud emas")

    def _build_filter(self, col: str, f: FilterClause, idx: int) -> tuple[str, dict]:
        op = f.operator.upper()
        if op in ("=", "!=", ">", "<", ">=", "<=", "LIKE"):
            key = f"p_{f.dimension}_{f.attribute}_{idx}"
            return f"{col} {op} :{key}", {key: f.value}
        if op in ("IN", "NOT IN"):
            values = f.values or [f.value]
            keys = [f"p_{f.dimension}_{f.attribute}_{idx}_{i}" for i in range(len(values))]
            placeholders = ", ".join(f":{k}" for k in keys)
            return f"{col} {op} ({placeholders})", dict(zip(keys, values))
        if op == "BETWEEN":
            values = f.values or [0, 0]
            k1, k2 = f"p_btw_{idx}_a", f"p_btw_{idx}_b"
            return f"{col} BETWEEN :{k1} AND :{k2}", {k1: values[0], k2: values[1]}
        raise ValueError(f"Yaroqsiz operator: {op}")
