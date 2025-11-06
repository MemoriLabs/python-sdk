import asyncio
import time
from unittest.mock import Mock

import pytest

from memori._config import Config
from memori.memory.augmentation._manager import Manager, _AugmentationRuntime, _runtime


def test_augmentation_runtime_init():
    runtime = _AugmentationRuntime()
    assert runtime.loop is None
    assert runtime.thread is None
    assert runtime.semaphore is None
    assert runtime.max_workers == 50


def test_manager_init():
    config = Config()
    config.augmentation_max_workers = 75

    manager = Manager(config)

    assert manager.config == config
    assert manager._active is False


def test_manager_start_sets_max_workers():
    config = Config()
    config.augmentation_max_workers = 75
    mock_conn = Mock()

    manager = Manager(config)
    manager.start(mock_conn)

    assert _runtime.max_workers == 75


def test_manager_start_with_none_conn():
    config = Config()
    manager = Manager(config)

    result = manager.start(None)

    assert result == manager
    assert manager.conn_factory is None
    assert manager._active is False


def test_manager_start_with_conn():
    config = Config()
    manager = Manager(config)
    mock_conn = Mock()

    result = manager.start(mock_conn)

    assert result == manager
    assert manager.conn_factory == mock_conn
    assert manager._active is True


def test_manager_enqueue_inactive():
    config = Config()
    manager = Manager(config)
    payload = {"test": "data"}

    result = manager.enqueue(payload)

    assert result == manager


def test_manager_enqueue_no_conn_factory():
    config = Config()
    manager = Manager(config)
    manager._active = True
    payload = {"test": "data"}

    result = manager.enqueue(payload)

    assert result == manager


def test_runtime_ensure_started():
    original_thread = _runtime.thread

    _runtime.ensure_started(50)

    if original_thread is None:
        assert _runtime.thread is not None
        time.sleep(0.1)
        assert _runtime.loop is not None
        assert _runtime.semaphore is not None


@pytest.mark.asyncio
async def test_manager_process_augmentations_no_augmentations():
    config = Config()
    manager = Manager(config)
    manager.conn_factory = Mock()
    manager.augmentations = []
    payload = {"conversation_id": 123}

    original_runtime = _runtime.semaphore
    _runtime.semaphore = asyncio.Semaphore(10)

    try:
        await manager._process_augmentations(payload)
    finally:
        _runtime.semaphore = original_runtime
