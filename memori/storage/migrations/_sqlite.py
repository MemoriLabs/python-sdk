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

migrations = {
    1: [
        {
            "description": "create table memori_schema_version",
            "operation": """
                CREATE TABLE IF NOT EXISTS memori_schema_version(
                    num INTEGER NOT NULL PRIMARY KEY
                )
            """,
        },
        {
            "description": "create table memori_parent",
            "operation": """
                CREATE TABLE IF NOT EXISTS memori_parent(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    date_created TEXT NOT NULL DEFAULT (datetime('now')),
                    date_updated TEXT DEFAULT NULL,
                    --
                    CONSTRAINT uk_memori_parent_external_id UNIQUE (external_id),
                    CONSTRAINT uk_memori_parent_uuid UNIQUE (uuid)
                )
            """,
        },
        {
            "description": "create table memori_process",
            "operation": """
                CREATE TABLE IF NOT EXISTS memori_process(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    date_created TEXT NOT NULL DEFAULT (datetime('now')),
                    date_updated TEXT DEFAULT NULL,
                    --
                    CONSTRAINT uk_memori_process_external_id UNIQUE (external_id),
                    CONSTRAINT uk_memori_process_uuid UNIQUE (uuid)
                )
            """,
        },
        {
            "description": "create table memori_session",
            "operation": """
                CREATE TABLE IF NOT EXISTS memori_session(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    parent_id INTEGER DEFAULT NULL,
                    process_id INTEGER DEFAULT NULL,
                    date_created TEXT NOT NULL DEFAULT (datetime('now')),
                    date_updated TEXT DEFAULT NULL,
                    --
                    CONSTRAINT uk_memori_session_parent_id UNIQUE (parent_id, id),
                    CONSTRAINT uk_memori_session_process_id UNIQUE (process_id, id),
                    CONSTRAINT uk_memori_session_uuid UNIQUE (uuid),
                    --
                    CONSTRAINT fk_memori_sess_parent
                       FOREIGN KEY (parent_id)
                        REFERENCES memori_parent (id)
                         ON DELETE CASCADE,
                    CONSTRAINT fk_memori_sess_process
                       FOREIGN KEY (process_id)
                        REFERENCES memori_process (id)
                         ON DELETE CASCADE
                )
            """,
        },
        {
            "description": "create table memori_conversation",
            "operation": """
                CREATE TABLE IF NOT EXISTS memori_conversation(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    session_id INTEGER NOT NULL,
                    date_created TEXT NOT NULL DEFAULT (datetime('now')),
                    date_updated TEXT DEFAULT NULL,
                    --
                    CONSTRAINT uk_memori_conversation_session_id UNIQUE (session_id),
                    CONSTRAINT uk_memori_conversation_uuid UNIQUE (uuid),
                    --
                    CONSTRAINT fk_memori_conv_session
                       FOREIGN KEY (session_id)
                        REFERENCES memori_session (id)
                         ON DELETE CASCADE
                )
            """,
        },
        {
            "description": "create table memori_conversation_message",
            "operation": """
                CREATE TABLE IF NOT EXISTS memori_conversation_message(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    type TEXT DEFAULT NULL,
                    content TEXT NOT NULL,
                    date_created TEXT NOT NULL DEFAULT (datetime('now')),
                    date_updated TEXT DEFAULT NULL,
                    --
                    CONSTRAINT uk_memori_conversation_message_conversation_id UNIQUE (conversation_id, id),
                    CONSTRAINT uk_memori_conversation_message_uuid UNIQUE (uuid),
                    --
                    CONSTRAINT fk_memori_conv_msg_conv
                       FOREIGN KEY (conversation_id)
                        REFERENCES memori_conversation (id)
                         ON DELETE CASCADE
                )
            """,
        },
    ]
}
