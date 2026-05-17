"""Baho sxemalari."""
from datetime import date, datetime

from pydantic import BaseModel, Field


class AssessmentTypeBase(BaseModel):
    name: str
    description: str | None = None
    weight_percentage: float = 25.0


class AssessmentTypeCreate(AssessmentTypeBase):
    pass


class AssessmentTypeResponse(AssessmentTypeBase):
    id: int

    model_config = {"from_attributes": True}


class GradeBase(BaseModel):
    student_id: int
    subject_id: int
    teacher_id: int
    assessment_type_id: int
    grade_value: float = Field(..., ge=0, le=100)
    attendance_percentage: float = Field(100.0, ge=0, le=100)
    is_passed: bool = True
    semester: str
    academic_year: str
    grade_date: date


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    grade_value: float | None = Field(None, ge=0, le=100)
    attendance_percentage: float | None = Field(None, ge=0, le=100)
    is_passed: bool | None = None


class GradeResponse(GradeBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
