import time
from unittest.mock import MagicMock

import pytest

from memori._config import Config
from memori.storage import Manager as StorageManager
from memori.storage.session.asynchronous.queued._manager import Manager, Queue
from memori.storage.session.asynchronous.queued._transaction import Task, Transaction


@pytest.fixture
def mock_config():
    config = Config()
    config.storage = StorageManager(config)
    config.storage.adapter = MagicMock()
    config.storage.driver = MagicMock()
    return config


@pytest.fixture
def queue_manager(mock_config):
    manager = Manager(mock_config, MagicMock())
    return manager


def test_transaction_creation(mock_config):
    manager = Manager(mock_config, MagicMock())
    transaction = manager.start()

    assert isinstance(transaction, Transaction)
    assert transaction.config == mock_config
    assert len(transaction.tasks) == 0


def test_transaction_execute_task(mock_config):
    transaction = Transaction(mock_config)
    transaction.execute("SELECT * FROM test", param1="value1")

    assert len(transaction.tasks) == 1
    assert transaction.tasks[0].type_id == Task.TASK_TYPE_EXECUTE
    assert transaction.tasks[0].args == ("SELECT * FROM test",)
    assert transaction.tasks[0].kwargs == {"param1": "value1"}


def test_transaction_commit_task(mock_config):
    transaction = Transaction(mock_config)
    transaction.commit()

    assert len(transaction.tasks) == 1
    assert transaction.tasks[0].type_id == Task.TASK_TYPE_COMMIT


def test_transaction_flush_task(mock_config):
    transaction = Transaction(mock_config)
    transaction.flush()

    assert len(transaction.tasks) == 1
    assert transaction.tasks[0].type_id == Task.TASK_TYPE_FLUSH


def test_transaction_chaining(mock_config):
    transaction = Transaction(mock_config)
    transaction.execute("INSERT INTO test").commit().flush()

    assert len(transaction.tasks) == 3
    assert transaction.tasks[0].type_id == Task.TASK_TYPE_EXECUTE
    assert transaction.tasks[1].type_id == Task.TASK_TYPE_COMMIT
    assert transaction.tasks[2].type_id == Task.TASK_TYPE_FLUSH


def test_queue_initialization(mock_config):
    caller = MagicMock()
    queue = Queue(mock_config, caller)

    assert queue.config == mock_config
    assert queue._loop is None
    assert queue._running is False
    assert queue._thread is None
    assert queue.transactions is None
    assert queue.worker is None


def test_queue_start_and_stop(mock_config):
    caller = MagicMock()
    queue = Queue(mock_config, caller)

    queue.start()
    time.sleep(0.1)

    assert queue._running is True
    assert queue._loop is not None
    assert queue._thread is not None
    assert queue.transactions is not None
    assert queue.worker is not None

    queue.stop()
    time.sleep(0.1)

    assert queue._running is False


def test_manager_run_with_execute(mock_config):
    mock_config.storage.adapter.execute.return_value = "result"

    manager = Manager(mock_config, MagicMock())
    manager.queue.start()
    time.sleep(0.1)

    try:
        transaction = manager.start()
        transaction.execute("SELECT * FROM test")

        result = manager.run(transaction)

        assert result == "result"
        assert mock_config.storage.adapter.execute.called
    finally:
        manager.queue.stop()


def test_manager_run_with_commit(mock_config):
    mock_config.storage.adapter.commit.return_value = None

    manager = Manager(mock_config, MagicMock())
    manager.queue.start()
    time.sleep(0.1)

    try:
        transaction = manager.start()
        transaction.commit()

        result = manager.run(transaction)

        assert result is None
        assert mock_config.storage.adapter.commit.called
    finally:
        manager.queue.stop()


def test_manager_run_with_flush(mock_config):
    mock_config.storage.adapter.flush.return_value = None

    manager = Manager(mock_config, MagicMock())
    manager.queue.start()
    time.sleep(0.1)

    try:
        transaction = manager.start()
        transaction.flush()

        result = manager.run(transaction)

        assert result is None
        assert mock_config.storage.adapter.flush.called
    finally:
        manager.queue.stop()


def test_manager_run_multiple_transactions(mock_config):
    mock_config.storage.adapter.execute.side_effect = ["result1", "result2", "result3"]

    manager = Manager(mock_config, MagicMock())
    manager.queue.start()
    time.sleep(0.1)

    try:
        results = []
        for i in range(3):
            transaction = manager.start()
            transaction.execute(f"SELECT {i}")
            results.append(manager.run(transaction))

        assert results == ["result1", "result2", "result3"]
        assert mock_config.storage.adapter.execute.call_count == 3
    finally:
        manager.queue.stop()


def test_queue_timeout_on_not_ready(mock_config):
    caller = MagicMock()
    queue = Queue(mock_config, caller)

    # Don't start the queue
    transaction = Transaction(mock_config)

    with pytest.raises(RuntimeError, match="Queue failed to start within timeout"):
        queue.enqueue(transaction)


def test_enqueue_with_null_loop_raises_error(mock_config):
    caller = MagicMock()
    queue = Queue(mock_config, caller)
    queue._ready.set()

    transaction = Transaction(mock_config)

    with pytest.raises(RuntimeError, match="Event loop not initialized"):
        queue.enqueue(transaction)


def test_storage_none_handling(mock_config):
    mock_config.storage = None

    transaction = Transaction(mock_config)
    transaction.execute("SELECT * FROM test").commit().flush()

    assert len(transaction.tasks) == 3
