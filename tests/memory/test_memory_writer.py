import pytest

from memori._config import Config
from memori.memory._writer import Writer


def test_parse_query_anthropic_openai():
    assert Writer(Config()).parse_query(
        {
            "query": {
                "messages": [
                    {"content": "abc", "role": "user"},
                    {"content": "def", "role": "system"},
                ]
            }
        }
    ) == [{"content": "abc", "role": "user"}, {"content": "def", "role": "system"}]


def test_parse_query_google():
    assert Writer(Config()).parse_query(
        {
            "query": {
                "contents": [
                    {"parts": [{"text": "abc"}, {"text": "def"}], "role": "user"},
                    {"parts": [{"text": "ghi"}], "role": "system"},
                ]
            }
        }
    ) == [{"content": "abc def", "role": "user"}, {"content": "ghi", "role": "system"}]


def test_parse_bedrock():
    assert Writer(Config()).parse_query(
        {
            "query": {
                "body": {
                    "messages": [
                        {"content": "abc", "role": "user"},
                        {"content": "def", "role": "system"},
                    ]
                }
            }
        }
    ) == [{"content": "abc", "role": "user"}, {"content": "def", "role": "system"}]


def test_execute(config):
    Writer(config).execute(
        {
            "query": {
                "messages": [
                    {"content": "abc", "role": "user"}
                ]
            }
        }
    )

    assert config.cache.session_id is not None
    assert config.cache.conversation_id is not None

    assert (
        config.conn.execute(
            """
            select role,
                   content
              from memori_conversation_message
             where conversation_id = %s
            """,
            (config.cache.conversation_id,)
        )
        .mappings()
        .fetchall()
    ) == [{'role': 'user', 'content': 'abc'}]
