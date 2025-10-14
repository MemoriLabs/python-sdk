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

from memori.storage.adaptors.sqlalchemy._adaptor import (
    Adaptor as SqlAlchemyStorageAdaptor,
)


class Router:
    def configure(self, conn):
        if type(session).__module__ == "sqlalchemy.orm.session":
            return SqlAlchemyStorageAdaptor(conn)

        raise RuntimeError("could not determine storage system")
