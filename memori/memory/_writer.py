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

from uuid import uuid4 as uuid4

from memori._config import Config


class Writer:
    def __init__(self, config: Config):
        self.config = config

    def execute(self, payload):
        if self.config.cache.session_id is None:
            self.config.conn.execute(
                """
                insert ignore into memori_session(
                    uuid
                ) values (
                    :uuid
                )""",
                {"uuid": self.config.session_id},
            )
            self.config.conn.commit()

            self.config.cache.session_id = (
                self.config.conn.execute(
                    """
                    select id
                      from memori_session
                     where uuid = :uuid
                    """,
                    {"uuid": self.config.session_id},
                )
                .mappings()
                .first()
                .get("ID", None)
            )

            if self.config.cache.session_id is None:
                raise RuntimeError("session ID is unexpectedly None")

        if self.config.cache.conversation_id is None:
            uuid = uuid4()

            self.config.conn.execute(
                """
                insert ignore into memori_conversation(
                    uuid,
                    session_id
                ) values (
                    :uuid,
                    :session_id
                )
                """,
                {"uuid": uuid, "session_id": self.config.cache.session_id},
            )
            self.config.conn.commit()

            self.config.cache.conversation_id = (
                self.config.conn.execute(
                    """
                    select id
                      from memori_conversation
                     where session_id = :session_id
                    """,
                    {"session_id": self.config.cache.session_id},
                )
                .mappings()
                .first()
                .get("ID", None)
            )

            if self.config.cache.conversation_id is None:
                raise RuntimeError("conversation ID is unexpectedly None")
