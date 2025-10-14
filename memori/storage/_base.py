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

    def rollback(self):
        raise NotImplementedError
