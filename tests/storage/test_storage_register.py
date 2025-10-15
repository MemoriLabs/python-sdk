from memori.storage._registry import Registry
from memori.storage.adaptors.sqlalchemy._adaptor import (
    Adaptor as SqlAlchemyStorageAdaptor,
)
from memori.storage.drivers.mysql._driver import Driver as MysqlStorageDriver


def test_storage_adaptor_sqlalchemy(session):
    assert isinstance(Registry().adaptor(session), SqlAlchemyStorageAdaptor)


def test_storage_driver_mysql(session):
    assert isinstance(
        Registry().driver(Registry().adaptor(session)), MysqlStorageDriver
    )
