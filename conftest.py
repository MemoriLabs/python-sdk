import pytest
from core.settings import settings
from database.core import TestDBSession
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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
