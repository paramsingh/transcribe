from transcribe.db import init_db


def main():
    print("Creating user_transcription_attempt table...")
    connection = init_db()
    cursor = connection.cursor()
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
    print("Done!")


if __name__ == "__main__":
    main()
