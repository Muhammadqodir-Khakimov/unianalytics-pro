"""Generic CRUD service — barcha resurslar uchun umumiy logika."""
from math import ceil
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.database import OLTPBase

ModelType = TypeVar("ModelType", bound=OLTPBase)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchema, UpdateSchema]):
    """Generic CRUD operatsiyalar uchun bazaviy klass."""

    def __init__(self, model: Type[ModelType], resource_name: str = "Resurs"):
        self.model = model
        self.resource_name = resource_name

    def get(self, db: Session, obj_id: int) -> ModelType:
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            raise NotFoundException(self.resource_name)
        return obj

    def list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        query = db.query(self.model)
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if page_size else 0,
        }

    def create(self, db: Session, payload: CreateSchema) -> ModelType:
        obj = self.model(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, obj_id: int, payload: UpdateSchema) -> ModelType:
        obj = self.get(db, obj_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj_id: int) -> None:
        obj = self.get(db, obj_id)
        db.delete(obj)
        db.commit()
