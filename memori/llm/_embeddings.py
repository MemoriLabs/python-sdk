r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                 perfectam memoriam
                        by GibsonAI
                      memorilabs.ai
"""

import asyncio
import struct
from concurrent.futures import ProcessPoolExecutor
from typing import Any

from sentence_transformers import SentenceTransformer

_MODEL_CACHE: dict[str, SentenceTransformer] = {}
_DEFAULT_DIMENSION = 768
_EMBEDDING_EXECUTOR: ProcessPoolExecutor | None = None
_EMBEDDING_EXECUTOR_MAX_WORKERS = 4


def _get_model(model_name: str) -> SentenceTransformer:
    if model_name not in _MODEL_CACHE:
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]


def format_embedding_for_db(embedding: list[float], dialect: str) -> Any:
    """Format embedding for database storage.

    Args:
        embedding: List of floats representing the embedding vector
        dialect: Database dialect (postgresql, mysql, sqlite, mongodb)

    Returns:
        Formatted embedding optimized for the target database:
        - PostgreSQL/CockroachDB/MySQL/SQLite: Binary (BYTEA/BLOB) - compact & fast
        - MongoDB: Binary (BinData) - compact & fast
    """
    binary_data = struct.pack(f"<{len(embedding)}f", *embedding)

    if dialect == "mongodb":
        try:
            import bson

            return bson.Binary(binary_data)
        except ImportError:
            return binary_data
    else:
        return binary_data


def _get_embedding_executor() -> ProcessPoolExecutor:
    global _EMBEDDING_EXECUTOR
    if _EMBEDDING_EXECUTOR is None:
        _EMBEDDING_EXECUTOR = ProcessPoolExecutor(
            max_workers=_EMBEDDING_EXECUTOR_MAX_WORKERS
        )
    return _EMBEDDING_EXECUTOR


def embed_texts(
    texts: str | list[str], model: str = "all-mpnet-base-v2"
) -> list[list[float]]:
    inputs = [texts] if isinstance(texts, str) else [t for t in texts if t]
    if not inputs:
        return []

    try:
        encoder = _get_model(model)
    except (OSError, RuntimeError, ValueError):
        return [[0.0] * _DEFAULT_DIMENSION for _ in inputs]

    try:
        embeddings = encoder.encode(inputs, convert_to_numpy=True)
        return embeddings.tolist()
    except (RuntimeError, ValueError):
        try:
            dim = int(encoder.get_sentence_embedding_dimension())
        except (RuntimeError, ValueError, AttributeError):
            dim = _DEFAULT_DIMENSION
        return [[0.0] * dim for _ in inputs]


async def embed_texts_async(
    texts: str | list[str], model: str = "all-mpnet-base-v2"
) -> list[list[float]]:
    loop = asyncio.get_event_loop()
    executor = _get_embedding_executor()
    return await loop.run_in_executor(executor, embed_texts, texts, model)
