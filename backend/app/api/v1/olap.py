"""OLAP API endpointlari — kub bilan ko'p o'lchovli tahlil."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_olap_db
from app.olap import operations as ops
from app.olap.cube import get_cube
from app.olap.query_builder import FilterClause, OLAPQuery, OLAPQueryBuilder
from app.schemas.olap import (
    CubeAggregateSchema,
    DiceSchema,
    DrillSchema,
    OLAPQuerySchema,
    OLAPResultResponse,
    PivotSchema,
    SliceSchema,
)

router = APIRouter(prefix="/olap", tags=["OLAP"], dependencies=[Depends(require_any)])


@router.get("/dimensions")
def get_dimensions(cube_name: str = "student_grades"):
    """Kub o'lchovlari ro'yxati (frontend metadata uchun)."""
    return ops.list_dimensions(cube_name)


@router.get("/measures")
def get_measures(cube_name: str = "student_grades"):
    """Kub o'lchamlari ro'yxati."""
    return ops.list_measures(cube_name)


@router.get("/cube/metadata")
def get_cube_metadata(cube_name: str = "student_grades"):
    """Kub haqida to'liq metadata."""
    cube = get_cube(cube_name)
    return {
        "name": cube.name,
        "description": cube.description,
        "fact_table": cube.fact_table,
        "dimensions": ops.list_dimensions(cube_name),
        "measures": ops.list_measures(cube_name),
    }


@router.post("/query", response_model=OLAPResultResponse)
def olap_query(payload: OLAPQuerySchema, db: Session = Depends(get_olap_db)):
    """Universal OLAP so'rov — SELECT + GROUP BY + agregatsiya."""
    cube = get_cube(payload.cube_name)
    query = OLAPQuery(
        cube_name=payload.cube_name,
        dimensions=[d.model_dump() for d in payload.dimensions],
        measures=payload.measures,
        filters=[FilterClause(**f.model_dump()) for f in payload.filters],
        order_by=payload.order_by,
        limit=payload.limit,
        grouping_mode=payload.grouping_mode,
    )
    builder = OLAPQueryBuilder(cube)
    sql, _ = builder.build(query)
    rows = builder.execute(db, query)
    return OLAPResultResponse(rows=rows, row_count=len(rows), sql=sql)


@router.post("/slice", response_model=OLAPResultResponse)
def olap_slice(payload: SliceSchema, db: Session = Depends(get_olap_db)):
    """SLICE: bir o'lchov, bir qiymat bo'yicha filtrlash."""
    rows = ops.slice_operation(
        db=db,
        dimension=payload.dimension,
        attribute=payload.attribute,
        value=payload.value,
        group_by_dimensions=[d.model_dump() for d in payload.group_by_dimensions],
        measures=payload.measures,
    )
    return OLAPResultResponse(rows=rows, row_count=len(rows))


@router.post("/dice", response_model=OLAPResultResponse)
def olap_dice(payload: DiceSchema, db: Session = Depends(get_olap_db)):
    """DICE: bir nechta filter."""
    rows = ops.dice_operation(
        db=db,
        filters=[f.model_dump() for f in payload.filters],
        group_by_dimensions=[d.model_dump() for d in payload.group_by_dimensions],
        measures=payload.measures,
    )
    return OLAPResultResponse(rows=rows, row_count=len(rows))


@router.post("/drill-down")
def olap_drill_down(payload: DrillSchema, db: Session = Depends(get_olap_db)):
    """DRILL-DOWN: yuqori daraja -> past daraja."""
    return ops.drill_down(
        db=db,
        dimension=payload.dimension,
        from_level=payload.from_level,
        to_level=payload.to_level,
        parent_filter=payload.parent_filter.model_dump() if payload.parent_filter else None,
        measures=payload.measures,
    )


@router.post("/roll-up")
def olap_roll_up(payload: DrillSchema, db: Session = Depends(get_olap_db)):
    """ROLL-UP: past daraja -> yuqori daraja."""
    return ops.roll_up(
        db=db,
        dimension=payload.dimension,
        from_level=payload.from_level,
        to_level=payload.to_level,
        measures=payload.measures,
    )


@router.post("/pivot")
def olap_pivot(payload: PivotSchema, db: Session = Depends(get_olap_db)):
    """PIVOT: qator x ustun matritsa."""
    return ops.pivot_operation(
        db=db,
        row_dimension=payload.row_dimension.model_dump(),
        column_dimension=payload.column_dimension.model_dump(),
        measure=payload.measure,
        filters=[f.model_dump() for f in payload.filters],
    )


@router.post("/cube/aggregate", response_model=OLAPResultResponse)
def cube_aggregate_endpoint(payload: CubeAggregateSchema, db: Session = Depends(get_olap_db)):
    """CUBE / ROLLUP / GROUPING SETS — barcha kombinatsiyalar."""
    rows = ops.cube_aggregate(
        db=db,
        dimensions=[d.model_dump() for d in payload.dimensions],
        measures=payload.measures,
        filters=[f.model_dump() for f in payload.filters],
        grouping_mode=payload.grouping_mode,
    )
    return OLAPResultResponse(rows=rows, row_count=len(rows))
