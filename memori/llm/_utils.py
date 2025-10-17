r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       trymemori.com
"""

from memori.llm._constants import (
    ATHROPIC_CLIENT_TITLE,
    GOOGLE_CLIENT_TITLE,
    LANGCHAIN_CHATBEDROCK_CLIENT_TITLE,
    LANGCHAIN_CHATGOOGLEGENAI_CLIENT_TITLE,
    LANGCHAIN_CHATVERTEXAI_CLIENT_TITLE,
    LANGCHAIN_CLIENT_PROVIDER,
    LANGCHAIN_OPENAI_CLIENT_TITLE,
    OPENAI_CLIENT_TITLE,
)


def client_is_bedrock(provider, title):
    return (
        provider_is_langchain(provider) and title == LANGCHAIN_CHATBEDROCK_CLIENT_TITLE
    )


def llm_is_anthropic(provider, title):
    return title == ATHROPIC_CLIENT_TITLE


def llm_is_bedrock(provider, title):
    return (
        provider_is_langchain(provider) and title == LANGCHAIN_CHATBEDROCK_CLIENT_TITLE
    )


def llm_is_google(provider, title):
    return title == GOOGLE_CLIENT_TITLE or (
        provider_is_langchain(provider)
        and title
        in [LANGCHAIN_CHATGOOGLEGENAI_CLIENT_TITLE, LANGCHAIN_CHATVERTEXAI_CLIENT_TITLE]
    )


def llm_is_openai(provider, title):
    return title == OPENAI_CLIENT_TITLE or (
        provider_is_langchain(provider) and title == LANGCHAIN_OPENAI_CLIENT_TITLE
    )


def provider_is_langchain(provider):
    return provider == LANGCHAIN_CLIENT_PROVIDER
