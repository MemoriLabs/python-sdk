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

from memori._cli import Cli
from memori._config import Config
from memori.storage._registry import Registry


class Manager:
    def __init__(self, config: Config):
        self.cli = Cli(config)
        self.config = config
        self.registry = Registry()
    
    def _get_supported_dialects(self):
        return list(self.registry._drivers.keys())
    
    def _get_dialect_family(self, dialect):
        if dialect in self.registry._drivers:
            driver_class = self.registry._drivers[dialect]
            return driver_class.migrations
        
        return None
    
    def _requires_rollback(self, dialect):
        if dialect in self.registry._drivers:
            driver_class = self.registry._drivers[dialect]
            return getattr(driver_class, 'requires_rollback_on_error', False)
        return False

    def build(self):
        if self.config.conn is None:
            return self

        dialect = self.config.conn.get_dialect()
        supported_dialects = self._get_supported_dialects()
        
        if dialect in supported_dialects:
            self.build_for_rdbms()
        else:
            raise NotImplementedError(
                f"Unsupported dialect: {dialect}. "
                f"Supported dialects: {supported_dialects}."
            )

        return self

    def build_for_rdbms(self):
        self.cli.banner()

        if self.config.conn is None:
            return self

        dialect = self.config.conn.get_dialect()
        
        try:
            num = self.config.driver.schema.version.read()
        except:
            if self._requires_rollback(dialect):
                self.config.conn.rollback()
            num = 0

        self.cli.notice(f"Currently at revision #{num}.")

        migrations = self._get_dialect_family(dialect)
        if migrations is None:
            raise NotImplementedError(
                f"No migration mapping found for dialect: {dialect}."
            )

        if num == max(migrations.keys()):
            self.cli.notice("data structures are up-to-date", 1)
        else:
            while True:
                num += 1
                if num not in migrations:
                    break

                self.cli.notice(f"Building revision #{num}...")

                for migration in migrations[num]:
                    self.cli.notice(migration["description"], 1)
                    self.config.conn.execute(migration["operation"])
                    self.config.conn.commit()

            self.config.driver.schema.version.delete()
            self.config.driver.schema.version.create(num - 1)

            self.config.conn.commit()

        self.cli.notice("Build executed successfully!")
        self.cli.newline()

        return self
