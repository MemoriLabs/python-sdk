from uuid import UUID

from memori.storage.drivers.sqlite._driver import (
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


def test_parent_create(mock_conn, mock_single_result):
    """Test creating a parent record."""
    mock_conn.execute.return_value = mock_single_result({"id": 123})

    parent = Parent(mock_conn)
    result = parent.create("external-parent-id")

    assert result == 123
    assert mock_conn.execute.call_count == 2
    assert mock_conn.flush.call_count == 1

    # Verify INSERT query
    insert_call = mock_conn.execute.call_args_list[0]
    assert "insert or ignore into memori_parent" in insert_call[0][0].lower()
    assert insert_call[0][1][1] == "external-parent-id"

    # Verify SELECT query
    select_call = mock_conn.execute.call_args_list[1]
    assert "select id" in select_call[0][0].lower()
    assert "from memori_parent" in select_call[0][0].lower()
    assert select_call[0][1] == ("external-parent-id",)


def test_parent_generates_uuid(mock_conn, mock_single_result):
    """Test that create generates a valid UUID string."""
    mock_conn.execute.return_value = mock_single_result({"id": 123})

    parent = Parent(mock_conn)
    parent.create("external-parent-id")

    # Check that a UUID was generated in the INSERT
    insert_call = mock_conn.execute.call_args_list[0]
    uuid_arg = insert_call[0][1][0]

    # SQLite driver uses str(uuid4()), so verify it's a string
    assert isinstance(uuid_arg, str)
    # Verify it can be parsed as a UUID
    UUID(uuid_arg)


def test_process_create(mock_conn, mock_single_result):
    """Test creating a process record."""
    mock_conn.execute.return_value = mock_single_result({"id": 456})

    process = Process(mock_conn)
    result = process.create("external-process-id")

    assert result == 456
    assert mock_conn.execute.call_count == 2
    assert mock_conn.flush.call_count == 1

    # Verify INSERT query
    insert_call = mock_conn.execute.call_args_list[0]
    assert "insert or ignore into memori_process" in insert_call[0][0].lower()
    assert insert_call[0][1][1] == "external-process-id"

    # Verify SELECT query
    select_call = mock_conn.execute.call_args_list[1]
    assert "select id" in select_call[0][0].lower()
    assert "from memori_process" in select_call[0][0].lower()
    assert select_call[0][1] == ("external-process-id",)


def test_session_create(mock_conn, mock_single_result):
    """Test creating a session record."""
    mock_conn.execute.return_value = mock_single_result({"id": 789})

    session = Session(mock_conn)
    session_uuid = "test-session-uuid"
    result = session.create(session_uuid, parent_id=123, process_id=456)

    assert result == 789
    assert mock_conn.execute.call_count == 2
    assert mock_conn.flush.call_count == 1

    # Verify INSERT query
    insert_call = mock_conn.execute.call_args_list[0]
    assert "insert or ignore into memori_session" in insert_call[0][0].lower()
    assert insert_call[0][1] == (session_uuid, 123, 456)

    # Verify SELECT query
    select_call = mock_conn.execute.call_args_list[1]
    assert "select id" in select_call[0][0].lower()
    assert "from memori_session" in select_call[0][0].lower()
    assert select_call[0][1] == (session_uuid,)


def test_conversation_initialization(mock_conn):
    """Test that Conversation initializes its sub-components."""
    conversation = Conversation(mock_conn)

    assert isinstance(conversation.message, ConversationMessage)
    assert isinstance(conversation.messages, ConversationMessages)
    assert conversation.conn == mock_conn


def test_conversation_create(mock_conn, mock_single_result):
    """Test creating a conversation record."""
    mock_conn.execute.return_value = mock_single_result({"id": 101})

    conversation = Conversation(mock_conn)
    result = conversation.create(session_id=789)

    assert result == 101
    assert mock_conn.execute.call_count == 2
    assert mock_conn.flush.call_count == 1

    # Verify INSERT query
    insert_call = mock_conn.execute.call_args_list[0]
    assert "insert or ignore into memori_conversation" in insert_call[0][0].lower()

    # Verify the UUID is generated and session_id is passed
    uuid_arg, session_id_arg = insert_call[0][1]
    UUID(uuid_arg)  # Verify it's a valid UUID string
    assert session_id_arg == 789

    # Verify SELECT query
    select_call = mock_conn.execute.call_args_list[1]
    assert "select id" in select_call[0][0].lower()
    assert "from memori_conversation" in select_call[0][0].lower()
    assert select_call[0][1] == (789,)


def test_conversation_message_create(mock_conn):
    """Test creating a conversation message."""
    message = ConversationMessage(mock_conn)
    message.create(
        conversation_id=101, role="user", type="text", content="Hello, world!"
    )

    assert mock_conn.execute.call_count == 1

    # Verify INSERT query
    insert_call = mock_conn.execute.call_args_list[0]
    assert "insert into memori_conversation_message" in insert_call[0][0].lower()

    # Verify parameters
    uuid_arg, conv_id, role, type_, content = insert_call[0][1]
    UUID(uuid_arg)  # Verify it's a valid UUID string
    assert conv_id == 101
    assert role == "user"
    assert type_ == "text"
    assert content == "Hello, world!"


def test_conversation_messages_read(mock_conn, mock_multiple_results):
    """Test reading conversation messages."""
    mock_conn.execute.return_value = mock_multiple_results(
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    )

    messages = ConversationMessages(mock_conn)
    result = messages.read(conversation_id=101)

    assert len(result) == 2
    assert result[0] == {"content": "Hello", "role": "user"}
    assert result[1] == {"content": "Hi there!", "role": "assistant"}

    # Verify SELECT query
    select_call = mock_conn.execute.call_args_list[0]
    assert "select role" in select_call[0][0].lower()
    assert "from memori_conversation_message" in select_call[0][0].lower()
    assert "order by id" in select_call[0][0].lower()
    assert select_call[0][1] == (101,)


def test_conversation_messages_read_empty(mock_conn, mock_empty_result):
    """Test reading messages when none exist."""
    mock_conn.execute.return_value = mock_empty_result

    messages = ConversationMessages(mock_conn)
    result = messages.read(conversation_id=999)

    assert result == []


def test_schema_version_create(mock_conn):
    """Test creating a schema version record."""
    schema_version = SchemaVersion(mock_conn)
    schema_version.create(num=1)

    assert mock_conn.execute.call_count == 1

    # Verify INSERT query
    insert_call = mock_conn.execute.call_args_list[0]
    assert "insert into memori_schema_version" in insert_call[0][0].lower()
    assert insert_call[0][1] == (1,)


def test_schema_version_read(mock_conn, mock_single_result):
    """Test reading the current schema version."""
    mock_conn.execute.return_value = mock_single_result({"num": 5})

    schema_version = SchemaVersion(mock_conn)
    result = schema_version.read()

    assert result == 5

    # Verify SELECT query
    select_call = mock_conn.execute.call_args_list[0]
    assert "select num" in select_call[0][0].lower()
    assert "from memori_schema_version" in select_call[0][0].lower()


def test_schema_version_delete(mock_conn):
    """Test deleting schema version records."""
    schema_version = SchemaVersion(mock_conn)
    schema_version.delete()

    assert mock_conn.execute.call_count == 1

    # Verify DELETE query
    delete_call = mock_conn.execute.call_args_list[0]
    assert "delete from memori_schema_version" in delete_call[0][0].lower()


def test_schema_initialization(mock_conn):
    """Test that Schema initializes SchemaVersion correctly."""
    schema = Schema(mock_conn)

    assert isinstance(schema.version, SchemaVersion)
    assert schema.conn == mock_conn
