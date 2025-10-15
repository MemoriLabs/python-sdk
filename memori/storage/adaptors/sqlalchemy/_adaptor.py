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


class Adaptor(BaseStorageAdaptor):
    def commit(self):
        self.conn.commit()
        return self

    def execute(self, operation, binds={}):
        return self.conn.execute(operation, binds)

    def flush(self):
        self.conn.flush()
        return self

    def get_dialect(self):
        return self.conn.bind.dialect.name

    def rollback(self):
        self.conn.rollback()
        return self
