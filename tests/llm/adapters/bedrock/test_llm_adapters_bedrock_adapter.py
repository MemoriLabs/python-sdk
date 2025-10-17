from memori.llm.adapters.bedrock._adapter import Adapter


def test_get_formatted_query():
    assert Adapter().get_formatted_query({}) == []
    assert Adapter().get_formatted_query({"conversation": {"query": {}}}) == []

    assert Adapter().get_formatted_query(
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


def test_get_formatted_response_streamed():
    assert Adapter().get_formatted_response({}) == []
    assert Adapter().get_formatted_query({"conversation": {"response": {}}}) == []

    assert Adapter().get_formatted_response(
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
