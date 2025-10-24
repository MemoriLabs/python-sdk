r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""

from datetime import datetime, timezone
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
from memori.storage.migrations._mongodb import migrations


class Conversation(BaseConversation):
    def __init__(self, conn: BaseStorageAdapter):
        super().__init__(conn)
        self.message = ConversationMessage(conn)
        self.messages = ConversationMessages(conn)

    def create(self, session_id):
        conversation_uuid = str(uuid4())
        
        # Check if conversation already exists for this session
        existing = self.conn.execute(
            "memori_conversation",
            "find_one",
            {"session_id": session_id}
        )
        
        if existing:
            return existing.get("_id")
        
        # Create new conversation
        conversation_doc = {
            "uuid": conversation_uuid,
            "session_id": session_id,
            "date_created": datetime.now(timezone.utc),
            "date_updated": None
        }
        
        result = self.conn.execute(
            "memori_conversation",
            "insert_one",
            conversation_doc
        )
        
        return result.inserted_id


class ConversationMessage(BaseConversationMessage):
    def create(self, conversation_id: int, role: str, type: str, content: str):
        message_doc = {
            "uuid": str(uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "type": type,
            "content": content,
            "date_created": datetime.now(timezone.utc),
            "date_updated": None
        }
        
        self.conn.execute(
            "memori_conversation_message",
            "insert_one",
            message_doc
        )


class ConversationMessages(BaseConversationMessages):
    def read(self, conversation_id: int):
        results = self.conn.execute(
            "memori_conversation_message",
            "find",
            {"conversation_id": conversation_id},
            {"role": 1, "content": 1, "_id": 0}
        )
        
        messages = []
        for result in results:
            messages.append({
                "content": result["content"], 
                "role": result["role"]
            })
        
        return messages


class Parent(BaseParent):
    def create(self, external_id: str):
        # Check if parent already exists
        existing = self.conn.execute(
            "memori_parent",
            "find_one",
            {"external_id": external_id}
        )
        
        if existing:
            return existing.get("_id")
        
        # Create new parent
        parent_doc = {
            "uuid": str(uuid4()),
            "external_id": external_id,
            "date_created": datetime.now(timezone.utc),
            "date_updated": None
        }
        
        self.conn.execute(
            "memori_parent",
            "insert_one",
            parent_doc
        )
        
        # Return the ID of the created or existing parent
        result = self.conn.execute(
            "memori_parent",
            "find_one",
            {"external_id": external_id}
        )
        
        return result.get("_id")


class Process(BaseProcess):
    def create(self, external_id: str):
        # Check if process already exists
        existing = self.conn.execute(
            "memori_process",
            "find_one",
            {"external_id": external_id}
        )
        
        if existing:
            return existing.get("_id")
        
        # Create new process
        process_doc = {
            "uuid": str(uuid4()),
            "external_id": external_id,
            "date_created": datetime.now(timezone.utc),
            "date_updated": None
        }
        
        self.conn.execute(
            "memori_process",
            "insert_one",
            process_doc
        )
        
        # Return the ID of the created or existing process
        result = self.conn.execute(
            "memori_process",
            "find_one",
            {"external_id": external_id}
        )
        
        return result.get("_id")


class Session(BaseSession):
    def create(self, uuid: str, parent_id: int, process_id: int):
        # Check if session already exists
        existing = self.conn.execute(
            "memori_session",
            "find_one",
            {"uuid": str(uuid)}
        )
        
        if existing:
            return existing.get("_id")
        
        # Create new session
        session_doc = {
            "uuid": str(uuid),
            "parent_id": parent_id,
            "process_id": process_id,
            "date_created": datetime.now(timezone.utc),
            "date_updated": None
        }
        
        self.conn.execute(
            "memori_session",
            "insert_one",
            session_doc
        )
        
        # Return the ID of the created or existing session
        result = self.conn.execute(
            "memori_session",
            "find_one",
            {"uuid": str(uuid)}
        )
        
        return result.get("_id")


class Schema(BaseSchema):
    def __init__(self, conn: BaseStorageAdapter):
        super().__init__(conn)
        self.version = SchemaVersion(conn)


class SchemaVersion(BaseSchemaVersion):
    def create(self, num: int):
        schema_doc = {
            "num": num
        }
        
        self.conn.execute(
            "memori_schema_version",
            "insert_one",
            schema_doc
        )

    def delete(self):
        self.conn.execute(
            "memori_schema_version",
            "delete_many",
            {}
        )

    def read(self):
        result = self.conn.execute(
            "memori_schema_version",
            "find_one",
            {},
            {"num": 1, "_id": 0}
        )
        
        return result.get("num") if result else None


@Registry.register_driver("mongodb")
class Driver:
    """MongoDB storage driver.
    
    Attributes:
        migrations: Database schema migrations for MongoDB.
        requires_rollback_on_error: MongoDB does not abort transactions on query 
            errors by default, so no rollback is needed to continue executing queries.
    """
    migrations = migrations
    requires_rollback_on_error = False
    
    def __init__(self, conn: BaseStorageAdapter):
        self.conversation = Conversation(conn)
        self.parent = Parent(conn)
        self.process = Process(conn)
        self.schema = Schema(conn)
        self.session = Session(conn)
