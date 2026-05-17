"""Alembic env — OLTP va OLAP databazalari uchun bir vaqtda migration.

`alembic upgrade head` ikkala bazani ham yangilaydi. OLTP modellari OLTPBase metadata sida,
OLAP modellari OLAPBase metadata sida joylashgan.
"""
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.database import OLAPBase, OLTPBase  # noqa: E402
from app import models  # noqa: F401, E402  -- modellarni yuklash uchun

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TARGET-ni tanlash tartibi (yuqori → past prioritet):
#   1) -x target=olap          (CLI x-argument)
#   2) [alembic] target = ...  (alembic.ini main option)
#   3) "oltp"                  (default)
_x_args = context.get_x_argument(as_dictionary=True)
TARGET = (
    _x_args.get("target")
    or config.get_main_option("target")
    or "oltp"
).lower()

if TARGET not in {"oltp", "olap"}:
    raise ValueError(
        f"Noma'lum target='{TARGET}'. Faqat 'oltp' yoki 'olap' qabul qilinadi."
    )


def get_url() -> str:
    return settings.oltp_database_url if TARGET == "oltp" else settings.olap_database_url


def get_metadata():
    return OLTPBase.metadata if TARGET == "oltp" else OLAPBase.metadata


def include_object(object, name, type_, reflected, compare_to):
    """Bir target migratsiyasi boshqa target jadvallariga tegmasligi uchun filtr.

    OLTP va OLAP modellari `app.models` orqali bitta Python jarayonida
    yuklanadi (FK importlar uchun zarur). Lekin har bir baza faqat o'z
    metadata.tables ni yaratishi kerak — aks holda alembic OLTP DB da
    OLAP jadvallarini ham yaratishga urinadi.
    """
    if type_ == "table":
        return name in get_metadata().tables
    return True


# Eslatma: multi-head loyiha bo'lgani uchun upgrade buyrug'ini doim
# `<branch>@head` bilan yozish kerak — masalan:
#   alembic -x target=oltp upgrade oltp@head
#   alembic -x target=olap upgrade olap@head
# Yoki Makefile orqali (`make migrate-oltp`, `make migrate-olap`).


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=get_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            compare_type=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
