"""OLTP va OLAP databazalariga ulanish."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class OLTPBase(DeclarativeBase):
    """OLTP (transactional) modellar uchun baza."""

    pass


class OLAPBase(DeclarativeBase):
    """OLAP (star schema) modellar uchun baza."""

    pass


def _make_engine(url: str):
    """SQLite yoki Postgres uchun engine yaratish."""
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.app_debug,
    )


# OLTP engine — kunlik tranzaktsion ish uchun
oltp_engine = _make_engine(settings.oltp_database_url)

# OLAP engine — agregatsiya va tahlil uchun
olap_engine = _make_engine(settings.olap_database_url)

OLTPSession = sessionmaker(autocommit=False, autoflush=False, bind=oltp_engine)
OLAPSession = sessionmaker(autocommit=False, autoflush=False, bind=olap_engine)


def get_oltp_db() -> Generator[Session, None, None]:
    """FastAPI dependency — OLTP session."""
    db = OLTPSession()
    try:
        yield db
    finally:
        db.close()


def get_olap_db() -> Generator[Session, None, None]:
    """FastAPI dependency — OLAP session."""
    db = OLAPSession()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def oltp_session() -> Generator[Session, None, None]:
    """OLTP session uchun context manager (skriptlar uchun)."""
    db = OLTPSession()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def olap_session() -> Generator[Session, None, None]:
    """OLAP session uchun context manager."""
    db = OLAPSession()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
