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

from uuid import uuid4

from memori.storage._base import (
    BaseConversation,
    BaseConversationMessage,
    BaseConversationMessages,
    BaseParent,
    BaseProcess,
    BaseSchema,
    BaseSchemaVersion,
    BaseSession,
    BaseStorageAdapter,
)
from memori.storage._registry import Registry
from memori.storage.migrations._mysql import migrations


class Conversation(BaseConversation):
    def __init__(self, conn: BaseStorageAdapter):
        super().__init__(conn)
        self.message = ConversationMessage(conn)
        self.messages = ConversationMessages(conn)

    def create(self, session_id):
        uuid = uuid4()

        self.conn.execute(
            """
            insert ignore into memori_conversation(
                uuid,
                session_id
            ) values (
                %s,
                %s
            )
            """,
            (
                uuid,
                session_id,
            ),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                select id
                  from memori_conversation
                 where session_id = %s
                """,
                (session_id,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )


class ConversationMessage(BaseConversationMessage):
    def create(self, conversation_id: int, role: str, type: str, content: str):
        self.conn.execute(
            """
            insert into memori_conversation_message(
                uuid,
                conversation_id,
                role,
                type,
                content
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                uuid4(),
                conversation_id,
                role,
                type,
                content,
            ),
        )


class ConversationMessages(BaseConversationMessages):
    def read(self, conversation_id: int):
        results = (
            self.conn.execute(
                """
                select role,
                       content
                  from memori_conversation_message
                 where conversation_id = %s
                """,
                (conversation_id,),
            )
            .mappings()
            .fetchall()
        )

        messages = []
        for result in results:
            messages.append({"content": result["content"], "role": result["role"]})

        return messages


class Parent(BaseParent):
    def create(self, external_id: str):
        self.conn.execute(
            """
            insert ignore into memori_parent(
                uuid,
                external_id
            ) values (
                %s,
                %s
            )
            """,
            (uuid4(), external_id),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                select id
                  from memori_parent
                 where external_id = %s
                """,
                (external_id,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )


class Process(BaseProcess):
    def create(self, external_id: str):
        self.conn.execute(
            """
            insert ignore into memori_process(
                uuid,
                external_id
            ) values (
                %s,
                %s
            )
            """,
            (uuid4(), external_id),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                select id
                  from memori_process
                 where external_id = %s
                """,
                (external_id,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )


class Session(BaseSession):
    def create(self, uuid: str, parent_id: int, process_id: int):
        self.conn.execute(
            """
            insert ignore into memori_session(
                uuid,
                parent_id,
                process_id
            ) values (
                %s,
                %s,
                %s
            )
            """,
            (uuid, parent_id, process_id),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                select id
                  from memori_session
                 where uuid = %s
                """,
                (uuid,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )


class Schema(BaseSchema):
    def __init__(self, conn: BaseStorageAdapter):
        super().__init__(conn)
        self.version = SchemaVersion(conn)


class SchemaVersion(BaseSchemaVersion):
    def create(self, num: int):
        self.conn.execute(
            """
            insert into memori_schema_version(
                num
            ) values (
                %s
            )
            """,
            (num,),
        )

    def delete(self):
        self.conn.execute(
            """
            delete from memori_schema_version
            """
        )

    def read(self):
        return (
            self.conn.execute(
                """
                select num
                  from memori_schema_version
                """
            )
            .mappings()
            .fetchone()
            .get("num", None)
        )


@Registry.register_driver("mysql")
@Registry.register_driver("mariadb")
class Driver:
    """MySQL storage driver (also supports MariaDB).

    Attributes:
        migrations: Database schema migrations for MySQL.
        requires_rollback_on_error: MySQL does not abort transactions on query
            errors, so no rollback is needed to continue executing queries.
    """

    migrations = migrations
    requires_rollback_on_error = False

    def __init__(self, conn: BaseStorageAdapter):
        self.conversation = Conversation(conn)
        self.parent = Parent(conn)
        self.process = Process(conn)
        self.schema = Schema(conn)
        self.session = Session(conn)
