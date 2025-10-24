#!/usr/bin/env python3

from tests.database.core import MySQLTestDBSession
from memori import Memori

session = MySQLTestDBSession()

for table_name in [
    "memori_conversation_message",
    "memori_conversation",
    "memori_session",
    "memori_parent",
    "memori_process",
    "memori_schema_version",
]:
    session.connection().exec_driver_sql(f"drop table if exists {table_name}")

# Executes all migrations.
Memori(conn=session).storage.build()
print("-" * 50)
# Has no effect, version number is set correctly.
Memori(conn=session).storage.build()
print("-" * 50)

session.connection().exec_driver_sql(
    """
    drop table memori_schema_version
    """
)

# Executes all migrations again.
Memori(conn=session).storage.build()

session.connection().exec_driver_sql(
    """
    delete from memori_schema_version
    """
)
session.commit()
