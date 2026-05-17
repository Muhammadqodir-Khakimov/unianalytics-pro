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

# Standart maydon: OLTP. Buni "--name oltp" yoki "--name olap" bilan boshqarish mumkin.
TARGET = config.get_main_option("target", "oltp")


def get_url() -> str:
    return settings.oltp_database_url if TARGET == "oltp" else settings.olap_database_url


def get_metadata():
    return OLTPBase.metadata if TARGET == "oltp" else OLAPBase.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=get_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
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
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
