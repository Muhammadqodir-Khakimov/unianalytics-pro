"""5 ta professional OLAP cube ta'rifi.

BMI mavzusi uchun MUHIM — har bir cube alohida domen va o'lchovlar.
"""
from app.olap.cube import CubeDefinition, Dimension, Hierarchy, Measure

# Umumiy dimensionlarni qayta ishlatish uchun yordamchi
def _dim_student():
    return Dimension(
        name="student", label="Talaba", table="dim_student",
        key_column="student_key", fact_fk="student_key",
        attributes=["student_id", "full_name", "gender", "enrollment_year",
                    "group_name", "education_form", "status"],
    )


def _dim_subject():
    return Dimension(
        name="subject", label="Fan", table="dim_subject",
        key_column="subject_key", fact_fk="subject_key",
        attributes=["subject_code", "subject_name", "department", "credit_hours",
                    "subject_type", "semester"],
    )


def _dim_teacher():
    return Dimension(
        name="teacher", label="O'qituvchi", table="dim_teacher",
        key_column="teacher_key", fact_fk="teacher_key",
        attributes=["teacher_id", "full_name", "academic_degree", "position", "department"],
    )


def _dim_time():
    return Dimension(
        name="time", label="Vaqt", table="dim_time",
        key_column="time_key", fact_fk="time_key",
        attributes=["full_date", "day", "week", "month", "month_name", "quarter",
                    "semester", "academic_year", "year"],
        hierarchies=[Hierarchy(name="time_hierarchy",
                                levels=["year", "academic_year", "semester", "quarter", "month", "week", "day"])],
    )


def _dim_faculty():
    return Dimension(
        name="faculty", label="Fakultet", table="dim_faculty",
        key_column="faculty_key", fact_fk="faculty_key",
        attributes=["faculty_name", "department", "specialty", "course", "group_name"],
        hierarchies=[Hierarchy(name="org_hierarchy",
                                levels=["faculty_name", "specialty", "course", "group_name"])],
    )


# ============================================================
# CUBE 1: ACADEMIC PERFORMANCE (Akademik o'zlashtirish)
# ============================================================

ACADEMIC_PERFORMANCE_CUBE = CubeDefinition(
    name="academic_performance",
    fact_table="fact_student_grades",
    description="Akademik o'zlashtirish: o'rtacha ball, GPA, o'tish darajasi",
    dimensions=[_dim_student(), _dim_subject(), _dim_teacher(), _dim_time(), _dim_faculty()],
    measures=[
        Measure(name="avg_grade", label="O'rtacha ball", column="grade_value", aggregation="AVG", format="decimal"),
        Measure(name="avg_gpa", label="O'rtacha GPA", column="gpa_points", aggregation="AVG", format="decimal"),
        Measure(name="total_grades", label="Baholar soni", column="grade_id", aggregation="COUNT", format="number"),
        Measure(name="max_grade", label="Eng yuqori", column="grade_value", aggregation="MAX", format="decimal"),
        Measure(name="min_grade", label="Eng past", column="grade_value", aggregation="MIN", format="decimal"),
        Measure(name="passed_count", label="O'tganlar", column="is_passed", aggregation="SUM", format="number"),
        Measure(name="total_credits", label="Kreditlar", column="credit_hours", aggregation="SUM", format="number"),
    ],
)


# ============================================================
# CUBE 2: ATTENDANCE (Davomat)
# ============================================================

ATTENDANCE_CUBE = CubeDefinition(
    name="attendance",
    fact_table="fact_student_grades",
    description="Davomat tahlili: kelishlar, kelmaganlar, kechikkanlar",
    dimensions=[_dim_student(), _dim_subject(), _dim_time(), _dim_faculty()],
    measures=[
        Measure(name="avg_attendance", label="O'rtacha davomat %", column="attendance_percentage",
                aggregation="AVG", format="percent"),
        Measure(name="total_lessons", label="Darslar soni", column="grade_id", aggregation="COUNT", format="number"),
        Measure(name="min_attendance", label="Eng past davomat", column="attendance_percentage",
                aggregation="MIN", format="percent"),
        Measure(name="max_attendance", label="Eng yuqori davomat", column="attendance_percentage",
                aggregation="MAX", format="percent"),
    ],
)


# ============================================================
# CUBE 3: DROP-OUT RISK
# ============================================================

DROPOUT_RISK_CUBE = CubeDefinition(
    name="dropout_risk",
    fact_table="fact_student_grades",
    description="Chetlashtirish xavfi (XGBoost asosida o'tmaganlar/past GPA)",
    dimensions=[_dim_student(), _dim_time(), _dim_faculty()],
    measures=[
        Measure(name="failed_count", label="O'tmagan baholar", column="is_passed",
                aggregation="COUNT", format="number"),
        Measure(name="avg_gpa", label="O'rtacha GPA", column="gpa_points",
                aggregation="AVG", format="decimal"),
        Measure(name="min_attendance", label="Eng past davomat", column="attendance_percentage",
                aggregation="MIN", format="percent"),
        Measure(name="grades_below_55", label="55 dan past baholar",
                column="grade_value", aggregation="COUNT", format="number"),
    ],
)


# ============================================================
# CUBE 4: TEACHER PERFORMANCE
# ============================================================

TEACHER_PERFORMANCE_CUBE = CubeDefinition(
    name="teacher_performance",
    fact_table="fact_student_grades",
    description="O'qituvchi samaradorligi: berilgan baholar, talabalar soni",
    dimensions=[_dim_teacher(), _dim_subject(), _dim_time(), _dim_faculty()],
    measures=[
        Measure(name="avg_grade_given", label="O'rtacha berilgan ball",
                column="grade_value", aggregation="AVG", format="decimal"),
        Measure(name="students_taught", label="Talabalar soni",
                column="student_key", aggregation="COUNT_DISTINCT", format="number"),
        Measure(name="grades_given", label="Baholar bergan",
                column="grade_id", aggregation="COUNT", format="number"),
        Measure(name="pass_rate", label="O'tish darajasi",
                column="is_passed", aggregation="AVG", format="percent"),
        Measure(name="subjects_taught", label="Fanlar",
                column="subject_key", aggregation="COUNT_DISTINCT", format="number"),
    ],
)


# ============================================================
# CUBE 5: FINANCIAL (To'lov)
# ============================================================

FINANCIAL_CUBE = CubeDefinition(
    name="financial",
    fact_table="fact_student_grades",  # placeholder — production da fact_payments bo'lardi
    description="Moliyaviy tahlil: kontrakt to'lovlari, qarz, statistika",
    dimensions=[_dim_student(), _dim_time(), _dim_faculty()],
    measures=[
        Measure(name="total_credits_billed", label="Hisoblangan kreditlar",
                column="credit_hours", aggregation="SUM", format="number"),
        Measure(name="students_count", label="Talabalar soni",
                column="student_key", aggregation="COUNT_DISTINCT", format="number"),
    ],
)


# ============================================================
# Registry
# ============================================================

ALL_CUBES = {
    "academic_performance": ACADEMIC_PERFORMANCE_CUBE,
    "attendance": ATTENDANCE_CUBE,
    "dropout_risk": DROPOUT_RISK_CUBE,
    "teacher_performance": TEACHER_PERFORMANCE_CUBE,
    "financial": FINANCIAL_CUBE,
}


def get_cube_v2(name: str) -> CubeDefinition:
    if name not in ALL_CUBES:
        raise ValueError(f"Cube topilmadi: {name}. Mavjud: {list(ALL_CUBES.keys())}")
    return ALL_CUBES[name]


def list_cubes() -> list[dict]:
    return [
        {
            "name": name,
            "label": cube.description,
            "fact_table": cube.fact_table,
            "dimensions_count": len(cube.dimensions),
            "measures_count": len(cube.measures),
        }
        for name, cube in ALL_CUBES.items()
    ]
