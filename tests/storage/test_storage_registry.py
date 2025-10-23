from unittest.mock import Mock

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


def test_storage_driver_mariadb():
    mariadb_session = Mock()
    mariadb_session.get_bind.return_value.dialect.name = "mariadb"
    type(mariadb_session).__module__ = "sqlalchemy.orm.session"
    
    adapter = Registry().adapter(mariadb_session)
    driver = Registry().driver(adapter)
    
    assert isinstance(driver, MysqlStorageDriver)


def test_storage_driver_cockroachdb():
    cockroachdb_session = Mock()
    cockroachdb_session.get_bind.return_value.dialect.name = "cockroachdb"
    type(cockroachdb_session).__module__ = "sqlalchemy.orm.session"
    
    adapter = Registry().adapter(cockroachdb_session)
    driver = Registry().driver(adapter)
    
    assert isinstance(driver, PostgresqlStorageDriver)
