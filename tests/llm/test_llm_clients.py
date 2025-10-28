import pytest

from memori._config import Config
from memori.llm._clients import Anthropic, Google, LangChain, OpenAi, PydanticAi


class TestAnthropic:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def anthropic_client(self, config):
        return Anthropic(config)

    def test_register_adds_memori_wrappers_sync(self, anthropic_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.messages.create = mocker.MagicMock()
        mock_client.beta.messages.create = mocker.MagicMock()
        del mock_client._memori_installed

        mocker.patch("asyncio.get_running_loop", side_effect=RuntimeError)

        result = anthropic_client.register(mock_client)

        assert result is anthropic_client
        assert hasattr(mock_client, "_memori_installed")
        assert mock_client._memori_installed is True
        assert hasattr(mock_client, "_messages_create")
        assert hasattr(mock_client.beta, "_messages_create")

    @pytest.mark.asyncio
    async def test_register_adds_memori_wrappers_async(self, anthropic_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.messages.create = mocker.MagicMock()
        mock_client.beta.messages.create = mocker.MagicMock()
        del mock_client._memori_installed

        result = anthropic_client.register(mock_client)

        assert result is anthropic_client
        assert hasattr(mock_client, "_memori_installed")
        assert mock_client._memori_installed is True

    def test_register_skips_if_already_installed(self, anthropic_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client._memori_installed = True
        original_create = mock_client.messages.create

        result = anthropic_client.register(mock_client)

        assert result is anthropic_client
        assert mock_client.messages.create == original_create

    def test_register_raises_without_messages_attr(self, anthropic_client, mocker):
        mock_client = mocker.MagicMock(spec=[])

        with pytest.raises(RuntimeError, match="not instance of Anthropic"):
            anthropic_client.register(mock_client)


class TestGoogle:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def google_client(self, config):
        return Google(config)

    def test_register_adds_memori_wrappers(self, google_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.models.generate_content = mocker.MagicMock()
        del mock_client._memori_installed

        result = google_client.register(mock_client)

        assert result is google_client
        assert hasattr(mock_client, "_memori_installed")
        assert mock_client._memori_installed is True
        assert hasattr(mock_client.models, "actual_generate_content")

    def test_register_skips_if_already_installed(self, google_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client._memori_installed = True
        original_generate = mock_client.models.generate_content

        result = google_client.register(mock_client)

        assert result is google_client
        assert mock_client.models.generate_content == original_generate

    def test_register_raises_without_models_attr(self, google_client, mocker):
        mock_client = mocker.MagicMock(spec=[])

        with pytest.raises(RuntimeError, match="not instance of genai.Client"):
            google_client.register(mock_client)


class TestOpenAi:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def openai_client(self, config):
        return OpenAi(config)

    def test_register_adds_memori_wrappers_sync(self, openai_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.chat.completions.create = mocker.MagicMock()
        mock_client.beta.chat.completions.parse = mocker.MagicMock()
        del mock_client._memori_installed

        mocker.patch("asyncio.get_running_loop", side_effect=RuntimeError)

        result = openai_client.register(mock_client)

        assert result is openai_client
        assert hasattr(mock_client, "_memori_installed")
        assert mock_client._memori_installed is True
        assert hasattr(mock_client.chat, "_completions_create")
        assert hasattr(mock_client.beta, "_chat_completions_parse")

    def test_register_with_streaming_sync(self, openai_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.chat.completions.create = mocker.MagicMock()
        mock_client.beta.chat.completions.parse = mocker.MagicMock()
        del mock_client._memori_installed

        mocker.patch("asyncio.get_running_loop", side_effect=RuntimeError)

        result = openai_client.register(mock_client, stream=True)

        assert result is openai_client
        assert mock_client._memori_installed is True

    @pytest.mark.asyncio
    async def test_register_adds_memori_wrappers_async(self, openai_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.chat.completions.create = mocker.MagicMock()
        mock_client.beta.chat.completions.parse = mocker.MagicMock()
        del mock_client._memori_installed

        result = openai_client.register(mock_client)

        assert result is openai_client
        assert mock_client._memori_installed is True

    @pytest.mark.asyncio
    async def test_register_with_streaming_async(self, openai_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.chat.completions.create = mocker.MagicMock()
        mock_client.beta.chat.completions.parse = mocker.MagicMock()
        del mock_client._memori_installed

        result = openai_client.register(mock_client, stream=True)

        assert result is openai_client
        assert mock_client._memori_installed is True

    def test_register_skips_if_already_installed(self, openai_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client._memori_installed = True
        original_create = mock_client.chat.completions.create

        result = openai_client.register(mock_client)

        assert result is openai_client
        assert mock_client.chat.completions.create == original_create

    def test_register_raises_without_chat_attr(self, openai_client, mocker):
        mock_client = mocker.MagicMock(spec=[])

        with pytest.raises(RuntimeError, match="not instance of OpenAI"):
            openai_client.register(mock_client)


class TestPydanticAi:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def pydantic_client(self, config):
        return PydanticAi(config)

    def test_register_adds_memori_wrappers(self, pydantic_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client.chat.completions.create = mocker.MagicMock()
        del mock_client._memori_installed

        result = pydantic_client.register(mock_client)

        assert result is pydantic_client
        assert hasattr(mock_client, "_memori_installed")
        assert mock_client._memori_installed is True
        assert hasattr(mock_client.chat.completions, "actual_chat_completions_create")

    def test_register_skips_if_already_installed(self, pydantic_client, mocker):
        mock_client = mocker.MagicMock()
        mock_client._version = "1.0.0"
        mock_client._memori_installed = True
        original_create = mock_client.chat.completions.create

        result = pydantic_client.register(mock_client)

        assert result is pydantic_client
        assert mock_client.chat.completions.create == original_create

    def test_register_raises_without_chat_attr(self, pydantic_client, mocker):
        mock_client = mocker.MagicMock(spec=[])

        with pytest.raises(RuntimeError, match="not instantiated using PydanticAi"):
            pydantic_client.register(mock_client)


class TestLangChain:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def langchain_client(self, config):
        return LangChain(config)

    def test_register_without_any_client_raises(self, langchain_client):
        with pytest.raises(RuntimeError, match="called without client"):
            langchain_client.register()

    def test_register_chatbedrock(self, langchain_client, mocker):
        mock_chatbedrock = mocker.MagicMock()
        mock_chatbedrock.client.invoke_model = mocker.MagicMock()
        mock_chatbedrock.client.invoke_model_with_response_stream = mocker.MagicMock()
        del mock_chatbedrock.client._memori_installed

        result = langchain_client.register(chatbedrock=mock_chatbedrock)

        assert result is langchain_client
        assert hasattr(mock_chatbedrock.client, "_memori_installed")
        assert mock_chatbedrock.client._memori_installed is True
        assert hasattr(mock_chatbedrock.client, "_invoke_model")

    def test_register_chatgooglegenai(self, langchain_client, mocker):
        mock_chatgooglegenai = mocker.MagicMock()
        mock_chatgooglegenai.client.generate_content = mocker.MagicMock()
        mock_chatgooglegenai.async_client = None
        del mock_chatgooglegenai.client._memori_installed

        result = langchain_client.register(chatgooglegenai=mock_chatgooglegenai)

        assert result is langchain_client
        assert hasattr(mock_chatgooglegenai.client, "_memori_installed")
        assert mock_chatgooglegenai.client._memori_installed is True

    def test_register_chatgooglegenai_with_async_client(self, langchain_client, mocker):
        mock_chatgooglegenai = mocker.MagicMock()
        mock_chatgooglegenai.client.generate_content = mocker.MagicMock()
        mock_chatgooglegenai.async_client.stream_generate_content = mocker.MagicMock()
        del mock_chatgooglegenai.client._memori_installed

        result = langchain_client.register(chatgooglegenai=mock_chatgooglegenai)

        assert result is langchain_client
        assert mock_chatgooglegenai.client._memori_installed is True

    def test_register_chatopenai(self, langchain_client, mocker):
        mock_chatopenai = mocker.MagicMock()
        mock_chatopenai.http_client = None
        mock_chatopenai.async_http_client = None
        mock_chatopenai.client._client.beta.chat.completions.create = mocker.MagicMock()
        mock_chatopenai.client._client.beta.chat.completions.parse = mocker.MagicMock()
        mock_chatopenai.client._client.chat.completions.create = mocker.MagicMock()
        mock_chatopenai.client._client.chat.completions.parse = mocker.MagicMock()
        del mock_chatopenai.client._client._memori_installed

        mock_chatopenai.async_client._client.beta.chat.completions.create = (
            mocker.MagicMock()
        )
        mock_chatopenai.async_client._client.beta.chat.completions.parse = (
            mocker.MagicMock()
        )
        mock_chatopenai.async_client._client.chat.completions.create = (
            mocker.MagicMock()
        )
        mock_chatopenai.async_client._client.chat.completions.parse = mocker.MagicMock()
        del mock_chatopenai.async_client._client._memori_installed

        result = langchain_client.register(chatopenai=mock_chatopenai)

        assert result is langchain_client
        assert mock_chatopenai.client._client._memori_installed is True
        assert mock_chatopenai.async_client._client._memori_installed is True

    def test_register_chatvertexai(self, langchain_client, mocker):
        mock_chatvertexai = mocker.MagicMock()
        mock_chatvertexai.prediction_client.generate_content = mocker.MagicMock()
        del mock_chatvertexai.prediction_client._memori_installed

        result = langchain_client.register(chatvertexai=mock_chatvertexai)

        assert result is langchain_client
        assert hasattr(mock_chatvertexai.prediction_client, "_memori_installed")
        assert mock_chatvertexai.prediction_client._memori_installed is True

    def test_register_chatbedrock_raises_without_client_attr(
        self, langchain_client, mocker
    ):
        mock_chatbedrock = mocker.MagicMock(spec=[])

        with pytest.raises(RuntimeError, match="not instance of ChatBedrock"):
            langchain_client.register(chatbedrock=mock_chatbedrock)

    def test_register_chatgooglegenai_raises_without_client_attr(
        self, langchain_client, mocker
    ):
        mock_chatgooglegenai = mocker.MagicMock(spec=[])

        with pytest.raises(
            RuntimeError, match="not instance of ChatGoogleGenerativeAI"
        ):
            langchain_client.register(chatgooglegenai=mock_chatgooglegenai)

    def test_register_chatopenai_raises_without_client_attrs(
        self, langchain_client, mocker
    ):
        mock_chatopenai = mocker.MagicMock(spec=["client"])

        with pytest.raises(RuntimeError, match="not instance of ChatOpenAI"):
            langchain_client.register(chatopenai=mock_chatopenai)

    def test_register_chatvertexai_raises_without_prediction_client(
        self, langchain_client, mocker
    ):
        mock_chatvertexai = mocker.MagicMock(spec=[])

        with pytest.raises(RuntimeError, match="not instance of ChatVertexAI"):
            langchain_client.register(chatvertexai=mock_chatvertexai)
