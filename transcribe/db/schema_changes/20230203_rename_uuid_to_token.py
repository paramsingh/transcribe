from transcribe.db import init_db


def main():
    """Add a column to the transcription table."""
    print("Renaming column uuid to token!")
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        ALTER TABLE transcription RENAME COLUMN uuid TO token;
    """
    )
    connection.commit()
    connection.close()
    print("Done!")


if __name__ == "__main__":
    main()
