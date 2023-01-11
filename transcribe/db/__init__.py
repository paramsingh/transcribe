import sqlite3

connection = None


def init_db() -> sqlite3.Connection:
    global connection
    # TODO: this path needs to be a config option.
    if connection is None:
        connection = sqlite3.connect("database.db")
    return connection


def create_tables() -> None:
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transcription (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid            TEXT NOT NULL,
            link            TEXT NOT NULL,
            result          TEXT,
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS transcription_uuid_ndx ON prompt(uuid);
        CREATE UNIQUE INDEX IF NOT EXISTS transcription_link_ndx ON prompt(link);
    """
    )
    connection.commit()
    connection.close()
