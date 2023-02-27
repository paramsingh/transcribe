import sqlite3
from transcribe.login.db import create_user_table, create_session_table, create_magic_link_table


def init_db(database_filename: str = "database.db") -> sqlite3.Connection:
    connection = sqlite3.connect(database_filename, detect_types=sqlite3.PARSE_DECLTYPES |
                                 sqlite3.PARSE_COLNAMES)
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transcription (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            token               TEXT NOT NULL,
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
        CREATE UNIQUE INDEX IF NOT EXISTS transcription_uuid_ndx ON transcription(token);
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_transcription_attempt (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER NOT NULL,
            transcription_id    INTEGER NOT NULL,
            created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (transcription_id) REFERENCES transcription(id)
        );
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX
              IF NOT EXISTS user_transcription_attempt_ndx
                         ON user_transcription_attempt(user_id, transcription_id);
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embedding (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id    INTEGER NOT NULL,
            embedding_json      TEXT NOT NULL,
            created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX
              IF NOT EXISTS embedding_ndx
                         ON embedding(transcription_id);
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcription_group (
            group_id            INTEGER NOT NULL,
            transcription_id    INTEGER NOT NULL
        );
    """)

    connection.commit()
