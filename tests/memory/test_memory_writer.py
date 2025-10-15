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
