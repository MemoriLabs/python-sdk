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
from memori.storage.migrations._oracle import migrations


class Conversation(BaseConversation):
    def __init__(self, conn: BaseStorageAdapter):
        super().__init__(conn)
        self.message = ConversationMessage(conn)
        self.messages = ConversationMessages(conn)

    def create(self, session_id):
        uuid = str(uuid4())

        self.conn.execute(
            """
            MERGE INTO memori_conversation dst
            USING (SELECT :1 AS uuid, :2 AS session_id FROM DUAL) src
            ON (dst.session_id = src.session_id)
            WHEN NOT MATCHED THEN
                INSERT (uuid, session_id)
                VALUES (src.uuid, src.session_id)
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
                SELECT id
                  FROM memori_conversation
                 WHERE session_id = :1
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
            INSERT INTO memori_conversation_message(
                uuid,
                conversation_id,
                role,
                type,
                content
            ) VALUES (
                :1,
                :2,
                :3,
                :4,
                :5
            )
            """,
            (
                str(uuid4()),
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
                SELECT role,
                       content
                  FROM memori_conversation_message
                 WHERE conversation_id = :1
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
            MERGE INTO memori_parent dst
            USING (SELECT :1 AS uuid, :2 AS external_id FROM DUAL) src
            ON (dst.external_id = src.external_id)
            WHEN NOT MATCHED THEN
                INSERT (uuid, external_id)
                VALUES (src.uuid, src.external_id)
            """,
            (str(uuid4()), external_id),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_parent
                 WHERE external_id = :1
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
            MERGE INTO memori_process dst
            USING (SELECT :1 AS uuid, :2 AS external_id FROM DUAL) src
            ON (dst.external_id = src.external_id)
            WHEN NOT MATCHED THEN
                INSERT (uuid, external_id)
                VALUES (src.uuid, src.external_id)
            """,
            (str(uuid4()), external_id),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_process
                 WHERE external_id = :1
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
            MERGE INTO memori_session dst
            USING (SELECT :1 AS uuid, :2 AS parent_id, :3 AS process_id FROM DUAL) src
            ON (dst.uuid = src.uuid)
            WHEN NOT MATCHED THEN
                INSERT (uuid, parent_id, process_id)
                VALUES (src.uuid, src.parent_id, src.process_id)
            """,
            (str(uuid), parent_id, process_id),
        )
        self.conn.flush()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_session
                 WHERE uuid = :1
                """,
                (str(uuid),),
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
            INSERT INTO memori_schema_version(
                num
            ) VALUES (
                :1
            )
            """,
            (num,),
        )

    def delete(self):
        self.conn.execute(
            """
            DELETE FROM memori_schema_version
            """
        )

    def read(self):
        return (
            self.conn.execute(
                """
                SELECT num
                  FROM memori_schema_version
                """
            )
            .mappings()
            .fetchone()
            .get("num", None)
        )


@Registry.register_driver("oracle")
class Driver:
    """Oracle storage driver.

    Attributes:
        migrations: Database schema migrations for Oracle.
        requires_rollback_on_error: Oracle aborts transactions when a query
            fails and requires an explicit ROLLBACK before executing new queries.
    """

    migrations = migrations
    requires_rollback_on_error = True

    def __init__(self, conn: BaseStorageAdapter):
        self.conversation = Conversation(conn)
        self.parent = Parent(conn)
        self.process = Process(conn)
        self.schema = Schema(conn)
        self.session = Session(conn)
