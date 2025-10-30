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
from memori.storage._registry import Registry


class Manager:
    def __init__(self, config: Config):
        self.adapter = None
        self.config = config
        self.__conn = None
        self.driver = None

    def build(self):
        if self.__conn is None:
            return self

        Builder(self.config).execute()

        return self

    def start(self, conn):
        if conn is None:
            return self

        self.adapter = Registry().adapter(conn)
        self.__conn = conn
        self.driver = Registry().driver(self.adapter)

        return self
