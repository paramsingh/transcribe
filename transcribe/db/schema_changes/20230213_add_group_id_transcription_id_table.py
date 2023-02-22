from transcribe.db import init_db


def main():
    print("Creating group, transcription relationship table...")
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcription_group (
            group_id            INTEGER NOT NULL,
            transcription_id    INTEGER NOT NULL
        );
    """)
    # Create foreign key constraints when we move to PostgreSQL for easy cleanup
    print("Done!")


if __name__ == "__main__":
    main()
