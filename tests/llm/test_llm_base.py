import json

from memori._config import Config
from memori.llm._base import BaseInvoke, BaseLlmAdaptor
from memori.llm._constants import (
    LANGCHAIN_CLIENT_PROVIDER,
    LANGCHAIN_OPENAI_CLIENT_TITLE,
    OPENAI_CLIENT_TITLE,
)
from tests.llm.unit_test_objects import UnitTestX, UnitTestY


def test_list_to_json_native_types():
    assert BaseInvoke(Config(), "abc").list_to_json([1, 2, 3]) == [1, 2, 3]

    assert BaseInvoke(Config(), "abc").list_to_json([{"a": "b"}, {"c": "d"}]) == [
        {"a": "b"},
        {"c": "d"},
    ]

    assert BaseInvoke(Config(), "abc").list_to_json([[1, 2], [3, 4], [{"a", "b"}]]) == [
        [1, 2],
        [3, 4],
        [{"a", "b"}],
    ]

    assert BaseInvoke(Config(), "abc").list_to_json(
        [[1, {"a": "b"}], [{"c": "d"}, 2]]
    ) == [
        [1, {"a": "b"}],
        [{"c": "d"}, 2],
    ]


def test_list_to_json_object_simple():
    assert BaseInvoke(Config(), "abc").list_to_json([1, UnitTestX()]) == [
        1,
        {"a": 1, "b": 2},
    ]


def test_list_to_json_object_complex():
    assert BaseInvoke(Config(), "abc").list_to_json([1, UnitTestY()]) == [
        1,
        {"c": 3, "d": {"a": 1, "b": 2}},
    ]


def test_list_to_json_list_list_list():
    assert BaseInvoke(Config(), "abc").list_to_json([1, [2, [3, [4]]]]) == [
        1,
        [2, [3, [4]]],
    ]


def test_list_to_dict_to_list():
    assert BaseInvoke(Config(), "abc").list_to_json([{"a": 1, "b": [1, [2]]}]) == [
        {"a": 1, "b": [1, [2]]}
    ]


def test_dict_to_json_dict():
    assert BaseInvoke(Config(), "abc").dict_to_json({"a": "b", "c": "d"}) == {
        "a": "b",
        "c": "d",
    }


def test_dist_to_json_dict_has_dict():
    assert BaseInvoke(Config(), "abc").dict_to_json(
        {"a": {"b": {"c": "d"}, "e": 123}}
    ) == {"a": {"b": {"c": "d"}, "e": 123}}


def test_configure_for_streaming_usage_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_title = OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def", "stream": True}) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {"include_usage": False}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}


def test_configure_for_streaming_usage_streaming_options_is_not_dict_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_title = OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": 123}
    ) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }


def test_configure_for_streaming_usage_only_if_stream_is_true_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_title = OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def"}) == {"abc": "def"}


def test_configure_for_streaming_usage_langchain_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def", "stream": True}) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {"include_usage": False}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}


def test_configure_for_streaming_usage_streaming_opts_is_not_dict_langchain_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": 123}
    ) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }


def test_configure_for_streaming_usage_only_if_stream_is_true_langchain_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def"}) == {"abc": "def"}


def test_get_response_content():
    invoke = BaseInvoke(Config(), "abc")

    assert invoke.get_response_content({"abc": "def"}) == {"abc": "def"}

    class MockLegacyAPIResponse:
        def __init__(self):
            self.text = json.dumps({"abc": "def"})

    legacy_api_response = MockLegacyAPIResponse()
    legacy_api_response.__class__.__name__ = "LegacyAPIResponse"
    legacy_api_response.__class__.__module__ = "openai._legacy_response"

    assert invoke.get_response_content(legacy_api_response) == {"abc": "def"}


def test_exclude_injected_messages():
    adapter = BaseLlmAdaptor()

    # No injected count - returns all messages
    messages = [{"role": "user", "content": "Hello"}]
    payload = {"conversation": {"query": {}}}
    assert adapter._exclude_injected_messages(messages, payload) == messages

    # Injected count of 2 - slices off first 2 messages
    messages = [
        {"role": "user", "content": "injected 1"},
        {"role": "assistant", "content": "injected 2"},
        {"role": "user", "content": "new message"},
    ]
    payload = {"conversation": {"query": {"_memori_injected_count": 2}}}
    assert adapter._exclude_injected_messages(messages, payload) == [
        {"role": "user", "content": "new message"}
    ]

    # Safe navigation - missing keys don't cause errors
    assert adapter._exclude_injected_messages(messages, {}) == messages
