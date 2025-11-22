from unittest.mock import Mock, patch

from memori.llm._embeddings import _get_model


def test_get_model_uses_bundled_path_when_exists():
    with patch("memori.llm._embeddings.SentenceTransformer") as mock_transformer:
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            mock_model = Mock()
            mock_transformer.return_value = mock_model

            result = _get_model("all-mpnet-base-v2")

            assert result is mock_model
            mock_transformer.assert_called_once()
            call_args = mock_transformer.call_args[0][0]
            assert "memori/models/all-mpnet-base-v2" in call_args


def test_get_model_falls_back_to_huggingface_when_bundled_not_exists():
    with patch("memori.llm._embeddings.SentenceTransformer") as mock_transformer:
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            mock_model = Mock()
            mock_transformer.return_value = mock_model

            from memori.llm import _embeddings

            _embeddings._MODEL_CACHE.clear()

            result = _get_model("all-mpnet-base-v2")

            assert result is mock_model
            mock_transformer.assert_called_once_with("all-mpnet-base-v2")


def test_get_model_bundled_path_caching():
    with patch("memori.llm._embeddings.SentenceTransformer") as mock_transformer:
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            mock_model = Mock()
            mock_transformer.return_value = mock_model

            from memori.llm import _embeddings

            _embeddings._MODEL_CACHE.clear()

            result1 = _get_model("test-model")
            result2 = _get_model("test-model")

            assert result1 is result2
            mock_transformer.assert_called_once()


def test_get_model_different_models_with_mixed_bundled_status():
    with patch("memori.llm._embeddings.SentenceTransformer") as mock_transformer:
        with patch("pathlib.Path.exists") as mock_exists:
            mock_model1 = Mock()
            mock_model2 = Mock()
            mock_transformer.side_effect = [mock_model1, mock_model2]
            mock_exists.side_effect = [True, False]

            from memori.llm import _embeddings

            _embeddings._MODEL_CACHE.clear()

            result1 = _get_model("model-1")
            result2 = _get_model("model-2")

            assert result1 is not result2
            assert mock_transformer.call_count == 2
