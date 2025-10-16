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


class BaseStorageAdaptor:
    def __init__(self, conn):
        self.conn = conn

    def commit(self):
        raise NotImplementedError

    def execute(self, operation):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def get_dialect(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError


class BaseConversation:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn

    def create(self, session_id: int):
        raise NotImplementedError


class BaseConversationMessage:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn

    def create(self, conversation_id: int, role: str, type: str, content: str):
        raise NotImplementedError


class BaseParent:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn

    def create(self, external_id: str):
        raise NotImplementedError


class BaseProcess:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn

    def create(self, external_id: str):
        raise NotImplementedError


class BaseSession:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn

    def create(self, uuid: str, parent_id: int, process_id: int):
        raise NotImplementedError


class BaseSchema:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn


class BaseSchemaVersion:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conn = conn

    def create(self, num: int):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError
