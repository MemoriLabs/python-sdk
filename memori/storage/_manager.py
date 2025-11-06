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

from memori._config import Config
from memori.storage._builder import Builder
from memori.storage._connection import connection_context
from memori.storage._registry import Registry


class Manager:
    def __init__(self, config: Config) -> None:
        self.adapter = None
        self.config = config
        self.conn_factory = None
        self.driver = None

    @property
    def conn(self):
        return connection_context(self.conn_factory)

    def build(self) -> "Manager":
        if self.conn_factory is None:
            return self

        Builder(self.config).execute()

        return self

    def start(self, conn) -> "Manager":
        if conn is None:
            return self

        self.conn_factory = conn
        self.adapter = Registry().adapter(conn)
        self.driver = Registry().driver(self.adapter)

        return self
