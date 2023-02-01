def create_user_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         TEXT NOT NULL,
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
            session_id      TEXT NOT NULL,
            user_id         TEXT NOT NULL,
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS session_uuid_ndx ON session(uuid);")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS session_user_uuid_ndx ON session(user_uuid);")


def create_magic_link_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS magic_link (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            link_token      TEXT NOT NULL,
            user_id         INTEGER NOT NULL,
            session_id      INTEGER,
            redeemed        BOOLEAN DEFAULT 0,
            redeemed_at     TIMESTAMP,
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            FOREIGN KEY (user_id) REFERENCES user(id)
            FOREIGN KEY (session_id) REFERENCES session(id)
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS magic_link_uuid_ndx ON magic_link(uuid);")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS magic_link_session_id_ndx ON magic_link(session_id);")
