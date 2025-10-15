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

from memori._cli import Cli
from memori._config import Config
from memori.storage.migrations._mysql import migrations as mysql_migrations


class Manager:
    def __init__(self, config: Config):
        self.cli = Cli(config)
        self.config = config

    def build(self):
        if self.config.conn is None:
            return self

        dialect = self.config.conn.get_dialect()
        if dialect in ["mysql"]:
            self.build_for_rdbms()
        else:
            raise NotImplementedError

        return self

    def build_for_rdbms(self):
        self.cli.banner()

        if self.config.conn is None:
            return self

        try:
            result = (
                self.config.conn.execute(
                    """
                    select num
                      from memori_schema_version
                    """
                )
                .mappings()
                .first()
            )
        except:
            result = None

        if result is None:
            num = 0
        else:
            num = result["num"]

        self.cli.notice(f"Currently at revision #{num}.")

        if self.config.conn.get_dialect() == "mysql":
            migrations = mysql_migrations
        else:
            raise NotImplementedError

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

            self.config.conn.execute(
                """
                delete from memori_schema_version
                """
            )

            self.config.conn.execute(
                """
                insert into memori_schema_version(
                    num
                ) values (
                    %s
                )
                """,
                (num - 1,)
            )
            self.config.conn.commit()

        self.cli.notice("Build executed successfully!")
        self.cli.newline()

        return self
