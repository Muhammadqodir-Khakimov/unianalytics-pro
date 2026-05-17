"""Fakultet, yo'nalish va guruh sxemalari."""
from datetime import datetime

from pydantic import BaseModel, Field


class FacultyBase(BaseModel):
    name: str = Field(..., max_length=256)
    code: str = Field(..., max_length=32)
    description: str | None = None


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None


class FacultyResponse(FacultyBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SpecialtyBase(BaseModel):
    name: str
    code: str
    faculty_id: int


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyResponse(SpecialtyBase):
    id: int

    model_config = {"from_attributes": True}


class GroupBase(BaseModel):
    name: str
    course: int
    specialty_id: int
    enrollment_year: int


class GroupCreate(GroupBase):
    pass


class GroupResponse(GroupBase):
    id: int

    model_config = {"from_attributes": True}
