"""O'qituvchi sxemalari."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TeacherBase(BaseModel):
    teacher_id: str = Field(..., max_length=32)
    full_name: str = Field(..., max_length=256)
    academic_degree: str | None = None
    position: str | None = None
    department: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    full_name: str | None = None
    academic_degree: str | None = None
    position: str | None = None
    department: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
