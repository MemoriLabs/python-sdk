from memori.storage import Registry
from memori.storage.adapters.dbapi._adapter import Adapter as DBAPIAdapter, is_dbapi_connection
from memori.storage.adapters.sqlalchemy._adapter import Adapter as SQLAlchemyAdapter


def test_sqlalchemy_session_not_detected_as_dbapi(session):
    assert is_dbapi_connection(session) is False


def test_registry_routes_sqlalchemy_to_sqlalchemy_adapter(session):
    registry = Registry()
    adapter = registry.adapter(session)
    assert isinstance(adapter, SQLAlchemyAdapter)
    assert not isinstance(adapter, DBAPIAdapter)


def test_registry_routes_postgres_session_to_sqlalchemy_adapter(postgres_session):
    registry = Registry()
    adapter = registry.adapter(postgres_session)
    assert isinstance(adapter, SQLAlchemyAdapter)
    assert not isinstance(adapter, DBAPIAdapter)
