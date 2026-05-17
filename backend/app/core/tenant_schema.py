"""Schema-per-tenant: Postgres `search_path` orqali izolyatsiya.

Har bir tenant uchun alohida schema yaratiladi:
    tenant_acme.students
    tenant_bsu.students
    tenant_nuu.students

Hamma so'rovlar avtomatik `SET search_path TO tenant_<name>, public` orqali
shu tenant'ning ma'lumotlariga yo'naltiriladi.

## Foydalanish

```python
from app.core.tenant_schema import tenant_scope

@router.get("/students")
def list_students(tenant_id: int, db: Session = Depends(get_db)):
    with tenant_scope(db, tenant_id):
        return db.query(Student).all()  # avtomatik shu schema dan
```

## Migration

`alembic upgrade` har bir schema uchun alohida:
```bash
TENANT_SCHEMA=tenant_acme alembic upgrade head
```
"""
import re
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import text
from sqlalchemy.orm import Session

SCHEMA_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,30}$")


def schema_name(slug: str) -> str:
    """Subdomain/slug → safe schema name."""
    slug = slug.lower().strip()
    if not SCHEMA_NAME_RE.match(slug):
        raise ValueError(f"Yaroqsiz tenant slug: {slug}")
    return f"tenant_{slug}"


def create_tenant_schema(db: Session, slug: str) -> str:
    """Yangi tenant uchun schema yaratish + barcha jadvallar."""
    schema = schema_name(slug)
    db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
    # Copy table structure from `public` (or run Alembic separately)
    # Bu yerda jadval ro'yxati app.models dan keladi:
    from app.database import OLTPBase
    for table in OLTPBase.metadata.sorted_tables:
        if table.schema is None:  # skip cross-tenant tables
            ddl = str(table.tometadata(OLTPBase.metadata, schema=schema).compile())
            try:
                db.execute(text(ddl))
            except Exception:
                pass  # already exists
    db.commit()
    return schema


def drop_tenant_schema(db: Session, slug: str, cascade: bool = False) -> None:
    """Tenant'ni o'chirish (ehtiyot — barcha ma'lumotlar yo'qoladi)."""
    schema = schema_name(slug)
    cascade_clause = " CASCADE" if cascade else ""
    db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}"{cascade_clause}'))
    db.commit()


@contextmanager
def tenant_scope(db: Session, tenant_slug: str | None) -> Iterator[Session]:
    """Tenant'ning search_path'iga vaqtinchalik o'tish (with-block uchun)."""
    if not tenant_slug:
        yield db
        return
    schema = schema_name(tenant_slug)
    old = db.execute(text("SHOW search_path")).scalar()
    try:
        db.execute(text(f'SET search_path TO "{schema}", public'))
        yield db
    finally:
        db.execute(text(f"SET search_path TO {old}"))


def list_tenant_schemas(db: Session) -> list[str]:
    """DB'dagi mavjud tenant schema'larini ro'yxatlash."""
    rows = db.execute(text("""
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
        ORDER BY schema_name
    """)).fetchall()
    return [r[0] for r in rows]
