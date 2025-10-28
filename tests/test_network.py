from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import requests

from memori._config import Config
from memori._network import AsyncRequest, _ApiRetryRecoverable


class TestApiRetryRecoverable:
    def test_is_retry_returns_true_for_5xx_errors(self):
        retry = _ApiRetryRecoverable()
        assert retry.is_retry("GET", 500) is True
        assert retry.is_retry("GET", 503) is True
        assert retry.is_retry("GET", 599) is True

    def test_is_retry_returns_false_for_non_5xx_errors(self):
        retry = _ApiRetryRecoverable()
        assert retry.is_retry("GET", 200) is False
        assert retry.is_retry("GET", 404) is False
        assert retry.is_retry("GET", 400) is False


class TestAsyncRequest:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def async_request(self, config):
        return AsyncRequest(config)

    def test_init(self, config):
        request = AsyncRequest(config)
        assert request.config == config

    def test_configure_session(self, async_request):
        session = requests.Session()
        configured = async_request.configure_session(session)

        assert configured is session
        assert configured.get_adapter("https://") is not None
        assert configured.get_adapter("http://") is not None

    def test_delete_calls_send(self, async_request, mocker):
        mock_send = mocker.patch.object(async_request, "send")
        async_request.delete("https://api.example.com", headers={"X-Test": "value"})
        mock_send.assert_called_once_with(
            "DELETE", "https://api.example.com", headers={"X-Test": "value"}
        )

    def test_get_calls_send(self, async_request, mocker):
        mock_send = mocker.patch.object(async_request, "send")
        async_request.get("https://api.example.com")
        mock_send.assert_called_once_with("GET", "https://api.example.com")

    def test_patch_calls_send(self, async_request, mocker):
        mock_send = mocker.patch.object(async_request, "send")
        async_request.patch("https://api.example.com", json={"key": "value"})
        mock_send.assert_called_once_with(
            "PATCH", "https://api.example.com", json={"key": "value"}
        )

    def test_post_calls_send(self, async_request, mocker):
        mock_send = mocker.patch.object(async_request, "send")
        async_request.post("https://api.example.com", data={"test": "data"})
        mock_send.assert_called_once_with(
            "POST", "https://api.example.com", data={"test": "data"}
        )

    def test_put_calls_send(self, async_request, mocker):
        mock_send = mocker.patch.object(async_request, "send")
        async_request.put("https://api.example.com")
        mock_send.assert_called_once_with("PUT", "https://api.example.com")

    @pytest.mark.asyncio
    async def test_send_async_success(self, async_request, mocker):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_request_ctx = AsyncMock()
        mock_request_ctx.__aenter__.return_value = mock_response
        mock_request_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_request_ctx
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await async_request.send_async(
                "GET", "https://api.example.com", headers={"X-Test": "value"}
            )

            assert result == mock_response

    @pytest.mark.asyncio
    async def test_send_async_retries_on_5xx_error(self, async_request, mocker):
        async_request.config.request_num_backoff = 2
        async_request.config.request_backoff_factor = 0.1

        error = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=503
        )

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=[error, error, None])
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_request_ctx = MagicMock()
        mock_request_ctx.__aenter__.return_value = mock_response
        mock_request_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_request_ctx
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await async_request.send_async(
                    "GET", "https://api.example.com"
                )

                assert result == mock_response
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_send_async_raises_on_4xx_error(self, async_request):
        error = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=404
        )

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=error)

        mock_request_ctx = MagicMock()
        mock_request_ctx.__aenter__.return_value = mock_response
        mock_request_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_request_ctx
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(aiohttp.ClientResponseError):
                await async_request.send_async("GET", "https://api.example.com")

    @pytest.mark.asyncio
    async def test_send_async_raises_after_max_retries(self, async_request):
        async_request.config.request_num_backoff = 1
        async_request.config.request_backoff_factor = 0.1

        error = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=503
        )

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=error)

        mock_request_ctx = MagicMock()
        mock_request_ctx.__aenter__.return_value = mock_response
        mock_request_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_request_ctx
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(aiohttp.ClientResponseError):
                    await async_request.send_async("GET", "https://api.example.com")

    def test_send_sync_success(self, async_request, mocker):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.request = MagicMock(return_value=mock_response)

        mocker.patch.object(
            async_request, "configure_session", return_value=mock_session
        )

        result = async_request.send_sync("POST", "https://api.example.com")

        assert result == mock_response
        mock_session.request.assert_called_once_with("POST", "https://api.example.com")

    def test_send_sync_raises_on_error(self, async_request, mocker):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(
            side_effect=requests.HTTPError("404 Not Found")
        )

        mock_session = MagicMock()
        mock_session.request = MagicMock(return_value=mock_response)

        mocker.patch.object(
            async_request, "configure_session", return_value=mock_session
        )

        with pytest.raises(requests.HTTPError):
            async_request.send_sync("GET", "https://api.example.com")

    @pytest.mark.asyncio
    async def test_send_uses_async_when_loop_running(self, async_request, mocker):
        mock_result = MagicMock()

        async def mock_async_send(*args, **kwargs):
            return mock_result

        mock_send_async = mocker.patch.object(
            async_request, "send_async", side_effect=mock_async_send
        )

        coro = async_request.send("GET", "https://api.example.com")
        result = await coro
        assert result == mock_result
        mock_send_async.assert_called_once_with("GET", "https://api.example.com")

    def test_send_uses_sync_when_no_loop(self, async_request, mocker):
        mock_result = MagicMock()
        mocker.patch.object(async_request, "send_sync", return_value=mock_result)
        mocker.patch("asyncio.get_running_loop", side_effect=RuntimeError)

        mock_loop = MagicMock()
        mock_loop.run_until_complete = MagicMock(return_value=mock_result)

        mock_executor = MagicMock()
        async_request.config.thread_pool_executor = mock_executor

        with patch("asyncio.new_event_loop", return_value=mock_loop):
            with patch("asyncio.set_event_loop") as mock_set_loop:
                result = async_request.send("GET", "https://api.example.com")

                mock_set_loop.assert_called_once_with(mock_loop)
                assert mock_loop.run_until_complete.called
                assert result == mock_result
