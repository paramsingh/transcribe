def create_user_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            token           TEXT NOT NULL,
            email           TEXT NOT NULL,
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS user_token_ndx ON user(token);")

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS user_email_ndx ON user(email);")


def create_session_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS session (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            token                   TEXT NOT NULL,
            user_id                 TEXT NOT NULL,
            created                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logged_out              BOOLEAN DEFAULT 0,
            logged_out_at           TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS session_token_ndx ON session(token);")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS session_user_id_ndx ON session(user_id);")


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
            created         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (session_id) REFERENCES session(id)
        );
        """
    )

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS magic_link_token_ndx ON magic_link(link_token);")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS magic_link_session_id_ndx ON magic_link(session_id);")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS magic_link_user_id_ndx ON magic_link(user_id);")
