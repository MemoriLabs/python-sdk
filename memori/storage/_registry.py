r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""

from memori.storage._base import BaseStorageAdapter
from memori.storage.adapters.sqlalchemy._adapter import (
    Adapter as SqlAlchemyStorageAdapter,
)
from memori.storage.drivers.mysql._driver import Driver as MysqlStorageDriver


class Registry:
    def adapter(self, conn):
        if type(conn).__module__ == "sqlalchemy.orm.session":
            return SqlAlchemyStorageAdapter(conn)

        raise RuntimeError("could not determine storage system for adapter")

    def driver(self, conn: BaseStorageAdapter):
        if conn.get_dialect() == "mysql":
            return MysqlStorageDriver(conn)

        raise RuntimeError("could not determine storage system for driver")
