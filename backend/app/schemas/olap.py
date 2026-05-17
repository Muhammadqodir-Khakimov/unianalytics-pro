"""OLAP API uchun Pydantic sxemalari."""
from typing import Any, List, Literal

from pydantic import BaseModel, Field


class DimensionSelect(BaseModel):
    """SELECT/GROUP BY uchun dimension+attribute juftligi."""

    dimension: str = Field(..., description="dim_* nomi (masalan, 'faculty')")
    attribute: str = Field(..., description="dim ustuni (masalan, 'faculty_name')")


class FilterClauseSchema(BaseModel):
    dimension: str
    attribute: str
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "IN", "NOT IN", "BETWEEN", "LIKE"] = "="
    value: Any | None = None
    values: List[Any] | None = None


class OLAPQuerySchema(BaseModel):
    """Universal OLAP query."""

    cube_name: str = "student_grades"
    dimensions: List[DimensionSelect] = []
    measures: List[str] = ["avg_grade", "total_grades"]
    filters: List[FilterClauseSchema] = []
    order_by: List[str] = []
    limit: int | None = Field(None, ge=1, le=100000)
    grouping_mode: Literal["GROUP BY", "CUBE", "ROLLUP", "GROUPING SETS"] = "GROUP BY"


class SliceSchema(BaseModel):
    dimension: str
    attribute: str
    value: Any
    group_by_dimensions: List[DimensionSelect]
    measures: List[str] = ["avg_grade"]


class DiceSchema(BaseModel):
    filters: List[FilterClauseSchema]
    group_by_dimensions: List[DimensionSelect]
    measures: List[str] = ["avg_grade"]


class DrillSchema(BaseModel):
    dimension: str
    from_level: str
    to_level: str
    parent_filter: FilterClauseSchema | None = None
    measures: List[str] = ["avg_grade", "total_grades"]


class PivotSchema(BaseModel):
    row_dimension: DimensionSelect
    column_dimension: DimensionSelect
    measure: str = "avg_grade"
    filters: List[FilterClauseSchema] = []


class CubeAggregateSchema(BaseModel):
    dimensions: List[DimensionSelect]
    measures: List[str] = ["avg_grade"]
    filters: List[FilterClauseSchema] = []
    grouping_mode: Literal["CUBE", "ROLLUP", "GROUPING SETS"] = "CUBE"


class OLAPResultRow(BaseModel):
    """Bitta natija qatori — dinamik kalitlar bilan."""

    model_config = {"extra": "allow"}


class OLAPResultResponse(BaseModel):
    rows: List[dict[str, Any]]
    row_count: int
    sql: str | None = None
