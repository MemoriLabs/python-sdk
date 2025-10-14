from memori.storage.adaptors.sqlalchemy._adaptor import (
    Adaptor as SqlAlchemyStorageAdaptor
)


class Router:
    def configure(self, conn):
        if type(session).__module__ == "sqlalchemy.orm.session":
            return SqlAlchemyStorageAdaptor(conn)

        raise RuntimeError("could not determine storage system")
