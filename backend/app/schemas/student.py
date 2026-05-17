"""Talaba sxemalari."""
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.oltp.student import EducationForm, Gender, StudentStatus


class StudentBase(BaseModel):
    student_id: str = Field(..., max_length=32)
    full_name: str = Field(..., max_length=256)
    gender: Gender
    birth_date: date
    phone: str | None = None
    email: EmailStr | None = None
    group_id: int
    education_form: EducationForm = EducationForm.KUNDUZGI
    status: StudentStatus = StudentStatus.FAOL
    enrollment_year: int


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    group_id: int | None = None
    education_form: EducationForm | None = None
    status: StudentStatus | None = None


class StudentResponse(StudentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
