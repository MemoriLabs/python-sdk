import pytest
from core.settings import settings
from memori import Memori
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def config(session):
    mem = Memori(conn=session)
    yield mem.config


@pytest.fixture(scope="module")
def connection(engine):
    connection = engine.connect()

    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture(scope="session")
def engine():
    return create_engine(settings.SQLALCHEMY_TEST_DATABASE_URI)


@pytest.fixture
def session(connection):
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.close()
