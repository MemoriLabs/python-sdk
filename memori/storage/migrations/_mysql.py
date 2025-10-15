r"""
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                         by GibsonAI
                       trymemori.com
"""

migrations = {
    1: [
        {
            "description": "create table memori_schema_version",
            "operation": """
                create table if not exists memori_schema_version(
                    num bigint not null primary key
                )
            """,
        },
        {
            "description": "create table memori_session",
            "operation": """
                create table if not exists memori_session(
                    id bigint not null auto_increment,
                    uuid varchar(36) not null,
                    date_created datetime not null default current_timestamp,
                    date_updated datetime default null on update current_timestamp,
                    --
                    primary key (id),
                    unique key (uuid)
                )
            """,
        },
        {
            "description": "create table memori_conversation",
            "operation": """
                create table if not exists memori_conversation(
                    id bigint not null auto_increment,
                    uuid varchar(36) not null,
                    session_id bigint not null,
                    date_created datetime not null default current_timestamp,
                    date_updated datetime default null on update current_timestamp,
                    --
                    primary key (id),
                    unique key (session_id),
                    unique key (uuid),
                    --
                    constraint fk_memori_conv_session
                   foreign key (session_id)
                    references memori_session (id)
                )
            """,
        },
        {
            "description": "create table memori_conversation_message",
            "operation": """
                create table if not exists memori_conversation_message(
                    id bigint not null auto_increment,
                    uuid varchar(36) not null,
                    conversation_id bigint not null,
                    role varchar(255) not null,
                    type varchar(255) default null,
                    content text not null,
                    date_created datetime not null default current_timestamp,
                    date_updated datetime default null on update current_timestamp,
                    --
                    primary key (id),
                    unique key (conversation_id, id),
                    unique key (uuid),
                    --
                    constraint fk_memori_conv_msg_conv
                   foreign key (conversation_id)
                    references memori_conversation (id)
                )
            """,
        },
    ]
}
