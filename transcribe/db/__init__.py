import sqlite3
from transcribe.login.db import create_user_table, create_session_table, create_magic_link_table


def init_db() -> sqlite3.Connection:
    # TODO: this path needs to be a config option.
    connection = sqlite3.connect("database.db", detect_types=sqlite3.PARSE_DECLTYPES |
                                 sqlite3.PARSE_COLNAMES)
    return connection


def create_tables() -> None:
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transcription (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid                TEXT NOT NULL,
            link                TEXT NOT NULL,
            result              TEXT,
            created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            improvement         TEXT,
            summary             TEXT,
            improvement_failed  BOOLEAN DEFAULT 0,
            transcribe_failed   BOOLEAN DEFAULT 0,
            user_id             INTEGER,
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
    """
    )

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS transcription_uuid_ndx ON transcription(uuid);
    """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS transcription_link_ndx ON transcription(link);
    """
    )
    create_user_table(cursor)
    create_session_table(cursor)
    create_magic_link_table(cursor)
    connection.commit()
    connection.close()
