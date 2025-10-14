class BaseStorageAdaptor:
    def __init__(self, conn):
        self.conn = conn

    def commit(self):
        raise NotImplementedError

    def execute(self, operation):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError
