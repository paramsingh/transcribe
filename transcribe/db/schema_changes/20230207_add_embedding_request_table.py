from transcribe.db import init_db


def main():
    print("Creating embedding_request table...")
    connection = init_db()
    cursor = connection.cursor()
    # embedding request tabls
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embedding_request (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id    INTEGER NOT NULL,
            created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transcription_id) REFERENCES transcription(id)
        );
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS embedding_request_ndx ON embedding_request(transcription_id);
    """)
    print("Done!")


if __name__ == "__main__":
    main()
