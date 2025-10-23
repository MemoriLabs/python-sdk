import pytest

from memori._config import Config
from memori.llm._constants import OPENAI_CLIENT_TITLE
from memori.memory._writer import Writer


def test_execute(config, mocker):
    mock_messages = [
        {"role": "user", "content": "abc"},
        {"role": "assistant", "content": "def"},
        {"role": "assistant", "content": "ghi"},
    ]
    config.conn.execute.return_value.mappings.return_value.fetchall.return_value = (
        mock_messages
    )

    Writer(config).execute(
        {
            "conversation": {
                "client": {"provider": None, "title": OPENAI_CLIENT_TITLE},
                "query": {"messages": [{"content": "abc", "role": "user"}]},
                "response": {
                    "choices": [
                        {"message": {"content": "def", "role": "assistant"}},
                        {"message": {"content": "ghi", "role": "assistant"}},
                    ]
                },
            }
        }
    )

    assert config.cache.session_id is not None
    assert config.cache.conversation_id is not None
    
    assert config.driver.session.create.called
    assert config.driver.conversation.create.called
    assert config.driver.conversation.message.create.call_count == 3
    
    calls = config.driver.conversation.message.create.call_args_list
    assert calls[0][0][1] == "user"
    assert calls[0][0][3] == "abc"
    assert calls[1][0][1] == "assistant"
    assert calls[1][0][3] == "def"
    assert calls[2][0][1] == "assistant"
    assert calls[2][0][3] == "ghi"


def test_execute_with_parent_and_process(config, mocker):
    config.parent_id = "123"
    config.process_id = "456"

    mock_messages = [
        {"role": "user", "content": "abc"},
        {"role": "assistant", "content": "def"},
        {"role": "assistant", "content": "ghi"},
    ]
    config.conn.execute.return_value.mappings.return_value.fetchall.return_value = (
        mock_messages
    )
    config.conn.execute.return_value.mappings.return_value.fetchone.return_value = {
        "external_id": "123"
    }

    Writer(config).execute(
        {
            "conversation": {
                "client": {"provider": None, "title": OPENAI_CLIENT_TITLE},
                "query": {"messages": [{"content": "abc", "role": "user"}]},
                "response": {
                    "choices": [
                        {"message": {"content": "def", "role": "assistant"}},
                        {"message": {"content": "ghi", "role": "assistant"}},
                    ]
                },
            }
        }
    )

    assert config.cache.parent_id is not None
    assert config.cache.process_id is not None
    assert config.cache.session_id is not None
    assert config.cache.conversation_id is not None
    
    assert config.driver.parent.create.called
    assert config.driver.parent.create.call_args[0][0] == "123"
    
    assert config.driver.process.create.called
    assert config.driver.process.create.call_args[0][0] == "456"
    
    assert config.driver.session.create.called
    session_call_args = config.driver.session.create.call_args[0]
    assert session_call_args[1] == config.cache.parent_id
    assert session_call_args[2] == config.cache.process_id
    
    assert config.driver.conversation.message.create.call_count == 3
