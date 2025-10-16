import pytest

from memori._config import Config
from memori.memory._writer import Writer


def test_parse_query_anthropic_openai():
    assert Writer(Config()).parse_query(
        {
            "conversation": {
                "query": {
                    "messages": [
                        {"content": "abc", "role": "user"},
                        {"content": "def", "role": "system"},
                    ]
                }
            }
        }
    ) == [{"content": "abc", "role": "user"}, {"content": "def", "role": "system"}]


def test_parse_query_bedrock():
    assert Writer(Config()).parse_query(
        {
            "conversation": {
                "query": {
                    "body": {
                        "messages": [
                            {"content": "abc", "role": "user"},
                            {"content": "def", "role": "system"},
                        ]
                    }
                }
            }
        }
    ) == [{"content": "abc", "role": "user"}, {"content": "def", "role": "system"}]


def test_parse_query_google():
    assert Writer(Config()).parse_query(
        {
            "conversation": {
                "query": {
                    "contents": [
                        {"parts": [{"text": "abc"}, {"text": "def"}], "role": "user"},
                        {"parts": [{"text": "ghi"}], "role": "system"},
                    ]
                }
            }
        }
    ) == [{"content": "abc def", "role": "user"}, {"content": "ghi", "role": "system"}]


def test_parse_response_anthropic_unstreamed():
    assert Writer(Config()).parse_response(
        {
            "conversation": {
                "response": {
                    "content": [
                        {"text": "abc", "type": "text"},
                        {"text": "def", "type": "text"},
                    ]
                }
            }
        }
    ) == [
        {"role": "model", "text": "abc", "type": "text"},
        {"role": "model", "text": "def", "type": "text"},
    ]


def test_parse_response_bedrock_streamed():
    assert Writer(Config()).parse_response(
        {
            "conversation": {
                "response": [
                    {"chunk": {"bytes": {"message": {"role": "assistant"}}}},
                    {"chunk": {"bytes": {"delta": {"text": "abc"}}}},
                    {"chunk": {"bytes": {"delta": {"text": "def"}}}},
                ]
            }
        }
    ) == [{"role": "assistant", "text": "abcdef", "type": "text"}]


def test_parse_response_google_streamed():
    assert Writer(Config()).parse_response(
        {
            "conversation": {
                "response": [
                    {
                        "candidates": [
                            {
                                "content": {
                                    "parts": [{"text": "abc"}, {"text": "def"}],
                                    "role": "model",
                                }
                            },
                        ]
                    },
                    {
                        "candidates": [
                            {"content": {"parts": [{"text": "ghi"}], "role": "model"}}
                        ]
                    },
                ]
            }
        }
    ) == [{"role": "model", "text": "abcdefghi", "type": "text"}]


def test_parse_response_google_unstreamed():
    assert Writer(Config()).parse_response(
        {
            "conversation": {
                "response": {
                    "candidates": [
                        {"content": {"parts": [{"text": "abc"}], "role": "model"}},
                        {"content": {"parts": [{"text": "def"}], "role": "model"}},
                    ]
                }
            }
        }
    ) == [
        {"role": "model", "text": "abc", "type": "text"},
        {"role": "model", "text": "def", "type": "text"},
    ]


def test_parse_response_openai_streamed():
    assert Writer(Config()).parse_response(
        {
            "conversation": {
                "query": {"stream": True},
                "response": {
                    "choices": [
                        {
                            "delta": {
                                "content": "abc",
                                "role": "assistant",
                            }
                        },
                        {
                            "delta": {
                                "content": "def",
                                "role": "assistant",
                            }
                        },
                    ]
                },
            }
        }
    ) == [{"role": "assistant", "text": "abcdef", "type": "text"}]


def test_parse_response_openai_unstreamed():
    assert Writer(Config()).parse_response(
        {
            "conversation": {
                "query": {},
                "response": {
                    "choices": [
                        {"message": {"content": "abc", "role": "assistant"}},
                        {"message": {"content": "def", "role": "assistant"}},
                    ]
                },
            }
        }
    ) == [
        {"role": "assistant", "text": "abc", "type": "text"},
        {"role": "assistant", "text": "def", "type": "text"},
    ]


def test_execute(config):
    Writer(config).execute(
        {
            "conversation": {
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

    assert (
        (
            config.conn.execute(
                """
            select role,
                   content
              from memori_conversation_message
             where conversation_id = %s
            """,
                (config.cache.conversation_id,),
            )
            .mappings()
            .fetchall()
        )
        == [
            {"role": "user", "content": "abc"},
            {"role": "assistant", "content": "def"},
            {"role": "assistant", "content": "ghi"},
        ]
    )


def test_execute_with_parent_and_process(config):
    config.parent_id = "123"
    config.process_id = "456"

    Writer(config).execute(
        {
            "conversation": {
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

    assert (
        (
            config.conn.execute(
                """
            select role,
                   content
              from memori_conversation_message
             where conversation_id = %s
            """,
                (config.cache.conversation_id,),
            )
            .mappings()
            .fetchall()
        )
        == [
            {"role": "user", "content": "abc"},
            {"role": "assistant", "content": "def"},
            {"role": "assistant", "content": "ghi"},
        ]
    )

    assert (
        (
            config.conn.execute(
                """
                select external_id
                  from memori_parent
                 where id = %s
                """,
                (config.cache.parent_id,),
            )
            .mappings()
            .fetchone()
            .get("external_id", None)
        )
        == "123"
    )

    assert (
        (
            config.conn.execute(
                """
                select external_id
                  from memori_process
                 where id = %s
                """,
                (config.cache.process_id,),
            )
            .mappings()
            .fetchone()
            .get("external_id", None)
        )
        == "456"
    )

    assert (
        (
            config.conn.execute(
                """
                select parent_id,
                       process_id
                  from memori_session
                 where id = %s
                """,
                (config.cache.session_id,),
            )
            .mappings()
            .fetchone()
        )
        == {"parent_id": config.cache.parent_id, "process_id": config.cache.process_id}
    )
