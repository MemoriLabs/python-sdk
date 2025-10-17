from memori.llm.adapters.anthropic._adapter import Adapter


def test_get_formatted_query():
    assert Adapter().get_formatted_query({}) == []
    assert Adapter().get_formatted_query({"conversation": {"query": {}}}) == []

    assert Adapter().get_formatted_query(
        {
            "conversation": {
                "query": {
                    "messages": [
                        {"content": "abc", "role": "user"},
                        {"content": "def", "role": "assistant"},
                    ]
                }
            }
        }
    ) == [{"content": "abc", "role": "user"}, {"content": "def", "role": "assistant"}]


def test_get_formatted_response_unstreamed():
    assert Adapter().get_formatted_response({}) == []
    assert Adapter().get_formatted_query({"conversation": {"response": {}}}) == []

    assert Adapter().get_formatted_response(
        {
            "conversation": {
                "response": {
                    "content": [
                        {"text": "abc", "type": "text"},
                        {"text": "def", "type": "text"},
                    ],
                    "role": "user",
                }
            }
        }
    ) == [
        {"role": "user", "text": "abc", "type": "text"},
        {"role": "user", "text": "def", "type": "text"},
    ]
