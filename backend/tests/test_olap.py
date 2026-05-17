"""OLAP core unit testlari."""
import pytest

from app.olap.aggregations import build_aggregation_expr
from app.olap.cube import get_cube
from app.olap.query_builder import FilterClause, OLAPQuery, OLAPQueryBuilder


def test_cube_definition_loads():
    cube = get_cube("student_grades")
    assert cube.name == "student_grades"
    assert cube.fact_table == "fact_student_grades"
    assert len(cube.dimensions) == 6
    assert len(cube.measures) >= 6


def test_dimension_by_name():
    cube = get_cube()
    faculty = cube.dimension_by_name("faculty")
    assert faculty.table == "dim_faculty"
    assert "faculty_name" in faculty.attributes

    with pytest.raises(ValueError):
        cube.dimension_by_name("nonexistent")


def test_aggregation_expr():
    assert build_aggregation_expr("AVG", "grade_value") == "AVG(grade_value)"
    assert build_aggregation_expr("count", "id") == "COUNT(id)"
    assert "DISTINCT" in build_aggregation_expr("COUNT_DISTINCT", "student_id")


def test_aggregation_rejects_invalid():
    with pytest.raises(ValueError):
        build_aggregation_expr("DROP_TABLE", "grade_value")
    with pytest.raises(ValueError):
        build_aggregation_expr("AVG", "grade_value; DROP TABLE users")


def test_query_builder_simple():
    cube = get_cube()
    query = OLAPQuery(
        dimensions=[{"dimension": "faculty", "attribute": "faculty_name"}],
        measures=["avg_grade", "total_grades"],
    )
    builder = OLAPQueryBuilder(cube)
    sql, params = builder.build(query)

    assert "FROM fact_student_grades" in sql
    assert "dim_faculty" in sql
    assert "GROUP BY" in sql
    assert "AVG(fact_student_grades.grade_value)" in sql


def test_query_builder_with_filter():
    cube = get_cube()
    query = OLAPQuery(
        dimensions=[{"dimension": "faculty", "attribute": "faculty_name"}],
        measures=["avg_grade"],
        filters=[FilterClause(dimension="time", attribute="academic_year", operator="=", value="2024-2025")],
    )
    builder = OLAPQueryBuilder(cube)
    sql, params = builder.build(query)

    assert "WHERE" in sql
    assert "dim_time.academic_year" in sql
    assert any(v == "2024-2025" for v in params.values())


def test_query_builder_rejects_invalid_attribute():
    cube = get_cube()
    query = OLAPQuery(
        dimensions=[{"dimension": "faculty", "attribute": "DROP TABLE"}],
        measures=["avg_grade"],
    )
    with pytest.raises(ValueError):
        OLAPQueryBuilder(cube).build(query)


def test_query_builder_cube_mode():
    cube = get_cube()
    query = OLAPQuery(
        dimensions=[
            {"dimension": "faculty", "attribute": "faculty_name"},
            {"dimension": "time", "attribute": "semester"},
        ],
        measures=["avg_grade"],
        grouping_mode="CUBE",
    )
    sql, _ = OLAPQueryBuilder(cube).build(query)
    assert "GROUP BY CUBE" in sql
