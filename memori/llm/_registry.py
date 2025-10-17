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

from memori.llm._utils import (
    llm_is_anthropic,
    llm_is_bedrock,
    llm_is_google,
    llm_is_openai,
)
from memori.llm.adapters.anthropic._adapter import Adapter as AnthropicLlmAdapter
from memori.llm.adapters.bedrock._adapter import Adapter as BedrockLlmAdapter
from memori.llm.adapters.google._adapter import Adapter as GoogleLlmAdapter
from memori.llm.adapters.openai._adapter import Adapter as OpenAiLlmAdapter


class Registry:
    def llm(self, provider, title):
        if llm_is_openai(provider, title):
            return OpenAiLlmAdapter()
        elif llm_is_anthropic(provider, title):
            return AnthropicLlmAdapter()
        elif llm_is_google(provider, title):
            return GoogleLlmAdapter()
        if llm_is_bedrock(provider, title):
            return BedrockLlmAdapter()

        raise RuntimeError("could not determine LLM for adapter")
