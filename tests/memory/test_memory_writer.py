import pytest

from memori._config import Config
from memori.llm._constants import OPENAI_CLIENT_TITLE
from memori.memory._writer import Writer


def test_execute(config):
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
