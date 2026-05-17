"""OLAP Cube ta'rifi — Star Schema asosida.

Ushbu modulda kub o'lchovlari (dimensions), o'lchamlari (measures) va ierarxiyalari
deklarativ ravishda aniqlanadi. Frontend bu metadatadan foydalanib, foydalanuvchiga
mavjud tahlil imkoniyatlarini ko'rsatadi.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Hierarchy:
    """Ierarxiya — drill-down/roll-up uchun darajalar ketma-ketligi."""

    name: str
    levels: List[str]  # eng yuqoridan eng pastga


@dataclass
class Dimension:
    """O'lchov — fakt jadvalga JOIN qilinadigan dimension."""

    name: str
    table: str
    key_column: str  # dim.key_column = fact.fk
    fact_fk: str  # fakt jadvaldagi FK ustun nomi
    attributes: List[str]  # querydagi mumkin ustunlar
    label: str = ""
    description: str = ""
    hierarchies: List[Hierarchy] = field(default_factory=list)


@dataclass
class Measure:
    """O'lcham — agregatsiya qilinadigan numerik ustun."""

    name: str
    column: str  # fact_student_grades.column
    aggregation: str = "AVG"  # AVG, SUM, COUNT, MIN, MAX
    label: str = ""
    description: str = ""
    format: str = "number"  # number, percent, decimal


@dataclass
class CubeDefinition:
    """Kub — fakt jadval + dimensions + measures."""

    name: str
    fact_table: str
    dimensions: List[Dimension]
    measures: List[Measure]
    description: str = ""

    def dimension_by_name(self, name: str) -> Dimension:
        for d in self.dimensions:
            if d.name == name:
                return d
        raise ValueError(f"Dimension topilmadi: {name}")

    def measure_by_name(self, name: str) -> Measure:
        for m in self.measures:
            if m.name == name:
                return m
        raise ValueError(f"Measure topilmadi: {name}")


# ============================================================
# STUDENT GRADES kub ta'rifi
# ============================================================

STUDENT_GRADES_CUBE = CubeDefinition(
    name="student_grades",
    fact_table="fact_student_grades",
    description="Talabalarning baholarini tahlil qilish uchun kub",
    dimensions=[
        Dimension(
            name="student",
            label="Talaba",
            table="dim_student",
            key_column="student_key",
            fact_fk="student_key",
            attributes=[
                "student_id",
                "full_name",
                "gender",
                "enrollment_year",
                "group_name",
                "education_form",
                "status",
            ],
        ),
        Dimension(
            name="subject",
            label="Fan",
            table="dim_subject",
            key_column="subject_key",
            fact_fk="subject_key",
            attributes=[
                "subject_code",
                "subject_name",
                "department",
                "credit_hours",
                "subject_type",
                "semester",
            ],
        ),
        Dimension(
            name="teacher",
            label="O'qituvchi",
            table="dim_teacher",
            key_column="teacher_key",
            fact_fk="teacher_key",
            attributes=[
                "teacher_id",
                "full_name",
                "academic_degree",
                "position",
                "department",
            ],
        ),
        Dimension(
            name="time",
            label="Vaqt",
            table="dim_time",
            key_column="time_key",
            fact_fk="time_key",
            attributes=[
                "full_date",
                "day",
                "week",
                "month",
                "month_name",
                "quarter",
                "semester",
                "academic_year",
                "year",
            ],
            hierarchies=[
                Hierarchy(
                    name="time_hierarchy",
                    levels=["year", "academic_year", "semester", "quarter", "month", "week", "day"],
                )
            ],
        ),
        Dimension(
            name="faculty",
            label="Fakultet",
            table="dim_faculty",
            key_column="faculty_key",
            fact_fk="faculty_key",
            attributes=[
                "faculty_name",
                "department",
                "specialty",
                "course",
                "group_name",
            ],
            hierarchies=[
                Hierarchy(
                    name="org_hierarchy",
                    levels=["faculty_name", "specialty", "course", "group_name"],
                )
            ],
        ),
        Dimension(
            name="assessment",
            label="Baholash turi",
            table="dim_assessment_type",
            key_column="assessment_type_key",
            fact_fk="assessment_type_key",
            attributes=["type_name", "weight_percentage"],
        ),
    ],
    measures=[
        Measure(
            name="avg_grade",
            label="O'rtacha ball",
            column="grade_value",
            aggregation="AVG",
            format="decimal",
        ),
        Measure(
            name="total_grades",
            label="Baholar soni",
            column="grade_id",
            aggregation="COUNT",
            format="number",
        ),
        Measure(
            name="avg_gpa",
            label="O'rtacha GPA",
            column="gpa_points",
            aggregation="AVG",
            format="decimal",
        ),
        Measure(
            name="avg_attendance",
            label="O'rtacha davomat",
            column="attendance_percentage",
            aggregation="AVG",
            format="percent",
        ),
        Measure(
            name="max_grade",
            label="Eng yuqori ball",
            column="grade_value",
            aggregation="MAX",
            format="decimal",
        ),
        Measure(
            name="min_grade",
            label="Eng past ball",
            column="grade_value",
            aggregation="MIN",
            format="decimal",
        ),
        Measure(
            name="total_credits",
            label="Jami kreditlar",
            column="credit_hours",
            aggregation="SUM",
            format="number",
        ),
        Measure(
            name="passed_count",
            label="O'tganlar soni",
            column="is_passed",
            aggregation="SUM",
            format="number",
        ),
    ],
)


def get_cube(name: str = "student_grades") -> CubeDefinition:
    """Berilgan nomdagi kub ta'rifini qaytaradi."""
    if name == "student_grades":
        return STUDENT_GRADES_CUBE
    raise ValueError(f"Kub topilmadi: {name}")
