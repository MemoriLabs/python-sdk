r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       memorilabs.ai
"""

migrations = {
    1: [
        {
            "description": "create collection memori_schema_version",
            "operation": """
                db.memori_schema_version.createIndex({"num": 1}, {"unique": true})
            """,
        },
        {
            "description": "create collection memori_parent",
            "operation": """
                db.memori_parent.createIndex({"external_id": 1}, {"unique": true})
                db.memori_parent.createIndex({"uuid": 1}, {"unique": true})
            """,
        },
        {
            "description": "create collection memori_process",
            "operation": """
                db.memori_process.createIndex({"external_id": 1}, {"unique": true})
                db.memori_process.createIndex({"uuid": 1}, {"unique": true})
            """,
        },
        {
            "description": "create collection memori_session",
            "operation": """
                db.memori_session.createIndex({"uuid": 1}, {"unique": true})
                db.memori_session.createIndex({"parent_id": 1, "_id": 1}, {"unique": true, "sparse": true})
                db.memori_session.createIndex({"process_id": 1, "_id": 1}, {"unique": true, "sparse": true})
            """,
        },
        {
            "description": "create collection memori_conversation",
            "operation": """
                db.memori_conversation.createIndex({"session_id": 1}, {"unique": true})
                db.memori_conversation.createIndex({"uuid": 1}, {"unique": true})
            """,
        },
        {
            "description": "create collection memori_conversation_message",
            "operation": """
                db.memori_conversation_message.createIndex({"uuid": 1}, {"unique": true})
                db.memori_conversation_message.createIndex({"conversation_id": 1, "_id": 1}, {"unique": true})
            """,
        },
    ]
}
