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
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE memori_schema_version(
                            num NUMBER(19) NOT NULL PRIMARY KEY
                        )
                    ';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN NULL; -- ORA-00955: name is already used
                        ELSE RAISE;
                        END IF;
                END;
            """,
        },
        {
            "description": "create table memori_parent",
            "operation": """
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE memori_parent(
                            id NUMBER(19) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            uuid VARCHAR2(36) NOT NULL,
                            external_id VARCHAR2(100) NOT NULL,
                            date_created TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                            date_updated TIMESTAMP DEFAULT NULL,
                            CONSTRAINT uk_memori_parent_external_id UNIQUE (external_id),
                            CONSTRAINT uk_memori_parent_uuid UNIQUE (uuid)
                        )
                    ';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN NULL;
                        ELSE RAISE;
                        END IF;
                END;
            """,
        },
        {
            "description": "create table memori_process",
            "operation": """
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE memori_process(
                            id NUMBER(19) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            uuid VARCHAR2(36) NOT NULL,
                            external_id VARCHAR2(100) NOT NULL,
                            date_created TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                            date_updated TIMESTAMP DEFAULT NULL,
                            CONSTRAINT uk_memori_process_external_id UNIQUE (external_id),
                            CONSTRAINT uk_memori_process_uuid UNIQUE (uuid)
                        )
                    ';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN NULL;
                        ELSE RAISE;
                        END IF;
                END;
            """,
        },
        {
            "description": "create table memori_session",
            "operation": """
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE memori_session(
                            id NUMBER(19) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            uuid VARCHAR2(36) NOT NULL,
                            parent_id NUMBER(19) DEFAULT NULL,
                            process_id NUMBER(19) DEFAULT NULL,
                            date_created TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                            date_updated TIMESTAMP DEFAULT NULL,
                            CONSTRAINT uk_memori_session_parent_id UNIQUE (parent_id, id),
                            CONSTRAINT uk_memori_session_process_id UNIQUE (process_id, id),
                            CONSTRAINT uk_memori_session_uuid UNIQUE (uuid),
                            CONSTRAINT fk_memori_sess_parent
                               FOREIGN KEY (parent_id)
                                REFERENCES memori_parent (id)
                                 ON DELETE CASCADE,
                            CONSTRAINT fk_memori_sess_process
                               FOREIGN KEY (process_id)
                                REFERENCES memori_process (id)
                                 ON DELETE CASCADE
                        )
                    ';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN NULL;
                        ELSE RAISE;
                        END IF;
                END;
            """,
        },
        {
            "description": "create table memori_conversation",
            "operation": """
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE memori_conversation(
                            id NUMBER(19) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            uuid VARCHAR2(36) NOT NULL,
                            session_id NUMBER(19) NOT NULL,
                            date_created TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                            date_updated TIMESTAMP DEFAULT NULL,
                            CONSTRAINT uk_memori_conversation_session_id UNIQUE (session_id),
                            CONSTRAINT uk_memori_conversation_uuid UNIQUE (uuid),
                            CONSTRAINT fk_memori_conv_session
                               FOREIGN KEY (session_id)
                                REFERENCES memori_session (id)
                                 ON DELETE CASCADE
                        )
                    ';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN NULL;
                        ELSE RAISE;
                        END IF;
                END;
            """,
        },
        {
            "description": "create table memori_conversation_message",
            "operation": """
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE memori_conversation_message(
                            id NUMBER(19) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            uuid VARCHAR2(36) NOT NULL,
                            conversation_id NUMBER(19) NOT NULL,
                            role VARCHAR2(255) NOT NULL,
                            type VARCHAR2(255) DEFAULT NULL,
                            content CLOB NOT NULL,
                            date_created TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                            date_updated TIMESTAMP DEFAULT NULL,
                            CONSTRAINT uk_memori_conversation_message_conversation_id UNIQUE (conversation_id, id),
                            CONSTRAINT uk_memori_conversation_message_uuid UNIQUE (uuid),
                            CONSTRAINT fk_memori_conv_msg_conv
                               FOREIGN KEY (conversation_id)
                                REFERENCES memori_conversation (id)
                                 ON DELETE CASCADE
                        )
                    ';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN NULL;
                        ELSE RAISE;
                        END IF;
                END;
            """,
        },
    ]
}
