#!/usr/bin/env python3

from memori import Memori
from tests.database.core import SQLiteTestDBSession

session = SQLiteTestDBSession()

for table_name in [
    "memori_conversation_message",
    "memori_conversation",
    "memori_session",
    "memori_parent",
    "memori_process",
    "memori_schema_version",
]:
    session.connection().exec_driver_sql(f"DROP TABLE IF EXISTS {table_name}")

# Executes all migrations.
Memori(conn=session).config.storage.build()
print("-" * 50)
# Has no effect, version number is set correctly.
Memori(conn=session).config.storage.build()
print("-" * 50)

session.connection().exec_driver_sql(
    """
    DROP TABLE IF EXISTS memori_schema_version
    """
)
session.commit()

# Executes all migrations again.
Memori(conn=session).config.storage.build()

session.connection().exec_driver_sql(
    """
    DELETE FROM memori_schema_version
    """
)
session.commit()
