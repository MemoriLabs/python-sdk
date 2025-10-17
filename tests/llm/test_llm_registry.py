from memori.llm._constants import (
    ATHROPIC_CLIENT_TITLE,
    GOOGLE_CLIENT_TITLE,
    LANGCHAIN_CHATBEDROCK_CLIENT_TITLE,
    LANGCHAIN_CLIENT_PROVIDER,
    OPENAI_CLIENT_TITLE,
)
from memori.llm._registry import Registry
from memori.llm.adapters.anthropic._adapter import Adapter as AnthropicLlmAdapter
from memori.llm.adapters.bedrock._adapter import Adapter as BedrockLlmAdapter
from memori.llm.adapters.google._adapter import Adapter as GoogleLlmAdapter
from memori.llm.adapters.openai._adapter import Adapter as OpenAiLlmAdapter


def test_llm_anthropic():
    assert isinstance(Registry().llm(None, ATHROPIC_CLIENT_TITLE), AnthropicLlmAdapter)


def test_llm_bedrock():
    assert isinstance(
        Registry().llm(LANGCHAIN_CLIENT_PROVIDER, LANGCHAIN_CHATBEDROCK_CLIENT_TITLE),
        BedrockLlmAdapter,
    )


def test_llm_google():
    assert isinstance(Registry().llm(None, GOOGLE_CLIENT_TITLE), GoogleLlmAdapter)


def test_llm_openai():
    assert isinstance(Registry().llm(None, OPENAI_CLIENT_TITLE), OpenAiLlmAdapter)
