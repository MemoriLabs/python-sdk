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

from memori._utils import generate_uniq
from memori.storage._base import (
    BaseConversation,
    BaseConversationMessage,
    BaseConversationMessages,
    BaseKnowledgeGraph,
    BaseParent,
    BaseParentFact,
    BaseProcess,
    BaseProcessAttribute,
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
            INSERT IGNORE INTO memori_conversation(
                uuid,
                session_id
            ) VALUES (
                %s,
                %s
            )
            """,
            (
                uuid,
                session_id,
            ),
        )
        self.conn.commit()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_conversation
                 WHERE session_id = %s
                """,
                (session_id,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )

    def update(self, id: int, summary: str):
        if summary is None:
            return self

        self.conn.execute(
            """
            UPDATE memori_conversation
               SET summary = %s
             WHERE id = %s
            """,
            (
                summary,
                id,
            ),
        )
        self.conn.commit()


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
                SELECT role,
                       content
                  FROM memori_conversation_message
                 WHERE conversation_id = %s
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


class KnowledgeGraph(BaseKnowledgeGraph):
    def create(self, entity_id: int, semantic_triples: list):
        if semantic_triples is None or len(semantic_triples) == 0:
            return self

        for semantic_triple in semantic_triples:
            uniq = generate_uniq(
                [semantic_triple.subject_name, semantic_triple.subject_type]
            )

            self.conn.execute(
                """
                INSERT IGNORE INTO memori_subject(
                    uuid,
                    name,
                    type,
                    uniq
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    uuid4(),
                    semantic_triple.name,
                    semantic_triple.type,
                    uniq,
                ),
            )
            self.conn.commit()

            subject_id = (
                self.conn.execute(
                    """
                    SELECT id
                      FROM memori_subject
                     WHERE uniq = %s
                    """,
                    (uniq,),
                )
                .mappings()
                .fetchone()
                .get("id", None)
            )

            uniq = generate_uniq([semantic_triple.predicate])

            self.conn.execute(
                """
                INSERT IGNORE INTO memori_predicate(
                    uuid,
                    content,
                    uniq
                ) VALUES (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    uuid4(),
                    semantic_triple.predicate,
                    uniq,
                ),
            )
            self.conn.commit()

            predicate_id = (
                self.conn.execute(
                    """
                    SELECT id
                      FROM memori_predicate
                     WHERE uniq = %s
                    """,
                    (uniq,),
                )
                .mappings()
                .fetchone()
                .get("id", None)
            )

            uniq = generate_uniq(
                [semantic_triple.object_name, semantic_triple.object_type]
            )

            self.conn.execute(
                """
                INSERT IGNORE INTO memori_object(
                    uuid,
                    name,
                    type,
                    uniq
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    uuid4(),
                    semantic_triple.object_name,
                    semantic_triple.object_type,
                    uniq,
                ),
            )
            self.conn.commit()

            object_id = (
                self.conn.execute(
                    """
                    SELECT id
                      FROM memori_object
                     WHERE uniq = %s
                    """,
                    (uniq,),
                )
                .mappings()
                .fetchone()
                .get("id", None)
            )

            if (
                entity_id is not None
                and subject_id is not None
                and predicate_id is not None
                and object_id is not None
            ):
                self.conn.execute(
                    """
                    INSERT INTO memori_knowledge_graph(
                        uuid,
                        entity_id,
                        subject_id,
                        predicate_id,
                        object_id,
                        num_times,
                        date_last_time
                    ) VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        1,
                        current_timestamp()
                    )
                    ON DUPLICATE KEY UPDATE
                        num_times = num_times + 1
                        date_last_time = current_timestamp()
                    """,
                    (uuid4(), entity_id, subject_id, predicate_id, object_id),
                )
                self.conn.commit()

        return self


class Parent(BaseParent):
    def create(self, external_id: str):
        self.conn.execute(
            """
            INSERT IGNORE INTO memori_parent(
                uuid,
                external_id
            ) VALUES (
                %s,
                %s
            )
            """,
            (uuid4(), external_id),
        )
        self.conn.commit()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_parent
                 WHERE external_id = %s
                """,
                (external_id,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )


class ParentFact(BaseParentFact):
    def create(self, entity_id: str, facts: list):
        if facts is None or len(facts) == 0:
            return self

        for fact in facts:
            self.conn.execute(
                """
                INSERT INTO memori_entity_fact(
                    uuid,
                    entity_id,
                    content,
                    num_times,
                    date_last_time,
                    uniq
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    current_timestamp(),
                    %s
                )
                ON DUPLICATE KEY UPDATE
                    num_times = num_times + 1
                    date_last_time = current_timestamp()
                """,
                (
                    uuid4(),
                    entity_id,
                    fact,
                    1,
                    generate_uniq(fact),
                ),
            )

        self.conn.commit()

        return self


class Process(BaseProcess):
    def create(self, external_id: str):
        self.conn.execute(
            """
            INSERT IGNORE INTO memori_process(
                uuid,
                external_id
            ) VALUES (
                %s,
                %s
            )
            """,
            (
                uuid4(),
                external_id,
            ),
        )
        self.conn.commit()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_process
                 WHERE external_id = %s
                """,
                (external_id,),
            )
            .mappings()
            .fetchone()
            .get("id", None)
        )


class ProcessAttribute(BaseProcessAttribute):
    def create(self, process_id: int, attributes: list):
        if attributes is None or len(attributes) == 0:
            return self

        for attribute in attributes:
            self.conn.execute(
                """
                INSERT INTO memori_process_attribute(
                    uuid,
                    process_id,
                    content,
                    num_times,
                    date_last_time,
                    uniq
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    current_timestamp(),
                    %s
                )
                ON DUPLICATE KEY UPDATE
                    num_times = num_times + 1
                    date_last_time = current_timestamp()
                """,
                (
                    uuid4(),
                    process_id,
                    attribute,
                    1,
                    generate_uniq(attribute),
                ),
            )

        self.conn.commit()

        return self


class Session(BaseSession):
    def create(self, uuid: str, parent_id: int, process_id: int):
        self.conn.execute(
            """
            INSERT IGNORE INTO memori_session(
                uuid,
                parent_id,
                process_id
            ) VALUES (
                %s,
                %s,
                %s
            )
            """,
            (
                uuid,
                parent_id,
                process_id,
            ),
        )
        self.conn.commit()

        return (
            self.conn.execute(
                """
                SELECT id
                  FROM memori_session
                 WHERE uuid = %s
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
            INSERT INTO memori_schema_version(
                num
            ) VALUES (
                %s
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
