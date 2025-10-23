from unittest.mock import MagicMock, Mock
import pytest

from memori._config import Config
from memori.storage._manager import Manager
from memori.storage.drivers.mysql._driver import Driver as MysqlDriver
from memori.storage.drivers.postgresql._driver import Driver as PostgresqlDriver


@pytest.fixture
def mock_config():
    """Create a mock Config object with connection."""
    config = Config()
    config.conn = MagicMock()
    config.driver = MagicMock()
    return config


@pytest.fixture
def manager(mock_config):
    """Create a Manager instance with mocked config."""
    return Manager(mock_config)


def test_get_supported_dialects(manager):
    """Test that _get_supported_dialects returns registered dialects."""
    supported = manager._get_supported_dialects()

    # Should contain at least mysql and postgresql
    assert "mysql" in supported
    assert "postgresql" in supported
    assert isinstance(supported, list)


def test_get_dialect_family_exact_match(manager):
    """Test dialect family detection with exact matches."""
    # Test exact matches
    assert manager._get_dialect_family("mysql") == MysqlDriver.migrations
    assert manager._get_dialect_family("postgresql") == PostgresqlDriver.migrations
    assert manager._get_dialect_family("cockroachdb") == PostgresqlDriver.migrations


def test_get_dialect_family_no_match(manager):
    """Test dialect family detection returns None for unknown dialects."""
    assert manager._get_dialect_family("invalid") is None
    assert manager._get_dialect_family("redis") is None
    assert manager._get_dialect_family("unknown") is None


def test_requires_rollback_true(manager):
    """Test rollback requirement for dialects that need it."""
    assert manager._requires_rollback("postgresql") is True
    assert manager._requires_rollback("cockroachdb") is True


def test_requires_rollback_false(manager):
    """Test rollback requirement for dialects that don't need it."""
    assert manager._requires_rollback("mysql") is False


def test_requires_rollback_unknown_dialect(manager):
    """Test rollback returns False for unknown dialects."""
    assert manager._requires_rollback("unknown") is False


def test_build_unsupported_dialect(mock_config):
    """Test that build raises NotImplementedError for unsupported dialects."""
    mock_config.conn.get_dialect.return_value = "invalid"
    manager = Manager(mock_config)

    with pytest.raises(NotImplementedError) as exc_info:
        manager.build()

    assert "Unsupported dialect: invalid" in str(exc_info.value)
    assert "Supported dialects:" in str(exc_info.value)


def test_build_supported_dialect(mock_config):
    """Test that build works with supported dialects."""
    mock_config.conn.get_dialect.return_value = "mysql"

    # Mock the cli to avoid banner output
    manager = Manager(mock_config)
    manager.cli = MagicMock()

    # Mock schema version read
    mock_config.driver.schema.version.read.return_value = len(MysqlDriver.migrations)

    result = manager.build()

    assert result == manager
    assert mock_config.driver.schema.version.read.called


def test_build_for_rdbms_postgresql_rollback(mock_config):
    """Test that build_for_rdbms triggers rollback for PostgreSQL on error."""
    mock_config.conn.get_dialect.return_value = "postgresql"

    manager = Manager(mock_config)
    manager.cli = MagicMock()

    # Simulate schema version read failure
    mock_config.driver.schema.version.read.side_effect = Exception("Schema error")
    mock_config.driver.schema.version.read.return_value = len(
        PostgresqlDriver.migrations
    )

    manager.build_for_rdbms()

    # Verify rollback was called for postgresql
    assert mock_config.conn.rollback.called


def test_build_for_rdbms_cockroachdb_rollback(mock_config):
    """Test that build_for_rdbms triggers rollback for CockroachDB on error."""
    mock_config.conn.get_dialect.return_value = "cockroachdb"

    manager = Manager(mock_config)
    manager.cli = MagicMock()

    # Simulate schema version read failure
    mock_config.driver.schema.version.read.side_effect = Exception("Schema error")

    manager.build_for_rdbms()

    # Verify rollback was called for cockroachdb
    assert mock_config.conn.rollback.called


def test_build_for_rdbms_mysql_no_rollback(mock_config):
    """Test that build_for_rdbms does not trigger rollback for MySQL on error."""
    mock_config.conn.get_dialect.return_value = "mysql"

    manager = Manager(mock_config)
    manager.cli = MagicMock()

    # Simulate schema version read failure
    mock_config.driver.schema.version.read.side_effect = Exception("Schema error")

    manager.build_for_rdbms()

    # Verify rollback was NOT called for mysql
    assert not mock_config.conn.rollback.called


def test_build_for_rdbms_no_migration_mapping(mock_config):
    """Test that build_for_rdbms raises error for unmapped dialect."""
    mock_config.conn.get_dialect.return_value = "unknown_dialect"

    manager = Manager(mock_config)
    manager.cli = MagicMock()

    # Mock to bypass the initial schema version check
    mock_config.driver.schema.version.read.return_value = 0

    with pytest.raises(NotImplementedError) as exc_info:
        manager.build_for_rdbms()

    assert "No migration mapping found for dialect: unknown_dialect" in str(
        exc_info.value
    )
