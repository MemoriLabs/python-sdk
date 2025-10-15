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

from uuid import uuid4

from memori.storage._base import (
    BaseConversation,
    BaseConversationMessage,
    BaseSchema,
    BaseSchemaVersion,
    BaseSession,
    BaseStorageAdaptor,
)


class Conversation(BaseConversation):
    def __init__(self, conn: BaseStorageAdaptor):
        super().__init__(conn)
        self.message = ConversationMessage(conn)

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


class Session(BaseSession):
    def create(self, uuid):
        self.conn.execute(
            """
            insert ignore into memori_session(
                uuid
            ) values (
                %s
            )
            """,
            (uuid,),
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
    def __init__(self, conn: BaseStorageAdaptor):
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


class Driver:
    def __init__(self, conn: BaseStorageAdaptor):
        self.conversation = Conversation(conn)
        self.schema = Schema(conn)
        self.session = Session(conn)
