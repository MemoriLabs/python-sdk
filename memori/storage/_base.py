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


class BaseStorageAdapter:
    def __init__(self, conn):
        if not callable(conn):
            raise TypeError(
                "conn must be a callable function or method that returns a database connection. "
                "Example: def get_conn(): return session_maker() or lambda: psycopg2.connect(...)"
            )
        self._conn_factory = conn
        self._conn = None

    @property
    def conn(self):
        if self._conn is None:
            self._conn = self._conn_factory()
        return self._conn

    def close(self):
        """Close the underlying connection if it exists."""
        if self._conn is not None:
            if hasattr(self._conn, "close"):
                self._conn.close()
            self._conn = None

    def reset(self):
        """Reset the connection, forcing recreation on next access."""
        self.close()

    def commit(self):
        raise NotImplementedError

    def execute(self, operation, *args, **kwargs):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def get_dialect(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError


class BaseConversation:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def create(self, session_id: int):
        raise NotImplementedError


class BaseConversationMessage:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def create(self, conversation_id: int, role: str, type: str, content: str):
        raise NotImplementedError


class BaseConversationMessages:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def read(self, conversation_id: int):
        raise NotImplementedError


class BaseParent:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def create(self, external_id: str):
        raise NotImplementedError


class BaseProcess:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def create(self, external_id: str):
        raise NotImplementedError


class BaseSession:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def create(self, uuid: str, parent_id: int, process_id: int):
        raise NotImplementedError


class BaseSchema:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn


class BaseSchemaVersion:
    def __init__(self, conn: BaseStorageAdapter):
        self.conn = conn

    def create(self, num: int):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError
