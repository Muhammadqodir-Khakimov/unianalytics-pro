"""Pytest konfiguratsiyasi va umumiy fixturalar."""
import os

os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import OLAPBase, OLTPBase, get_oltp_db, get_olap_db
from app.main import app
from app.core.rate_limit import limiter

# Disable rate-limiter in tests to avoid 429 between fixtures
limiter.enabled = False

TEST_OLTP_URL = "sqlite:///./test_oltp.db"
TEST_OLAP_URL = "sqlite:///./test_olap.db"


@pytest.fixture(scope="session")
def oltp_engine():
    engine = create_engine(TEST_OLTP_URL, connect_args={"check_same_thread": False})
    OLTPBase.metadata.create_all(engine)
    yield engine
    OLTPBase.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def olap_engine():
    engine = create_engine(TEST_OLAP_URL, connect_args={"check_same_thread": False})
    OLAPBase.metadata.create_all(engine)
    yield engine
    OLAPBase.metadata.drop_all(engine)


@pytest.fixture
def oltp_session(oltp_engine):
    Session = sessionmaker(bind=oltp_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(oltp_session, olap_engine):
    def _oltp_db():
        yield oltp_session

    def _olap_db():
        Session = sessionmaker(bind=olap_engine)
        s = Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_oltp_db] = _oltp_db
    app.dependency_overrides[get_olap_db] = _olap_db
    yield TestClient(app)
    app.dependency_overrides.clear()
