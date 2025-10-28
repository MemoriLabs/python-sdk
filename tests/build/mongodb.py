#!/usr/bin/env python3

from memori import Memori
from tests.database.core import MongoTestDBSession

# MongoTestDBSession is already a MongoClient instance
client = MongoTestDBSession
db = client["memori_test"]

# Drop existing collections
for collection_name in [
    "memori_conversation_message",
    "memori_conversation",
    "memori_session",
    "memori_parent",
    "memori_process",
    "memori_schema_version",
]:
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

# Executes all migrations.
Memori(conn=client).storage.build()
print("-" * 50)
# Has no effect, version number is set correctly.
Memori(conn=client).storage.build()
print("-" * 50)

# Drop schema version collection
if "memori_schema_version" in db.list_collection_names():
    db.drop_collection("memori_schema_version")

# Executes all migrations again.
Memori(conn=client).storage.build()

# Clear schema version
db["memori_schema_version"].delete_many({})
client.admin.command("ping")
