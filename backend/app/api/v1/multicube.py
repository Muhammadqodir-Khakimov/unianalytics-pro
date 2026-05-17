"""5 ta multi-cube uchun universal API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_olap_db
from app.olap.cubes import ALL_CUBES, get_cube_v2, list_cubes
from app.olap.query_builder import FilterClause, OLAPQuery, OLAPQueryBuilder
from app.olap import operations as ops
from app.schemas.olap import OLAPQuerySchema, OLAPResultResponse

router = APIRouter(prefix="/cubes", tags=["Multi-Cube OLAP"], dependencies=[Depends(require_any)])


@router.get("")
def list_all_cubes():
    """Mavjud 5 ta cube ro'yxati."""
    return list_cubes()


@router.get("/{cube_name}/metadata")
def cube_metadata(cube_name: str):
    """Bitta cube haqida to'liq metadata."""
    try:
        cube = get_cube_v2(cube_name)
    except ValueError as e:
        raise HTTPException(404, str(e))

    return {
        "name": cube.name,
        "description": cube.description,
        "fact_table": cube.fact_table,
        "dimensions": [
            {
                "name": d.name,
                "label": d.label,
                "attributes": d.attributes,
                "hierarchies": [{"name": h.name, "levels": h.levels} for h in d.hierarchies],
            }
            for d in cube.dimensions
        ],
        "measures": [
            {"name": m.name, "label": m.label, "aggregation": m.aggregation, "format": m.format}
            for m in cube.measures
        ],
    }


@router.post("/{cube_name}/query", response_model=OLAPResultResponse)
def query_cube(cube_name: str, payload: OLAPQuerySchema, db: Session = Depends(get_olap_db)):
    """Bitta cube ga OLAP query."""
    try:
        cube = get_cube_v2(cube_name)
    except ValueError as e:
        raise HTTPException(404, str(e))

    query = OLAPQuery(
        cube_name=cube_name,
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
