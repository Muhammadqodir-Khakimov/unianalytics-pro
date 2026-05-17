"""Fan sxemalari."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.oltp.subject import SubjectType


class SubjectBase(BaseModel):
    code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=256)
    department: str | None = None
    credit_hours: int = 3
    subject_type: SubjectType = SubjectType.MAJBURIY
    semester: int = 1
    description: str | None = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = None
    department: str | None = None
    credit_hours: int | None = None
    subject_type: SubjectType | None = None
    semester: int | None = None
    description: str | None = None


class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
