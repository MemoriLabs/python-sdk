r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       trymemori.com
"""

from memori.storage._base import BaseStorageAdaptor
from memori.storage.adaptors.sqlalchemy._adaptor import (
    Adaptor as SqlAlchemyStorageAdaptor,
)
from memori.storage.drivers.mysql._driver import Driver as MysqlStorageDriver


class Registry:
    def adaptor(self, conn):
        if type(conn).__module__ == "sqlalchemy.orm.session":
            return SqlAlchemyStorageAdaptor(conn)

        raise RuntimeError("could not determine storage system for adaptor")

    def driver(self, conn: BaseStorageAdaptor):
        if conn.get_dialect() == "mysql":
            return MysqlStorageDriver(conn)

        raise RuntimeError("could not determine storage system for driver")
