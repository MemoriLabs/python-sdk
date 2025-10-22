from memori.storage import Registry
from memori.storage.adapters.sqlalchemy._adapter import (
    Adapter as SqlAlchemyStorageAdapter,
)
from memori.storage.drivers.mysql._driver import Driver as MysqlStorageDriver
from memori.storage.drivers.postgresql._driver import Driver as PostgresqlStorageDriver


def test_storage_adapter_sqlalchemy(session):
    assert isinstance(Registry().adapter(session), SqlAlchemyStorageAdapter)


def test_storage_driver_mysql(session):
    assert isinstance(
        Registry().driver(Registry().adapter(session)), MysqlStorageDriver
    )


def test_storage_driver_postgresql(postgres_session):
    assert isinstance(
        Registry().driver(Registry().adapter(postgres_session)), PostgresqlStorageDriver
    )
