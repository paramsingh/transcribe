from transcribe.db import init_db


def main():
    print("Creating embedding table...")
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embedding (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id    INTEGER NOT NULL,
            embedding_json      TEXT NOT NULL,
            created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX
              IF NOT EXISTS embedding_ndx
                         ON embedding(transcription_id);
    """)
    print("Done!")


if __name__ == "__main__":
    main()
