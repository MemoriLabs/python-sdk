from uuid import UUID
import pytest
from datetime import datetime
from unittest.mock import Mock

from memori.storage.drivers.mongodb._driver import (
    Conversation,
    ConversationMessage,
    ConversationMessages,
    Driver,
    Parent,
    Process,
    Schema,
    SchemaVersion,
    Session,
)


def test_driver_initialization(mock_conn):
    """Test that Driver initializes all components correctly."""
    driver = Driver(mock_conn)
    
    assert isinstance(driver.conversation, Conversation)
    assert isinstance(driver.parent, Parent)
    assert isinstance(driver.process, Process)
    assert isinstance(driver.schema, Schema)
    assert isinstance(driver.session, Session)


def test_parent_create(mock_conn):
    """Test creating a parent record."""
    # Mock the find_one to return None (no existing record)
    mock_conn.execute.side_effect = [
        None,  # find_one returns None (no existing record)
        Mock(inserted_id=123),  # insert_one returns mock result
    ]
    
    parent = Parent(mock_conn)
    result = parent.create("external-parent-id")
    
    assert result == 123
    assert mock_conn.execute.call_count == 2  # find_one, insert_one
    
    # Verify find_one query for existing record
    find_call = mock_conn.execute.call_args_list[0]
    assert find_call[0][0] == "memori_parent"
    assert find_call[0][1] == "find_one"
    assert find_call[0][2] == {"external_id": "external-parent-id"}
    
    # Verify insert_one query
    insert_call = mock_conn.execute.call_args_list[1]
    assert insert_call[0][0] == "memori_parent"
    assert insert_call[0][1] == "insert_one"
    doc = insert_call[0][2]
    assert doc["external_id"] == "external-parent-id"
    assert "uuid" in doc
    assert "date_created" in doc


def test_parent_create_existing_record(mock_conn):
    """Test creating a parent record when it already exists."""
    # Mock the find_one to return existing record
    existing_record = Mock()
    existing_record.get.return_value = 456
    mock_conn.execute.return_value = existing_record
    
    parent = Parent(mock_conn)
    result = parent.create("external-parent-id")
    
    assert result == 456
    assert mock_conn.execute.call_count == 1  # Only find_one


def test_parent_generates_uuid(mock_conn):
    """Test that create generates a valid UUID."""
    mock_conn.execute.side_effect = [
        None,  # find_one returns None
        Mock(inserted_id=123),  # insert_one returns mock result
    ]
    
    parent = Parent(mock_conn)
    parent.create("external-parent-id")
    
    # Check that a UUID was generated in the insert_one
    insert_call = mock_conn.execute.call_args_list[1]
    doc = insert_call[0][2]
    uuid_str = doc["uuid"]
    
    # Verify it's a valid UUID string
    UUID(uuid_str)  # Will raise ValueError if invalid


def test_process_create(mock_conn):
    """Test creating a process record."""
    mock_conn.execute.side_effect = [
        None,  # find_one returns None
        Mock(inserted_id=456),  # insert_one returns mock result
    ]
    
    process = Process(mock_conn)
    result = process.create("external-process-id")
    
    assert result == 456
    assert mock_conn.execute.call_count == 2
    
    # Verify find_one query
    find_call = mock_conn.execute.call_args_list[0]
    assert find_call[0][0] == "memori_process"
    assert find_call[0][1] == "find_one"
    assert find_call[0][2] == {"external_id": "external-process-id"}
    
    # Verify insert_one query
    insert_call = mock_conn.execute.call_args_list[1]
    assert insert_call[0][0] == "memori_process"
    assert insert_call[0][1] == "insert_one"
    doc = insert_call[0][2]
    assert doc["external_id"] == "external-process-id"


def test_session_create(mock_conn):
    """Test creating a session record."""
    mock_conn.execute.side_effect = [
        None,  # find_one returns None
        Mock(inserted_id=789),  # insert_one returns mock result
    ]
    
    session = Session(mock_conn)
    session_uuid = "test-session-uuid"
    result = session.create(session_uuid, parent_id=123, process_id=456)
    
    assert result == 789
    assert mock_conn.execute.call_count == 2
    
    # Verify find_one query
    find_call = mock_conn.execute.call_args_list[0]
    assert find_call[0][0] == "memori_session"
    assert find_call[0][1] == "find_one"
    assert find_call[0][2] == {"uuid": "test-session-uuid"}
    
    # Verify insert_one query
    insert_call = mock_conn.execute.call_args_list[1]
    assert insert_call[0][0] == "memori_session"
    assert insert_call[0][1] == "insert_one"
    doc = insert_call[0][2]
    assert doc["uuid"] == "test-session-uuid"
    assert doc["parent_id"] == 123
    assert doc["process_id"] == 456


def test_conversation_initialization(mock_conn):
    """Test that Conversation initializes its sub-components."""
    conversation = Conversation(mock_conn)
    
    assert isinstance(conversation.message, ConversationMessage)
    assert isinstance(conversation.messages, ConversationMessages)
    assert conversation.conn == mock_conn


def test_conversation_create(mock_conn):
    """Test creating a conversation record."""
    mock_conn.execute.side_effect = [
        None,  # find_one returns None
        Mock(inserted_id=101)  # insert_one returns mock result
    ]
    
    conversation = Conversation(mock_conn)
    result = conversation.create(session_id=789)
    
    assert result == 101
    assert mock_conn.execute.call_count == 2
    
    # Verify find_one query
    find_call = mock_conn.execute.call_args_list[0]
    assert find_call[0][0] == "memori_conversation"
    assert find_call[0][1] == "find_one"
    assert find_call[0][2] == {"session_id": 789}
    
    # Verify insert_one query
    insert_call = mock_conn.execute.call_args_list[1]
    assert insert_call[0][0] == "memori_conversation"
    assert insert_call[0][1] == "insert_one"
    doc = insert_call[0][2]
    assert doc["session_id"] == 789
    assert "uuid" in doc


def test_conversation_create_existing_record(mock_conn):
    """Test creating a conversation when it already exists."""
    existing_record = Mock()
    existing_record.get.return_value = 999
    mock_conn.execute.return_value = existing_record
    
    conversation = Conversation(mock_conn)
    result = conversation.create(session_id=789)
    
    assert result == 999
    assert mock_conn.execute.call_count == 1  # Only find_one


def test_conversation_message_create(mock_conn):
    """Test creating a conversation message."""
    message = ConversationMessage(mock_conn)
    message.create(
        conversation_id=101,
        role="user",
        type="text",
        content="Hello, world!"
    )
    
    assert mock_conn.execute.call_count == 1
    
    # Verify insert_one query
    insert_call = mock_conn.execute.call_args_list[0]
    assert insert_call[0][0] == "memori_conversation_message"
    assert insert_call[0][1] == "insert_one"
    doc = insert_call[0][2]
    
    assert doc["conversation_id"] == 101
    assert doc["role"] == "user"
    assert doc["type"] == "text"
    assert doc["content"] == "Hello, world!"
    assert "uuid" in doc
    assert "date_created" in doc


def test_conversation_messages_read(mock_conn):
    """Test reading conversation messages."""
    # Mock the find query to return cursor with messages
    mock_cursor = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    mock_conn.execute.return_value = mock_cursor
    
    messages = ConversationMessages(mock_conn)
    result = messages.read(conversation_id=101)
    
    assert len(result) == 2
    assert result[0] == {"content": "Hello", "role": "user"}
    assert result[1] == {"content": "Hi there!", "role": "assistant"}
    
    # Verify find query
    find_call = mock_conn.execute.call_args_list[0]
    assert find_call[0][0] == "memori_conversation_message"
    assert find_call[0][1] == "find"
    assert find_call[0][2] == {"conversation_id": 101}
    assert find_call[0][3] == {"role": 1, "content": 1, "_id": 0}


def test_conversation_messages_read_empty(mock_conn):
    """Test reading messages when none exist."""
    mock_conn.execute.return_value = []
    
    messages = ConversationMessages(mock_conn)
    result = messages.read(conversation_id=999)
    
    assert result == []


def test_schema_version_create(mock_conn):
    """Test creating a schema version record."""
    schema_version = SchemaVersion(mock_conn)
    schema_version.create(num=1)
    
    assert mock_conn.execute.call_count == 1
    
    # Verify insert_one query
    insert_call = mock_conn.execute.call_args_list[0]
    assert insert_call[0][0] == "memori_schema_version"
    assert insert_call[0][1] == "insert_one"
    doc = insert_call[0][2]
    assert doc["num"] == 1


def test_schema_version_read(mock_conn):
    """Test reading the current schema version."""
    mock_result = {"num": 5}
    mock_conn.execute.return_value = mock_result
    
    schema_version = SchemaVersion(mock_conn)
    result = schema_version.read()
    
    assert result == 5
    
    # Verify find_one query
    find_call = mock_conn.execute.call_args_list[0]
    assert find_call[0][0] == "memori_schema_version"
    assert find_call[0][1] == "find_one"
    assert find_call[0][2] == {}
    assert find_call[0][3] == {"num": 1, "_id": 0}


def test_schema_version_read_none(mock_conn):
    """Test reading schema version when none exists."""
    mock_conn.execute.return_value = None
    
    schema_version = SchemaVersion(mock_conn)
    result = schema_version.read()
    
    assert result is None


def test_schema_version_delete(mock_conn):
    """Test deleting schema version records."""
    schema_version = SchemaVersion(mock_conn)
    schema_version.delete()
    
    assert mock_conn.execute.call_count == 1
    
    # Verify delete_many query
    delete_call = mock_conn.execute.call_args_list[0]
    assert delete_call[0][0] == "memori_schema_version"
    assert delete_call[0][1] == "delete_many"
    assert delete_call[0][2] == {}


def test_schema_initialization(mock_conn):
    """Test that Schema initializes SchemaVersion correctly."""
    schema = Schema(mock_conn)
    
    assert isinstance(schema.version, SchemaVersion)
    assert schema.conn == mock_conn


def test_driver_migrations_attribute():
    """Test that Driver has migrations attribute."""
    from memori.storage.drivers.mongodb._driver import Driver
    from memori.storage.migrations._mongodb import migrations
    
    assert Driver.migrations == migrations


def test_driver_requires_rollback_on_error_attribute():
    """Test that Driver has requires_rollback_on_error attribute."""
    from memori.storage.drivers.mongodb._driver import Driver
    
    assert Driver.requires_rollback_on_error is False


def test_driver_registry_registration():
    """Test that Driver is properly registered with the registry."""
    from memori.storage._registry import Registry
    
    registry = Registry()
    assert "mongodb" in registry._drivers


def test_mongodb_operations_with_datetime(mock_conn):
    """Test that MongoDB operations properly handle datetime fields."""
    mock_conn.execute.side_effect = [
        None,  # find_one returns None
        Mock(inserted_id=123),  # insert_one returns mock result
    ]
    
    parent = Parent(mock_conn)
    parent.create("external-parent-id")
    
    # Verify insert_one query includes date_created
    insert_call = mock_conn.execute.call_args_list[1]
    doc = insert_call[0][2]
    
    assert "date_created" in doc
    assert isinstance(doc["date_created"], datetime)
    assert doc["date_updated"] is None


def test_mongodb_conversation_message_with_datetime(mock_conn):
    """Test that conversation message creation includes proper datetime fields."""
    message = ConversationMessage(mock_conn)
    message.create(
        conversation_id=101,
        role="user",
        type="text",
        content="Test message"
    )
    
    # Verify insert_one query includes date_created
    insert_call = mock_conn.execute.call_args_list[0]
    doc = insert_call[0][2]
    
    assert "date_created" in doc
    assert isinstance(doc["date_created"], datetime)
    assert doc["date_updated"] is None


def test_mongodb_session_with_datetime(mock_conn):
    """Test that session creation includes proper datetime fields."""
    mock_conn.execute.side_effect = [
        None,  # find_one returns None
        Mock(inserted_id=789),  # insert_one returns mock result
    ]
    
    session = Session(mock_conn)
    session.create("test-uuid", parent_id=123, process_id=456)
    
    # Verify insert_one query includes date_created
    insert_call = mock_conn.execute.call_args_list[1]
    doc = insert_call[0][2]
    
    assert "date_created" in doc
    assert isinstance(doc["date_created"], datetime)
    assert doc["date_updated"] is None
