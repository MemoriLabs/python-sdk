import pytest
from core.settings import settings
from database.core import TestDBSession, PostgresTestDBSession
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from memori import Memori


@pytest.fixture
def config(session):
    mem = Memori(conn=session)
    yield mem.config


@pytest.fixture
def session():
    session = TestDBSession()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def postgres_session():
    """Provides a PostgreSQL session for testing."""
    session = PostgresTestDBSession()

    try:
        yield session
    finally:
        session.close()
