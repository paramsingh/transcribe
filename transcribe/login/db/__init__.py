def create_user_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid            TEXT NOT NULL,
            email           TEXT NOT NULL,
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS user_uuid_ndx ON user(uuid);")

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS user_email_ndx ON user(email);")


def create_session_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS session (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid            TEXT NOT NULL,
            user_uuid       TEXT NOT NULL,
            expires_at      TIMESTAMP,
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS session_uuid_ndx ON session(uuid);")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS session_user_uuid_ndx ON session(user_uuid);")
